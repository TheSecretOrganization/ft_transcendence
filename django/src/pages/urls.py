from django.urls import path
from . import views

urlpatterns = [
	path('index/', views.index),
	path('pong/', views.pong),
	path('tournament/', views.tournament),
	path('login/', views.login),
	path('register/', views.register),
	path('authorize/', views.authorize),
	path('404/', views.error_404),
]
