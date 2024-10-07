from django.urls import path
from . import views

urlpatterns = [
	path('index/', views.index),
	path('pong/', views.pong),
	path('pong/local/', views.pong_local),
    path('pong/online/', views.pong_online),
    path('pong/online/<uuid:id>/', views.pong_online),
	path('login/', views.authentification),
	path('register/', views.authentification),
	path('authorize/', views.authorize),
	path('404/', views.error_404),
]
