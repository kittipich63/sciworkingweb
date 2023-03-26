from django.db import models

STATUS_CHOICES = (
    ('เปิด', 'เปิด'),
    ('ปิด', 'ปิด'),
)

class MyRoom(models.Model):
    room_name = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default="เปิด")

    class Meta:
        db_table = 'room'

    def __str__(self):
        return self.room_name

