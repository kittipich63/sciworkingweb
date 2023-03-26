from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from myapp_admin.forms import *
from django.contrib.auth.decorators import login_required #ใส่เพื่อให้เข้าระบบก่อนถึงจะทำรายการแต่ละอย่างได้
from .models import *
from myapp_user.models import *
from django.contrib import messages


#ข้อมูลส่วนตัว admin
def admin_profile(req):
    if req.user.status != "ผู้ดูแลระบบ" :
        return redirect('/')
    return render(req, 'pages/admin_profile.html')    

#หน้าแรก admin
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
    messages.success(req, "อนุมัติสำเร็จ")
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
    messages.success(req, "ไม่อนุมัติสำเร็จ")
    context = {
        "booking" : booking,
    }
    return redirect('/admin_dashboard', context)

