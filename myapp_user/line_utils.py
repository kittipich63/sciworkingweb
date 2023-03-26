from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage

from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, redirect

line_bot_api = LineBotApi(settings.LINE_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

def send_line_message(user_id, message):
    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=message))
    except:
        pass

def send_booking_update_notification(booking):
    if booking.line_user_id:
        status_str = dict(settings.STATUS_CHOICES).get(booking.status, '')
        message = f"Booking {booking.room.room_name} on {booking.date} has been updated to {status_str}."
        send_line_message(booking.line_user_id, message)

def line_liff_success(request):
    return render(request, 'pages/liff_success.html')

def line_liff_error(request):
    return render(request, 'pages/liff_error.html')


#get token line liff
from django.shortcuts import render
from django.http import HttpResponse

def line_liff_callback(request):
    token = request.GET.get('token')
    # Do something with the token, such as store it in the database
    return HttpResponse('Token received')

<a href="https://example.com/line_liff_callback?token=123456">Get Token</a>


#สร้างมุมมอง Django ที่จะส่งการแจ้งเตือน:
import requests

def send_line_notification(request):
    access_token = 'YOUR_ACCESS_TOKEN'  # Replace with your Line Notify access token
    message = 'Booking status updated'
    headers = {'Authorization': f'Bearer {access_token}'}
    payload = {'message': message}
    response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=payload)
    if response.status_code == 200:
        return HttpResponse('Notification sent')
    else:
        return HttpResponse
    


from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage

from myapp.models import MyUser

line_bot_api = LineBotApi('<YOUR_CHANNEL_ACCESS_TOKEN>')
handler = WebhookHandler('<YOUR_CHANNEL_SECRET>')

@csrf_exempt
def line_login(request):
    if request.method == 'POST':
        signature = request.headers['X-Line-Signature']
        body = request.body.decode('utf-8')
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponseBadRequest()
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    google_user = authenticate(request, user_id=user_id)
    if google_user:
        # Google Login user found
        try:
            my_user = MyUser.objects.get(google_user=google_user)
            # MyUser object already exists for this Google Login user
            login(request, my_user)
            return redirect('dashboard')
        except MyUser.DoesNotExist:
            # MyUser object doesn't exist for this Google Login user
            my_user = MyUser.objects.create(google_user=google_user, line_user_id=user_id)
            login(request, my_user)
            return redirect('profile')
    else:
        # Google Login user not found
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Please login with Google first.')
        )


// LIFF app code  รับ userid เมื่อผู้ใช้เปิด line liff
liff.init({ ... });

liff.getProfile()
  .then(function(profile) {
    var userId = profile.userId;
    $.ajax({
      url: '/login/',
      method: 'POST',
      data: { user_id: userId },
      success: function(response) {
        // Handle the response from the backend
      }
    });
  })
  .catch(function(error) {
    console.log(error);
  });