from django.urls import path
from .views import FetchPageView

urlpatterns = [
    path('fetch-page/<str:page_name>/', FetchPageView.as_view(), name='fetch_page'),
]
