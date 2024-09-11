from django.urls import path
from . import views

urlpatterns = [
	path('index/', views.index),
	path('games/', views.games),
	path('login/', views.login),
	path('404/', views.error_404),
]
