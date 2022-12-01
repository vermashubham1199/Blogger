import imp
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import RegistrationForm
from django.urls import reverse_lazy
from user_profile.models import ProfilePic
from django.contrib.auth.models import User
from blog.models import Blog, Bookmark, Category, LikeCat, Like
from blog.tests import pint
from django.db.models import Count

class RegisterView(View):

    sucess_url = reverse_lazy('home:all')

    def get(self, request):
        fm = RegistrationForm()
        return render(request, 'home/register.html', {'fm':fm})
    
    def post(self, request):
        fm = RegistrationForm(request.POST)
        if fm.is_valid():
            user = fm.save()
            pic = ProfilePic(owner=user)
            pic.save()
            return redirect(self.sucess_url)
        return render(request, 'home/register.html', {'fm':fm})

class HomepageView(View):

    def get(self, request):
        if request.user.is_authenticated:
            count_list = Category.recomendations.user_recomendation()
            
        else:
             count_list = Category.recomendations.anonymous_recomendation()
             
        ctx = {'count_list':count_list}
        return render(request, 'home/home.html', ctx)