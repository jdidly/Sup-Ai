#!/usr/bin/env python3
"""
PSC TON Trading System Dashboard Launcher
Launches the Streamlit dashboard for the trading system
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Change to the core_system directory
    core_dir = Path(__file__).parent
    os.chdir(core_dir)
    
    print("🚀 Starting PSC TON Trading Dashboard...")
    print(f"📁 Working directory: {core_dir}")
    print("🌐 Dashboard will be available at: http://localhost:8501")
    print("📱 Use /dashboard command in Telegram for remote access info")
    print("-" * 50)
    
    try:
        # Launch Streamlit dashboard
        cmd = [sys.executable, "-m", "streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n⏹️ Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("Make sure streamlit is installed: pip install streamlit")

if __name__ == "__main__":
    main()
