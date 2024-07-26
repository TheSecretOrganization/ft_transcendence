from django.urls import path
from . import views

urlpatterns = [
    path('example/', views.ExampleView.as_view(), name='example'),
]
