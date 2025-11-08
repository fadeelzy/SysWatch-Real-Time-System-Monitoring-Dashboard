"""
SysWatch Agent Script
---------------------
This lightweight agent collects system metrics (CPU, RAM, Disk, Ping)
and sends them securely to your SysWatch Django backend periodically.

🚀 HOW TO USE:
1. Update the `SERVER_URL` below to your Django backend address.
   Example:
       SERVER_URL = "https://syswatch.yourdomain.com/api/agent/metrics/"

2. Run this script on any computer you want to monitor:
       python syswatch_agent.py

3. The agent will keep sending metrics automatically every few seconds.

NOTES:
- You can stop it anytime using (Ctrl + C).
- Works on Windows, macOS, and Linux.
- Generates a unique System ID on first run (saved locally in syswatch_id.json).
"""

import psutil          # For CPU, RAM, and Disk metrics
import time            # To control timing between updates
import json            # For reading/writing the system ID file
import requests        # To send metrics to your Django backend
import platform        # To detect operating system (Windows/Linux/macOS)
import subprocess      # To run ping commands
import uuid            # To generate unique IDs for each monitored system
import os              # For file handling
import socket          # To get the system hostname automatically

# 🌐 Your backend endpoint (update this when deployed)
SERVER_URL = "https://syswatch-6c1r.onrender.com/api/agent/metrics/"
# 🕒 How often to send updates (in seconds)
UPDATE_INTERVAL = 5

# 🧾 Local file that stores your unique system ID
IDENTITY_FILE = "syswatch_id.json"


def get_or_create_system_id():
    """
    Generates or loads a unique ID for this computer.
    This helps the SysWatch server know which system is sending data.
    """
    if os.path.exists(IDENTITY_FILE):
        with open(IDENTITY_FILE, "r") as f:
            return json.load(f)["id"]
    else:
        system_id = str(uuid.uuid4())
        with open(IDENTITY_FILE, "w") as f:
            json.dump({"id": system_id}, f)
        return system_id


def get_ping_latency(host="8.8.8.8"):
    """
    Measures network latency (ping) to a host (default: Google DNS).
    Returns latency in milliseconds, or 0 if ping fails.
    """
    try:
        # On Windows, use "-n"; on Linux/macOS, use "-c"
        ping_cmd = ["ping", "-n" if platform.system().lower() == "windows" else "-c", "1", host]
        output = subprocess.check_output(ping_cmd, universal_newlines=True)

        # Look for "time=" in the ping output to extract latency
        for line in output.split("\n"):
            if "time=" in line:
                # Extract numeric value (remove "ms")
                return float(line.split("time=")[1].split("ms")[0].strip())
    except Exception:
        return 0.0

    return 0.0


def collect_metrics():
    """
    Collects system statistics (CPU, RAM, Disk, Ping, Hostname)
    and returns them in a dictionary.
    """
    try:
        cpu_usage = psutil.cpu_percent(interval=1)           # CPU usage percentage
        ram_usage = psutil.virtual_memory().percent           # RAM usage percentage
        disk_usage = psutil.disk_usage("/").percent           # Disk usage percentage
        ping_latency = get_ping_latency()                     # Ping latency (in ms)
        hostname = socket.gethostname()                       # Auto-detected hostname

        return {
            "cpu": cpu_usage,
            "ram": ram_usage,
            "disk": disk_usage,
            "ping": ping_latency,
            "hostname": hostname,
        }

    except Exception as e:
        print("⚠️ Error collecting metrics:", e)
        return None


def send_metrics(system_id, metrics):
    """
    Sends collected metrics to your SysWatch backend via HTTP POST.
    Includes the system's unique ID and hostname.
    """
    try:
        headers = {"Content-Type": "application/json"}
        payload = {"system_id": system_id, **metrics}  # Merge system_id and metrics
        response = requests.post(SERVER_URL, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            print(f"✅ Metrics sent for {metrics['hostname']} ({system_id[:8]}...)")

            # Optional: print dashboard URL if backend responds with it
            try:
                resp_data = response.json()
                if "dashboard_url" in resp_data:
                    print(f"🌍 View live dashboard: {resp_data['dashboard_url']}\n")
            except Exception:
                pass
        else:
            print(f"⚠️ Failed to send metrics. HTTP {response.status_code}")

    except Exception as e:
        print("❌ Error sending metrics:", e)


def run_agent():
    """
    Main loop — keeps collecting and sending metrics every few seconds.
    """
    print("🚀 SysWatch Agent started.")
    print(f"📡 Sending metrics to: {SERVER_URL}")
    print(f"⏱️ Update interval: {UPDATE_INTERVAL} seconds\n")

    # Automatically detect or create a system ID
    system_id = get_or_create_system_id()

    # Print key info for the user
    print(f"🧠 This system’s unique ID: {system_id}")
    print(f"💻 Detected hostname: {socket.gethostname()}")
    print(f"🌍 Dashboard will be available at: /dashboard/{system_id}/ (after first data upload)\n")

    # Start the infinite monitoring loop
    while True:
        metrics = collect_metrics()
        if metrics:
            send_metrics(system_id, metrics)
        time.sleep(UPDATE_INTERVAL)


# Run the agent
if __name__ == "__main__":
    try:
        run_agent()
    except KeyboardInterrupt:
        print("\n🛑 SysWatch Agent stopped by user.")
