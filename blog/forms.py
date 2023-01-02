from django.contrib.auth.models import User
from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from .humanise import naturalsize
from .tests import pint
from .models import (
    Blog, Category, Comment, Report, ReportCategory, History, Tag, Bookmark, Like, Para
)



class BlogForm(forms.ModelForm):
    """"Creates a form for model Blog"""
    
    class Meta:
        model = Blog
        fields = ['name', 'category', 'abstract', 'tag']
    
    

class PictureForm(forms.ModelForm):
    """"Creates a form for model Para"""

    max_upload_limit = 5*1024*1024
    max_upload_limit_text = naturalsize(max_upload_limit)
    max_upload_words_limit = 250
    picture = forms.FileField(required=False, label='File to Upload <= '+max_upload_limit_text)
    upload_field_name = 'picture'

    def __init__(self, *args, **kwargs): # creating a instance variable of blog_id 
        if kwargs.get('blog_id'): 
            pint('add_id working')
            self.blog_id = kwargs.pop('blog_id')
        else:
            self.blog_id = None
        super(PictureForm, self).__init__(*args, **kwargs)
    class Meta:
        model = Para
        fields = ['p_title', 'text', 'picture']

    def clean(self):
        cleaned_data = super().clean()
        pic = cleaned_data.get('picture')
        tex = cleaned_data.get('text')
        tex_l = tex.split(' ')
        if self.blog_id:
            para_list = Para.objects.filter(blog=self.blog_id) # getting all the para objects of a blog
            if len(para_list)+ 1 > 4:
                raise forms.ValidationError({'text':['max para limit reached']}) # checking the max limit of creating a para object
        if len(tex_l) > self.max_upload_words_limit:
            self.add_error('text', f'text must be  < {self.max_upload_words_limit}')
        if pic is None:
            return
        if len(pic)> self.max_upload_limit:
            self.add_error('picture', f'file must be < {self.max_upload_limit_text} bytes') # checking the max limit of a picture in para object
        
    
    def save(self, commit=True):
        instance = super(PictureForm, self).save(commit=False)
        f = instance.picture
        if isinstance(f, InMemoryUploadedFile) or isinstance(f, TemporaryUploadedFile):
            bytearr = f.read()
            instance.content_type = f.content_type
            instance.picture = bytearr
        if commit:
            instance.save()
        return instance

class CommentForm(forms.Form):
    text = forms.CharField(max_length=256)