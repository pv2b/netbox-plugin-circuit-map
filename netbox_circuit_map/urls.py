from django.urls import path
from . import views

urlpatterns = [
    path('', views.MapView.as_view(), name='map'),
    path('connected-circuit/<int:pk>', views.ConnectedCircuitAjaxView.as_view(), name='connected-circuit')
]
