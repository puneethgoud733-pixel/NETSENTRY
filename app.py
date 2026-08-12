from flask import Flask, render_template, jsonify, request
import sqlite3
import subprocess
import platform
from datetime import datetime
import os
import ipaddress


# ==================================================
# APPLICATION
# ==================================================

app = Flask(__name__)


# ==================================================
# PATHS
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATABASE_DIR = os.path.join(
    BASE_DIR,
    "database"
)

DATABASE = os.path.join(
    DATABASE_DIR,
    "netsentry.db"
)

os.makedirs(
    DATABASE_DIR,
    exist_ok=True
)


# ==================================================
# DATABASE
# ==================================================

def get_db():

    conn = sqlite3.connect(
        DATABASE
    )

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_db()

    # --------------------------------------------------
    # DEVICES TABLE
    # --------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS devices (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            hostname TEXT NOT NULL,

            ip_address TEXT NOT NULL,

            device_type TEXT NOT NULL,

            status TEXT DEFAULT 'Offline',

            response TEXT DEFAULT 'Unknown',

            last_checked TEXT

        )
    """)


    # --------------------------------------------------
    # MONITORING HISTORY TABLE
    # --------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS monitoring_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            device_id INTEGER NOT NULL,

            hostname TEXT NOT NULL,

            ip_address TEXT NOT NULL,

            status TEXT NOT NULL,

            response TEXT NOT NULL,

            checked_at TEXT NOT NULL

        )
    """)


    # --------------------------------------------------
    # DEMO DEVICES
    # --------------------------------------------------

    count = conn.execute(
        "SELECT COUNT(*) FROM devices"
    ).fetchone()[0]


    if count == 0:

        conn.execute("""
            INSERT INTO devices
            (
                hostname,
                ip_address,
                device_type,
                status,
                response
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            "core_router_01",
            "192.168.1.1",
            "Router",
            "Offline",
            "Not checked"
        ))


        conn.execute("""
            INSERT INTO devices
            (
                hostname,
                ip_address,
                device_type,
                status,
                response
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            "test_offline",
            "192.168.250.250",
            "Computer",
            "Offline",
            "Not checked"
        ))


    conn.commit()

    conn.close()


# ==================================================
# IP VALIDATION
# ==================================================

def valid_ip(ip):

    try:

        ipaddress.ip_address(ip)

        return True

    except ValueError:

        return False


# ==================================================
# NETWORK CHECK
# ==================================================

def check_device(ip_address):

    system = platform.system().lower()


    try:

        # Windows
        if system == "windows":

            command = [
                "ping",
                "-n",
                "1",
                "-w",
                "1000",
                ip_address
            ]

        # Linux / macOS
        else:

            command = [
                "ping",
                "-c",
                "1",
                "-W",
                "1",
                ip_address
            ]


        result = subprocess.run(

            command,

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            timeout=3

        )


        if result.returncode == 0:

            return (
                "Online",
                "Reachable"
            )


        return (
            "Offline",
            "Unreachable"
        )


    except subprocess.TimeoutExpired:

        return (
            "Offline",
            "Timeout"
        )


    except Exception as error:

        print(
            "Network check error:",
            error
        )

        return (
            "Offline",
            "Check failed"
        )


# ==================================================
# DASHBOARD
# ==================================================

@app.route("/")
def dashboard():

    return render_template(
        "dashboard.html"
    )


# ==================================================
# GET ALL DEVICES
# ==================================================

@app.route(
    "/devices",
    methods=["GET"]
)
def get_devices():

    conn = get_db()


    devices = conn.execute("""
        SELECT *
        FROM devices
        ORDER BY id ASC
    """).fetchall()


    conn.close()


    return jsonify([

        dict(device)

        for device in devices

    ])


# ==================================================
# GET SINGLE DEVICE
# ==================================================

@app.route(
    "/devices/<int:device_id>",
    methods=["GET"]
)
def get_device(device_id):

    conn = get_db()


    device = conn.execute("""
        SELECT *
        FROM devices
        WHERE id = ?
    """, (
        device_id,
    )).fetchone()


    conn.close()


    if device is None:

        return jsonify({
            "error": "Device not found"
        }), 404


    return jsonify(
        dict(device)
    )


# ==================================================
# ADD DEVICE
# ==================================================

@app.route(
    "/devices",
    methods=["POST"]
)
def add_device():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({
            "error": "Invalid JSON"
        }), 400


    hostname = str(
        data.get(
            "hostname",
            ""
        )
    ).strip()


    ip_address = str(
        data.get(
            "ip_address",
            ""
        )
    ).strip()


    device_type = str(
        data.get(
            "device_type",
            "Computer"
        )
    ).strip()


    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    if not hostname:

        return jsonify({
            "error": "Hostname is required"
        }), 400


    if not ip_address:

        return jsonify({
            "error": "IP address is required"
        }), 400


    if not valid_ip(ip_address):

        return jsonify({
            "error": "Invalid IP address"
        }), 400


    if not device_type:

        device_type = "Computer"


    # --------------------------------------------------
    # INSERT
    # --------------------------------------------------

    conn = get_db()


    cursor = conn.execute("""
        INSERT INTO devices
        (
            hostname,
            ip_address,
            device_type,
            status,
            response
        )
        VALUES (?, ?, ?, ?, ?)
    """, (

        hostname,

        ip_address,

        device_type,

        "Offline",

        "Not checked"

    ))


    conn.commit()


    device_id = cursor.lastrowid


    device = conn.execute("""
        SELECT *
        FROM devices
        WHERE id = ?
    """, (
        device_id,
    )).fetchone()


    conn.close()


    return jsonify(
        dict(device)
    ), 201


