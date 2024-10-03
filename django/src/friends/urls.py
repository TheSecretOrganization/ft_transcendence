from django.urls import path

from . import views

urlpatterns = [
	path('invite/', views.invite),
	path('accept/', views.accept),
	path('deny/', views.deny),
	path('delete/', views.delete),
]
