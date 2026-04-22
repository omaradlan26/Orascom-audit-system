import streamlit as st
import os
import sys

# Add backend to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import backend modules to run API server in background
import threading
import time
from backend.app.main import app as fastapi_app
import uvicorn

def start_backend():
    """Start FastAPI backend in a background thread"""
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="error")

# Start backend in background
backend_thread = threading.Thread(target=start_backend, daemon=True)
backend_thread.start()

# Wait a moment for backend to start
time.sleep(3)

# Now import and run the frontend
from frontend.app import main

if __name__ == "__main__":
    main()
