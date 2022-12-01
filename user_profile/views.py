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

# Create your views here.

class UserProfileView(LoginRequiredMixin, View):

    sucess_url = reverse_lazy('home:all')

    def get(self,request):
        if 'pk' in request.session:
            del request.session['pk']
        owner = get_object_or_404(User, pk=self.request.user.id)
        categories = Category.objects.all()
        if request.user.is_authenticated:
            rows = request.user.user_category_like.values('id')
            fav_category = [row['id'] for row in rows]
        ctx = {'owner':owner, 'categories':categories, 'fav_category':fav_category}
        return render(request, 'user_profile/home.html', ctx)
    
class ProfilePicUpdateView(LoginRequiredMixin, View):

    def get(self, request):
        fm = ProfilePicForm()
        ctx = {'fm':fm}
        return render(request, 'user_profile/profile_pic_create.html', ctx)
    
    def post(self, request):
        pc = get_object_or_404(ProfilePic, owner=request.user)
        fm = ProfilePicForm(request.POST, request.FILES or None, instance=pc)
        ctx = {'fm':fm}
        if fm.is_valid():
            p = fm.save()
            return redirect(reverse('user_profile:profile_page'))
        return render(request, 'profile_pic_create', ctx)

def profile_stream_file(request):
    pic = get_object_or_404(ProfilePic, owner=request.user)
    response = HttpResponse()
    response['Content-Type'] = pic.content_type
    response['Content-Length'] = len(pic.picture)
    response.write(pic.picture)
    return response

class ProfilePicDeleteView(LoginRequiredMixin, View):

    def get(self, request):
        fm = ProfilePicForm()
        ctx = {}
        return render(request, 'blog/delete.html', ctx)
    
    def post(self, request):
        pc = get_object_or_404(ProfilePic, owner=request.user)
        pc.picture = None
        pc.content_type = None
        pc.save()
        return redirect(reverse('user_profile:profile_page'))


class OwnerAboutView(View):

    def get(self, request, pk):
        owner = get_object_or_404(User, pk=pk)
        if request.user.is_authenticated:
            follow = Follow.objects.filter(owner=owner, follower=request.user )
            follow_list = [i.follower for i in follow]
            ctx = {'owner':owner, 'follow_list':follow_list}
        else:
            ctx = {'owner':owner}
        return render(request, 'user_profile/owner_about.html', ctx)



@method_decorator(csrf_exempt, name='dispatch')
class AddLikeCat(LoginRequiredMixin, View):

    def post(self,request,pk):
        b = get_object_or_404(Category, pk=pk)
        bm = LikeCat(category=b, owner=self.request.user)
        try:
            bm.save()
        except IntegrityError as e:
            pass
        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class DeleteLikeCat(LoginRequiredMixin, View):

    def post(self,request,pk):
        b = get_object_or_404(Category, pk=pk)
        try:
            b = LikeCat.objects.get(category=b, owner=self.request.user).delete()
        except LikeCat.DoesNotExist as e:
            pass
        return HttpResponse()
@method_decorator(csrf_exempt, name='dispatch')
class AddFollowView(LoginRequiredMixin, View):

    def post(self,request,pk):
        u = get_object_or_404(User, pk=pk)
        bm = Follow(owner=u, follower=self.request.user)
        try:
            bm.save()
        except IntegrityError as e:
            pass
        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class DeleteFollowView(LoginRequiredMixin, View):

    def post(self,request,pk):
        u = get_object_or_404(User, pk=pk)
        try:
            b = Follow.objects.get(owner=u, follower=self.request.user).delete()
        except Follow.DoesNotExist as e:
            pass
        return HttpResponse()



class UserProfileUpdateView(LoginRequiredMixin,View):

    def get(self, request):
        fm = UserUpdateForm(instance=request.user)
        ctx = {'fm':fm}
        return render(request, 'user_profile/user_update.html', ctx)

    def post(self, request):
        fm = UserUpdateForm(request.POST, instance=request.user)
        ctx = {'fm':fm}
        if fm.is_valid():
            fm.save()
            return redirect(reverse('user_profile:profile_page'))
        return render(request, 'user_profile/user_update.html', ctx)

class UserPasswordUpdateView(LoginRequiredMixin,View):

    def get(self, request):
        fm = PasswordChangeForm(user=request.user)
        ctx = {'fm':fm}
        return render(request, 'user_profile/user_update.html', ctx)

    def post(self, request):
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



