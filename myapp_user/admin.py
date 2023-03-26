from django.contrib import admin
from myapp_user.models import *
from django.contrib.auth.models import User

admin.site.register(Booking)


STATUS = (
    ("ผู้ดูแลระบบ", "ผู้ดูแลระบบ"),
    ("นักศึกษา", "นักศึกษา"),
)

RIGHT = (
    ("อนุญาต", "อนุญาต"),
    ("ไม่อนุญาต", "ไม่อนุญาต"),
)

User.add_to_class("status", models.CharField(max_length = 100, choices = STATUS, default = "ผู้ดูแลระบบ"))
User.add_to_class("right", models.CharField(max_length = 100, choices = RIGHT, default = "อนุญาต"))
User.add_to_class("stdID", models.CharField(max_length = 11, null=True, blank=True))
User.add_to_class("line_user_id", models.CharField(max_length = 100, null=True, blank=True))