from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse
from django import forms
from .forms import BlogForm, PictureForm, CommentForm
from .owner import OwnerDeleteView, OwnerUpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .tests import pint
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError
from .models import (
    Blog, Category, Comment, Report, ReportCategory, History, Tag, Bookmark, Like, Para
)

# Create your views here.

#Blog
#<--------------------------------------------------------------------------------------------------------------->
class BlogListView(View):

    def get(self, request):
        blogs = Blog.objects.all()
        fav_blogs = []
        if request.user.is_authenticated:
            rows = request.user.user_blog_bookmark.values('id')
            fav_blogs = [row['id'] for row in rows]
        ctx=  {'blogs':blogs, 'fav_blogs':fav_blogs}
        return render(request, 'blog/list.html', ctx)


class BlogCreateView(LoginRequiredMixin, View):

    sucess_url = reverse_lazy('blog:blog_picture')

    def get(self, request):
        if 'pk' in request.session:
            pk = request.session['pk']
            blog = get_object_or_404(Blog, pk=pk, owner=self.request.user)
            fm = BlogForm(instance=blog)
        else:
            fm = BlogForm()
        return render(request, 'blog/blog_create.html', {'fm':fm})
    
    def post(self, request):
        if 'pk' in request.session:
            pk = request.session['pk']
            blog = get_object_or_404(Blog, pk=pk, owner=self.request.user)
            fm = BlogForm(request.POST, instance=blog)
        else:
            fm = BlogForm(request.POST)
        if fm.is_valid():
            row = fm.save(commit=False)
            row.owner = request.user
            row.save()
            request.session['pk'] = row.pk
            return redirect(self.sucess_url)
        return render(request, 'blog/blog_create.html', {'fm':fm})


class BlogDetailView(View):

    def get(self, request, pk):
        blog = get_object_or_404(Blog, pk=pk)
        pics = blog.picture_blog.all()
        fm = CommentForm()
        comments = Comment.objects.filter(blog=blog.id)
        if request.user.is_authenticated:
            like_blogs = request.user.user_like.filter(blog=blog.id)
            if like_blogs:
                l = like_blogs[0].like
            else:
                l = None
            bl = [b.blog.id for b in like_blogs]
        ctx = {'pics':pics, 'blog':blog, 'fm':fm, 'commnets':comments, 'like_blogs':like_blogs, 'bl':bl, 'l':l}
        return render(request, 'blog/detail.html', ctx)

class BlogUpdateView(LoginRequiredMixin, View):

    sucess_url = reverse_lazy('blog:blog_list')

    def get(self, request, pk):
        blog = get_object_or_404(Blog, pk=pk, owner=self.request.user)
        fm = BlogForm(instance=blog)
        return render(request, 'blog/blog_update.html', {'fm':fm, 'blog':blog.id})
    
    def post(self, request, pk):
        blog = get_object_or_404(Blog, pk=pk, owner=self.request.user)
        fm = BlogForm(request.POST, instance=blog)
        if fm.is_valid():
            fm.save()
            return redirect(reverse('blog:owner_detail', args=[blog.id]))
        return render(request, 'blog/blog_create.html', {'fm':fm, 'blog':blog.id})

class DeleteBlogView(OwnerDeleteView):
    model = Blog

class DeleteParaView(LoginRequiredMixin, View):
    sucess_url = reverse_lazy('blog:owner_list')

    def get(self, request, pk):
        return render(request, 'blog/delete.html', {})
    
    def post(self, request, pk):
        pic = get_object_or_404(Para, pk=pk) 
        if pic.blog.owner == self.request.user:
            pic.delete()
            return redirect(reverse('blog:owner_detail', args=[pic.blog.id]))
        raise forms.ValidationError('you are not the owner')
#<--------------------------------------------------------------------------------------------------------------->





#Owner
#<--------------------------------------------------------------------------------------------------------------->
def stream_file(request, pk):
    pic = get_object_or_404(Para, id=pk)
    response = HttpResponse()
    if pic.content_type:
        response['Content-Type'] = pic.content_type
        response['Content-Length'] = len(pic.picture)
        response.write(pic.picture)
    return response

class OwnerListView(LoginRequiredMixin, View):

    def get(self, request):
        blogs = Blog.objects.filter(owner=self.request.user)
        ctx=  {'blogs':blogs}
        return render(request, 'blog/owner_list.html', ctx)

class OwnerDetailView(LoginRequiredMixin, View):

    def get(self, request, pk):
        blog = get_object_or_404(Blog, pk=pk, owner=self.request.user)
        pics = blog.picture_blog.all()
        ctx = {'pics':pics, 'blog':blog}
        return render(request, 'blog/owner_detail.html', ctx)
#<--------------------------------------------------------------------------------------------------------------->




#Picture
#<--------------------------------------------------------------------------------------------------------------->
class BlogParaCreateView(LoginRequiredMixin,View):
    sucess_url = reverse_lazy('blog:blog_picture')
    home = reverse_lazy('home:all')

    def get(self, request):
        fm = PictureForm()
        return render(request, 'blog/blog_picture.html', {'fm':fm})
    
    def post(self, request):
        if 'pk' in request.session:
            pk = request.session['pk']
            blog = get_object_or_404(Blog,pk=pk, owner=request.user.id)
        else:
            return redirect(self.home)
        fm = PictureForm(request.POST, request.FILES or None, blog_id=blog.id)
        if fm.is_valid():
            row = fm.save(commit=False)
            row.blog = blog
            row.save()
            return redirect(self.sucess_url)
        return render(request, 'blog/blog_picture.html', {'fm':fm})

