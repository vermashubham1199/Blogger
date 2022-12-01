from email.policy import default
from django.db import models
from django.contrib.auth.models import User
from .managers import CategoryManager

class Category(models.Model):
    name = models.CharField(max_length=70)
    cat_like = models.ManyToManyField(User, through='Likecat', related_name='user_category_like')

    recomendations = CategoryManager()
    objects = models.Manager()
    
    def __str__(self) -> str:
        return self.name



class LikeCat(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='cats_like')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_cat_like')

    def __str__(self) -> str:
        return f'{self.owner.username} -> {self.category.name}'

    class Meta:
        unique_together = ('category', 'owner')




class ReportCategory(models.Model):
    name = models.CharField(max_length=70)

    def __str__(self) -> str:
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=70)

    def __str__(self) -> str:
        return self.name

class History(models.Model):
    text = models.CharField(max_length=256)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_history')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.owner.username

class Bookmark(models.Model):
    blog = models.ForeignKey('Blog', on_delete=models.CASCADE, related_name='blog_bookmark')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_bookmark')

    def __str__(self) -> str:
        return self.owner.username

    class Meta:
        unique_together = ('blog', 'owner')

class Like(models.Model):
    blog = models.ForeignKey('Blog', on_delete=models.CASCADE, related_name='blog_like')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_like')
    like = models.BooleanField()

    def __str__(self) -> str:
        return self.owner.username

    class Meta:
        unique_together = ('blog', 'owner')

class Report(models.Model):
    blog = models.ForeignKey('Blog', on_delete=models.CASCADE, related_name='blog_report')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_report')
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=256, null=True, blank=True)
    report_category = models.ForeignKey('ReportCategory', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.owner.username

class Comment(models.Model):
    blog = models.ForeignKey('Blog', on_delete=models.CASCADE, related_name='blog_comment')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comment')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    text = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.owner.username


class Blog(models.Model):
    name = models.CharField(max_length=70)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_blog')
    abstract = models.CharField(max_length=256, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tag = models.ManyToManyField('Tag', blank=True)
    bookmark = models.ManyToManyField(User, through='Bookmark', related_name='user_blog_bookmark')
    like = models.ManyToManyField(User, through='Like', related_name='User_blog_like')
    report = models.ManyToManyField(User, through='Report', related_name='user_blog_report')
    comment = models.ManyToManyField(User, through='Comment', related_name='user_blog_comment')
    counter = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.name

class Para(models.Model):
    picture = models.BinaryField(null = True, blank = True, editable=True)
    content_type = models.CharField(max_length=256, null=True, blank=True, help_text='The MIMEType of the file')
    text = models.TextField()
    p_title = models.CharField(max_length=70)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='picture_blog')

    def __str__(self) -> str:
        return self.p_title