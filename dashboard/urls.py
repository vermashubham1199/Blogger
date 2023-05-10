from django.urls import path, reverse_lazy
from django.views.generic import TemplateView
from .views import DashboardView



app_name = 'dashboard'
urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard_view'),
   
]