from django.urls import path
from myapp_admin.views import *
from . import views

urlpatterns = [  
    path('admin_dashboard', admin_dashboard, name='admin_dashboard'),
    path('admin_profile/', views.admin_profile, name='admin_profile'),

    path('admin_room', views.admin_room, name='admin_room'), 
    path('delete_room/<int:id>',views.delete_room, name="delete_room"),
    path('edit_room/<int:id>',views.edit_room, name="edit_room"),    

    path('admin_user', views.admin_user, name='admin_user'),
    path('admin_manage_user/<int:id>',views.admin_manage_user, name="admin_manage_user"),
    path('admin_delete_user/<int:id>',views.admin_delete_user, name="admin_delete_user"),

    path('approve_booking/<int:id>', views.approve_booking, name='approve_booking'),
    path('disapproval_booking/<int:id>', views.disapproval_booking, name='disapproval_booking'),
]
