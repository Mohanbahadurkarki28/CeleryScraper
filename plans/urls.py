from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("provider/<int:pk>/", views.provider_detail, name="provider_detail"),
    path("provider/<int:pk>/weekly-chart/", views.provider_weekly_chart, name="provider_weekly_chart"),
    path("run-scraper/", views.run_scraper, name="run_scraper"),
]
