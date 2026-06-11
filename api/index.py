from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import json
import redis

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Connect to Vercel KV
redis_client = None
try:
    # Vercel provides KV_URL when Vercel KV is linked to the project
    kv_url = os.environ.get('KV_URL')
    if kv_url:
        redis_client = redis.from_url(kv_url)
except Exception as e:
    print("Redis connection error:", e)

# Fallback in-memory state (Note: resets when serverless function cold starts)
memory_states = {
    "light1": "OFF", "light2": "OFF", "light3": "OFF", "hallfan": "OFF",
    "r1light1": "OFF", "r1light2": "OFF", "r1fan": "OFF",
    "r2light1": "OFF", "r2light2": "OFF", "r2fan": "OFF"
}
last_memory_ping = 0

def get_all_states():
    global memory_states
    if redis_client:
        try:
            states = redis_client.get('device_states')
            if states:
                parsed_states = json.loads(states)
                memory_states.update(parsed_states) # Cache the latest successful read
                return parsed_states
            else:
                redis_client.set('device_states', json.dumps(memory_states))
                return memory_states
        except Exception as e:
            print("Redis get error:", e)
            # Fallback to last known states instead of resetting to OFF
            return memory_states
    return memory_states

def update_state(device_id, state):
    global memory_states
    states = get_all_states()
    if device_id in states:
        states[device_id] = state
        memory_states[device_id] = state # Always update local cache
        if redis_client:
            try:
                redis_client.set('device_states', json.dumps(states))
            except Exception as e:
                print("Redis set error:", e)
        return True
    return False

def record_ping():
    global last_memory_ping
    if redis_client:
        try:
            redis_client.set('last_esp_ping', str(time.time()))
        except Exception as e:
            pass
    else:
        last_memory_ping = time.time()

def get_last_ping():
    if redis_client:
        try:
            val = redis_client.get('last_esp_ping')
            if val:
                return float(val)
        except Exception as e:
            pass
    return last_memory_ping

@app.route('/api/update_device', methods=['POST'])
@app.route('/update_device', methods=['POST'])
def update_device():
    user_agent = request.headers.get('User-Agent', '')
    if 'ESP' in user_agent or 'Arduino' in user_agent:
        record_ping()

    data = request.get_json()
    device_id = data.get('id')
    new_state = data.get('state')
    
    success = update_state(device_id, new_state)
    
    if success:
        return jsonify({"status": "success", "device": device_id, "state": new_state}), 200
    else:
        return jsonify({"status": "error", "message": "Device not found"}), 404

@app.route('/api/get_states', methods=['GET'])
@app.route('/get_states', methods=['GET'])
def get_states():
    user_agent = request.headers.get('User-Agent', '')
    if 'ESP' in user_agent or 'Arduino' in user_agent:
        record_ping()

    current_states = get_all_states()
    return jsonify(current_states), 200

@app.route('/api/esp_status', methods=['GET'])
@app.route('/esp_status', methods=['GET'])
def esp_status():
    last_ping = get_last_ping()
    # 5 seconds is very tight for serverless cold starts. Let's make it 10s.
    is_online = (time.time() - last_ping) < 10
    return jsonify({"online": is_online}), 200

# Vercel Serverless requires the app to be available as `app`
