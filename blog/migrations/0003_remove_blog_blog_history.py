# Generated by Django 4.1.2 on 2023-04-09 07:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_blog_blog_history"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="blog",
            name="blog_history",
        ),
    ]