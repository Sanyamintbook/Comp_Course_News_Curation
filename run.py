"""
Module: Project Runner
Purpose: Starts both the FastAPI backend and Streamlit frontend simultaneously.
Logic: Uses the subprocess module to spawn both processes and gracefully shut them down together on exit.
"""
import subprocess
import sys
import time

def main():
    print("==========================================")
    print("Starting Unified Educational Platform...")
    print("==========================================\n")
    
    # Define commands
    backend_cmd = [sys.executable, "src/api/main.py"]
    frontend_cmd = [sys.executable, "-m", "streamlit", "run", "frontend/app.py"]
    
    backend_process = None
    frontend_process = None
    try:
        # Start Backend
        print("-> Launching FastAPI Backend (Port 8000)...")
        backend_process = subprocess.Popen(backend_cmd)
        
        # Give backend 2 seconds to initialize before starting frontend
        time.sleep(2)
        
        # Start Frontend
        print("-> Launching Streamlit Frontend (Port 8501)...")
        frontend_process = subprocess.Popen(frontend_cmd)
        
        print("\nAll systems are running!")
        print("Press CTRL+C at any time to safely shut down both servers.\n")
        
        # Keep script alive while servers run
        backend_process.wait()
        frontend_process.wait()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Shutting down all services gracefully...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        if backend_process:
            backend_process.wait()
        if frontend_process:
            frontend_process.wait()
        print("✅ Shutdown complete.")

if __name__ == "__main__":
    main()
