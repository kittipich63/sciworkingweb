from myapp_admin.models import *
from django.forms import ModelForm

class RoomModelForm(ModelForm):
    class Meta:
        model = MyRoom
        fields = ('room_name', 'description', 'status')