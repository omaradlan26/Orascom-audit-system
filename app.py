import streamlit as st
import os
import sys
import threading
import time
import uvicorn

# Set environment variables for Hugging Face Spaces
if "AUDIT_API_URL" not in os.environ:
    os.environ["AUDIT_API_URL"] = "http://127.0.0.1:8000"

if "AUDIT_DB_PATH" not in os.environ:
    # Use persistent storage in Spaces
    os.environ["AUDIT_DB_PATH"] = "/data/audit_system.db"

# Add backend to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import backend modules to run API server in background
from backend.app.main import app as fastapi_app

def start_backend():
    """Start FastAPI backend in a background thread"""
    # Configure uvicorn for Spaces
    config = uvicorn.Config(
        fastapi_app, 
        host="127.0.0.1", 
        port=8000, 
        log_level="error",
        access_log=False
    )
    server = uvicorn.Server(config)
    server.run()

# Start backend in background
backend_thread = threading.Thread(target=start_backend, daemon=True)
backend_thread.start()

# Wait for backend to start
time.sleep(5)

# Now import and run the frontend
from frontend.app import main

if __name__ == "__main__":
    main()
