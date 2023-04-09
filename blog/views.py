from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Q
from django.contrib.auth.models import User
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
import asyncio
from asgiref.sync import sync_to_async
from blog.humanise import naturalsize
import json
from django.middleware.csrf import get_token
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.paginator import Paginator
from itertools import chain
from .models import (
    Blog, Category, Comment, Report, ReportCategory, History, Tag, Bookmark, Like, Para, CoverPhoto
)

# Create your views here.

#Blog
#<--------------------------------------------------------------------------------------------------------------->
class BlogListView(View):
    """Displays a list of blogs"""

    def get(self, request):
        """
        Displays list of blogs.

        :praram ASGIRequest request: request object
        :context: 
            blogs: an instance of model class Blog
            fav_blogs: A list of blog IDs that user has set to favrioute
        :return: HttpResponse
        """

        blogs = Blog.objects.all()
        search = request.GET.get("q")
        search_owner = []
        q = False
        final_list = list(blogs)
        if search:
            search = search.replace("+", " ")
            q = search
            blogs = Blog.objects.filter(name__contains=search)
            search_owner = User.objects.filter(Q(first_name__contains=search)|Q(last_name__contains=search)|Q(username__contains=search))
            final_list = list(chain(search_owner, blogs))
            pint(final_list)
        fav_blogs = []
        if request.user.is_authenticated:
            rows = request.user.user_blog_bookmark.values('id') # returns a list of bookmarked Blogs in form of dict objects
            fav_blogs = [row['id'] for row in rows] # creating a list of blog IDs that user has bookmarked
        paginator = Paginator(final_list, 5)
        page = request.GET.get("page")
        page_obj = paginator.get_page(page)
        total_pages = [i+1 for i in range(paginator.num_pages)]
        if page_obj.has_next():
            next_page = page_obj.next_page_number()
        else:
            next_page = False
        
        if page_obj.has_previous():
            previous_page = page_obj.previous_page_number()
        else:
            previous_page = False
        current_page = page_obj.number
        ctx=  {
            'fav_blogs':fav_blogs, "final_list":page_obj, "total_pages":total_pages, "current_page":current_page,
              "next_page":next_page, "previous_page":previous_page, "search":q
        }
        return render(request, 'blog/list.html', ctx)


class BlogCreateView(LoginRequiredMixin, View):
    """Creating a new blog"""

    sucess_url = reverse_lazy('blog:blog_picture')

    def get(self, request):
        """
        Displays BlogForm

        if user tries to acesss this view without compeleting whole creation process
        this view will display the same blog the user didn't completed.

        :praram ASGIRequest request: request object
        :context: 
            fm: an instance of form class ProfilePicForm
        :return: HttpResponse
        """

        if 'pk' in request.session:
            pk = request.session['pk'] 
            blog = get_object_or_404(Blog, pk=pk, owner=self.request.user)
            fm = BlogForm(instance=blog)
        else:
            fm = BlogForm()
        return render(request, 'blog/blog_create.html', {'fm':fm})
    
    def post(self, request):
        """
        Creates new Blog
        
        also saves the user's ongoing progress of blog creation

        :praram ASGIRequest request: request object
        :context: 
            fm: an instance of form class ProfilePicForm
        :return if form is valid: HttpResponseRedirect
        :return if from is not valid: HttpResponse
        """

        if 'pk' in request.session:
            pk = request.session['pk']
            blog = get_object_or_404(Blog, pk=pk, owner=self.request.user) # creating blog object from blog id stored in session
            fm = BlogForm(request.POST, instance=blog)
        else:
            fm = BlogForm(request.POST)
        if fm.is_valid():
            row = fm.save(commit=False)
            row.owner = request.user
            row.save()
            para_create_url = reverse('blog:blog_picture', kwargs={"pk":row.id})
            request.session['pk'] = row.pk # saving current blog id in session
            pint("session created")
            pint(request.session.get("pk"), "get, session created")
            pint(request.session)
            return redirect(para_create_url)
        return render(request, 'blog/blog_create.html', {'fm':fm})


