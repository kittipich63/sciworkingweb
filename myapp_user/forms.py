from myapp_user.models import *
from myapp_admin.models import *
from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.forms.widgets import TextInput, Select
from datetime import datetime, timedelta, time
from django.utils.timezone import make_aware
from django.db.models import Q

class BookingModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room'].queryset = MyRoom.objects.filter(status='เปิด')

    class Meta:
        model = Booking
        fields = ['room', 'date', 'start_time', 'end_time', 'reason']
        labels = {
            'room': 'เลือกห้อง',
            'date': 'เลือกวันที่',
            'start_time': 'เวลาเริ่มต้น',
            'end_time': 'เวลาสิ้นสุด',
            'reason': 'เหตุผลการจอง',
        }
        widgets = {
            'room': Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control datepicker','type': 'date'}),
            'start_time': forms.Select(choices=[(f"{i:02}:{j:02}", f"{i:02}:{j:02}") for i in range(8, 23) for j in [0, 30]], attrs={'class': 'form-control'}),
            'end_time': forms.Select(choices=[(f"{i:02}:{j:02}", f"{i:02}:{j:02}") for i in range(8, 24) for j in [0, 30] if i != 8 or j == 30], attrs={'class': 'form-control'}),
            'reason': TextInput(attrs={'class': 'form-control','placeholder': 'เหตุผลการจอง'})
        }
        

    def clean(self):
            cleaned_data = super().clean()
            start_time = cleaned_data.get("start_time")
            end_time = cleaned_data.get("end_time")
            room = cleaned_data.get("room")
            date = cleaned_data.get("date")

            #ตรวจสอบเวลาเริ่มและเวลาสิ้นสุด
            if start_time and end_time and end_time <= start_time:
                raise forms.ValidationError(_("เวลาเริ่มต้นต้องก่อนเวลาสิ้นสุด"))

            #ตรวจสอบการจอง
            if room and date and start_time and end_time:
                bookings = Booking.objects.filter(
                    status="อนุมัติ",
                    room=room,
                    date=date,
                    start_time__lt=end_time,
                    end_time__gt=start_time
                )
                if self.instance:
                    bookings = bookings.exclude(pk=self.instance.pk)
                if bookings.exists():
                    raise ValidationError(_("ห้องนี้มีการจองแล้วในวันหรือช่วงเวลานี้"))
                
            #ตรวจสอบเวลาในการจอง
            start_datetime = make_aware(datetime.combine(date, start_time))
            end_datetime = make_aware(datetime.combine(date, end_time))
            duration = end_datetime - start_datetime
            if duration > timedelta(hours=2):
                raise forms.ValidationError(_("การจองต้องไม่เกิน 2 ชั่วโมง"))
            
            #ตรวจสอบวันในการจอง
            if date and date < timezone.localdate():
                raise ValidationError("ไม่สามารถจองย้อนหลังได้")

            return cleaned_data