from django.urls import path, reverse_lazy, include
from django.views.generic import TemplateView
from .views import (
    BlogListAPI, ParaAPI, LikeAPI, BookmarkAPI, CommentAPI, FollowAPI, LikeCatAPI
)
from rest_framework import routers

router = routers.DefaultRouter()
app_name = 'blog_api'
router.register(r"blog_api", BlogListAPI, basename="blog")
router.register(r"para_api", ParaAPI, basename="para")
router.register(r"like_api", LikeAPI, basename="like")
router.register(r"bookmark_api", BookmarkAPI, basename="bookmark")
router.register(r"comment_api", CommentAPI, basename="comment")
router.register(r"follow_api", FollowAPI, basename="follow")
router.register(r"like_cat_api", LikeCatAPI, basename="like_cat")
urlpatterns = [
    path("", include(router.urls)),
]