class BlogDetailView(View):
    """This view displays the detail page of blog"""

    @sync_to_async(thread_sensitive=False)
    def helper_blog(self, pk):
        """A helper method which returns Blog object using sync_to_async decorator"""

        b = get_object_or_404(Blog, pk=pk)
        return b
    
    @sync_to_async(thread_sensitive=False)
    def helper_pics(self, blog):
        """A helper method which returns list of Para objects using sync_to_async decorator"""

        p = blog.picture_blog.all()
        return list(p)
    
    @sync_to_async(thread_sensitive=False)
    def helper_comments(self, blog):
        """A helper method which returns list of Comment objects using sync_to_async decorator"""

        c = Comment.objects.filter(blog=blog.id)
        return list(c)
    
    @sync_to_async(thread_sensitive=False)
    def helper_like_blog(self, blog, request):
        """A helper method which returns list of like objects using sync_to_async decorator"""

        l = request.user.user_like.filter(blog=blog.id)
        return list(l)
    
    @sync_to_async
    def helper_blog_id(self, request, ctx):
        """A helper method which returns HttpResponse object using sync_to_async decorator"""
        return render(request, 'blog/detail.html', ctx)
    
    @sync_to_async
    def helper_like_blog_list(self, like_blogs=None):
        """A helper method which returns list of blog id which are liked by the user object using sync_to_async decorator"""
        return [b.blog.id for b in like_blogs]

    async def get(self, request, pk):
        """
        Displays a detail page Blog

        :praram ASGIRequest request: request object
        :praram int pk: primary key of model Blog
        :context: 
            fm: an instance of form class CommentForm
            pics: a list of instances of model class Para
            blog: an instance of model class Blog
            comments: a list of instances of model class Comment
            like_blogs: a list of instances of model class Like
            bl: a list of blog.id that are liked by user
            like: an instance of model class Like
        :return: HttpResponse
        """

        blog = await self.helper_blog(pk)
        pics, comments = await asyncio.gather(self.helper_pics(blog), self.helper_comments(blog))
        fm = CommentForm()
        if request.user.is_authenticated:
            like_blogs = await self.helper_like_blog(blog, request)
            if like_blogs:
                like = like_blogs[0].like
            else:
                like = None
            bl = await self.helper_like_blog_list(like_blogs)
        else:
            like_blogs = []
            bl = []
            like = None
        ctx = {'pics':pics, 'blog':blog, 'fm':fm, 'commnets':comments, 'like_blogs':like_blogs, 'bl':bl, 'l':like}
        return await self.helper_blog_id(request, ctx)
    
    

class BlogUpdateView(LoginRequiredMixin, View):
    """This view updates the blog"""

    sucess_url = reverse_lazy('blog:blog_list')

    def get(self, request, pk):
        """
        Displays a BlogForm

        :praram ASGIRequest request: request object
        :praram int pk: primary key of model Blog 
        :context: 
            fm: an instance of form class BlogForm
            blog: an instance of model class Blog
        :return: HttpResponse
        """

        blog = get_object_or_404(Blog, pk=pk, owner=self.request.user)
        fm = BlogForm(instance=blog)
        ctx = {'fm':fm, 'blog':blog.id}
        return render(request, 'blog/blog_update.html', ctx)
    
    def post(self, request, pk):
        """
        Updates the blog 

        :praram ASGIRequest request: request object
        :praram int pk: primary key of model Blog 
        :context: 
            fm: an instance of form class BlogForm
            blog: an instance of model class Blog
        :return if form is valid: HttpResponseRedirect
        :return if from is not valid: HttpResponse
        """

        blog = get_object_or_404(Blog, pk=pk, owner=self.request.user)
        fm = BlogForm(request.POST, instance=blog)
        ctx = {'fm':fm, 'blog':blog.id}
        if fm.is_valid():
            fm.save()
            return redirect(reverse('blog:owner_detail', args=[blog.id]))
        return render(request, 'blog/blog_create.html', ctx)

class DeleteBlogView(OwnerDeleteView):
    """This view deletes a blog"""

    model = Blog

class DeleteParaView(LoginRequiredMixin, View):
    """This view deletes a paragraph in the blog"""

    sucess_url = reverse_lazy('blog:owner_list')

    def get(self, request, pk):
        """
        Displays a delete form

        :praram ASGIRequest request: request object
        :praram pk: int
        :return: HttpResponse
        """

        return render(request, 'blog/delete.html', {})
    
    def post(self, request, pk):
        """
        Deletes a paragraph in the blog 

        :praram ASGIRequest request: request object
        :praram int pk: primary key of model Para 
        :return if form is valid: HttpResponseRedirect
        """

        pic = get_object_or_404(Para, pk=pk) 
        if pic.blog.owner == self.request.user:
            pic.delete()
            return redirect(reverse('blog:owner_detail', args=[pic.blog.id]))
        raise forms.ValidationError('you are not the owner')
#<--------------------------------------------------------------------------------------------------------------->





