from datetime import datetime
from django.shortcuts import render, redirect , get_object_or_404
from datetime import *
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
import datetime
from django.http import HttpResponse
from linebot import LineBotApi, WebhookHandler ,WebhookParser
from linebot.models import TextSendMessage ,MessageEvent, TextMessage
from linebot.exceptions import InvalidSignatureError , LineBotApiError
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings


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

# ---------------------------- Line ------------------------------------#
#line liff

line_bot_api = LineBotApi('AzpZXSQ6zKvBC5hXYxtl79AkvRhtpA8Vhn9VD3bFbQD83UagJiwY33YLatoDnfn4ZuhUHWoQVJOYtHfPp7225a+hbIr2KkuG57q+UkMN7oFGggGNqnSVaeQldUd3fK3hKHP+zcKLrLNr4ntQXliMXQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('19b6f53ad25ecbd161e8a8b48d65b73d')

def get_line_user_id(req):
    # get the user ID from the request object
    user_id = req.GET.get('user_id')

    # create a new user object with the user ID and save it to the database
    user = User(line_user_id=user_id)
    user.save()

    # return a JSON response with the success message
    return JsonResponse({'message': 'User ID saved successfully'})

'''@csrf_exempt
def booking_status_update(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found'})

    # Update the booking status here...

    # Send a message to the Chat Line OA using the LINE Messaging API
    line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
    message = TextSendMessage(text=f"Booking {booking.id} status updated to {booking.status}")
    line_bot_api.push_message(booking.line_user_id, message)

    return JsonResponse({'success': True})


@csrf_exempt
def booking_status_update(req):
    if req.method == 'POST':
        signature = req.META['HTTP_X_LINE_SIGNATURE']
        body = req.body.decode('utf-8')

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponse(status=400)

        return HttpResponse(status=200)
    else:
        return HttpResponse(status=405)

@handler.add(event=MessageEvent, message=TextMessage)
def handle_message(event):
    booking_status = event.message.text
    line_user_id = event.source.user_id
    message = TextSendMessage(text=f'Booking status updated to {booking_status}')
    line_bot_api.push_message(line_user_id, message) '''


'''@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    booking = Booking.objects.filter(line_user_id=user_id).first()
    if booking:
        booking.status = 'อนุมัติ'
        booking.save()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='ระบบได้รับการอนุมัติการจองของท่านแล้ว')
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='ไม่พบการจองของท่านในระบบ')
        ) '''

#link user
'''@login_required
def link_line_user(req):
    line_user_id = req.GET.get('line_user_id')
    if line_user_id:
        line_user, created = LineUser.objects.get_or_create(line_user_id=line_user_id, user=req.user)
        return redirect('home')'''



###################

'''# Set up the LineBotApi with your Channel Access Token
line_bot_api = LineBotApi(os.environ.get('AzpZXSQ6zKvBC5hXYxtl79AkvRhtpA8Vhn9VD3bFbQD83UagJiwY33YLatoDnfn4ZuhUHWoQVJOYtHfPp7225a+hbIr2KkuG57q+UkMN7oFGggGNqnSVaeQldUd3fK3hKHP+zcKLrLNr4ntQXliMXQdB04t89/1O/w1cDnyilFU='))

# Set up the WebhookHandler with your Channel Secret
handler = WebhookHandler(os.environ.get('19b6f53ad25ecbd161e8a8b48d65b73d'))

# View to handle LIFF request from user
def liff_view(req):
    context = {}
    if req.method == 'GET':
        # Render the LIFF template with the user's Line ID as a parameter
        context['line_id'] = req.GET.get('line_id')
        return render(req, 'liff_template.html', context)

@csrf_exempt
def callback(req):
    # Verify the signature of the incoming request
    signature = req.headers['X-Line-Signature']
    body = req.body.decode('utf-8')
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return HttpResponse(status=400)

    return HttpResponse(status=200)

# Implement a webhook to receive updates from your booking system
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_id = event.source.user_id
    booking_status = get_booking_status(line_id) # Implement your own function to get the user's booking status
    message = TextSendMessage(text=f"Your booking status is now {booking_status}")
    try:
        line_bot_api.push_message(line_id, message)
    except LineBotApiError as e:
        # Handle the LineBotApiError if necessary
        pass '''



#Define a view that will handle the incoming request from LINE LIFF:
'''import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def liff_login(request):
    user_id = request.data.get('user_id')
    # Make a request to LINE API to get the user profile
    profile_response = requests.get(f'https://api.line.me/v2/bot/profile/{user_id}', headers={
        'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'
    })
    if profile_response.status_code == 200:
        # If the request is successful, get the user profile data
        profile_data = profile_response.json()
        # Get or create the user based on the user ID
        user, created = User.objects.get_or_create(username=user_id)
        # Update the user's profile data with the LINE data
        user.first_name = profile_data.get('displayName')
        user.save()
        return Response({'success': True})
    else:
        return Response({'success': False}) '''


'''
from linebot import LineBotApi
from linebot.exceptions import LineBotApiError

def get_line_profile(access_token):
    line_bot_api = LineBotApi(access_token)
    try:
        profile = line_bot_api.get_profile()
        user_id = profile.user_id
        display_name = profile.display_name
        # Bind the user ID and profile information to the user in Django
        # You can use the user_id to find or create a user object in your database
        # and update the profile information as needed
        # For example:
        user = User.objects.get(line_user_id=user_id)
        user.display_name = display_name
        user.save()
    except LineBotApiError as e:
        # Handle any errors that occur while making API requests
        print(e)

'''
