#!/usr/bin/env python3
"""
PSC TON Trading System Dashboard - Minimal Version
Interactive web interface for monitoring and controlling the trading bot
Works without external ML dependencies
"""

import json
import yaml
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging
import sys
import os

# Add the parent directory to path for imports
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))

print("🚀 PSC TON Trading Dashboard - Minimal Version")
print("=" * 50)

class SimpleDashboard:
    def __init__(self):
        self.config_file = Path("config/settings.yaml")
        self.data_dir = Path("data")
        self.logs_dir = Path("logs")
        
    def load_config(self):
        """Load current configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return yaml.safe_load(f)
            else:
                return self.get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()
    
    def get_default_config(self):
        """Default configuration values"""
        return {
            'trading': {
                'scan_interval': 30,
                'confidence_threshold': 0.7,
                'ratio_threshold': 1.5,
                'max_positions': 5,
                'position_size': 1000,
                'stop_loss_pct': 5.0,
                'take_profit_pct': 10.0,
            },
            'superp': {
                'enabled': True,
                'conservative_range': [1, 100],
                'moderate_range': [100, 1000],
                'aggressive_range': [1000, 5000],
                'time_limit_minutes': 10
            },
            'ml': {
                'enabled': True,
                'retrain_interval': 50,
                'confidence_boost': 0.1,
            }
        }
    
    def load_config(self):
        """Load current configuration with fallback to defaults"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = yaml.safe_load(f)
                    # Ensure all required sections exist
                    default_config = self.get_default_config()
                    for section in default_config:
                        if section not in config:
                            config[section] = default_config[section]
                        else:
                            # Ensure all keys exist in each section
                            for key in default_config[section]:
                                if key not in config[section]:
                                    config[section][key] = default_config[section][key]
                    return config
            else:
                return self.get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()
    
    def save_config(self, config):
        """Save configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            print("✅ Configuration saved successfully!")
            return True
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False
    
    def show_config(self):
        """Display current configuration"""
        config = self.load_config()
        
        print("\n📊 CURRENT CONFIGURATION")
        print("-" * 30)
        
        try:
            if 'trading' in config:
                print("🎯 Trading Parameters:")
                for key, value in config['trading'].items():
                    print(f"  {key}: {value}")
            
            if 'superp' in config:
                print("\n🎢 Superp Settings:")
                for key, value in config['superp'].items():
                    print(f"  {key}: {value}")
            
            if 'ml' in config:
                print("\n🧠 ML Settings:")
                for key, value in config['ml'].items():
                    print(f"  {key}: {value}")
        except Exception as e:
            print(f"Error displaying config: {e}")
            print("Using default configuration...")
            config = self.get_default_config()
            self.save_config(config)
            print("✅ Default configuration created!")
    
    def modify_config(self):
        """Interactive configuration modification"""
        config = self.load_config()
        
        print("\n⚙️ CONFIGURATION MODIFICATION")
        print("-" * 35)
        
        while True:
            print("\nSelect category to modify:")
            print("1. Trading Parameters")
            print("2. Superp Settings")
            print("3. ML Settings")
            print("4. Save and Exit")
            print("5. Exit without saving")
            
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == "1":
                self.modify_trading_config(config)
            elif choice == "2":
                self.modify_superp_config(config)
            elif choice == "3":
                self.modify_ml_config(config)
            elif choice == "4":
                self.save_config(config)
                break
            elif choice == "5":
                print("Exiting without saving...")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def modify_trading_config(self, config):
        """Modify trading configuration"""
        print("\n🎯 Trading Parameters:")
        trading = config['trading']
        
        try:
            scan_interval = input(f"Scan Interval [{trading['scan_interval']}]: ").strip()
            if scan_interval:
                trading['scan_interval'] = int(scan_interval)
            
            confidence = input(f"Confidence Threshold [{trading['confidence_threshold']}]: ").strip()
            if confidence:
                trading['confidence_threshold'] = float(confidence)
            
            ratio = input(f"Ratio Threshold [{trading['ratio_threshold']}]: ").strip()
            if ratio:
                trading['ratio_threshold'] = float(ratio)
            
            max_pos = input(f"Max Positions [{trading['max_positions']}]: ").strip()
            if max_pos:
                trading['max_positions'] = int(max_pos)
            
            pos_size = input(f"Position Size [{trading['position_size']}]: ").strip()
            if pos_size:
                trading['position_size'] = int(pos_size)
                
            print("✅ Trading parameters updated!")
            
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
    
    def modify_superp_config(self, config):
        """Modify Superp configuration"""
        print("\n🎢 Superp Settings:")
        superp = config['superp']
        
        try:
            enabled = input(f"Enable Superp [{superp['enabled']}] (y/n): ").strip().lower()
            if enabled in ['y', 'yes', 'true']:
                superp['enabled'] = True
            elif enabled in ['n', 'no', 'false']:
                superp['enabled'] = False
            
            conservative = input(f"Conservative Max [{superp['conservative_range'][1]}]: ").strip()
            if conservative:
                superp['conservative_range'][1] = int(conservative)
            
            moderate = input(f"Moderate Max [{superp['moderate_range'][1]}]: ").strip()
            if moderate:
                superp['moderate_range'][1] = int(moderate)
            
            aggressive = input(f"Aggressive Max [{superp['aggressive_range'][1]}]: ").strip()
            if aggressive:
                superp['aggressive_range'][1] = int(aggressive)
            
            time_limit = input(f"Time Limit Minutes [{superp['time_limit_minutes']}]: ").strip()
            if time_limit:
                superp['time_limit_minutes'] = int(time_limit)
                
            print("✅ Superp parameters updated!")
            
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
    
    def modify_ml_config(self, config):
        """Modify ML configuration"""
        print("\n🧠 ML Settings:")
        ml = config['ml']
        
        try:
            enabled = input(f"Enable ML [{ml['enabled']}] (y/n): ").strip().lower()
            if enabled in ['y', 'yes', 'true']:
                ml['enabled'] = True
            elif enabled in ['n', 'no', 'false']:
                ml['enabled'] = False
            
            retrain = input(f"Retrain Interval [{ml['retrain_interval']}]: ").strip()
            if retrain:
                ml['retrain_interval'] = int(retrain)
            
            boost = input(f"Confidence Boost [{ml['confidence_boost']}]: ").strip()
            if boost:
                ml['confidence_boost'] = float(boost)
                
            print("✅ ML parameters updated!")
            
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
    
    def show_logs(self):
        """Display recent logs"""
        print("\n📋 RECENT LOGS")
        print("-" * 20)
        
        log_file = self.logs_dir / "hybrid_system.log"
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    recent_lines = lines[-20:]  # Show last 20 lines
                    
                for line in recent_lines:
                    print(line.strip())
            except Exception as e:
                print(f"❌ Error reading logs: {e}")
        else:
            print("📝 No log file found")
    
    def test_ml_engine(self):
        """Test ML engine functionality"""
        print("\n🧠 TESTING ML ENGINE")
        print("-" * 25)
        
        try:
            # Import ML engine from core_system/src
            core_system_src_path = Path(__file__).parent / "core_system" / "src"
            sys.path.append(str(core_system_src_path))
            from ml_engine import MLEngine # type: ignore
            
            ml_engine = MLEngine()
            print("✅ ML Engine initialized successfully")
            
            # Test basic functionality with correct parameters
            prediction = ml_engine.predict_trade_outcome(
                psc_price=1.5, 
                ton_price=50.0, 
                ratio=1.5,
                amount=1000
            )
            print(f"✅ Test prediction: {prediction}")
            
            performance = ml_engine.get_model_performance()
            print(f"✅ Model performance: {performance}")
            
            return True
            
        except Exception as e:
            print(f"❌ ML Engine test failed: {e}")
            return False

def main():
    """Main dashboard function"""
    dashboard = SimpleDashboard()
    
    while True:
        print("\n🚀 PSC TON TRADING DASHBOARD")
        print("=" * 35)
        print("1. Show Current Configuration")
        print("2. Modify Configuration")
        print("3. View Recent Logs")
        print("4. Test ML Engine")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            dashboard.show_config()
        elif choice == "2":
            dashboard.modify_config()
        elif choice == "3":
            dashboard.show_logs()
        elif choice == "4":
            dashboard.test_ml_engine()
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
