# Generated by Django 4.1.7 on 2023-03-26 21:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myapp_user', '0005_remove_booking_line_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='line_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='line_user_bookings', to=settings.AUTH_USER_MODEL),
        ),
    ]
