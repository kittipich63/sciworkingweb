from datetime import datetime, timedelta
from django.shortcuts import render, redirect , get_object_or_404
from myapp_user.forms import *
from myapp_user.models import *
from myapp_admin.models import *
from django.contrib.auth.models import User
from .models import *
from .forms import *
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
import requests
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookHandler ,WebhookParser

#ปฎิทิน
def CalendarView(req):
    template_name = 'pages/calendar.html'
    All_room = MyRoom.objects.filter(status="เปิด")
    context = {
        "All_room" : All_room,
    }
    return render(req, template_name, context)

#ดึงการจองมาแสดง
def get_events(req):
    events = []
    for booking in Booking.objects.filter(status="อนุมัติ"):
        event = {
            'ID': booking.id,
            'title': f' | {booking.user.stdID} , ห้อง {booking.room.room_name}',
            'start': booking.date.strftime('%Y-%m-%d') + 'T' + booking.start_time.strftime('%H:%M:%S'),
            'end': booking.date.strftime('%Y-%m-%d') + 'T' + booking.end_time.strftime('%H:%M:%S'),
            'room':booking.room.room_name,
        }
        events.append(event)
    return JsonResponse(events, safe=False)

#ข้อมูลส่วนตัว
@login_required
def user_profile(req):
    return render(req, 'pages/user_profile.html') 

@login_required
def user_std(req,id):
    obj = User.objects.get(id=id)
    obj.stdID = req.POST['stdID']
    obj.save()
    messages.success(req, "เพิ่มรหัสนักศึกษาสำเร็จ")
    return redirect('/user_profile') 

#เพิ่มการจอง
@login_required
def addbooking(req):
    # Check if user is allowed to make a booking
    if req.user.status == "ไม่อนุญาต" or req.user.stdID is None or req.user.right == "ไม่อนุญาต":
        return redirect('/')
    
    
    
    if req.method == 'POST':
        bookingform = BookingModelForm(req.POST, initial={'user': req.user})
        if bookingform.is_valid():
            booking = bookingform.save(commit=False)
            booking.user = req.user
            booking.line_user_id = req.user.line_user_id
            booking.save()
            formatted_date = booking.date.strftime('%d/%m/%y')
            formatted_start_time = booking.start_time.strftime('%H:%M')
            formatted_end_time = booking.end_time.strftime('%H:%M')
            message = f"{booking.user.stdID} ได้ทำการจองห้อง {booking.room.room_name} วันที่ {formatted_date} เวลา {formatted_start_time} - {formatted_end_time} เรียบร้อย"
            send_line_message(booking.line_user_id, message)
            messages.success(req, "ทำการจองสำเร็จ")
            return redirect('user_mybooking')   
    else:
        bookingform = BookingModelForm()
    context = {
        'bookingform': bookingform
    }            
    return render(req, 'pages/addbooking.html', context)

#แก้ไขการจอง
@login_required
def user_mybooking_edit(req, id):
    if req.user.status == "ไม่อนุญาต" or req.user.stdID is None or req.user.right == "ไม่อนุญาต":
        return redirect('/')
    booking = Booking.objects.get(id=id)
    form = BookingModelForm(instance=booking) 
    if req.method == 'POST':
        form = BookingModelForm(req.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(req, "แก้ไขการจองสำเร็จ")
            return redirect('user_mybooking')
    context = {
        "booking" : booking,
        "form" : form
    }
    return render(req, 'pages/user_mybooking_edit.html', context)


#ลบการจอง
@login_required
def user_mybooking_delete(req, id):
    if req.user.status == "ไม่อนุญาต" or req.user.stdID is None or req.user.right == "ไม่อนุญาต":
        return redirect('/')
    obj = Booking.objects.get(id=id)
    obj.delete()
    messages.success(req, "ลบการจองสำเร็จ")
    return redirect('/user_mybooking')

#การจองของฉัน
@login_required
def user_mybooking(req):
    if req.user.status == "ไม่อนุญาต" or req.user.stdID is None :
        return redirect('/')
    Bookings = Booking.objects.all()
    bookings = Booking.objects.filter(user=req.user).order_by('status')
    # Paginate objects
    items_per_page = 100
    paginator = Paginator(bookings, items_per_page)
    page_number = req.GET.get('page', 1)
    page = paginator.get_page(page_number)
    try:
        page = paginator.page(page_number)
    except:
        page = paginator.page(1) 
    # Pass data to the template
    context = {
        'page' :page,
        'Bookings': Bookings,
    }
    return render(req, 'pages/user_mybooking.html', context)

# ============================================== LINE ================================================ #
# Function to send a Line message
def send_line_message(user_id, message):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {settings.LINE_ACCESS_TOKEN}'
    }
    data = {
        'to': user_id,
        'messages': [
            {
                'type': 'text',
                'text': message
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    
#เตือนการจองเมื่อใกล้ถึงและสิ้นสุดการจอง
#ยังไม่สำเร็จ

def send_booking_notifications():
    # Get current time
    now = timezone.now()
    # Get bookings with status 'อนุมัติ' and start time within the next 10 minutes
    bookings = Booking.objects.filter(status='อนุมัติ', start_time__range=(now, now+timedelta(minutes=10)))
    for booking in bookings:
        # Calculate time remaining until start time
        time_until_start = booking.start_time - now
        minutes_until_start = time_until_start.seconds // 60
        # Send notification if time remaining is 10 minutes or less
        if minutes_until_start <= 10:
            message = f"Your booking for {booking.room.room_name} will start in {minutes_until_start} minutes."
            send_line_message(booking.line_user_id, message)
        # Calculate time remaining until end time
        time_until_end = booking.end_time - now
        minutes_until_end = time_until_end.seconds // 60
        # Send notification if time remaining is 10 minutes or less
        if minutes_until_end <= 10:
            message = f"Your booking for {booking.room.room_name} will end in {minutes_until_end} minutes."
            send_line_message(booking.line_user_id, message)


# ---------------------------- Line ------------------------------------#
@login_required
def bind_line_user(req, user_id):
    # Retrieve the User object associated with the current request
    user = req.user

    # Update the User object with the Line user ID
    user.line_user_id = user_id
    user.save()
    message = f"ผูก Line สำเร็จ"
    send_line_message(user.line_user_id, message)
    messages.success(req, 'ผูกบัญชี Line สำเร็จ')

    # Redirect the user to a confirmation page
    return redirect('/user_profile')

@login_required
def line_user_bound(req):
    return render(req, 'pages/line_user_bound.html')