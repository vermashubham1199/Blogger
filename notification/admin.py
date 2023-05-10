from django.contrib import admin
from .models import NotificationModel, ChannelName

# Register your models here.
admin.site.register(NotificationModel)
admin.site.register(ChannelName)
