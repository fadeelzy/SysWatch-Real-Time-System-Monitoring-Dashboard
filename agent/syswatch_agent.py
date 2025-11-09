"""
================================================================================
                              SYSWATCH AGENT SCRIPT
================================================================================

This small program monitors your computer's system performance (CPU, RAM, Disk,
and Internet Ping Speed) and sends it to your SysWatch Dashboard in real-time.

You can run this on **any computer you want to monitor**.

--------------------------------------------------------------------------------
HOW TO USE (BEGINNER FRIENDLY):
--------------------------------------------------------------------------------

1. Make sure Python is installed.
   - Press Windows Key
   - Type "cmd" and press Enter
   - Type:    python --version
   - If it shows a version number, you're good.
   - If not → Download Python here: https://www.python.org/downloads/

2. Save this file somewhere (example: Desktop).

3. Open Command Prompt and go to the folder where the file is stored:
       cd Desktop

4. Run the agent:
       python syswatch_agent.py

   (If "python" doesn't work, try:   py syswatch_agent.py)

5. Leave the window open — the agent will send live data every few seconds.

6. To stop the program:
       Press CTRL + C in the Command Prompt window.

--------------------------------------------------------------------------------
WHAT YOU WILL SEE:
- A unique ID will be created for this computer.
- The dashboard link will be printed once data is received by your server.

--------------------------------------------------------------------------------
IMPORTANT:
Update the SERVER_URL below to match your deployed SysWatch API endpoint.
--------------------------------------------------------------------------------
"""

# ============================= CONFIGURATION ==================================

SERVER_URL = "https://syswatch-6c1r.onrender.com/api/agent/metrics/"   # <--- UPDATE THIS
UPDATE_INTERVAL = 5   # How often to send metrics (seconds)
IDENTITY_FILE = "syswatch_id.json"

# ============================== DEPENDENCIES ==================================

# Try importing requirements. Install if missing.
try:
    import psutil
    import requests
except ImportError:
    import os
    print("🛠 Installing required packages (one-time setup)...")
    os.system("pip install psutil requests")
    import psutil
    import requests

import time
import json
import platform
import subprocess
import uuid
import os
import socket


# ============================== CORE FUNCTIONS ================================

def get_or_create_system_id():
    """Generate or load the unique ID that identifies this system."""
    if os.path.exists(IDENTITY_FILE):
        with open(IDENTITY_FILE, "r") as f:
            return json.load(f)["id"]
    system_id = str(uuid.uuid4())
    with open(IDENTITY_FILE, "w") as f:
        json.dump({"id": system_id}, f)
    return system_id


def get_ping_latency(host="8.8.8.8"):
    """Check internet ping speed."""
    try:
        cmd = ["ping", "-n" if platform.system().lower() == "windows" else "-c", "1", host]
        output = subprocess.check_output(cmd, universal_newlines=True)
        for line in output.split("\n"):
            if "time=" in line:
                return float(line.split("time=")[1].replace("ms", "").strip())
    except:
        return 0.0
    return 0.0


def collect_metrics():
    """Collect local system resource usage."""
    try:
        return {
            "cpu": psutil.cpu_percent(interval=1),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage("/").percent,
            "ping": get_ping_latency(),
            "hostname": socket.gethostname(),
        }
    except Exception as e:
        print("⚠️ Error collecting metrics:", e)
        return None


def send_metrics(system_id, metrics):
    """Send metrics to the backend server."""
    try:
        response = requests.post(SERVER_URL,
                                 json={"system_id": system_id, **metrics},
                                 headers={"Content-Type": "application/json"},
                                 timeout=10)

        if response.status_code == 200:
            print(f"✅ Sent metrics for {metrics['hostname']} ({system_id[:8]}...)")
            try:
                data = response.json()
                if "dashboard_url" in data:
                    print(f"🌍 View dashboard: {data['dashboard_url']}\n")
            except:
                pass
        else:
            print(f"⚠️ Server responded with status: {response.status_code}")

    except Exception as e:
        print("❌ Error sending metrics:", e)


def run_agent():
    """Main background loop."""
    print("\n🚀 SysWatch Agent Running")
    print(f"📡 Sending data every {UPDATE_INTERVAL} seconds to:\n   {SERVER_URL}\n")

    system_id = get_or_create_system_id()

    print(f"🧠 Computer ID: {system_id}")
    print(f"💻 Device Name: {socket.gethostname()}")
    print("🛑 Press CTRL + C to stop.\n")

    while True:
        metrics = collect_metrics()
        if metrics:
            send_metrics(system_id, metrics)
        time.sleep(UPDATE_INTERVAL)


# ================================ START AGENT =================================

if __name__ == "__main__":
    try:
        run_agent()
    except KeyboardInterrupt:
        print("\n🛑 SysWatch Agent stopped.")
