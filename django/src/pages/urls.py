from django.urls import path
from . import views

urlpatterns = [
	path('index/', views.index),
	path('games/', views.games),
	path('login/', views.login),
	path('register/', views.register),
	path('authorize/', views.authorize),
	path('friends/', views.friends),
	path('404/', views.error_404),
]
