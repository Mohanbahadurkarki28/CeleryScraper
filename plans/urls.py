from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("provider/<int:pk>/", views.provider_detail, name="provider_detail"),
    path("plan/<int:pk>/chart/", views.provider_price_chart, name="provider_price_chart"),
    path("run-scraper/", views.run_scraper, name="run_scraper"),
    path("plans/<int:plan_id>/details/<int:index>/", views.plan_details, name="plan_details"),
    path("plans/<int:plan_id>/price-history/", views.price_history, name="price_history"),  
    path("plans/snapshot/<int:snapshot_id>/", views.snapshot_detail, name="snapshot_detail"), 
]
