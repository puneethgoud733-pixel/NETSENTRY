 🛡️ NETSENTRY

 Network Device Monitoring and Management System

NETSENTRY is a web-based network monitoring application designed to monitor and manage network-connected devices from a centralized dashboard.

The system allows administrators to register devices, check their connectivity, view Online/Offline status, search devices, delete devices, and monitor recent checking activity.

 🚀 Features

 📊 Centralized network dashboard
 🖥️ Device registration
 🌐 IP-based connectivity checking
 🟢 Online/Offline status monitoring
 🔄 Check individual devices
 🔄 Check all devices
 🔍 Device search
 🗑️ Device deletion
 📈 Network health statistics
 🕒 Monitoring history
 💾 SQLite database storage
 📱 Responsive web interface


 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Backend programming |
| Flask | Web framework |
| Flask-SQLAlchemy | Database ORM |
| SQLite | Data storage |
| HTML5 | Frontend structure |
| CSS3 | Interface design |
| JavaScript | Frontend functionality |
| Network Ping | Connectivity monitoring |


 📁 Project Structure

NETSENTRY/
│
├── app.py
├── extensions.py
├── requirements.txt
├── README.md
│
├── models/
│   └── device.py
│
├── database/
│   └── netsentry.db
│
├── templates/
│   └── dashboard.html
│
└── static/
    ├── css/
    │   └── style.css
    │
    └── js/
        └── dashboard.js


 ⚙️ Getting Started

 Prerequisites

 Python 3.8 or higher
 pip

 Installation

bash
 Clone the repository
git clone <your-repository-url>
cd NETSENTRY

 Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

 Install dependencies
pip install -r requirements.txt

 Run the application
python app.py


The dashboard will be available at `http://127.0.0.1:5000`.

 🔌 API Endpoints

| Method | Endpoint | Function |
|--------|----------|----------|
| GET | `/` | Load dashboard |
| GET | `/devices` | Get all devices |
| GET | `/devices/<id>` | Get one device |
| POST | `/devices` | Add device |
| POST | `/devices/<id>/check` | Check one device |
| POST | `/devices/check-all` | Check all devices |
| DELETE | `/devices/<id>` | Delete device |


🗄️ Database Schema

Table: devices

| Field | Description |
|-------|-------------|
| id | Unique device ID |
| hostname | Device hostname |
| ip_address | Device IP address |
| device_type | Type of device |
| status | Current device status |
| response | Network response information |
| last_checked | Last monitoring timestamp |

 ⚠️ Limitations

 Monitoring is based primarily on ping/connectivity checks
 No detailed CPU, RAM, or bandwidth statistics yet
 Authentication and role-based access are not implemented
 Designed mainly for local/small-scale monitoring
 Advanced network protocols are not currently integrated

 🔭 Roadmap

 🔐 Authentication — login, logout, admin accounts, role-based access
 📡 Advanced monitoring — CPU, RAM, bandwidth, packet loss, latency, port checks
 🚨 Alert system — email alerts, notifications, threshold-based alerts
 📊 Advanced dashboard — charts, graphs, historical analysis, uptime percentage
 🌐 Network discovery — automatic device discovery on an authorized network



🔒 Security Notice

Deploy NETSENTRY only on networks you are authorized to monitor. Future security improvements may include user authentication, password hashing, HTTPS, CSRF protection, input validation, and audit logging.