class PictureUpdateView(LoginRequiredMixin, View):
    sucess_url = reverse_lazy('blog:owner_list')

    def get(self, request, pid, bid):
        b = get_object_or_404(Blog, pk=bid, owner=self.request.user)
        pic = get_object_or_404(Para, pk=pid, blog=b )
        fm = PictureForm(instance=pic)
        return render(request, 'blog/update_picture.html', {'fm':fm, 'pic':pic.blog.id})

    def post(self, request, pid, bid):
        b = get_object_or_404(Blog, pk=bid, owner=self.request.user)
        pic = get_object_or_404(Para, pk=pid, blog=b )
        fm = PictureForm(request.POST, request.FILES or None, instance=pic)
        if fm.is_valid():
            fm.save()
            return redirect(reverse('blog:owner_detail', args=[b.id]))
        return render(request, 'blog/update_picture.html', {'fm':fm, 'pic':pic.blog.id})



class ParaAddView(LoginRequiredMixin, View):
    sucess_url = reverse_lazy('blog:owner_list')

    def get(self, request, bid):
        b = get_object_or_404(Blog, pk=bid, owner=self.request.user)
        fm = PictureForm()
        ctx = {'fm':fm, 'pic':b.id}
        return render(request, 'blog/blog_picture.html', ctx)

    def post(self, request, bid):
        b = get_object_or_404(Blog, pk=bid, owner=self.request.user)
        fm = PictureForm(request.POST, request.FILES or None, blog_id=b.id)
        if fm.is_valid():
            row = fm.save(commit=False)
            row.blog = b
            row.save()
            return redirect(reverse('blog:owner_detail', args=[b.id]))
        ctx = {'fm':fm, 'pic':b.id}
        return render(request, 'blog/blog_picture.html', ctx)



class DeletePictureView(LoginRequiredMixin, View):
    sucess_url = reverse_lazy('blog:owner_list')

    def get(self, request, pk):
        return render(request, 'blog/delete.html', {})
    
    def post(self, request, pk):
        pic = get_object_or_404(Para, pk=pk) 
        if pic.blog.owner == self.request.user:
            pic.picture = None
            pic.content_type = None
            pic.save()
            return redirect(reverse('blog:owner_detail', args=[pic.blog.id]))
        raise forms.ValidationError('you are not the owner')
#<--------------------------------------------------------------------------------------------------------------->




#Comment 
#<--------------------------------------------------------------------------------------------------------------->
class CommentView(LoginRequiredMixin, View):

    def post(self, request, pk):
        blog = get_object_or_404(Blog, pk=pk)
        fm = CommentForm(request.POST)
        if fm.is_valid():
            c = Comment(text=fm.cleaned_data['text'], owner=self.request.user, blog=blog)
            c.save()
            return redirect(reverse('blog:blog_detail', args=[blog.id]))
        return redirect(reverse('blog:blog_detail', args=[blog.id]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = 'blog/delete.html'

    def get_success_url(self):
        blog = self.object.blog
        return reverse('blog:blog_detail', args=[blog.id])
#<--------------------------------------------------------------------------------------------------------------->





#Bookmark
#<--------------------------------------------------------------------------------------------------------------->

@method_decorator(csrf_exempt, name='dispatch')
class AddBookmark(LoginRequiredMixin, View):

    def post(self,request,pk):
        b = get_object_or_404(Blog, pk=pk)
        bm = Bookmark(blog=b, owner=self.request.user)
        try:
            bm.save()
        except IntegrityError as e:
            pass
        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class DeleteBookmark(LoginRequiredMixin, View):

    def post(self,request,pk):
        b = get_object_or_404(Blog, pk=pk)
        try:
            b = Bookmark.objects.get(blog=b, owner=self.request.user).delete()
        except Bookmark.DoesNotExist as e:
            pass
        return HttpResponse()
#<--------------------------------------------------------------------------------------------------------------->




#Like
#<--------------------------------------------------------------------------------------------------------------->
@method_decorator(csrf_exempt, name='dispatch')
class AddLike(LoginRequiredMixin, View):

    def post(self,request,pk):
        b = get_object_or_404(Blog, pk=pk)
        try:
            defa = {'like':True}
            l, created = Like.objects.get_or_create(blog=b, owner=self.request.user, defaults=defa)
            if not created:
                l.like = True
                l.save()
            pint('like save working')
        except IntegrityError as e:
            pint('like error')
            pass
        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class AddDislike(LoginRequiredMixin, View):

    def post(self,request,pk):
        b = get_object_or_404(Blog, pk=pk)
        try:
            defa = {'like':False}
            l, created = Like.objects.get_or_create(blog=b, owner=self.request.user, defaults=defa)
            if not created:
                l.like = False
                l.save()
            pint('dislike save working')

        except IntegrityError as e:
            pint('dislike error')
            pass
        return HttpResponse()



@method_decorator(csrf_exempt, name='dispatch')
class DeleteLike(LoginRequiredMixin, View):

    def post(self,request,pk):
        b = get_object_or_404(Blog, pk=pk)
        try:
            l = Like.objects.get(blog=b, owner=self.request.user).delete()
        except Like.DoesNotExist as e:
            pass
        return HttpResponse()