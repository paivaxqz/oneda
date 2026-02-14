#!/usr/bin/env python3
"""
Startup script for ShardCloud deployment.
Starts both the manager (bot spawner) and web server.
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    # Initialize database if needed
    print("[*] Initializing database...")
    subprocess.run([sys.executable, "database.py"])
    
    # Start manager in background
    print("[*] Starting bot manager...")
    manager_proc = subprocess.Popen([sys.executable, "manager.py"])
    
    # Start web server (this blocks)
    print("[*] Starting web server...")
    subprocess.run([sys.executable, "-m", "gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "web:app"])
