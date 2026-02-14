#!/usr/bin/env python3
"""
Startup script for ShardCloud deployment.
Starts both the manager (bot spawner) and web server.
"""
import subprocess
import sys

if __name__ == "__main__":
    # Initialize database if needed
    print("[*] Initializing database...")
    subprocess.run([sys.executable, "database.py"])
    
    # Start manager in background
    print("[*] Starting bot manager...")
    subprocess.Popen([sys.executable, "manager.py"])
    
    # Start web server (import and run Flask directly)
    print("[*] Starting web server...")
    from web import app
    app.run(host='0.0.0.0', port=8080, debug=False)
