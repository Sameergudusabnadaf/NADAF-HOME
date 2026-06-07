from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

import db

# Initialize the database when the server starts
db.init_db()

@app.route('/')
def index():
    # Read and serve the home.html file
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'home.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    return render_template_string(html_content)

import time

# Global variable to track the last time the ESP pinged the server
last_esp_ping = 0

@app.route('/update_device', methods=['POST'])
def update_device():
    global last_esp_ping
    user_agent = request.headers.get('User-Agent', '')
    if 'ESP' in user_agent or 'Arduino' in user_agent:
        last_esp_ping = time.time()

    data = request.get_json()
    device_id = data.get('id')
    new_state = data.get('state')
    
    success = db.update_device_state(device_id, new_state)
    
    if success:
        print(f"Device {device_id} updated to {new_state} in Database")
        return jsonify({"status": "success", "device": device_id, "state": new_state}), 200
    else:
        return jsonify({"status": "error", "message": "Device not found"}), 404

@app.route('/get_states', methods=['GET'])
def get_states():
    global last_esp_ping
    user_agent = request.headers.get('User-Agent', '')
    if 'ESP' in user_agent or 'Arduino' in user_agent:
        last_esp_ping = time.time()

    # Fetch states from the database
    current_states = db.get_all_states()
    return jsonify(current_states), 200

@app.route('/esp_status', methods=['GET'])
def esp_status():
    # If the ESP polled the server within the last 5 seconds, it is connected
    is_online = (time.time() - last_esp_ping) < 5
    return jsonify({"online": is_online}), 200

if __name__ == '__main__':
    # Listen on all interfaces so the ESP32 can connect
    app.run(host='0.0.0.0', port=5000, debug=True)
