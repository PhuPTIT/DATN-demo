#!/usr/bin/env python3
"""
URL Guardian - Start Backend & Frontend
Comprehensive launcher for full application
"""
import os
import sys
import subprocess
import time
import platform
import requests

def check_port_available(port: int) -> bool:
    """Check if port is available"""
    try:
        requests.get(f"http://localhost:{port}/health", timeout=1)
        return False  # Port is in use
    except:
        return True  # Port is available

def start_backend():
    """Start backend server"""
    print("\n" + "="*60)
    print("🚀 Starting URL Guardian Backend")
    print("="*60)
    
    if not check_port_available(8001):
        print("⚠️  Port 8001 already in use. Backend might already be running.")
        return
    
    backend_path = os.path.join(os.path.dirname(__file__), "backend")
    
    if platform.system() == "Windows":
        subprocess.Popen(
            ["python", "main.py"],
            cwd=backend_path,
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        subprocess.Popen(
            ["python", "main.py"],
            cwd=backend_path
        )
    
    print("✅ Backend process started (Port 8001)")
    print("   Waiting for models to load (30-60 seconds)...")
    
    # Wait for backend to be ready
    max_wait = 120
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = requests.get("http://localhost:8001/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is ready!")
                return
        except:
            pass
        time.sleep(2)
    
    print("⚠️  Backend took too long to start. Check logs manually.")

def start_frontend():
    """Start frontend server"""
    print("\n" + "="*60)
    print("🎨 Starting URL Guardian Frontend")
    print("="*60)
    
    if not check_port_available(8080):
        print("⚠️  Port 8080 already in use. Frontend might already be running.")
        return
    
    root_path = os.path.dirname(__file__)
    
    if platform.system() == "Windows":
        subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=root_path,
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=root_path
        )
    
    print("✅ Frontend process started (Port 8080)")
    print("   Vite dev server initializing...")
    
    # Wait for frontend to be ready
    time.sleep(5)
    print("✅ Frontend should be ready!")

def main():
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "🔗 URL Guardian - Full Application" + " "*10 + "║")
    print("║" + " "*14 + "Phishing Detection with 3 AI Models" + " "*9 + "║")
    print("╚" + "="*58 + "╝")
    
    print("\n📋 System Check:")
    
    # Check Python
    try:
        python_version = subprocess.check_output(["python", "--version"], text=True).strip()
        print(f"  ✅ Python: {python_version}")
    except:
        print("  ❌ Python not found!")
        return
    
    # Check Node.js
    try:
        node_version = subprocess.check_output(["node", "--version"], text=True).strip()
        npm_version = subprocess.check_output(["npm", "--version"], text=True).strip()
        print(f"  ✅ Node.js: {node_version}")
        print(f"  ✅ npm: {npm_version}")
    except:
        print("  ❌ Node.js/npm not found!")
        return
    
    # Check required directories
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    if not os.path.exists(backend_dir):
        print("  ❌ Backend directory not found!")
        return
    print(f"  ✅ Backend directory found")
    
    print("\n🔌 Port Check:")
    print(f"  Port 8001 (Backend): {'✅ Available' if check_port_available(8001) else '⚠️  In use'}")
    print(f"  Port 8080 (Frontend): {'✅ Available' if check_port_available(8080) else '⚠️  In use'}")
    
    print("\n🚀 Starting Application:")
    
    # Start both
    start_backend()
    time.sleep(3)
    start_frontend()
    
    print("\n" + "="*60)
    print("✅ Application Started!")
    print("="*60)
    print("\n📍 Access Points:")
    print("   • Frontend:  http://localhost:8080")
    print("   • Backend:   http://localhost:8001")
    print("   • API Docs:  http://localhost:8001/docs")
    print("\n💡 Tips:")
    print("   • Use CTRL+C to stop the application")
    print("   • Check console windows for error messages")
    print("   • Refresh browser if frontend doesn't load")
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        main()
        print("\n⏳ Keeping application running...")
        print("(Press Ctrl+C to stop)\n")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
