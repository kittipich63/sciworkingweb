from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.CalendarView, name='calendar'),
    path('events', views.get_events, name='events'),

    path('bind-line-user/<str:user_id>/', views.bind_line_user, name='bind_line_user'),
    path('line_user_bound', views.line_user_bound, name='line_user_bound'),
    
    path('user_profile', views.user_profile, name='user_profile'),
    path('user_std/<int:id>', views.user_std, name='user_std'),
    
    path('addbooking', views.addbooking, name='addbooking'),
    path('user_mybooking', views.user_mybooking, name='user_mybooking'),
    path('user_mybooking_edit/<int:id>', views.user_mybooking_edit, name='user_mybooking_edit'),
    path('user_mybooking_delete/<int:id>', views.user_mybooking_delete, name='user_mybooking_delete'),
]
