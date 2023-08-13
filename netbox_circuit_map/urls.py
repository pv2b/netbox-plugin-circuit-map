from django.urls import path
from . import views

urlpatterns = [
    path('', views.MapView.as_view(), name='map'),
]
