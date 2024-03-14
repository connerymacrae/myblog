from django.urls import path

from . import views

urlpatterns = [
    path('blog/<int:pk>/', views.EntryDetail.as_view(), name='entry_detail'),
]
