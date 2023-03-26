from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.CalendarView, name='calendar'),
    path('events', views.get_events, name='events'),

    path('save-user-id/', get_line_user_id, name='save_user_id'),
    
    path('user_profile', views.user_profile, name='user_profile'),
    path('user_std/<int:id>', views.user_std, name='user_std'),
    
    path('addbooking', views.addbooking, name='addbooking'),
    path('user_mybooking', views.user_mybooking, name='user_mybooking'),
    path('user_mybooking_edit/<int:id>', views.user_mybooking_edit, name='user_mybooking_edit'),
    path('user_mybooking_delete/<int:id>', views.user_mybooking_delete, name='user_mybooking_delete'),
]
