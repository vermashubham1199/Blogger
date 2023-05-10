from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse
# from .models import NotificationModel
from blog.tests import pint
from django.contrib.auth.mixins import LoginRequiredMixin
import asyncio
from asgiref.sync import sync_to_async
from blog.models import (
    Blog, Category, Comment, Report, ReportCategory, History, Tag, Bookmark, Like, Para, CoverPhoto, BlogHistory
)



class DashboardView(View):

    async def get(self, request):
        blogs = await sync_to_async(list)(Blog.objects.filter(owner=request.user))
        final_dict = {}
        for blog in blogs:
            bookmarks, likes, blog_history, comments = await asyncio.gather(
            sync_to_async(list)(Bookmark.objects.filter(blog=blog)),
            sync_to_async(list)(Like.objects.filter(blog=blog)), 
            sync_to_async(list)(BlogHistory.objects.filter(blog=blog)),
            sync_to_async(list)(Comment.objects.filter(blog=blog)),
        )
            final_dict[blog] = {"bookmark":bookmarks, "like":likes, "blog_history":blog_history, "comment":comments}
        await self.pint_helper(final_dict)
        lis = [1,2,3,4,5,6]
        ctx = {"final_dict":final_dict, "lis":lis}
        return await sync_to_async(render)(request, "dashboard/dashboard.html", ctx)
    @sync_to_async
    def pint_helper(self, lis=None):
        pint(lis)
        for blog in lis:
            pint("for loop is working")
            for i in lis[blog]:
                pint(lis[blog][i])