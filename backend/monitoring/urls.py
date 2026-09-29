from django.urls import path
from .views import UserActivityListCreateView


urlpatterns = [
    path('activities/', UserActivityListCreateView.as_view(), name='activities'),
]