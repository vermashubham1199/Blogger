# Generated by Django 4.1.2 on 2023-05-02 05:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("notification", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="channelname",
            name="user_path",
        ),
    ]
