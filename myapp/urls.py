from django.urls import path
from . import views

urlpatterns = [
    # Agent metrics endpoint — used by syswatch_agent.py
    path("api/agent/metrics/", views.receive_metrics, name="receive_metrics"),

    # Dashboard view for each system
    path("view/<str:system_id>/", views.dashboard_view, name="dashboard_view"),

    # API endpoints for dashboard.js frontend
    path("api/metrics/<str:system_id>/<str:metric>/", views.get_metric_value),
    path("api/metrics/<str:system_id>/hostname/", views.get_hostname),

    # Optional: local testing endpoints
    path("api/metrics/cpu/", views.get_cpu_usage),
    path("api/metrics/ram/", views.get_ram_usage),
    path("api/metrics/disk/", views.get_disk_usage),
    path("api/metrics/ping/", views.get_ping_latency),
]
