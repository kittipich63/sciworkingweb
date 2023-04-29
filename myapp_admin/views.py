from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from myapp_admin.forms import *
from django.contrib.auth.decorators import login_required #ใส่เพื่อให้เข้าระบบก่อนถึงจะทำรายการแต่ละอย่างได้
from .models import *
from myapp_user.models import *
from django.contrib import messages
from linebot import LineBotApi
from linebot.models import TextSendMessage
import requests
from django.conf import settings

#ข้อมูลส่วนตัว admin
@login_required
def admin_profile(req):
    if req.user.status != "ผู้ดูแลระบบ" :
        return redirect('/')
    return render(req, 'pages/admin_profile.html')    

#หน้าแรก admin
@login_required
def admin_dashboard(req):
    if req.user.status != "ผู้ดูแลระบบ" :
        return redirect('/')
    User_count = User.objects.filter(status = "นักศึกษา")
    Bookings_count = Booking.objects.filter(status="รออนุมัติ").order_by('status')
    # Paginate objects
    items_per_page = 100
    paginator = Paginator(Bookings_count, items_per_page)
    page_number = req.GET.get('page', 1)
    page = paginator.get_page(page_number)
    try:
        page = paginator.page(page_number)
    except:
        page = paginator.page(1) 
    # Pass data to the template      
    context = {
        "User_count" : User_count,
        "page" : page,
        "Bookings_count" : Bookings_count,
    }
    return render(req, 'pages/admin_dashboard.html',context)


#จัดการผู้ใช้
@login_required
def admin_user(req):
    if req.user.status != "ผู้ดูแลระบบ" :
        return redirect('/')
    AllUser = User.objects.all().order_by('status')
    # Paginate objects
    items_per_page = 100
    paginator = Paginator(AllUser, items_per_page)
    page_number = req.GET.get('page', 1)
    page = paginator.get_page(page_number)
    try:
        page = paginator.page(page_number)
    except:
        page = paginator.page(1) 
    # Pass data to the template       
    context = {
        "AllUser" : AllUser,
        "page" : page,
    }
    return render(req, 'pages/admin_user.html', context)

#แก้ไขผู้ใช้
@login_required
def admin_manage_user(req, id):
    if req.user.status != "ผู้ดูแลระบบ" :
        return redirect('/')
    obj = User.objects.get(id = id)
    obj.stdID = req.POST['stdID']
    obj.right = req.POST['right']
    obj.status = req.POST['status']
    obj.save()
    messages.success(req, "แก้ไขข้อมูลสำเร็จ")
    return redirect("/admin_user")


#ลบผู้ใช้
@login_required
def admin_delete_user(req, id):
    if req.user.status != "ผู้ดูแลระบบ" :
        return redirect('/')
    obj = User.objects.get(id=id)
    obj.delete()
    return redirect('/admin_user')    


#จัดการห้อง
@login_required
def admin_room(req):
    if req.user.status != "ผู้ดูแลระบบ" :
        return redirect('/')
    AllRoom = MyRoom.objects.all()
    # Paginate objects
    items_per_page = 100
    paginator = Paginator(AllRoom, items_per_page)
    page_number = req.GET.get('page', 1)
    page = paginator.get_page(page_number)
    try:
        page = paginator.page(page_number)
    except:
        page = paginator.page(1)       
    context = {
        "AllRoom": AllRoom,
        "page" : page,
    }
    return render(req, 'pages/admin_room.html', context)

#เพิ่มห้อง
@login_required
def admin_addroom(req):
    if req.user.status != "ผู้ดูแลระบบ" :
        return redirect('/')
    if req.method == "POST":
        room_name = req.POST.get('room_name')
        status = req.POST.get('status')
        descriptions = req.POST.getlist('description')
        for description in descriptions:
            obj = MyRoom(room_name=room_name, status=status, description=description)
            obj.save()
            messages.success(req, "เพิ่มห้องสำเร็จ")
        return redirect('/admin_room')   
    else:
        obj = MyRoom()   
    AllRoom = MyRoom.objects.all()      
    context = {
        "AllRoom": AllRoom,
    }
    return render(req, 'pages/admin_addroom.html', context)

