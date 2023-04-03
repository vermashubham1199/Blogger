from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse
from .models import NotificationModel
from blog.tests import pint
from django.contrib.auth.mixins import LoginRequiredMixin


class NotificationList(LoginRequiredMixin, View):

    def get(self, request):
        notifications = NotificationModel.objects.filter(receiver=request.user)
        ctx = {"notifications":notifications}
        return render(request, "notification/notification_list.html", ctx)
    
class NotificationDetail(LoginRequiredMixin, View):

    def get(self, request, pk):
        notification = get_object_or_404(NotificationModel, pk=pk)
        notification.seen = True
        notification.save()
        ctx = {"notification":notification}
        return render(request, "notification/notification_detail.html", ctx)