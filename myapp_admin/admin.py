from django.contrib import admin
from myapp_admin.models import *
from django.contrib.auth.models import User

admin.site.register(MyRoom)


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
#User.add_to_class("Line_User_ID", models.CharField(max_length = 50, null=True, blank=True))