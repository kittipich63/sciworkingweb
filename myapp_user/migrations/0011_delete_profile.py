# Generated by Django 4.1.7 on 2023-04-18 10:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp_user', '0010_profile'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Profile',
        ),
    ]