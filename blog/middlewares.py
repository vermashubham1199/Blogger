from .tests import pint
from django.shortcuts import HttpResponse
from .models import History, Blog, BlogHistory
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import get_object_or_404


class MyMiddleware(MiddlewareMixin):

    def process_request(self, request):
        pint("middleware is working")
        if request.user.is_authenticated:
            row = History(text=request.path, owner=request.user)
            row.save()
            if "blog/details" in request.path:
                blog_pk = int(request.path[-2])
                blog = get_object_or_404(Blog, pk=blog_pk)
                if request.user != blog.owner:
                    blog_history = BlogHistory(blog=blog, owner=request.user)
                    blog_history.save()

    

