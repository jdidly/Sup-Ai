#!/usr/bin/env python3
"""
PSC TON Trading System Dashboard - Universal Version
Works with or without Streamlit, provides full functionality
"""

import sys
import os
from pathlib import Path

def check_streamlit():
    """Check if streamlit and required packages are available"""
    try:
        import streamlit # type: ignore
        import pandas
        import plotly
        return True
    except ImportError:
        return False

def launch_streamlit_dashboard():
    """Launch full Streamlit dashboard"""
    print("🌐 Launching Streamlit Dashboard...")
    print("📍 URL: http://localhost:8501")
    print("🔄 Starting server...")
    
    import subprocess
    try:
        # Run streamlit dashboard
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "dashboard.py", 
            "--server.port=8501",
            "--server.headless=true"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard closed")
    except Exception as e:
        print(f"❌ Error: {e}")

def launch_simple_interface():
    """Launch simple terminal interface"""
    import json
    import yaml
    from datetime import datetime
    
    # Add paths for trading system
    current_dir = Path(__file__).parent.parent
    sys.path.append(str(current_dir))
    sys.path.append(str(current_dir / "src"))
    
    print("🚀 PSC TON Trading System - Simple Interface")
    print("=" * 50)
    
    # Try to load trading system
    try:
        from src.ml_engine import MLEngine
        ml_available = True
        print("✅ ML Engine loaded successfully")
    except ImportError as e:
        ml_available = False
        print(f"⚠️ ML Engine not available: {e}")
    
    # Configuration management
    config_file = current_dir / "config" / "settings.yaml"
    
    def load_config():
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return {
            'trading': {'scan_interval': 30, 'confidence_threshold': 0.7, 'position_size': 1000},
            'superp': {'enabled': True, 'time_limit_minutes': 10},
            'ml': {'enabled': True}
        }
    
    def save_config(config):
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
    
    # Main interface loop
    while True:
        print(f"\n🚀 PSC TON DASHBOARD - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 40)
        print("1. 📊 View Configuration")
        print("2. ⚙️ Modify Settings")
        print("3. 🧠 Test ML Engine")
        print("4. 🌐 Try Web Dashboard")
        print("5. 🚪 Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            print("\n📊 CURRENT CONFIGURATION:")
            config = load_config()
            for section, settings in config.items():
                print(f"\n{section.upper()}:")
                for key, value in settings.items():
                    print(f"  {key}: {value}")
        
        elif choice == "2":
            print("\n⚙️ MODIFY SETTINGS:")
            config = load_config()
            
            try:
                new_interval = input(f"Scan interval [{config['trading']['scan_interval']}]: ").strip()
                if new_interval:
                    config['trading']['scan_interval'] = int(new_interval)
                
                new_threshold = input(f"Confidence threshold [{config['trading']['confidence_threshold']}]: ").strip()
                if new_threshold:
                    config['trading']['confidence_threshold'] = float(new_threshold)
                
                new_size = input(f"Position size [{config['trading']['position_size']}]: ").strip()
                if new_size:
                    config['trading']['position_size'] = int(new_size)
                
                save_config(config)
                print("✅ Configuration saved!")
                
            except ValueError as e:
                print(f"❌ Invalid input: {e}")
        
        elif choice == "3":
            print("\n🧠 TESTING ML ENGINE:")
            if ml_available:
                try:
                    ml_engine = MLEngine()
                    prediction = ml_engine.predict_trade_outcome(1.5, 50.0, 1.5, 1000)
                    print(f"✅ Test successful!")
                    print(f"   Recommendation: {prediction['recommendation']}")
                    print(f"   Confidence: {prediction['confidence']:.2%}")
                    print(f"   Win Probability: {prediction['win_probability']:.2%}")
                except Exception as e:
                    print(f"❌ Test failed: {e}")
            else:
                print("❌ ML Engine not available")
        
        elif choice == "4":
            print("\n🌐 WEB DASHBOARD SETUP:")
            if check_streamlit():
                print("✅ Streamlit available - launching...")
                launch_streamlit_dashboard()
                break
            else:
                print("❌ Missing dependencies. Install with:")
                print("   pip install streamlit pandas plotly")
        
        elif choice == "5":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

def main():
    """Main launcher function"""
    print("🚀 PSC TON Trading System Dashboard")
    print("=" * 40)
    
    if check_streamlit():
        print("✅ Full web dashboard available")
        print("🌐 Choose interface:")
        print("1. Web Dashboard (Streamlit)")
        print("2. Simple Terminal Interface")
        
        choice = input("\nSelect (1-2): ").strip()
        
        if choice == "1":
            launch_streamlit_dashboard()
        else:
            launch_simple_interface()
    else:
        print("⚠️ Web dashboard dependencies missing")
        print("📦 Install with: pip install streamlit pandas plotly")
        print("🔄 Using simple interface...")
        launch_simple_interface()

if __name__ == "__main__":
    main()
