from django.urls import path
from django.views.generic import TemplateView
from .views import RegisterView, HomepageView

app_name = 'home'
urlpatterns = [
    path('', HomepageView.as_view(), name='all'),
    path('register', RegisterView.as_view(), name='register'),
]