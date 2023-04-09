from django.contrib import admin
from .models import (
    Blog, Category, Comment, Report, ReportCategory, History, Tag, Bookmark, Like, Para, LikeCat, CoverPhoto, BlogHistory
)

# Register your models here.
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = [
         'name', 'category',  'owner', 'abstract'
    ]

admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Report)
admin.site.register(ReportCategory)
admin.site.register(History)
admin.site.register(Tag)
admin.site.register(Bookmark)
admin.site.register(Like)
admin.site.register(Para)
admin.site.register(LikeCat)
admin.site.register(CoverPhoto)
admin.site.register(BlogHistory)
