# webconfig/config_editor.py
from flask import Flask, render_template, request, jsonify
import json
import os
import shutil
import subprocess

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define manageable JSON configuration files and fallback examples
CONFIG_FILES = {
    "config.json": {
        "path": os.path.join(BASE_DIR, "config.json"),
        "example": os.path.join(BASE_DIR, "config.example.json")
    },
    "colors/teams.json": {
        "path": os.path.join(BASE_DIR, "colors", "teams.json"),
        "example": os.path.join(BASE_DIR, "colors", "teams.example.json")
    },
    "colors/scoreboard.json": {
        "path": os.path.join(BASE_DIR, "colors", "scoreboard.json"),
        "example": os.path.join(BASE_DIR, "colors", "scoreboard.example.json")
    }
}

def load_file_data(file_key):
    """Loads JSON data from the specified key or its example fallback."""
    if file_key not in CONFIG_FILES:
        return None
    
    file_info = CONFIG_FILES[file_key]
    target = file_info["path"] if os.path.exists(file_info["path"]) else file_info["example"]

    if not os.path.exists(target):
        return {}
    
    try:
        with open(target, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_file_data(file_key, data):
    """Saves data to the target path with backup handling."""
    if file_key not in CONFIG_FILES:
        raise ValueError("Invalid file key specified.")

    target_path = CONFIG_FILES[file_key]["path"]
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    if os.path.exists(target_path):
        shutil.copy2(target_path, f"{target_path}.bak")

    with open(target_path, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    initial_file = "config.json"
    data = load_file_data(initial_file)
    return render_template('index.html', initial_data=data, file_keys=list(CONFIG_FILES.keys()))

@app.route('/api/config/load', methods=['GET'])
def api_load():
    file_key = request.args.get('file', 'config.json')
    if file_key not in CONFIG_FILES:
        return jsonify({"status": "error", "message": "Unknown file specified"}), 400
    
    data = load_file_data(file_key)
    return jsonify({"status": "success", "data": data})

@app.route('/api/config/save', methods=['POST'])
def api_save():
    try:
        payload = request.json or {}
        file_key = payload.get("file")
        data = payload.get("data")

        if not file_key or data is None:
            return jsonify({"status": "error", "message": "Missing file key or payload data"}), 400

        save_file_data(file_key, data)
        return jsonify({"status": "success", "message": f"{file_key} saved successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/wifi/scan', methods=['GET'])
def wifi_scan():
    networks = []
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "dev", "wifi"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            seen = set()
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split(":")
                ssid = parts[0].strip()
                if ssid and ssid not in seen:
                    seen.add(ssid)
                    networks.append({
                        "ssid": ssid,
                        "signal": parts[1] if len(parts) > 1 else "Unknown",
                        "security": parts[2] if len(parts) > 2 else "Open"
                    })
            return jsonify({"status": "success", "networks": networks})
    except Exception:
        pass

    try:
        scan_proc = subprocess.run(
            ["sudo", "iwlist", "wlan0", "scan"],
            capture_output=True, text=True, timeout=10
        )
        lines = scan_proc.stdout.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("ESSID:"):
                current_ssid = line.split('"')[1]
                if current_ssid and not any(n["ssid"] == current_ssid for n in networks):
                    networks.append({"ssid": current_ssid, "signal": "N/A", "security": "WPA/WPA2"})
        return jsonify({"status": "success", "networks": networks})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Scan failed: {str(e)}", "networks": []}), 500

@app.route('/api/wifi/connect', methods=['POST'])
def wifi_connect():
    data = request.json or {}
    ssid = data.get("ssid", "").strip()
    password = data.get("password", "").strip()

    if not ssid:
        return jsonify({"status": "error", "message": "SSID is required"}), 400

    try:
        cmd = ["sudo", "nmcli", "dev", "wifi", "connect", ssid]
        if password:
            cmd.extend(["password", password])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        
        if result.returncode == 0:
            return jsonify({"status": "success", "message": f"Connected to {ssid}!"})
        else:
            return jsonify({"status": "error", "message": result.stderr or "Connection failed"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/service/restart', methods=['POST'])
def restart_service():
    service_name = "mlb-led-scoreboard.service"
    try:
        result = subprocess.run(
            ["sudo", "systemctl", "restart", service_name],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            return jsonify({"status": "success", "message": f"{service_name} restarted successfully!"})
        else:
            return jsonify({"status": "error", "message": result.stderr or f"Failed to restart {service_name}"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
