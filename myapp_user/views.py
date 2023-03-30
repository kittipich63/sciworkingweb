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
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
import requests
from linebot.exceptions import LineBotApiError
from linebot import LineBotApi, WebhookHandler ,WebhookParser
from linebot.models import TextSendMessage ,MessageEvent, TextMessage


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
            message = f"{booking.user.stdID} ได้ทำการจองห้อง {booking.room.room_name} วันที่ {formatted_date} เวลา {formatted_start_time} - {formatted_end_time} สำเร็จ"
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

# ========== LINE ============
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
    
#เตือนการจองเมื่อใกล้ถึงและสิ้นสุดการจอง
#ยังไม่สำเร็จ

def check_booking_status():
    now = timezone.now()
    # Find all bookings that have been approved and are coming up within the next 10 minutes
    upcoming_bookings = Booking.objects.filter(status="อนุมัติ", date__gte=now.date(), start_time__gte=now.time(), start_time__lte=(now + timedelta(minutes=2)).time())
    for booking in upcoming_bookings:
        # Send a notification message to the user when the reserved time is approaching
        message = f"Reminder: Your booking for {booking.room.room_name} is starting in 10 minutes."
        send_line_message(booking.line_user_id, message)

    # Find all bookings that have been approved and are ending within the next 10 minutes
    ending_bookings = Booking.objects.filter(status="อนุมัติ", date__gte=now.date(), end_time__gte=(now - timedelta(minutes=2)).time(), end_time__lte=now.time())
    for booking in ending_bookings:
        # Send a notification message to the user when the booking is about to end
        message = f"Reminder: Your booking for {booking.room.room_name} is ending in 10 minutes."
        send_line_message(booking.line_user_id, message)

# Function to check if a booking is approaching its reserved time or its end time by 10 minutes
'''def check_booking_time():
    bookings = Booking.objects.filter(status="อนุมัติ")
    for booking in bookings:
        time_left = booking.start_time - datetime.datetime.now(datetime.timezone.utc)
        time_left_min = int(time_left.total_seconds() / 60)
        if time_left_min == 10:
            message = f"คุณ {booking.user.stdID} มีการจองห้อง {booking.room.room_name} จะเริ่มในอีก 10 นาที"
            send_line_message(booking.line_user_id, message)
        elif time_left_min == 0:
            message = f"คุณ {booking.user.stdID} มีการจองห้อง {booking.room.room_name} เริ่มในขณะนี้"
            send_line_message(booking.line_user_id, message)'''


# ---------------------------- Line ------------------------------------#
#line liff - get userid to save bind account
line_bot_api = LineBotApi('AzpZXSQ6zKvBC5hXYxtl79AkvRhtpA8Vhn9VD3bFbQD83UagJiwY33YLatoDnfn4ZuhUHWoQVJOYtHfPp7225a+hbIr2KkuG57q+UkMN7oFGggGNqnSVaeQldUd3fK3hKHP+zcKLrLNr4ntQXliMXQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('19b6f53ad25ecbd161e8a8b48d65b73d')


def line_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')

    # Send a POST request to LINE's OAuth API to exchange the authorization code for an access token
    url = 'https://api.line.me/oauth2/v2.1/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'https://yourapp.com/line/callback',
        'client_id': 'your_client_id',
        'client_secret': 'your_client_secret'
    }
    response = requests.post(url, headers=headers, data=data)
    access_token = response.json()['access_token']

    # Send a GET request to LINE's Messaging API to get the user profile
    url = 'https://api.line.me/v2/profile'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    user_id = response.json()['userId']

    # Save the user ID to the user's account in your Django app
    user = request.user
    user.line_user_id = user_id
    user.save()

    return redirect('/')


#ผูก Line เข้ากับบัญชี
def bind_user_account(request):
    user_id = None
    try:
        # Get the user ID from the LINE access token
        access_token = request.GET.get('access_token')
        user_profile = line_bot_api.get_profile(access_token)
        user_id = user_profile.user_id
    except LineBotApiError as e:
        # Handle the LineBotApiError
        print(e)

    # Bind the user ID to the user account
    if user_id:
        user = request.user
        user.line_user_id = user_id
        user.save()
        messages.success(request, "ลิงก์ LINE สำเร็จ")
    else:
        messages.error(request, "ไม่สามารถลิงก์ LINE ได้")
    
    return redirect('/')



