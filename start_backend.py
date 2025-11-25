#!/usr/bin/env python
import os
import sys

# Change to backend directory
backend_path = r"c:\Users\PTC\Downloads\url-guardian-demo-main\url-guardian-demo-main\backend"
os.chdir(backend_path)
sys.path.insert(0, backend_path)

# Import and run uvicorn with port 8001
import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
