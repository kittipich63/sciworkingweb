# Generated by Django 4.1.7 on 2023-03-21 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp_user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='line_user_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
