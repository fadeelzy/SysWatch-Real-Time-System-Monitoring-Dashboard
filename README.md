🛰️ SysWatch – Real-Time System Monitoring Dashboard

🧠 SysWatch is a real-time system performance monitoring web app built with Django and Chart.js.
It allows you to view live CPU, RAM, Disk, and Network Ping statistics from any computer running the SysWatch Agent Script — beautifully visualized in an interactive dashboard.

🚀 Features

✅ Real-time system monitoring (CPU, RAM, Disk, Ping)

✅ Agent script that works on Windows, macOS, and Linux

✅ Auto-generated unique system ID per device

✅ Visual charts using Chart.js

✅ Smart threshold alerts for high usage

✅ Scalable Django backend API

✅ Responsive UI dashboard


⚙️ Tech Stack

Layer	Technology

Frontend	HTML, CSS, JavaScript, Chart.js

Backend	Django 5+, Python 3.10+

Agent Script	Python (psutil, requests)

Database	SQLite (local), PostgreSQL (production ready)

Deployment	Render, Railway, or any VPS


🧩 Architecture Overview
  
 SysWatch Agent  (Python + psutil)  🖥️   ─▶   Django API (/receive/) Stores & updates metrics 📡   ─▶  SysWatch Dashboard 🌐  (Chart.js + Realtime Fetch 
  
       
                              

💻 Local Setup

Clone the repository

git clone https://github.com/yourusername/syswatch.git
cd syswatch


Create & activate a virtual environment

python -m venv venv
source venv/bin/activate     # on macOS/Linux
venv\Scripts\activate        # on Windows


Install dependencies

pip install -r requirements.txt


Run migrations

python manage.py migrate


Start the development server

python manage.py runserver


Access the app

Dashboard: http://127.0.0.1:8000/view/
<system_id>/

Admin: http://127.0.0.1:8000/admin/


🛰️ Run the SysWatch Agent

Open syswatch_agent.py

Set the server URL:

SERVER_URL = "http://127.0.0.1:8000/receive/"


Run the agent:

python syswatch_agent.py


You’ll get a dashboard link like:

🌍 View live dashboard: /view/c2a9f4e2-2b3a-4e5a-a123-abcdef123456/


Open it in your browser to see live stats.

🪪 License

This project is licensed under the MIT License — free to use, modify, and distribute.

✨ Author

Fadilah Abdulkadir
💻 Site Reliability Engineer | Cloud Solutions Architect | Backend Developer | Python & Django Enthusiast
📧 Email : fadeelzy@gmail.com

🌐 Portfolio: 
