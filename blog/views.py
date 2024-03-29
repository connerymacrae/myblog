from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView

from .forms import CommentForm
from django.views import generic
from .models import Entry


class EntryDetail(CreateView):
    model = Entry
    template_name = 'blog/entry_detail.html'
    form_class = CommentForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['entry'] = self.get_object()
        return kwargs

    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)
        d['entry'] = self.get_object()
        return d

    def get_success_url(self):
        return self.get_object().get_absolute_url()
