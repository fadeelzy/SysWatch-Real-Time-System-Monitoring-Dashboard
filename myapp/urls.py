from django.urls import path
from . import views


urlpatterns = [
    path("receive/", views.receive_metrics, name="receive_metrics"),
    path("view/<str:system_id>/", views.dashboard_view, name="dashboard_view"),

    # API routes for dashboard.js
    path("api/metrics/<str:system_id>/<str:metric>/", views.get_metric_value),
    path("api/metrics/<str:system_id>/hostname/", views.get_hostname),

    # Optional: test endpoints (for local monitoring)
    path("api/metrics/cpu/", views.get_cpu_usage),
    path("api/metrics/ram/", views.get_ram_usage),
    path("api/metrics/disk/", views.get_disk_usage),
    path("api/metrics/ping/", views.get_ping_latency),
]
