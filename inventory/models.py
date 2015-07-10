from django.db import models

from pytz import timezone
import datetime

# Create your models here.

class Location(models.Model):

    x = models.FloatField(null=True, blank=True,
        help_text="An ordinate in some coordinate system to help locate the location.")
    y = models.FloatField(null=True, blank=True,
        help_text="An ordinate in some coordinate system to help locate the location.")
    z = models.FloatField(null=True, blank=True,
        help_text="An ordinate in some coordinate system to help locate the location.")
    short_desc = models.CharField(max_length=40,
        help_text="A short description/name for the location.")
    def __str__(self):
        return "L%04d, %s" % (self.pk, self.short_desc)
    class Meta:
        ordering = ['short_desc']

class ParkingPermit(models.Model):

    owner = models.ForeignKey("tasks.Member", null=False, blank=False, on_delete=models.PROTECT,
        help_text="The member who owns the parked item.")
    created = models.DateField(null=False, blank=False, auto_now_add=True,
        help_text="Date/time on which the parking permit was created.")
    #TODO: Table for renewals, so we have a complete history?
    renewed = models.DateField(null=False, blank=False, default=datetime.date.today,
        help_text="Date/time on which the parking permit was most recently renewed. Initially equal to date created.")
    short_desc = models.CharField(max_length=40, blank=False,
        help_text="A short description of the item parked.")
    ok_to_move = models.BooleanField(default=True,
        help_text="Is it OK to carefully move the item to another location, if necessary?")
    def __str__(self):
        return "#%04d, %s %s, '%s'" % (
            self.pk,
            self.owner.auth_user.first_name, self.owner.auth_user.last_name,
            self.short_desc)
    class Meta:
        ordering = ['renewed']


class PermitScan(models.Model):

    #REVIEW: Is there a good balance between Admin presentation and making these fields editable=False?
    permit = models.ForeignKey(ParkingPermit, null=False, blank=False, on_delete=models.CASCADE, related_name='scans',
        help_text="The parking permit that was scanned")
    when = models.DateTimeField(null=False, blank=False,
        help_text="Date/time on which the parking permit was created.")
    where = models.ForeignKey(Location, null=False, blank=False, on_delete=models.PROTECT,
        help_text="The location at which the parking permit was scanned.")
    def __str__(self):
        p = self.permit
        return "Permit #%04d at Location #%04d on %s" % (
            p.pk,
            self.where.pk,
            str(self.when.astimezone(timezone('US/Arizona')))[:10])
    class Meta:
        ordering = ['where','when']
