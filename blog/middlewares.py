from .tests import pint
from django.shortcuts import HttpResponse
from .models import History, Blog, BlogHistory
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import get_object_or_404
import re


class MyMiddleware(MiddlewareMixin):

    def process_request(self, request):
        pint("middleware is working")
        if request.user.is_authenticated:
            row = History(text=request.path, owner=request.user)
            row.save(request.path)
            if "blog/details" in request.path:
                pint(request.path)
                re_result = re.search(r"^/blog/details/(\d+?)/$", request.path)
                pint(re_result)
                blog_pk = int(re_result.groups()[0])
                pint(blog_pk)
                blog = get_object_or_404(Blog, pk=blog_pk)
                if request.user != blog.owner:
                    blog_history = BlogHistory(blog=blog, owner=request.user)
                    blog_history.save()
                    pint("blog history", blog_history)

    

