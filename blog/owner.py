from django.views.generic import  UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .tests import pint
from .models import (
    Blog, Category, Comment, Report, ReportCategory, History, Tag, Bookmark, Like, Para
)

class OwnerUpdateView(LoginRequiredMixin, UpdateView):

    def get_queryset(self):
        qs = super(OwnerUpdateView, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerDeleteView(LoginRequiredMixin, DeleteView):

    def get_queryset(self):
        pint('qs about to be formed')
        qs = super(OwnerDeleteView, self).get_queryset()
        pint(qs)
        return qs.filter(owner=self.request.user)
    


        