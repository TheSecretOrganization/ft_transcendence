from django.urls import path
from . import views

urlpatterns = [
	path('index/', views.index),
	path('games/', views.games),
]
