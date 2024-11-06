# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('handle_post/', views.handle_post, name='handle_post'),
    path('chat_history/', views.chat_history, name='chat_history'),
]