#Owner
#<--------------------------------------------------------------------------------------------------------------->
@sync_to_async(thread_sensitive=False)
def stream_file(request, pk):
    """
    returns a photo 

    :praram ASGIRequest request: request object
    :praram int pk: primary key of model Para 
    :return: HttpResponse
        """

    pic = get_object_or_404(Para, id=pk)
    response = HttpResponse()
    if pic.content_type:
        response['Content-Type'] = pic.content_type
        response['Content-Length'] = len(pic.picture)
        response.write(pic.picture)
    return response

class OwnerListView(LoginRequiredMixin, View):
    """displays the list of blogs created by the current user"""

    def get(self, request):
        """
        Displays list of blogs.

        :praram ASGIRequest request: request object
        :context: 
            blogs: an instance of model class Blog
        :return: HttpResponse
        """

        blogs = Blog.objects.filter(owner=self.request.user)
        ctx=  {'blogs':blogs}
        return render(request, 'blog/owner_list.html', ctx)

class OwnerDetailView(LoginRequiredMixin, View):
    """displays detail page blogs created by the current user"""

    def get(self, request, pk):
        """
        Displays a detail page Blog

        :praram ASGIRequest request: request object
        :praram int pk: primary key of model Blog 
        :context: 
            pics: a list of instances of model class Para
            blog: an instance of model class Blog
        :return: HttpResponse
        """
        if 'pk' in request.session:
            del request.session['pk'] # deleting session used to created a blog

        blog = get_object_or_404(Blog, pk=pk, owner=self.request.user) # no need for async because there is no point
        pics = blog.picture_blog.all()
        pic_id = [p.id for p in pics] # creating a list of blog ids
        pic_id_json = json.dumps(pic_id)
        csrf_token = get_token(request) # getting value of csrf token
        ctx = {'pics':pics, 'blog':blog, 'pic_id_json':pic_id_json, "csrf_token":csrf_token}
        return render(request, 'blog/owner_detail.html', ctx)
#<--------------------------------------------------------------------------------------------------------------->




#Para
#<--------------------------------------------------------------------------------------------------------------->
class BlogParaCreateView(LoginRequiredMixin,View):
    """
    creates a new para in the blog

    works with blog create view
    """
    sucess_url = reverse_lazy('blog:blog_picture')
    home = reverse_lazy('home:all')

    def get(self, request, pk):
        """
        Displays PictureForm

        :praram ASGIRequest request: request object
        :context: 
            fm: an instance of form class PictureForm
        :return: HttpResponse
        """
        blog = get_object_or_404(Blog,pk=pk, owner=request.user.id)
        if 'pk' in request.session: # This 'pk' (Primarykey) in session allows backend to know the current blog object 
            seeeion_pk = request.session['pk']
            pint(request.session)
        else: # if there is no 'pk' in session then you won't be able to save new para
            pint("can't read session in para crate view")
            pint(str(request.session), "str")
            pint(request.session.get("pk"), "get")
            raise forms.ValidationError('no blog found')
        
        fm = PictureForm()
        ctx = {'fm':fm, 'pk':pk}
        return render(request, 'blog/blog_picture.html', ctx)
    
    def post(self, request, pk):
        """
        creates a new para

        :praram ASGIRequest request: request object
        :context: 
            fm: an instance of form class PictureForm
        :return if form is valid: HttpResponseRedirect
        :return if from is not valid: HttpResponse
        """
        blog = get_object_or_404(Blog,pk=pk, owner=request.user.id)
        if 'pk' in request.session: # This 'pk' (Primarykey) in session allows backend to know the current blog object 
            session_pk = request.session['pk']
        else: # if there is no 'pk' in session then you won't be able to save new para
            raise forms.ValidationError('no blog found')
        fm = PictureForm(request.POST, request.FILES or None, blog_id=blog.id)
        if fm.is_valid():
            row = fm.save(commit=False)
            row.blog = blog
            row.save()
            return redirect(self.sucess_url)
        ctx = {'fm':fm, 'pk':pk}
        return render(request, 'blog/blog_picture.html', ctx)

