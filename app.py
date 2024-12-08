from flask import Flask, request, jsonify, send_from_directory
import os
import sys
import time
import threading

app = Flask(__name__)

# This should be stored securely, not in plain text
VALID_CREDENTIALS = {
    "admin": "password123"
}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password:
        return jsonify({"success": True, "message": "Login successful"}), 200
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/processes')
def get_processes():
    # In a real application, this would fetch from a database
    processes = [
        {"id": 1, "name": "Process 1"},
        {"id": 2, "name": "Process 2"},
        {"id": 3, "name": "Process 3"}
    ]
    return jsonify(processes)

def get_file_modification_times():
    file_times = {}
    for filename in os.listdir('.'):
        if filename.endswith('.py'):
            file_times[filename] = os.path.getmtime(filename)
    return file_times

def check_for_changes(initial_times):
    while True:
        time.sleep(1)  # Check every second
        current_times = get_file_modification_times()
        if current_times != initial_times:
            print("Detected change. Restarting server...")
            os.execv(sys.executable, ['python'] + sys.argv)

def start_file_watcher():
    initial_times = get_file_modification_times()
    watcher_thread = threading.Thread(target=check_for_changes, args=(initial_times,))
    watcher_thread.daemon = True
    watcher_thread.start()

if __name__ == '__main__':
    start_file_watcher()
    app.run(host='0.0.0.0', port=54545, debug=False, use_reloader=False)
