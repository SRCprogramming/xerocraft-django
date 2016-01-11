
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.generic import View
from members.models import Member, Tag, Tagging, VisitEvent, PaidMembership
from members.forms import Desktop_ChooseUserForm, Books_NotePaymentForm
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF
from reportlab.lib.units import inch, mm
from reportlab.lib.pagesizes import letter
from dateutil import relativedelta

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = PRIVATE

def _inform_other_systems_of_checkin(member, event_type):
    # TODO: Inform Kyle's system
    pass


# TODO: Move following to Event class?
def _log_visit_event(member_card_str, event_type):

    is_valid_evt = event_type in [x for (x,_) in VisitEvent.VISIT_EVENT_CHOICES]
    if not is_valid_evt:
        return False, "Invalid event type."

    member = Member.get_by_card_str(member_card_str)
    if member is None:
        return False, "No matching member found."
    else:
        VisitEvent.objects.create(who=member, event_type=event_type)
        _inform_other_systems_of_checkin(member, event_type)
        return True, member


# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = API

def api_member_details(request, member_card_str, staff_card_str):
    """ Respond with corresponding user/member info given the membership card string in the QR code. """

    success, info = Member.get_for_staff(member_card_str, staff_card_str)

    if not success:
        error_msg = info
        return JsonResponse({'error':error_msg})

    member, staff = info
    data = {
        'pk': member.pk,
        'is_active': member.is_active,
        'username': member.username,
        'first_name': member.first_name,
        'last_name': member.last_name,
        'email': member.email,
        'tags': [tag.name for tag in member.tags.all()]
    }
    return JsonResponse(data)


def api_member_details_pub(request, member_card_str):
    """ Respond with corresponding user/member tags given the membership card string. """

    subject = Member.get_by_card_str(member_card_str)

    if subject is None:
        return JsonResponse({'error':"Invalid member card string"})

    data = {
        'pk': subject.pk,
        'is_active': subject.is_active,
        'tags': [tag.name for tag in subject.tags.all()]
    }
    return JsonResponse(data)


def api_log_visit_event(request, member_card_str, event_type):

    success, result = _log_visit_event(member_card_str, event_type)
    if success:
        return JsonResponse({'success': "Visit event logged"})
    else:
        return JsonResponse({'error': result})


# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = DESKTOP

@login_required
def create_card(request):
    download_url = reverse('memb:create-card-download')
    params = {'download_url':download_url}
    return render(request, 'members/create-card.html', params)


@login_required
def create_card_download(request):

    filename = "member_card_%s.pdf" % request.user.username

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    member = request.user.member

    b64 = member.generate_member_card_str()

    # Produce PDF using ReportLab:
    p = canvas.Canvas(response, pagesize=letter)
    pageW, pageH = letter

    # Business card size is 2" x 3"
    # Credit card size is 2.2125" x 3.370"
    card_width = 2.125*inch
    card_height = 3.370*inch
    card_corner_r = 3.0*mm

    refX = pageW/2.0
    refY = 7.25*inch

    # Some text to place near the top of the page.
    p.setFont("Helvetica", 16)
    p.drawCentredString(refX, refY+3.00*inch, 'This is your new Xerocraft membership card.')
    p.drawCentredString(refX, refY+2.75*inch, 'Always bring it with you when you visit Xerocraft.')
    p.drawCentredString(refX, refY+2.50*inch, 'The rectangle is credit card sized, if you would like to cut it out.')
    p.drawCentredString(refX, refY+2.25*inch, 'If you have any older cards, they have been deactivated.')

    # Changing refY allows the following to be moved up/down as a group, w.r.t. the text above.
    refY -= 0.3*inch

    # Most of the wallet size card:
    p.roundRect(refX-card_width/2, refY-1.34*inch, card_width, card_height, card_corner_r)
    p.setFont("Helvetica", 21)
    p.drawCentredString(refX, refY-0.3*inch, 'XEROCRAFT')
    p.setFontSize(16)
    p.drawCentredString(refX, refY-0.65*inch, member.first_name)
    p.drawCentredString(refX, refY-0.85*inch, member.last_name)
    p.setFontSize(12)
    p.drawCentredString(refX, refY-1.2 *inch, date.today().isoformat())

    # QR Code:
    qr = QrCodeWidget(b64)
    qrSide = 2.3*inch # REVIEW: This isn't actually 2.3 inches.  What is it?
    bounds = qr.getBounds()
    qrW = bounds[2] - bounds[0]
    qrH = bounds[3] - bounds[1]
    drawing = Drawing(1000,1000,transform=[qrSide/qrW, 0, 0, qrSide/qrH, 0, 0])
    drawing.add(qr)
    renderPDF.draw(drawing, p, refX-qrSide/2, refY-0.19*inch)

    p.showPage()
    p.save()
    return response


