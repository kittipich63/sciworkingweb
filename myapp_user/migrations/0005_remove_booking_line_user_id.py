# Generated by Django 4.1.7 on 2023-03-26 21:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp_user', '0004_delete_lineuser'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='line_user_id',
        ),
    ]
