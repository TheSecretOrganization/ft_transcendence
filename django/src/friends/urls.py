from django.urls import path

from . import views

urlpatterns = [
	path('invite/', views.invite),
]