@login_required()
def member_tags(request, tag_pk=None, member_pk=None, op=None):

    staff = request.user.member
    member = None if member_pk is None else Member.objects.get(pk=member_pk)

    if member is not None and tag_pk is not None and op is not None:
        tag = Tag.objects.get(pk=tag_pk)
        if op == "+": Tagging.add_if_permitted(staff, member, tag)
        if op == "-": Tagging.remove_if_permitted(staff, member, tag)

    staff_can_tags = None
    staff_addable_tags = None
    members_tags = None

    if request.method == 'POST':  # Process the form data.
        form = Desktop_ChooseUserForm(request.POST)
        if form.is_valid():
            member_id = form.cleaned_data["userid"]
            member = Member.get_local_member(member_id)
        else:
            # We get here if the userid field was blank.
            member = None

    else:  # If a GET (or any other method) we'll create a blank form.
        username = None if member is None else member.username
        form = Desktop_ChooseUserForm(initial={'userid': username})

    if member is not None:
        members_tags = member.tags.all()
        staff_can_tags = [tagging.tag for tagging in Tagging.objects.filter(can_tag=True, tagged_member=staff)]
        staff_addable_tags = list(staff_can_tags) # copy contents, not pointer.
        # staff member can't add tags that member already has, so:
        for tag in member.tags.all():
            if tag in staff_addable_tags:
                staff_addable_tags.remove(tag)

    today = date.today()
    visits = VisitEvent.objects.filter(when__gt=today)
    visitors = [visit.who for visit in visits]

    return render(request, 'members/desktop-member-tags.html', {
        'form': form,
        'staff': staff,
        'member': member,
        'members_tags': members_tags,
        'staff_can_tags': staff_can_tags,
        'staff_addable_tags': staff_addable_tags,
        'visitors': set(visitors),
    })


# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = KIOSK

def kiosk_waiting(request):
    return render(request, 'members/kiosk-waiting.html',{})


def kiosk_visitevent_contentprovider(f):
    Kiosk_LogVisitEvent.extra_content_providers.append(f)
    return f


class Kiosk_LogVisitEvent(View):

    extra_content_providers = []

    def get(self, request, *args, **kwargs):
        member_card_str = kwargs['member_card_str']
        event_type = kwargs['event_type']

        success, result = _log_visit_event(member_card_str, event_type)
        if success:
            member = result
            actions = {
                VisitEvent.EVT_ARRIVAL:   "checked in",
                VisitEvent.EVT_DEPARTURE: "checked out",
                VisitEvent.EVT_PRESENT:   "made your presence known",
            }
            assert len(actions) == len(VisitEvent.VISIT_EVENT_CHOICES)

            extra_content = ""
            for f in self.extra_content_providers:
                extra_content += f(member, member_card_str, event_type)

            params = {
                "username" : member.username,
                "action"   : actions.get(event_type),
                "extra_content" : extra_content
            }
            return render(request, 'members/kiosk-check-in-member.html', params)
        else:
            # TODO: This needs to use a more generic error template.
            error_msg = result
            return render(request, 'members/kiosk-invalid-card.html', {})


def kiosk_member_details(request, member_card_str, staff_card_str):

    success, info = Member.get_for_staff(member_card_str, staff_card_str)

    if not success:
        return render(request, 'members/kiosk-invalid-card.html', {}) #TODO: use kiosk-domain-error template?

    member, staff = info
    staff_can_tags = [ting.tag for ting in Tagging.objects.filter(can_tag=True,tagged_member=staff)]
    # staff member can't add tags that member already has, so:
    for tag in member.tags.all():
        if tag in staff_can_tags:
            staff_can_tags.remove(tag)

    return render(request, 'members/kiosk-member-details.html',{
        "staff_card_str" : staff_card_str,
        "staff_fname" : staff.first_name,
        "memb_fname" : member.first_name,
        "memb_name" : "%s %s" % (member.first_name, member.last_name),
        "username" : member.username,
        "email" : member.email,
        "members_tags" : member.tags.all(),
        "staff_can_tags" : staff_can_tags,
    })


