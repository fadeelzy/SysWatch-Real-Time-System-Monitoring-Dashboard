from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import psutil
import subprocess
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from .models import SystemMetric

# Create your views here.


# Store latest metrics for each connected system

# In-memory store for live metrics (optional cache)
METRICS_DATA = {}

# ---------------- Agent POST endpoint ----------------
@csrf_exempt
def receive_metrics(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

        system_id = data.get("system_id")
        hostname = data.get("hostname")
        cpu = data.get("cpu", 0)
        ram = data.get("ram", 0)
        disk = data.get("disk", 0)
        ping = data.get("ping", 0)

        # Save/update DB
        SystemMetric.objects.update_or_create(
            system_id=system_id,
            defaults={
                "hostname": hostname,
                "cpu": cpu,
                "ram": ram,
                "disk": disk,
                "ping": ping
            }
        )

        # Update in-memory cache
        METRICS_DATA[system_id] = {
            "hostname": hostname,
            "cpu": cpu,
            "ram": ram,
            "disk": disk,
            "ping": ping,
        }

        # Return dashboard URL
        dashboard_url = f"https://syswatch-6c1r.onrender.com/view/{system_id}/"
        return JsonResponse({"status": "ok", "dashboard_url": dashboard_url})

    return JsonResponse({"status": "error", "message": "POST required"}, status=405)


# ---------------- API endpoints for dashboard.js ----------------
def get_metric_value(request, system_id, metric):
    """
    Returns the requested metric value for a system.
    Reads from METRICS_DATA if available, otherwise falls back to DB.
    Always returns 0 if metric not found instead of 404.
    """
    system_data = METRICS_DATA.get(system_id)

    if not system_data:
        system = SystemMetric.objects.filter(system_id=system_id).first()
        if system:
            system_data = {
                "cpu": system.cpu,
                "ram": system.ram,
                "disk": system.disk,
                "ping": system.ping,
                "hostname": system.hostname,
            }
            METRICS_DATA[system_id] = system_data  # cache in memory
        else:
            # system not found → return default 0
            return JsonResponse({"value": 0}, status=200)

    # Always return 0 if metric missing
    value = system_data.get(metric, 0)
    return JsonResponse({"value": value}, status=200)


def get_hostname(request, system_id):
    """
    Returns the hostname of the monitored system.
    Reads from METRICS_DATA if available, otherwise falls back to DB.
    Defaults to 'Unknown' if not found.
    """
    system_data = METRICS_DATA.get(system_id)

    if not system_data:
        system = SystemMetric.objects.filter(system_id=system_id).first()
        if system:
            system_data = {"hostname": system.hostname}
            METRICS_DATA[system_id] = system_data
        else:
            return JsonResponse({"hostname": "Unknown"}, status=200)

    return JsonResponse({"hostname": system_data.get("hostname", "Unknown")}, status=200)


# ---------------- Local system monitoring (optional) ----------------
def get_cpu_usage(request):
    return JsonResponse({"value": psutil.cpu_percent(interval=0.5)}, status=200)

def get_ram_usage(request):
    memory = psutil.virtual_memory()
    return JsonResponse({"value": memory.percent}, status=200)

def get_disk_usage(request):
    disk = psutil.disk_usage('/')
    return JsonResponse({"value": disk.percent}, status=200)

def get_ping_latency(request):
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "8.8.8.8"],
            capture_output=True, text=True
        )
        latency_line = [line for line in result.stdout.split('\n') if "time=" in line]
        latency = float(latency_line[0].split("time=")[1].split(" ")[0]) if latency_line else 0
    except Exception:
        latency = 0
    return JsonResponse({"value": latency}, status=200)


# ---------------- Dashboard rendering ----------------
def dashboard_view(request, system_id):
    """
    Renders the frontend dashboard for a specific system.
    Frontend JS will fetch metrics automatically.
    """
    system = SystemMetric.objects.filter(system_id=system_id).first()
    hostname = system.hostname if system else "Waiting for Agent..."

    return render(request, "index.html", {
        "system_id": system_id,
        "hostname": hostname,
    })