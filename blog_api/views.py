from django.http import Http404
from blog.tests import pint
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from .permissions import OwnerPermission, OwnerPermission2
from rest_framework.authentication import SessionAuthentication
from .serializers import (
    BlogSerializer, UserSerializer, BlogOnlySerializer, BlogParaSerializer, ParaSerializer, LikeDetailSerializer, BookmarkDetailSerializer, CommentDetailSerializer,
    FollowDetailSerializer, LikeCatDetailSerializer
)
from blog.models import (
    Blog, Category, Comment, Report, ReportCategory, History, Tag, Bookmark, Like, Para, CoverPhoto, LikeCat
)
from user_profile.models import (
    Follow
)
from django.contrib.auth.models import User

class BaseOwnerAPI(viewsets.ModelViewSet):

    def list(self, request, *args, **kwargs):
        querryset = self.model_class.objects.filter(owner=request.user)
        paginate_querryset = self.paginate_queryset(querryset)
        serializer = self.owner_serializer(paginate_querryset, many=True)
        return self.get_paginated_response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        row = self.owner_serializer(data=request.data, context={"owner":str(request.user.id)})
        if row.is_valid():
            row.save()
            return Response(row.data, status=status.HTTP_201_CREATED)
        return Response(row.errors)
    
    def partial_update(self, request, pk, *args, **kwargs):
        follow = get_object_or_404(self.model_class, pk=pk)
        row = self.owner_serializer(follow, data=request.data, context={"owner":str(request.user.id)})
        if row.is_valid():
            row.save()
            return Response(row.data, status=status.HTTP_201_CREATED)
        return Response(row.errors)



class BlogListAPI(viewsets.ModelViewSet):
    serializer_class = BlogOnlySerializer
    queryset = Blog.objects.all()
    authentication_classes = [SessionAuthentication]
    permission_classes = [OwnerPermission]

    def list(self, request, *args, **kwargs):
        serializer_class_list = BlogSerializer
        querryset = Blog.objects.all()
        name = request.query_params.get("name")
        if name:
            name = name.replace("+"," ")
            querryset = Blog.objects.filter(name=name)
        paginate_querryset = self.paginate_queryset(querryset)
        serializer = serializer_class_list(paginate_querryset, many=True)
        return self.get_paginated_response(serializer.data)
    
    def retrieve(self, request, pk, *args, **kwargs):
        blog = get_object_or_404(Blog, pk=pk)
        serializer = BlogSerializer(blog)
        return Response(serializer.data)
        
    

class ParaAPI(viewsets.ModelViewSet):
    serializer_class = ParaSerializer
    queryset = Para.objects.all()
    authentication_classes = [SessionAuthentication]
    permission_classes = [OwnerPermission]
    
    def list(self, request, *args, **kwargs):
        return Response()
    
    def retrieve(self, request, pk, *args, **kwargs):
        blog = get_object_or_404(Blog, pk=pk)
        serializer = BlogSerializer(blog)
        return Response()
    
class LikeAPI(BaseOwnerAPI):
    serializer_class = LikeDetailSerializer
    queryset = Like.objects.all()
    authentication_classes = [SessionAuthentication]
    permission_classes = [OwnerPermission2]
    owner_serializer = LikeDetailSerializer
    model_class = Like

    
    

class BookmarkAPI(BaseOwnerAPI):
    serializer_class = BookmarkDetailSerializer
    queryset = Bookmark.objects.all()
    authentication_classes = [SessionAuthentication]
    permission_classes = [OwnerPermission2]
    owner_serializer = BookmarkDetailSerializer
    model_class = Bookmark

    

class CommentAPI(BaseOwnerAPI):
    serializer_class = CommentDetailSerializer
    queryset = Comment.objects.all()
    authentication_classes = [SessionAuthentication]
    permission_classes = [OwnerPermission2]
    owner_serializer = CommentDetailSerializer
    model_class = Comment


        
class FollowAPI(BaseOwnerAPI):
    serializer_class = FollowDetailSerializer
    queryset = Follow.objects.all()
    authentication_classes = [SessionAuthentication]
    permission_classes = [OwnerPermission2]
    owner_serializer = FollowDetailSerializer
    model_class = Follow


class LikeCatAPI(BaseOwnerAPI):
    serializer_class = LikeCatDetailSerializer
    queryset = LikeCat.objects.all()
    authentication_classes = [SessionAuthentication]
    permission_classes = [OwnerPermission2]
    owner_serializer = LikeCatDetailSerializer
    model_class = LikeCat
    