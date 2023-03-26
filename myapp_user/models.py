from django.db import models
from django.contrib.auth.models import User ,AbstractUser

from myapp_admin.models import *

STATUS_CHOICES = (
    ("รออนุมัติ", "รออนุมัติ"),
    ("ไม่อนุมัติ", "ไม่อนุมัติ"),
    ("อนุมัติ", "อนุมัติ"),
)

class LineUser(models.Model):
    line_user_id = models.CharField(max_length=50, unique=True)
    django_user_id = models.IntegerField(null=True, blank=True)


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    room = models.ForeignKey(MyRoom,related_name='name_room', on_delete=models.CASCADE,null=True)
    date = models.DateField()
    start_time = models.TimeField(max_length = 20)
    end_time = models.TimeField(max_length = 20)
    reason = models.CharField(max_length=200, null=True, blank=True)
    admin_reason = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length = 20,choices = STATUS_CHOICES,default = 'รออนุมัติ')
    date_add = models.DateField(auto_now=True)
    time_add = models.TimeField(auto_now=True)
    line_user_id = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'booking'

    def __str__(self):
        return f"Booking {self.user} for room {self.room.room_name} on {self.date}"



