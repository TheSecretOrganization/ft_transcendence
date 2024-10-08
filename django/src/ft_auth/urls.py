from django.urls import path

from . import views

urlpatterns = [
	path('login/', views.login),
	path('logout/', views.logout),
	path('register/', views.register),
	path('authorize/', views.authorize),
	path('password/update/', views.password_update),
]