#แก้ไขห้อง
@login_required
def edit_room(req,id):
    if req.user.status != "ผู้ดูแลระบบ" :
        return redirect('/')
    obj = MyRoom.objects.get(id = id)
    obj.room_name = req.POST['room_name']
    obj.status = req.POST['status']
    obj.description = req.POST['description']
    obj.save()
    messages.success(req, "แก้ไขข้อมูลสำเร็จ")
    return redirect("/admin_room")
    

#ลบห้อง
@login_required
def delete_room(req, id):
    if req.user.status != "ผู้ดูแลระบบ" :
        return redirect('/')
    MyRoom.objects.get(id=id).delete()
    messages.success(req, "ลบห้องสำเร็จ")
    return redirect('/admin_room')

#อนุมัติการจองห้อง
@login_required
def approve_booking(req, id):
    if req.user.status != "ผู้ดูแลระบบ":
        return redirect('/')
    booking = Booking.objects.get(id=id)
    booking.status = 'อนุมัติ'
    booking.save()
    send_booking_status_update_message(booking)
    messages.success(req, "อนุมัติการจองสำเร็จ")
    return redirect('/admin_dashboard')

#ไม่อนุมัติการจองห้อง
@login_required
def disapproval_booking(req, id):
    if req.user.status != "ผู้ดูแลระบบ" :
        return redirect('/')
    booking = Booking.objects.get(id=id)
    booking.admin_reason = req.POST['admin_reason']
    booking.status = 'ไม่อนุมัติ'
    booking.save()
    send_booking_status_update_message(booking)
    messages.success(req, "ไม่อนุมัติการจองสำเร็จ")
    return redirect('/admin_dashboard')

#ดูประวัติการจองย้อนหลังทั้งหมด
def admin_history_booking(req):
    if req.user.status != "ผู้ดูแลระบบ" :
        return redirect('/')
    approved_bookings = Booking.objects.filter(status='อนุมัติ')
    # Paginate objects
    items_per_page = 100
    paginator = Paginator(approved_bookings, items_per_page)
    page_number = req.GET.get('page', 1)
    page = paginator.get_page(page_number)
    try:
        page = paginator.page(page_number)
    except:
        page = paginator.page(1) 
    context = {
        "approved_bookings": approved_bookings,
        "page" : page,
    }
    return render(req, 'pages/admin_history_booking.html', context)


#LINE Notification booking_status_update
def send_booking_status_update_message(booking):
    # Get the user's Line user ID from the booking object
    line_user_id = booking.line_user_id
    
    if not line_user_id:
        # If the user's Line user ID is not set, do nothing
        return
    
    # Set the message to be sent
    formatted_date = booking.date.strftime('%d/%m/%y')
    formatted_start_time = booking.start_time.strftime('%H:%M')
    formatted_end_time = booking.end_time.strftime('%H:%M')
    if booking.status == 'อนุมัติ':
        message = f"การจองของ {booking.user.stdID} ห้อง {booking.room.room_name} วันที่ {formatted_date} เวลา {formatted_start_time} - {formatted_end_time} ได้รับการอนุมัติ"
    else:
        message = f"การจองของ {booking.user.stdID} ห้อง {booking.room.room_name} วันที่ {formatted_date} เวลา {formatted_start_time} - {formatted_end_time} ไม่ได้รับการอนุมัติ เนื่องจาก {booking.admin_reason}"
    
    # Set the request headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {settings.LINE_ACCESS_TOKEN}',
    }
    
    # Set the request body
    data = {
        'to': line_user_id,
        'messages': [
            {
                'type': 'text',
                'text': message,
            }
        ],
    }
    
    # Send the request
    response = requests.post('https://api.line.me/v2/bot/message/push', headers=headers, json=data)
    
    if response.status_code != 200:
        # If the request failed, log an error
        print(f"Failed to send message to Line user ID {line_user_id}")
        print(response.text)

