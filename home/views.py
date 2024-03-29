"""
HOME VIEW MODULE
----------------
This module is use to store all views related to Home app
"""

import imp
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import RegistrationForm
from django.urls import reverse_lazy
from user_profile.models import ProfilePic
from django.contrib.auth.models import User
from blog.models import Blog, Bookmark, Category, LikeCat, Like
from .models import UserUuid
from blog.tests import pint
from django.db.models import Count
import asyncio
from blogger.tasks import test_funk
from django.core.paginator import Paginator
from blog.views import PaginationView
from asgiref.sync import sync_to_async

class RegisterView(View):
    """A view for regestring new users"""

    sucess_url = reverse_lazy('home:all')

    def get(self, request):
        """
        Displays a RegistrationForm

        :praram ASGIRequest request: request object
        :context: 
            fm: an instance of form class RegistrationForm
        :return: HttpResponse
        """


        fm = RegistrationForm()
        return render(request, 'home/register.html', {'fm':fm})
    
    
    def post(self, request):
        """
        Creats a User using RegistrationForm

        :praram ASGIRequest request: request object
        :context: 
            fm: an instance of form class RegistrationForm
        :return if form is valid: HttpResponse
        :return if from is not valid: HttpResponseRedirect
        """


        fm = RegistrationForm(request.POST)
        if fm.is_valid():
            user = fm.save()
            uuid = UserUuid(user=user) #creating uuid id for this user
            uuid.save()
            pic = ProfilePic(owner=user) #cerating a blank user profile pic
            pic.save() #saving a blank user profile pic
            return redirect(self.sucess_url)
        return render(request, 'home/register.html', {'fm':fm})



class HomepageView(PaginationView):
    """A view for displaying home page."""

    async def get(self, request):
        """
        Displays home page

        :praram ASGIRequest request: request object
        :context: 
            count_list: an instance of model class Category
        :return: HttpResponse
        """

        if request.user.is_authenticated:
            count_list = await sync_to_async(Category.recomendations.user_recomendation)(request.user.id) #coustom manager method 
            
        else:
             count_list = await sync_to_async(list)(Category.recomendations.anonymous_recomendation()) #coustom manager method
        
        paginator = Paginator(count_list, 2)
        page = request.GET.get("page")
        page_obj = paginator.get_page(page)
        page_lis = await self.helper_page_no(page_obj.number, paginator.num_pages)
        next_page, previous_page = await self.helper_next_page(page_obj)
             
        ctx = {"final_list":page_obj, "total_pages":page_lis, "next_page":next_page, "previous_page":previous_page}
        return await sync_to_async(render)(request, 'home/home.html', ctx)