# ==================================================
# CHECK SINGLE DEVICE
# ==================================================

@app.route(
    "/devices/<int:device_id>/check",
    methods=["POST"]
)
def check_single_device(device_id):

    conn = get_db()


    device = conn.execute("""
        SELECT *
        FROM devices
        WHERE id = ?
    """, (
        device_id,
    )).fetchone()


    if device is None:

        conn.close()

        return jsonify({
            "error": "Device not found"
        }), 404


    # --------------------------------------------------
    # NETWORK CHECK
    # --------------------------------------------------

    status, response = check_device(
        device["ip_address"]
    )


    last_checked = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    # --------------------------------------------------
    # UPDATE DEVICE
    # --------------------------------------------------

    conn.execute("""
        UPDATE devices

        SET
            status = ?,
            response = ?,
            last_checked = ?

        WHERE id = ?

    """, (

        status,

        response,

        last_checked,

        device_id

    ))


    # --------------------------------------------------
    # SAVE HISTORY
    # --------------------------------------------------

    conn.execute("""
        INSERT INTO monitoring_history
        (
            device_id,
            hostname,
            ip_address,
            status,
            response,
            checked_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (

        device["id"],

        device["hostname"],

        device["ip_address"],

        status,

        response,

        last_checked

    ))


    conn.commit()


    # --------------------------------------------------
    # GET UPDATED DEVICE
    # --------------------------------------------------

    updated_device = conn.execute("""
        SELECT *
        FROM devices
        WHERE id = ?
    """, (
        device_id,
    )).fetchone()


    conn.close()


    return jsonify(
        dict(updated_device)
    )


# ==================================================
# CHECK ALL DEVICES
# ==================================================

@app.route(
    "/devices/check-all",
    methods=["POST"]
)
def check_all_devices():

    conn = get_db()


    devices = conn.execute("""
        SELECT *
        FROM devices
        ORDER BY id ASC
    """).fetchall()


    # --------------------------------------------------
    # CHECK EACH DEVICE
    # --------------------------------------------------

    for device in devices:

        status, response = check_device(
            device["ip_address"]
        )


        last_checked = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        # Update device
        conn.execute("""
            UPDATE devices

            SET
                status = ?,
                response = ?,
                last_checked = ?

            WHERE id = ?

        """, (

            status,

            response,

            last_checked,

            device["id"]

        ))


        # Save history
        conn.execute("""
            INSERT INTO monitoring_history
            (
                device_id,
                hostname,
                ip_address,
                status,
                response,
                checked_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (

            device["id"],

            device["hostname"],

            device["ip_address"],

            status,

            response,

            last_checked

        ))


    conn.commit()


    # --------------------------------------------------
    # GET UPDATED DEVICES
    # --------------------------------------------------

    updated_devices = conn.execute("""
        SELECT *
        FROM devices
        ORDER BY id ASC
    """).fetchall()


    results = [

        dict(device)

        for device in updated_devices

    ]


    conn.close()


    return jsonify(results)


# ==================================================
# MONITORING HISTORY
# ==================================================

@app.route(
    "/history",
    methods=["GET"]
)
def get_history():

    conn = get_db()


    history = conn.execute("""
        SELECT
            id,
            device_id,
            hostname,
            ip_address,
            status,
            response,
            checked_at

        FROM monitoring_history

        ORDER BY id DESC

        LIMIT 50

    """).fetchall()


    conn.close()


    return jsonify([

        dict(item)

        for item in history

    ])


# ==================================================
# DEVICE HISTORY
# ==================================================

@app.route(
    "/devices/<int:device_id>/history",
    methods=["GET"]
)
def get_device_history(device_id):

    conn = get_db()


    history = conn.execute("""
        SELECT
            id,
            device_id,
            hostname,
            ip_address,
            status,
            response,
            checked_at

        FROM monitoring_history

        WHERE device_id = ?

        ORDER BY id DESC

        LIMIT 50

    """, (
        device_id,
    )).fetchall()


    conn.close()


    return jsonify([

        dict(item)

        for item in history

    ])


# ==================================================
# DELETE DEVICE
# ==================================================

@app.route(
    "/devices/<int:device_id>",
    methods=["DELETE"]
)
def delete_device(device_id):

    conn = get_db()


    device = conn.execute("""
        SELECT *
        FROM devices
        WHERE id = ?
    """, (
        device_id,
    )).fetchone()


    if device is None:

        conn.close()

        return jsonify({
            "error": "Device not found"
        }), 404


    # Delete history first
    conn.execute("""
        DELETE FROM monitoring_history
        WHERE device_id = ?
    """, (
        device_id,
    ))


    # Delete device
    conn.execute("""
        DELETE FROM devices
        WHERE id = ?
    """, (
        device_id,
    ))


    conn.commit()

    conn.close()


    return jsonify({

        "success": True,

        "message": "Device deleted"

    })


# ==================================================
# APPLICATION START
# ==================================================

if __name__ == "__main__":

    init_db()


    print("=" * 60)

    print(
        "NETSENTRY NETWORK MONITOR"
    )

    print("=" * 60)

    print(
        "Dashboard : "
        "http://127.0.0.1:5000/"
    )

    print(
        "Devices   : "
        "http://127.0.0.1:5000/devices"
    )

    print(
        "History   : "
        "http://127.0.0.1:5000/history"
    )

    print("=" * 60)


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )