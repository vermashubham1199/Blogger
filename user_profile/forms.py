from django.contrib.auth.models import User
from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from blog.humanise import naturalsize
from blog.tests import pint
from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm
from django.contrib.auth.models import User
from .models import (
    ProfilePic
)

class ProfilePicForm(forms.ModelForm):
    max_upload_limit = 5*1024*1024
    max_upload_limit_text = naturalsize(max_upload_limit)
    picture = forms.FileField(required=False, label='File to Upload <= '+max_upload_limit_text)
    upload_field_name = 'picture'

    class Meta:
        model = ProfilePic
        fields = ['picture']

    def clean(self):
        cleaned_data = super().clean()
        pint(type(cleaned_data))
        pic = cleaned_data.get('picture')
        if pic is None:
            return
        if len(pic)> self.max_upload_limit:
            self.add_error(f'file must be < {self.max_upload_limit_text} bytes')

    def save(self, commit=True):
        instance = super(ProfilePicForm, self).save(commit=False)
        f = instance.picture
        if isinstance(f,InMemoryUploadedFile) or isinstance(f, TemporaryUploadedFile):
            bytearr = f.read()
            instance.content_type = f.content_type
            instance.picture = bytearr
        if commit:
            instance.save()
        return instance


class ChatForm(forms.Form):
    chat = forms.CharField(max_length=256)


class UserUpdateForm(UserChangeForm):

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']