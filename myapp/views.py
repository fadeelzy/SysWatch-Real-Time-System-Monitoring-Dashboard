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
METRICS_DATA = {}
@csrf_exempt
def receive_metrics(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))

        system_id = data.get("system_id")
        hostname = data.get("hostname")
        cpu = data.get("cpu")
        ram = data.get("ram")
        disk = data.get("disk")
        ping = data.get("ping")

        # Save to DB
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

        #  Save to live metrics memory store
        METRICS_DATA[system_id] = {
            "hostname": hostname,
            "cpu": cpu,
            "ram": ram,
            "disk": disk,
            "ping": ping,
        }

        # ✅ Return correct dashboard link
        dashboard_url = f"https://syswatch-6c1r.onrender.com/view/{system_id}/"

        return JsonResponse({
            "status": "ok",
            "dashboard_url": dashboard_url
        })

# --------- API endpoints for the dashboard.js frontend ---------
def get_metric_value(request, system_id, metric):
    """
    Returns the requested metric value for a system.
    Reads from METRICS_DATA if available, otherwise falls back to DB.
    """
    system_data = METRICS_DATA.get(system_id)

    if not system_data:
        # fallback to DB
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
            return JsonResponse({"value": 0, "error": "System not found"}, status=404)

    value = system_data.get(metric)
    if value is None:
        return JsonResponse({"value": 0, "error": "Metric not found"}, status=404)

    return JsonResponse({"value": value})


def get_hostname(request, system_id):
    """
    Returns the hostname of the monitored system.
    Reads from METRICS_DATA if available, otherwise falls back to DB.
    """
    system_data = METRICS_DATA.get(system_id)

    if not system_data:
        # fallback to DB
        system = SystemMetric.objects.filter(system_id=system_id).first()
        if system:
            system_data = {"hostname": system.hostname}
            METRICS_DATA[system_id] = system_data
        else:
            return JsonResponse({"hostname": "Unknown"}, status=404)

    return JsonResponse({"hostname": system_data.get("hostname", "Unknown")})


# --------- Local system monitoring (optional, for testing locally) ---------

def get_cpu_usage(request):
    return JsonResponse({"value": psutil.cpu_percent(interval=0.5)})

def get_ram_usage(request):
    memory = psutil.virtual_memory()
    return JsonResponse({"value": memory.percent})

def get_disk_usage(request):
    disk = psutil.disk_usage('/')
    return JsonResponse({"value": disk.percent})

def get_ping_latency(request):
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "8.8.8.8"],
            capture_output=True, text=True
        )
        latency_line = [line for line in result.stdout.split('\n') if "time=" in line]
        if latency_line:
            latency = float(latency_line[0].split("time=")[1].split(" ")[0])
        else:
            latency = 0
    except Exception:
        latency = 0
    return JsonResponse({"value": latency})


# --------- Dashboard Rendering ---------

def dashboard_view(request, system_id):
    """
    Renders the frontend dashboard for a specific system.
    The frontend JS (dashboard.js) will fetch its metrics automatically.
    """
    system = SystemMetric.objects.filter(system_id=system_id).first()
    hostname = system.hostname if system else "Waiting for Agent..."

    return render(request, "index.html", {
        "system_id": system_id,
        "hostname": hostname,
    })