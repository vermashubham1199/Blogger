from django.urls import path, reverse_lazy
from django.views.generic import TemplateView
from .views import (
    BlogListView, BlogCreateView, BlogParaCreateView, BlogDetailView, BlogUpdateView, stream_file, OwnerListView, ParaUpdateView, OwnerDetailView, ParaAddView, 
    DeleteBlogView, DeleteParaView, DeletePictureView, CommentView, CommentDeleteView, AddBookmark, DeleteBookmark, AddDislike, AddLike, DeleteLike, CoverPhotoView,
    stream_cover_pic, DeleteCoverPhotoView
)


app_name = 'blog'
urlpatterns = [
    path('', BlogListView.as_view(), name='blog_list'),
    path('create/', BlogCreateView.as_view(), name='blog_create'),
    path('picture/<int:pk>', BlogParaCreateView.as_view(), name='blog_picture'),
    path('details/<int:pk>', BlogDetailView.as_view(), name='blog_detail'),
    path('update/<int:pk>', BlogUpdateView.as_view(), name='blog_update'),
    path('pic/<int:pk>', stream_file, name='stream_pic'),
    path('owner_list/', OwnerListView.as_view(), name='owner_list'),
    path('pic_update/<int:pid>/<int:bid>', ParaUpdateView.as_view(), name='picture_update'),
    path('owner_detail/<int:pk>', OwnerDetailView.as_view(), name='owner_detail'),
    path('add_para/<int:bid>', ParaAddView.as_view(), name='add_para'),
    path('blog_delete/<int:pk>', DeleteBlogView.as_view(template_name = 'blog/delete.html', success_url=reverse_lazy('blog:owner_list')), name='blog_delete'),
    path('para_delete/<int:pk>', DeleteParaView.as_view(), name='para_delete'),
    path('picture_delete/<int:pk>', DeletePictureView.as_view(), name='picture_delete'),
    path('add_comment/<int:pk>', CommentView.as_view(), name='add_comment'),
    path('comment_delete/<int:pk>', CommentDeleteView.as_view(), name='comment_delete'),
    path('blog/bookmark_add/<int:pk>', AddBookmark.as_view(), name='bookmark_add'),
    path('blog/bookmark_delete/<int:pk>', DeleteBookmark.as_view(), name='bookmark_delete'),
    path('blog/like_delete/<int:pk>', DeleteLike.as_view(), name='like_delete'),
    path('blog/like_add/<int:pk>', AddLike.as_view(), name='like_add'),
    path('blog/dislike_add/<int:pk>', AddDislike.as_view(), name='dislike_add'),
    path('blog_cover_photo/<int:pk>', CoverPhotoView.as_view(), name='blog_cover_photo'),
    path('cover_pic/<int:pk>', stream_cover_pic, name='stream_cover_pic'),
    path('delete_cover_photo/<int:pk>', DeleteCoverPhotoView.as_view(), name='delete_cover_photo'),
]