from django.urls import path
from . import views

urlpatterns = [
    path('routes', views.find_routes, name='find_routes'),
]
