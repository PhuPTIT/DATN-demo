#!/usr/bin/env python
"""
Simple script to run backend from root directory
"""
import os
import sys

# Add backend to path
sys.path.insert(0, 'backend')
os.chdir('backend')

# Import and run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=False)
