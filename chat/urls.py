from django.urls import path
from .views import ChatView, ChatListView



app_name = 'chat'
urlpatterns = [
    path('new_chat/<str:u_uid>', ChatView.as_view(), name='new_chat'),
    path('chats/', ChatListView.as_view(), name='chat_list'),
]