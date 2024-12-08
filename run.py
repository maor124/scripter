import http.server
import socketserver
import os
import time
import threading
from flask import Flask, request, jsonify, send_from_directory
import os

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



DIRECTORY = "."
PORT = 54545
CHECK_INTERVAL = 5  # Check for changes every 5 second

class ReloadHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path == '/reload':
            self.send_response(200)
            self.end_headers()
            return
        return super().do_GET()

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

class ReloadHTTPServer(socketserver.TCPServer):
    allow_reuse_address = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clients = set()

    def reload_clients(self):
        for client in self.clients:
            try:
                client.send(b'HTTP/1.1 200 OK\r\n\r\n')
                client.close()
            except:
                pass
        self.clients.clear()

def get_file_modification_times(directory):
    file_times = {}
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_times[file_path] = os.path.getmtime(file_path)
    return file_times

def check_for_changes(server, directory):
    last_file_times = get_file_modification_times(directory)
    while True:
        time.sleep(CHECK_INTERVAL)
        current_file_times = get_file_modification_times(directory)
        if current_file_times != last_file_times:
            print("Changes detected, reloading clients...")
            server.reload_clients()
            last_file_times = current_file_times

def run():
    os.chdir(DIRECTORY)
    handler = ReloadHTTPRequestHandler
    server = ReloadHTTPServer(("", PORT), handler)
    
    # Start the file change checking thread
    change_thread = threading.Thread(target=check_for_changes, args=(server, DIRECTORY))
    change_thread.daemon = True
    change_thread.start()

    print(f"Serving at port {PORT}")
    print(f"Serving files from directory: {DIRECTORY}")
    print(f"Checking for changes every {CHECK_INTERVAL} second(s)")
    server.serve_forever()

if __name__ == '__main__':
    run()
