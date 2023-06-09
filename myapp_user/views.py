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
import datetime
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookHandler ,WebhookParser

#ปฎิทิน
def CalendarView(req):
    All_room = MyRoom.objects.filter(status="เปิด")
    context = {
        "All_room" : All_room,
    }
    return render(req, 'pages/calendar.html' ,context)

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

#เพิ่มรหัสนักศึกษา
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
    if req.user.right == "ไม่อนุญาต":
        messages.warning(req, "ไม่สามารถเพิ่มการจองได้ เนื่องจากถูกระงับการจอง")
        return redirect('/')
    
    # Check if user has exceeded maximum number of bookings per week
    bookings_this_week = Booking.objects.filter(
        status="อนุมัติ",
        user=req.user,
        date__gte=timezone.localdate() - datetime.timedelta(days=7)
    )
    if bookings_this_week.count() >= 3:
        messages.warning(req, "คุณจองห้องมากเกินไป ในสัปดาห์นี้คุณได้ทำการจองไปแล้ว 3 ครั้ง")
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

#การจองของฉัน
@login_required
def user_mybooking(req):
    if req.user.right == "ไม่อนุญาต" or req.user.stdID is None :
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

#แก้ไขการจอง
@login_required
def user_mybooking_edit(req, id):
    if req.user.right == "ไม่อนุญาต":
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
    if req.user.right == "ไม่อนุญาต":
        return redirect('/')
    obj = Booking.objects.get(id=id)
    obj.delete()
    messages.success(req, "ลบการจองสำเร็จ")
    return redirect('/user_mybooking')



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
    #response.raise_for_status() #ต้องเชื่อมต่อไลน์ก่อน

#ผูกบัญชี line
@login_required
def bind_line_user(req, user_id):
    # Retrieve the User object associated with the current request
    user = req.user

    # Update the User object with the Line user ID
    user.line_user_id = user_id
    user.save()
    # Send Line message to the newly connected user using the user ID
    message = f"ผูกบัญชีกับ Line สำเร็จ"
    send_line_message(user.line_user_id, message)
    messages.success(req, 'ผูกบัญชีกับ Line สำเร็จ')

    # Redirect the user to a confirmation page
    return redirect('/user_profile')




