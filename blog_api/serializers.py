from rest_framework import serializers
from blog.tests import pint
from blog.models import (
    Blog, Category, Comment, Report, ReportCategory, History, Tag, Bookmark, Like, Para, CoverPhoto, LikeCat
)
from user_profile.models import (
    Follow
)
from django.contrib.auth.models import User

class BaseOwnerValidation(serializers.ModelSerializer):
    
    def validate_owner(self, attrs):
        pint(attrs)
        if str(attrs.id) == self.context["owner"]: 
            return super().validate(attrs)
        raise serializers.ValidationError("user must be logged in")

class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.StringRelatedField(many=False, read_only=True)
    class Meta:
        model = Follow
        fields = "__all__"


class BookmarkSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(many=False, read_only=True)
    class Meta:
        model = Bookmark
        fields = "__all__"

class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(many=False, read_only=True)
    blog = serializers.StringRelatedField(many=False, read_only=True)
    class Meta:
        model = Comment
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "id"]



class LikeSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(many=False, read_only=True)
    class Meta:
        model = Like
        fields = "__all__"



class LikeDetailSerializer(BaseOwnerValidation):
    class Meta:
        model = Like
        fields = "__all__"


class BlogParaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Para
        exclude = ["picture", "content_type"]


class CoverPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverPhoto
        exclude = ["picture", "content_type"]


class BlogSerializer(serializers.ModelSerializer):
    owner = UserSerializer(many=False, read_only=False)
    blog_like = LikeSerializer(many=True, read_only=True)
    blog_comment = CommentSerializer(many=True, read_only=True)
    picture_blog = BlogParaSerializer(many=True, read_only=True)
    cover_photo_blog = CoverPhotoSerializer(many=False, read_only=True)
    class Meta:
        model = Blog
        fields = "__all__"

class BlogOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = "__all__"


class ParaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Para
        fields = "__all__"

class BookmarkDetailSerializer(BaseOwnerValidation):
    class Meta:
        model = Bookmark
        fields = "__all__"


class CommentDetailSerializer(BaseOwnerValidation):
    class Meta:
        model = Comment
        fields = "__all__"

class FollowDetailSerializer(BaseOwnerValidation):
    
    def validate_follower(self, attrs):
        pint(attrs)
        if str(attrs.id) != self.context["owner"]: 
            return super().validate(attrs)
        raise serializers.ValidationError("you can't follow yourself")
    
    
    class Meta:
        model = Follow
        fields = "__all__"

    

class LikeCatDetailSerializer(BaseOwnerValidation):
    
    class Meta:
        model = LikeCat
        fields = "__all__"