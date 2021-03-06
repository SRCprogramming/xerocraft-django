from django.core.management.base import BaseCommand
from django.utils.timezone import get_default_timezone_name
from members.models import VisitEvent
from datetime import date, datetime
from dateutil import relativedelta
from .scraper import Scraper, djangofy_username, SERVER, \
    USERNAME_KEY, DJANGO_USERNAME_KEY, USERNUM_KEY, FIRSTNAME_KEY, LASTNAME_KEY, EMAIL_KEY
from nameparser import HumanName
import lxml.html
import sys
from pytz import timezone

__author__ = 'adrian'

CHECKIN_DATE_KEY = "Date"
CHECKIN_TIME_KEY = "Time"
CHECKIN_TYPE_KEY = "Type"
CHECKIN_NAME_KEY = "Name"
CHECKIN_USERNAME_KEY = "Username"
CHECKIN_USERID_KEY = "User ID"
CHECKIN_EMAIL_KEY = "Email"
CHECKIN_TOTAL_KEY = "Total # of CheckIns"

CHECKIN_FIRSTNAME_KEY = "First Name"  # Infered from real name using "nameparser"
CHECKIN_LASTNAME_KEY = "Last Name"  # Infered from real name using "nameparser"
CHECKIN_DJANGO_USERNAME_KEY = "Django Username"

METHOD_CODES = {v: k for (k,v) in VisitEvent.VISIT_METHOD_CHOICES}


class CheckinScraper(Scraper):
    """ Scrape the admin checkin page on xerocraft.org"""

    def process_checkin(self, dict):

        # Scraper base class has different keys than those used in this command.
        # Translate and then process the attrs to add/update the django account, if required.
        attrs = {}
        attrs[USERNAME_KEY]        = dict[CHECKIN_USERNAME_KEY]
        attrs[DJANGO_USERNAME_KEY] = dict[CHECKIN_DJANGO_USERNAME_KEY]
        attrs[USERNUM_KEY]         = dict[CHECKIN_USERID_KEY]
        attrs[FIRSTNAME_KEY]       = dict.get(CHECKIN_FIRSTNAME_KEY, "")
        attrs[LASTNAME_KEY]        = dict.get(CHECKIN_LASTNAME_KEY, "")
        attrs[EMAIL_KEY]           = dict.get(CHECKIN_EMAIL_KEY, "")
        django_user = self.process_attrs(attrs)

        # Since it's not possible to get non-overlapping info from checkinanalytics.php
        # we check to see if we've already recorded the checkin. If not, we create it.
        checkin_dt_str = dict[CHECKIN_DATE_KEY] + " " + dict[CHECKIN_TIME_KEY]
        checkin_dt = datetime.strptime(checkin_dt_str, "%m/%d/%Y %I:%M %p")
        checkin_dt = timezone(get_default_timezone_name()).localize(checkin_dt)
        try:
            VisitEvent.objects.get(who=django_user.member, when=checkin_dt)
        except VisitEvent.DoesNotExist:
            VisitEvent.objects.create(
                who=django_user.member,
                when=checkin_dt,
                event_type=VisitEvent.EVT_ARRIVAL,
                method=METHOD_CODES[dict[CHECKIN_TYPE_KEY]],
                sync1=True,  # Because we're synching FROM xerocraft.org, it already has this event.
            )

    def temp_backfill_datestr(self, given):
        old_count = VisitEvent.objects.filter(when__year="2014", when__month="9").count()
        if old_count == 0:
            self.logger.info("Running checkin backfill.")
            return "2014-09-13"
        else:
            return given

    def start(self):

        if not self.login():
            # Problem is already logged in self.login
            return

        yesterday_str = (date.today() + relativedelta.relativedelta(days=-1)).isoformat()
        #yesterday_str = self.temp_backfill_datestr(yesterday_str)  # Backfill is done.
        today_str = date.today().isoformat()
        post_data = {"viewing": "Total", "Start": yesterday_str, "End": today_str, "submit": ""}
        response = self.session.post(SERVER+"checkinanalytics.php", data=post_data)
        response.raise_for_status()

        page_parsed = lxml.html.fromstring(response.text)
        if page_parsed is None: raise AssertionError("Couldn't parse checkin page")

        names = page_parsed.xpath("//div[@id='checkintable']//table//tr[@class='topRow']/td/text()")
        if len(names) != 8:
            names_str = " ".join(x.strip() for x in names)
            self.logger.warning("Format of check-in table has changed: %s", names_str)
            body_text = [x for x in page_parsed.xpath("//body//text()") if not x.isspace()][:10]
            text_str = " ".join(x.strip() for x in body_text)
            self.logger.warning("Body begins: %s", text_str)

        for checkin_row in page_parsed.xpath("//div[@id='checkintable']//table//tr[not(@class)]"):

            values = []
            for td in checkin_row.xpath(".//td"):
                texts = td.xpath(".//text()")
                if len(texts) > 1:
                    self.logger.warning("More text nodes than expected in cell.")
                text = "" if texts == [] else texts[0]
                values.append(text)
            attrs = dict(zip(names, values))

            if attrs[CHECKIN_TYPE_KEY] == "Guardian-Checkin":
                # There are no accounts or usernames for minors being checked in by guardians.
                continue

            if CHECKIN_NAME_KEY in attrs:
                name = HumanName(attrs[CHECKIN_NAME_KEY])
                attrs[CHECKIN_FIRSTNAME_KEY] = name.first
                attrs[CHECKIN_LASTNAME_KEY] = name.last

            attrs[CHECKIN_DJANGO_USERNAME_KEY] = djangofy_username(attrs[CHECKIN_USERNAME_KEY])

            try:
                self.process_checkin(attrs)
            except:
                # Failure on a particular check-in doesn't mean we give up on the rest.
                # Just log the error and carry on with the rest.
                # REVIEW: Might want to give up if there are "too many" errors.
                exc_info = sys.exc_info()
                #traceback.print_exception(*exc_info)
                self.logger.error("Failure while processing checkin for %s (%s), %s",
                    attrs[CHECKIN_NAME_KEY],
                    attrs[CHECKIN_USERID_KEY],
                    str(exc_info[0]))

        self.logout()


class Command(CheckinScraper, BaseCommand):

    help = "Scrapes xerocraft.org/checkinanalytics.php and creates corresponding django accts, if not already created."

    def handle(self, *args, **options):
        self.start()