class ParaUpdateView(LoginRequiredMixin, View):
    """Updates a para in the blog"""

    sucess_url = reverse_lazy('blog:owner_list')

    def get(self, request, pid, bid):
        """
        Displays PictureForm

        :praram ASGIRequest request: request object
        :praram int pid: primary key of model Para 
        :praram int bid: primary key of model Blog 
        :context: 
            fm: an instance of form class PictureForm
            blog: primary key of a Blog object
        :return: HttpResponse
        """

        b = get_object_or_404(Blog, pk=bid, owner=self.request.user)
        pic = get_object_or_404(Para, pk=pid, blog=b)
        fm = PictureForm(instance=pic)
        ctx = {'fm':fm, 'blog':pic.blog.id}
        return render(request, 'blog/update_picture.html', ctx)

    def post(self, request, pid, bid):
        """
        Updates para

        :praram ASGIRequest request: request object
        :praram int pid: primary key of model Para 
        :praram int bid: primary key of model Blog 
        :context: 
            fm: an instance of form class PictureForm
            blog: primary key of a Blog object
        :return if form is valid: HttpResponseRedirect
        :return if from is not valid: HttpResponse
        """

        b = get_object_or_404(Blog, pk=bid, owner=self.request.user)
        pic = get_object_or_404(Para, pk=pid, blog=b )
        fm = PictureForm(request.POST, request.FILES or None, instance=pic)
        ctx = {'fm':fm, 'pic':pic.blog.id}
        if fm.is_valid():
            fm.save()
            return redirect(reverse('blog:owner_detail', args=[b.id]))
        return render(request, 'blog/update_picture.html', ctx)



class ParaAddView(LoginRequiredMixin, View):
    sucess_url = reverse_lazy('blog:owner_list')

    def get(self, request, bid):
        """
        Displays PictureForm

        :praram ASGIRequest request: request object
        :praram int bid: primary key of model Blog 
        :context: 
            fm: an instance of form class PictureForm
            blog: primary key of a Blog object
        :return: HttpResponse
        """

        b = get_object_or_404(Blog, pk=bid, owner=self.request.user)
        fm = PictureForm()
        ctx = {'fm':fm, 'pk':b.id}
        return render(request, 'blog/blog_picture.html', ctx)

    def post(self, request, bid):
        """
        Adds a new para

        :praram ASGIRequest request: request object
        :praram int bid: primary key of model Blog 
        :context: 
            fm: an instance of form class PictureForm
            blog: primary key of a Blog object
        :return if form is valid: HttpResponseRedirect
        :return if from is not valid: HttpResponse
        """

        b = get_object_or_404(Blog, pk=bid, owner=self.request.user)
        fm = PictureForm(request.POST, request.FILES or None, blog_id=b.id)
        if fm.is_valid():
            row = fm.save(commit=False)
            row.blog = b
            row.save()
            return redirect(reverse('blog:owner_detail', args=[b.id]))
        pint(b.id)
        ctx = {'fm':fm, 'pk':b.id}
        return render(request, 'blog/blog_picture.html', ctx)



class DeletePictureView(LoginRequiredMixin, View):
    """Deletes a picture from a para"""

    sucess_url = reverse_lazy('blog:owner_list')

    def get(self, request, pk):
        """
        Displays form

        :praram ASGIRequest request: request object
        :praram int pk: primary key of model Para
        :return: HttpResponse
        """

        return render(request, 'blog/delete.html', {})
    
    def post(self, request, pk):
        """
        Deletes a pic from para

        :praram ASGIRequest request: request object
        :praram int pk: primary key of model Para
        :return if form is valid: HttpResponseRedirect
        :return if from is not valid: HttpResponse
        """

        pic = get_object_or_404(Para, pk=pk) 
        if pic.blog.owner == self.request.user:
            pic.picture = None
            pic.content_type = None
            pic.save()
            return redirect(reverse('blog:owner_detail', args=[pic.blog.id]))
        raise forms.ValidationError('you are not the owner')


class CoverPhotoView(LoginRequiredMixin, View):
    max_upload_limit = 5*1024*1024
    max_upload_limit_text = naturalsize(max_upload_limit)

    def post(self, request, pk):
        pint('post working')
        blog = get_object_or_404(Blog, pk=pk)
        if request.user == blog.owner:
            if 'image' in request.FILES:
                img = request.FILES['image']
                if  isinstance(img, InMemoryUploadedFile) or isinstance(img, TemporaryUploadedFile):
                    try: 
                        bytearr = img.read()
                        instance = CoverPhoto(content_type=img.content_type, picture=bytearr, blog=blog)
                        cover_pics = blog.picture_blog.all()
                        for i in cover_pics: # checking are there any pre existing cover photos
                            i.cover = False #turning all exising cover photos to false
                            i.save()
                        instance.save()
                    except IntegrityError: # checking are there any pre existing cover photos
                        cov = get_object_or_404(CoverPhoto, blog=blog)
                        cov.delete()
                        bytearr = img.read() 
                        instance = CoverPhoto(content_type=img.content_type, picture=bytearr, blog=blog)
                        instance.save() # deleteing and then saving new cover photo
                        cover_pics = blog.picture_blog.all()
                        
            elif 'pic_id' in request.POST:
                cov = CoverPhoto.objects.filter(blog=blog)
                cover_pics = blog.picture_blog.all()
                if cov:
                    cov[0].delete() # deleteing and then saving before selecting existing cover photo
                for i in cover_pics:
                    i.cover = False # checking are there any pre existing cover photos
                    i.save()
                pk = request.POST['pic_id']
                pic = get_object_or_404(Para, pk=pk, blog=blog)
                pic.cover = True
                pic.save()
                pint(request.POST['pic_id'])
            return redirect(reverse('blog:owner_detail', args=[blog.id]))



