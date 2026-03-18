#!/usr/bin/env python3
"""
Simple HTTP server to serve the frontend
Run: python serve.py
Then visit: http://localhost:8888
"""

import http.server
import socketserver
import os

PORT = 8888
DIRECTORY = "frontend"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"✅ Frontend server running at http://localhost:{PORT}")
    print(f"📁 Serving from: {DIRECTORY}/")
    print(f"🌐 Open: http://localhost:{PORT}/dashboard.html")
    print(f"\nPress Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Server stopped")
