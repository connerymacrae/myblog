from django.shortcuts import render

from django.views import generic
from .models import Entry


class EntryDetail(generic.DetailView):
    model = Entry