def stream_cover_pic(request, pk):
    """
    returns a photo 

    :praram ASGIRequest request: request object
    :praram int pk: primary key of model Para 
    :return: HttpResponse
        """

    blog = get_object_or_404(Blog, id=pk)
    response = HttpResponse()
    cov = CoverPhoto.objects.filter(blog=blog)
    cover_pics = blog.picture_blog.all()
    if cov:
        response['Content-Type'] = cov[0].content_type
        response['Content-Length'] = len(cov[0].picture)
        response.write(cov[0].picture)
    else:
        for i in cover_pics:
            if i.cover:
                response['Content-Type'] = i.content_type
                response['Content-Length'] = len(i.picture)
                response.write(i.picture)    
    return response


class DeleteCoverPhotoView(LoginRequiredMixin, View):

    def get(self, request, pk):

        return render(request, 'blog/delete.html', {})

    def post(self, request, pk):
        blog = get_object_or_404(Blog, pk=pk)
        cov = CoverPhoto.objects.filter(blog=blog)
        cover_pics = blog.picture_blog.all()

        for i in cover_pics:
            i.cover = False # checking are there any pre existing cover photos
            i.save()
        if cov:
            cov[0].delete()
        return redirect(reverse('blog:owner_detail', args=[blog.id]))

#<--------------------------------------------------------------------------------------------------------------->




#Comment 
#<--------------------------------------------------------------------------------------------------------------->
class CommentView(LoginRequiredMixin, View):
    """Saves a new comment"""

    def post(self, request, pk):
        """
        Saves a new comment

        :praram ASGIRequest request: request object
        :praram int pk: primary key of model Blog
        :return: HttpResponseRedirect
        """

        blog = get_object_or_404(Blog, pk=pk)
        fm = CommentForm(request.POST)
        if fm.is_valid():
            c = Comment(text=fm.cleaned_data['text'], owner=self.request.user, blog=blog)
            c.save()
            return redirect(reverse('blog:blog_detail', args=[blog.id]))
        return redirect(reverse('blog:blog_detail', args=[blog.id]))

class CommentDeleteView(OwnerDeleteView):
    """Deletes a comment"""
    
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
    """Creates a Bookmark"""

    def post(self,request,pk):
        """
       Creates a new bookmark

        :praram ASGIRequest request: request object
        :praram int pk: primary key of model Blog
        :return: HttpResponse
        """

        b = get_object_or_404(Blog, pk=pk)
        bm = Bookmark(blog=b, owner=self.request.user)
        try:
            bm.save()
        except IntegrityError as e:
            pass
        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class DeleteBookmark(LoginRequiredMixin, View):
    """Deletes a Bookamark"""

    def post(self,request,pk):
        """
        Deletes a Bookmark

        :praram ASGIRequest request: request object
        :praram int pk: primary key of model Blog
        :return: HttpResponse
        """

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
    """Creates or saves a Like"""

    def post(self,request,pk):
        """
        Creates or saves a Like

        :praram ASGIRequest request: request object
        :praram int pk: primary key of model Blog
        :return: HttpResponse
        """

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
    """Creates or saves a Dislike"""

    def post(self,request,pk):
        """
        Creates or saves a Dislike

        :praram ASGIRequest request: request object
        :praram int pk: primary key of model Blog
        :return: HttpResponse
        """

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
    """Deletes Like or Dislike"""

    def post(self,request,pk):
        b = get_object_or_404(Blog, pk=pk)
        try:
            l = Like.objects.get(blog=b, owner=self.request.user).delete()
        except Like.DoesNotExist as e:
            pass
        return HttpResponse()