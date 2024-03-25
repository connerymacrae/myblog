from django.urls import path
#from django.conf.urls import url

from . import views

urlpatterns = [
    path('<int:year>/<int:month>/<int:day>/<int:pk>-<slug:slug>',
         views.EntryDetail.as_view(), name='entry_detail'),
]
