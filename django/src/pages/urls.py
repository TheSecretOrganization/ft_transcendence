from django.urls import path
from . import views

urlpatterns = [
	path('index/', views.index),
	path('pong/', views.pong),
	path('pong/local/', views.pong_local),
    path('pong/online/', views.pong_online),
    path('pong/online/<uuid:id>/<str:tournament_name>/', views.pong_online),
    path('pong/online/<uuid:id>/', views.pong_online),
	path('profiles/<str:username>/', views.profiles),
	path('tournaments/', views.tournaments),
    path('tournaments/pong/<str:name>/', views.pong_tournament),
	path('login/', views.authentification),
	path('register/', views.authentification),
	path('authorize/', views.authorize),
	path('friends/', views.friends),
	path('404/', views.error_404),
	path('settings/', views.settings),
]
