from django.urls import path, include, re_path
from DjangoApp import views
from .views import *
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register('companycontact', CompanyViewset)

urlpatterns = [
    path("", views.say_hello, name = "home"),
    path("home", views.say_hello, name = "home"),
    path("djangoapp", views.members, name="members"),
    path("join", views.join, name="join"),
    path("resume", views.resume, name="resume"),
    path("portfolio", views.portfolio, name="portfolio"),
    path("mlshowcase", views.mlshowcase, name="mlshowcase"),
    path("database", views.database, name="database"),
    #path('predict', PredictionView.as_view(), name='predict'),
    re_path('^', include(router.urls))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)