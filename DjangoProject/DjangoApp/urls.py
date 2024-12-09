from django.urls import path
from DjangoApp import views

urlpatterns = [
    path("", views.home, name="home"),
]