def kiosk_add_tag(request, member_card_str, staff_card_str, tag_pk):
    # We only get to this view from a link produced by a previous view.
    # This view assumes that the previous view is passing valid strs and pk.
    # Any exceptions raised in this view can be considered programming errors and are not caught.
    # This view DOES NOT use member PKs even though the previous view could provide them.
    # Using PKs would make this view vulnerable to brute force attacks to create unauthorized taggings.

    success, info = Member.get_for_staff(member_card_str, staff_card_str)

    if not success:
        error_msg = info
        return HttpResponse("Error: %s." % error_msg) #TODO: Use kiosk-domain-error template?

    tag = Tag.objects.get(pk=tag_pk)

    member, staff = info

    # The following can be considered an assertion that the given staff member is authorized to grant the given tag.
    Tagging.objects.get(can_tag=True,tagged_member=staff,tag=tag)

    # Create the new tagging and then go back to the member details view.
    Tagging.objects.create(tagged_member=member, authorizing_member=staff, tag=tag)
    return redirect('..')


def kiosk_main_menu(request, member_card_str):
    member = Member.get_by_card_str(member_card_str)

    if member is None:
        return render(request, 'members/kiosk-invalid-card.html',{}) #TODO: use kiosk-domain-error template?

    params = {
        "memb_fname"    : member.first_name,
        "memb_card_str" : member_card_str,
        "memb_is_staff" : member.is_tagged_with("Staff"),
        "evt_arrival"   : VisitEvent.EVT_ARRIVAL,
        "evt_departure" : VisitEvent.EVT_DEPARTURE,
    }
    return render(request, 'members/kiosk-main-menu.html', params)

def kiosk_staff_menu(request, member_card_str):

    member = Member.get_by_card_str(member_card_str)
    if member is None or not member.is_domain_staff():
        return render(request, 'members/kiosk-invalid-card.html',{}) #TODO: use kiosk-domain-error template?

    params = {
        "memb_fname" : member.first_name,
        "memb_card_str" : member_card_str
    }
    return render(request, 'members/kiosk-staff-menu.html', params)

def kiosk_identify_subject(request, staff_card_str, next_url):

    member = Member.get_by_card_str(staff_card_str)
    if member is None or not member.is_domain_staff():
        return render(request, 'members/kiosk-invalid-card.html',{}) #TODO: use kiosk-domain-error template?

    params = {
        "staff_card_str" : staff_card_str,
        "next_url" : next_url
    }
    return render(request, 'members/kiosk-identify-subject.html', params)


# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = BOOKS

# This is not meant for human users. Instead, processes running somewhere
# other than the website will be logging into our payment processing systems,
# extracting payment information, transforming it into this format, and then
# loading it into the website via this view. This keeps userids/pws for
# payment processing systems off the website.

PAYMENT_METHOD_STR2CODE = {string: code for (code, string) in PaidMembership.PAID_BY_CHOICES}


def books_note_payment(request):

    if request.method == "POST":
        form = Books_NotePaymentForm(request.POST)
        if form.is_valid():
            userid      = form.cleaned_data["userid"]
            password    = form.cleaned_data["password"]
            amt_paid    = form.cleaned_data["amt_paid"]
            when_paid   = form.cleaned_data["when_paid"]
            service     = form.cleaned_data["service"]
            service_fee = form.cleaned_data["service_fee"]
            service_id  = form.cleaned_data["service_id"]
            duration    = form.cleaned_data["duration"]
            fname       = form.cleaned_data["fname"]
            lname       = form.cleaned_data["lname"]
            email       = form.cleaned_data["email"]
            family      = form.cleaned_data["family"]

            member = None

            try:  # EMAIL MATCHING
                email_matches = User.objects.filter(email=email)
                if len(email_matches) == 1: member = email_matches[0].member
            except User.DoesNotExist:
                pass

            try:  # NAME MATCHING
                name_matches = User.objects.filter(first_name=fname, last_name=lname)
                if len(name_matches) == 1: member = name_matches[0].member
            except User.DoesNotExist:
                pass

            if member is None:
                print(fname, lname, email)

            payer_name = fname
            if lname != "": payer_name += " "+lname

            PaidMembership.objects.create(
                member=member,
                family_count=family,
                start_date=when_paid,
                end_date=when_paid + relativedelta.relativedelta(months=1),  # TODO: Actual calc based on duration
                payer_name=payer_name,
                payer_email=email,
                paid_by_member=amt_paid,
                processing_fee=service_fee,
                ctrlid=service_id,
                payment_date=when_paid,
                payment_method=PAYMENT_METHOD_STR2CODE[service]
            )
            return JsonResponse({'result':'success'})

    else:  # If a GET (or any other method) we'll create a blank form.
        form = Books_NotePaymentForm()

    return render(request, 'members/books-note-payment.html', {'form': form})
