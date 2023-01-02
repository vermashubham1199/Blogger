"""
USER_PROFILE VIEW MODULE
----------------
This module is use to store all views related to user_profile app
"""



from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .forms import ProfilePicForm, ChatForm, UserUpdateForm
from .models import ProfilePic, UserMessage, Chat, Follow
from django.http import HttpResponse
from blog.tests import pint
from blog.models import Category, LikeCat
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError
from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm
from django.contrib.auth import update_session_auth_hash
import asyncio
from asgiref.sync import sync_to_async

# Create your views here.

class UserProfileView(LoginRequiredMixin, View):
    """A view for displaying User's profile page."""

    sucess_url = reverse_lazy('home:all')

    async def get(self,request):
        """
        Displays Users's profile page.

        :praram request: ASGIRequest
        :context: 
            owner: an instance of model class User
            categories: a list contaning istance of model class Category
            fav_category: A list of category IDs that user has set to favrioute
        :return: HttpResponse
        """

        if 'pk' in request.session:
            del request.session['pk']
        owner, categories = await asyncio.gather(self.helper_user(), self.helper_cat())
        if request.user.is_authenticated:
            rows = await self.helper_fav()
            fav_category = [row['id'] for row in rows] # creating a list of category IDs that user has set to favrioute
        ctx = {'owner':owner, 'categories':categories, 'fav_category':fav_category}
        return render(request, 'user_profile/home.html', ctx)
    
    @sync_to_async(thread_sensitive=False)
    def helper_user(self):
        """A helper method which returns User object using sync_to_async decorator"""

        u = get_object_or_404(User, pk=self.request.user.id)
        return u
    
    @sync_to_async(thread_sensitive=False)
    def helper_cat(self):
        """A helper method which returns list of Category objects using sync_to_async decorator"""

        c = Category.objects.all()
        return list(c)
    
    @sync_to_async(thread_sensitive=False)
    def helper_fav(self):
        """A helper method which returns list of Category objects which are liked by current logged in user using sync_to_async decorator"""

        u = self.request.user.user_category_like.values('id')
        return list(u)




class ProfilePicUpdateView(LoginRequiredMixin, View):
    """A view to update User's profile picture."""

    def get(self, request):
        """
        Displays Users's profile picture update form.

        :praram request: ASGIRequest
        :context: 
            fm: an instance of form class ProfilePicForm
        :return: HttpResponse
        """

        fm = ProfilePicForm()
        ctx = {'fm':fm}
        return render(request, 'user_profile/profile_pic_create.html', ctx)
    
    def post(self, request):
        """
        Updates Users's profile picture.

        :praram request: ASGIRequest
        :context: 
            fm: an instance of form class ProfilePicForm
        :return if form is valid: HttpResponse
        :return if from is not valid: HttpResponseRedirect
        """

        pc = get_object_or_404(ProfilePic, owner=request.user)
        fm = ProfilePicForm(request.POST, request.FILES or None, instance=pc)
        ctx = {'fm':fm}
        if fm.is_valid():
            fm.save()
            return redirect(reverse('user_profile:profile_page'))
        return render(request, 'profile_pic_create', ctx)


def profile_stream_file(request):
    """
    this view function returns the profile pic of the user

    :praram request: ASGIRequest
        :return: HttpResponse
    """

    pic = get_object_or_404(ProfilePic, owner=request.user)
    response = HttpResponse()
    if pic.content_type:
        response['Content-Type'] = pic.content_type
        response['Content-Length'] = len(pic.picture)
        response.write(pic.picture)
    return response

class ProfilePicDeleteView(LoginRequiredMixin, View):
    """Deletes Users's profile picture."""

    def get(self, request):
        """
        Displays profile picture delete form

        :praram request: ASGIRequest
        :return: HttpResponse
        """

        ctx = {}
        return render(request, 'blog/delete.html', ctx)
    
    def post(self, request):
        """
        Deletes profile picture delete form

        :praram request: ASGIRequest
        :return: HttpResponseRedirect
        """

        pc = get_object_or_404(ProfilePic, owner=request.user)
        pc.picture = None
        pc.content_type = None
        pc.save()
        return redirect(reverse('user_profile:profile_page'))


class OwnerAboutView(View):
    """Displays blog's owner about page"""

    def get(self, request, pk):
        """
        Displays blog's owner about page

        :praram request: ASGIRequest
        :context: 
            owner: an instance of model class User
            follow_list: a list of objects of model class Follow
        :return: HttpResponse
        """
        owner = get_object_or_404(User, pk=pk)
        if request.user.is_authenticated:
            follow = Follow.objects.filter(owner=owner, follower=request.user) #checking if user is a follower of the owner of about page
            follow_list = [i.follower for i in follow] #creating a list of follow objects to be used in template 
            ctx = {'owner':owner, 'follow_list':follow_list}
        else:
            ctx = {'owner':owner}
        return render(request, 'user_profile/owner_about.html', ctx)



