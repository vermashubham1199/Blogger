from django.contrib import admin
from .models import (
    Group, ChatModel
)


admin.site.register(Group)
admin.site.register(ChatModel)