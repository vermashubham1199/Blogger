from django.contrib import admin
from .models import ProfilePic, Chat, UserMessage, Follow
# Register your models here.
admin.site.register(ProfilePic)
admin.site.register(Chat)
admin.site.register(UserMessage)
admin.site.register(Follow)