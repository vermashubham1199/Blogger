from django.urls import path
from django.views.generic import TemplateView
from .views import (
    UserProfileView, ProfilePicUpdateView, profile_stream_file, ProfilePicDeleteView, OwnerAboutView, AddLikeCat, DeleteLikeCat, AddFollowView, 
    DeleteFollowView, UserProfileUpdateView, UserPasswordUpdateView, chat_profile_stream_file
)
# from .models import Blog

app_name = 'user_profile'
urlpatterns = [
    path('', UserProfileView.as_view(), name = 'profile_page'),
    path('proflie_picture/', ProfilePicUpdateView.as_view(), name = 'profile_pic'),
    path('proflie_picture_stream/', profile_stream_file, name = 'profile_pic_stream'),
    path('proflie_picture_delete/', ProfilePicDeleteView.as_view(), name = 'delete_profile_pic'),
    path('owner_about/<int:pk>', OwnerAboutView.as_view(), name = 'owner_about'),
    path('user_add_like_cat/<int:pk>', AddLikeCat.as_view(), name = 'add_like_cat'),
    path('user_delete_like_cat/<int:pk>', DeleteLikeCat.as_view(), name = 'delete_like_cat'),
    path('user_profile/follow_add/<int:pk>', AddFollowView.as_view(), name='follow_add'),
    path('user_profile/follow_delete/<int:pk>', DeleteFollowView.as_view(), name='follow_delete'),
    path('user_profile_update/', UserProfileUpdateView.as_view(), name = 'user_update'),
    path('userpassword_update/', UserPasswordUpdateView.as_view(), name = 'password_update'),
    path('proflie_picture_stream_chat/<int:pk>', chat_profile_stream_file, name = 'profile_pic_stream_chat'),
]
