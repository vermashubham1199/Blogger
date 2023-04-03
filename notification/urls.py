from django.urls import path
from .views import NotificationList, NotificationDetail

app_name = 'notification'
urlpatterns = [
    path('notification_list', NotificationList.as_view(), name='notification_list'),
    path('notification_detail/<int:pk>', NotificationDetail.as_view(), name='notification_detail'),
]