@method_decorator(csrf_exempt, name='dispatch')
class AddLikeCat(LoginRequiredMixin, View):
    """This view creates an instance of model class LikeCat"""

    def post(self,request,pk):
        """
        This view creates an instance of model class LikeCat

        :praram request: ASGIRequest
        :praram pk: int
        :return: HttpResponse
        """

        b = get_object_or_404(Category, pk=pk)
        bm = LikeCat(category=b, owner=self.request.user)
        try:
            bm.save()
        except IntegrityError as e:
            pass
        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class DeleteLikeCat(LoginRequiredMixin, View):
    """This view deletes an instance of model class LikeCat"""

    def post(self,request,pk):
        """
        This view deletes an instance of model class LikeCat

        :praram request: ASGIRequest
        :praram pk: int
        :return: HttpResponse
        """

        b = get_object_or_404(Category, pk=pk)
        try:
            b = LikeCat.objects.get(category=b, owner=self.request.user).delete()
        except LikeCat.DoesNotExist as e:
            pass
        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class AddFollowView(LoginRequiredMixin, View):
    """This view creates an instance of model class Follow"""

    def post(self,request,pk):
        """
        This view creates an instance of model class Follow

        :praram request: ASGIRequest
        :praram pk: int
        :return: HttpResponse
        """

        u = get_object_or_404(User, pk=pk)
        bm = Follow(owner=u, follower=self.request.user)
        try:
            bm.save()
        except IntegrityError as e:
            pass
        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class DeleteFollowView(LoginRequiredMixin, View):
    """This view deletes an instance of model class LikeCat"""

    def post(self,request,pk):
        """
        This view deletes an instance of model class Follow

        :praram request: ASGIRequest
        :praram pk: int
        :return: HttpResponse
        """

        u = get_object_or_404(User, pk=pk)
        try:
            b = Follow.objects.get(owner=u, follower=self.request.user).delete()
        except Follow.DoesNotExist as e:
            pass
        return HttpResponse()



class UserProfileUpdateView(LoginRequiredMixin,View):
    """This view updates user's information """

    def get(self, request):
        """
        This view displays UserUpdateForm

        :praram request: ASGIRequest
        :context: 
            fm: an instance of form class UserUpdateForm
        :return: HttpResponse
        """

        fm = UserUpdateForm(instance=request.user)
        ctx = {'fm':fm}
        return render(request, 'user_profile/user_update.html', ctx)

    def post(self, request):
        """
        This view updates an instance of model class User

        :praram request: ASGIRequest
        :context: 
            fm: an instance of form class UserUpdateForm
        :return if form is valid: HttpResponse
        :return if from is not valid: HttpResponseRedirect
        """

        fm = UserUpdateForm(request.POST, instance=request.user)
        ctx = {'fm':fm}
        if fm.is_valid():
            fm.save()
            return redirect(reverse('user_profile:profile_page'))
        return render(request, 'user_profile/user_update.html', ctx)

class UserPasswordUpdateView(LoginRequiredMixin,View):
    """This view updates user's password """

    def get(self, request):
        """
        This view displays PasswordChangeForm

        :praram request: ASGIRequest
        :context: 
            fm: an instance of form class PasswordChangeForm
        :return: HttpResponse
        """

        fm = PasswordChangeForm(user=request.user)
        ctx = {'fm':fm}
        return render(request, 'user_profile/user_update.html', ctx)

    def post(self, request):
        """
        This view updates password of the User

        :praram request: ASGIRequest
        :context: 
            fm: an instance of form class UserUpdateForm
        :return if form is valid: HttpResponse
        :return if from is not valid: HttpResponseRedirect
        """

        fm = PasswordChangeForm(data=request.POST, user=request.user)
        ctx = {'fm':fm}
        if fm.is_valid():
            fm.save()
            update_session_auth_hash(request, fm.user)
            return redirect(reverse('user_profile:profile_page'))
        return render(request, 'user_profile/user_update.html', ctx)
            






































class CreateChat(LoginRequiredMixin, View):

    def get(self, request, pk):
        fm = ChatForm()
        op = get_object_or_404(User, pk=pk)
        sender = UserMessage.objects.filter(chat__sender=request.user, chat__receiver=op)
        receiver = UserMessage.objects.filter(chat__receiver=request.user, chat__sender=op)
        row = (sender | receiver)
        ordered_row = row.order_by('created_at')
        ctx = {'fm':fm, 'ordered_row':ordered_row}
        return render(request, 'user_profile/chat.html', ctx)
    
    def post(self, request, pk):
        fm = ChatForm(request.POST)
        ctx = {'fm':fm}
        if fm.is_valid():
            c = fm.cleaned_data.get('chat')
            rev = get_object_or_404(User, pk=pk)
            owner_row, created = Chat.objects.get_or_create(sender=request.user, receiver=rev)
            row1= UserMessage(text=c, chat=owner_row)
            row1.save()
            return redirect(reverse('user_profile:chat', args=[rev.id]))
        return render(request, 'user_profile/chat.html', ctx)

class ListChat(LoginRequiredMixin, View):

    def get(self, request):
        sender = Chat.objects.filter(sender=request.user)
        receiver = Chat.objects.filter(receiver=request.user)
        ordered_row = sender | receiver
        ctx = {'ordered_row':ordered_row}
        return render(request, 'user_profile/chat_list.html', ctx)



