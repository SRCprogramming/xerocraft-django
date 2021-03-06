import requests
import logging
import lxml.html
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from members.models import Member # REVIEW: I'd rather this were User from django.contrib.auth.models
from xerocraft.management.commands.scraper import Scraper


# From http://blog.shopfiber.com/?p=220.
# Note the comment regarding the need to add a case-insensitive index.
class CaseInsensitiveModelBackend(ModelBackend):
    """
    By default ModelBackend does case _sensitive_ username authentication, which isn't what is
    generally expected.  This backend supports case insensitive username authentication.
    """
    def authenticate(self, username=None, password=None):
        identifier = username  # Given username is actually a more generic identifier.

        user = Member.get_local_user(identifier)
        if user is None:
            return None
        elif user.check_password(password):
            return user
        else:
            return None


class XerocraftBackend(ModelBackend):

    def authenticate(self, username=None, password=None):

        # TODO: This would be a lot better/simpler if xerocraft.org's actions.php would offer
        # action:authenticate, SignInIdentifier:<email or username>, SignInPassword:<password>
        # that returned {auth:"yes", username:<username>, email:<email>, name:<name>} or {auth:"no"}

        identifier = username  # Given "username" is actually a more generic identifier.
        session = requests.session()
        logger = logging.getLogger("xerocraft-django")
        server = "http://www.xerocraft.org/"  # Allows easy switching to test site. IMPORTANT: Restore before commit
        action_url = server+"actions.php"

        # Try logging in to xerocraft.org to authenticate given username and password:
        postdata = {'SignInUsername':identifier, 'SignInPassword':password, 'action':'signin'}
        response = session.post(action_url, postdata)
        if response.text.find('<a href="./index.php?logout=true">[Logout?]</a>') == -1:
            # xerocraft.org said there's no such identifier/password.
            return None

        # At this point we know that the id/pw authenticated on remote xerocraft.
        # So we use Scraper to scrape it which will result in new or updated local account.
        try:  # to parse out the usernum
            usernum_seek = 'profiles.php?id='
            usernum_start = response.text.find(usernum_seek)
            if usernum_start == -1: raise AssertionError("Couldn't find start of usernum")
            usernum_end = response.text.find('"', usernum_start)
            if usernum_end == -1: raise AssertionError("Couldn't find end of usernum")
            usernum = response.text[usernum_start+len(usernum_seek):usernum_end]
            if not usernum.isdigit(): raise AssertionError("Didn't find a numeric usernum")
        except (AssertionError, requests.HTTPError) as err:
            logger.error(str(err))
            return None

        # Reuse the Scraper's logic to create a user for this usernum.
        scraper = Scraper()
        if scraper.login():  # Logs in using admin acct in its own requests.session.
            user = scraper.scrape_profile(usernum)
            scraper.logout()
        else:
            # scraper will log failure to login, so we don't do so here.
            # REVIEW: Is there any way to inform the person trying to log in?
            return None

        assert(user is not None)
        # Scraper doesn't have access to pws, so they need to be synched by this authenticator.
        password_before = user.password
        user.set_password(password)
        if password_before != user.password:
            user.save()
            logger.info("Updated password for %s.", user.username)

        # Xerocraft.org SERVER maintains a "logged in status" for display
        # to other users. So explicitly log out to prevent that.
        response = session.get(server+"index.php?logout=true")
        if response.text.find('<u>Sign In Options</u>') == -1:
            logger.error("Unexpected response from xerocraft.org logout.")

        return user
