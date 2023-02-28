from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from blog.tests import pint
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError
import asyncio
from asgiref.sync import sync_to_async
from .models import Group, ChatModel
from home.models import UserUuid




class ChatView(LoginRequiredMixin, View):

    def get(self, request, u_uid):
        c_user = request.user
        uuid_c = UserUuid.objects.get(user=c_user) #current user uuid
        uuid_o = UserUuid.objects.get(uuid=u_uid) #other user uuid
        o_user = uuid_o.user #other user
        group_name, uu1, uu2 = self.sorting(uuid_o, uuid_c)
        if uu1 == uu2:
            raise Http404('you can\'t chat with yourself')
        group, t = Group.objects.get_or_create(group_name=group_name, user1=uu1, user2=uu2)
        chats = ChatModel.objects.filter(group=group)
        ctx = {'group_name':group.group_name, "chats":chats, "other_user":o_user, "user_uuid":str(uuid_c)}
        return render(request, "chat/chat.html", ctx)
    
    def sorting(self, u1, u2):
        u1 = str(u1)
        u2 = str(u2)
        lis = [u1, u2]
        lis.sort()
        uu1 = UserUuid.objects.get(uuid=lis[0])
        uu2 = UserUuid.objects.get(uuid=lis[1])
        group_name = ".".join(lis)
        pint(group_name)
        return group_name, uu1.user, uu2.user


class ChatListView(LoginRequiredMixin, View):

    def get(self, request):
        groups = Group.objects.filter(user1=request.user)|Group.objects.filter(user2=request.user)
        pint(groups)
        ctx = {"groups":groups}
        return render(request, "chat/chat_list.html", ctx)