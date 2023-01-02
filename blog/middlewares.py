from .tests import pint
from django.shortcuts import HttpResponse
from .models import History
from django.utils.deprecation import MiddlewareMixin

class MyMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            row = History(text=request.path, owner=request.user)
            row.save()
        response = self.get_response(request)
        return response

