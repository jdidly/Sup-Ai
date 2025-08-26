#!/usr/bin/env python3
"""
PSC TON Trading System Dashboard
Interactive web interface for monitoring and controlling the trading bot
"""

# Check for required dependencies first
missing_deps = []
try:
    import streamlit as st # type: ignore
except ImportError:
    missing_deps.append("streamlit")

try:
    import pandas as pd
except ImportError:
    missing_deps.append("pandas")

try:
    import plotly.graph_objs as go
    import plotly.express as px
    from plotly.subplots import make_subplots
except ImportError:
    missing_deps.append("plotly")

if missing_deps:
    print("❌ Missing required dependencies:")
    for dep in missing_deps:
        print(f"   - {dep}")
    print("\n📦 To install missing dependencies, run:")
    print(f"   pip install {' '.join(missing_deps)}")
    print("\n⚠️  If pip hangs, try using conda or manual installation")
    print("\n🔄 Falling back to simple dashboard...")
    print("Run: python ../../simple_dashboard.py")
    exit(1)

import json
import yaml
import asyncio
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging
import sys
import os

# Add the parent directory to path for imports
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))
sys.path.append(str(current_dir / "src"))

try:
    from psc_ton_system import PSCTONTradingBot
    from src.ml_engine import MLEngine
    PSC_BOT_AVAILABLE = True
    ML_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    print("🔄 Some features may be limited")
    PSC_BOT_AVAILABLE = False
    ML_ENGINE_AVAILABLE = False
    
    # Create mock classes for dashboard to work
    class MockBot:
        def __init__(self):
            self.ml_engine = None
            self.open_positions = {}
    
    class MockMLEngine:
        def get_model_performance(self):
            return {'total_predictions': 0, 'accuracy': 0.0, 'model_status': 'Not available'}
    
    PSCTONTradingBot = MockBot
    MLEngine = MockMLEngine

# Configure Streamlit page
st.set_page_config(
    page_title="PSC TON Trading Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global variables for bot instance
if 'trading_bot' not in st.session_state:
    st.session_state.trading_bot = None
if 'bot_running' not in st.session_state:
    st.session_state.bot_running = False
if 'live_data' not in st.session_state:
    st.session_state.live_data = []

class TradingDashboard:
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
            if 'st' in globals():
                st.error(f"Error loading config: {e}")
            else:
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
                'max_leverage': 1000,
                'min_leverage': 10
            },
            'superp': {
                'enabled': True,
                'conservative_range': [1, 100],
                'moderate_range': [100, 1000],
                'aggressive_range': [1000, 5000],
                'extreme_range': [5000, 10000],
                'time_limit_minutes': 10
            },
            'ml': {
                'enabled': True,
                'retrain_interval': 50,
                'confidence_boost': 0.1,
                'feature_count': 9
            },
            'telegram': {
                'enabled': False,
                'send_signals': True,
                'send_trades': True,
                'send_status': True
            }
        }
    
    def save_config(self, config):
        """Save configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            return True
        except Exception as e:
            if 'st' in globals():
                st.error(f"Error saving config: {e}")
            else:
                print(f"Error saving config: {e}")
            return False
    
    def load_trading_data(self):
        """Load trading data for display"""
        data = {}
        
        # Load trade logs
        trade_file = self.data_dir / "live_trades.csv"
        if trade_file.exists():
            try:
                data['trades'] = pd.read_csv(trade_file)
            except:
                data['trades'] = pd.DataFrame()
        else:
            data['trades'] = pd.DataFrame()
        
        # Load signal logs  
        signal_file = self.data_dir / "psc_signals.csv"
        if signal_file.exists():
            try:
                data['signals'] = pd.read_csv(signal_file)
            except:
                data['signals'] = pd.DataFrame()
        else:
            data['signals'] = pd.DataFrame()
        
        # Load prediction data
        pred_file = self.data_dir / "ml" / "prediction_history.json"
        if pred_file.exists():
            try:
                with open(pred_file, 'r') as f:
                    pred_data = json.load(f)
                    data['predictions'] = pred_data.get('predictions', [])
            except:
                data['predictions'] = []
        else:
            data['predictions'] = []
        
        return data
    
    def get_system_status(self):
        """Get current system status"""
        status = {
            'bot_running': st.session_state.bot_running,
            'ml_engine': False,
            'config_loaded': self.config_file.exists(),
            'data_available': False,
            'total_trades': 0,
            'total_signals': 0,
            'last_update': 'Never'
        }
        
        if st.session_state.trading_bot:
            status['ml_engine'] = st.session_state.trading_bot.ml_engine is not None
        
        # Check data availability
        data = self.load_trading_data()
        if not data['trades'].empty:
            status['data_available'] = True
            status['total_trades'] = len(data['trades'])
            status['last_update'] = data['trades']['timestamp'].iloc[-1] if 'timestamp' in data['trades'].columns else 'Unknown'
        
        if not data['signals'].empty:
            status['total_signals'] = len(data['signals'])
        
        return status

def main():
    dashboard = TradingDashboard()
    
    # Header
    st.title("🚀 PSC TON Trading System Dashboard")
    st.markdown("---")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🎛️ Control Panel")
        
        # System Status
        st.subheader("📊 System Status")
        status = dashboard.get_system_status()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Bot Status", "🟢 Running" if status['bot_running'] else "🔴 Stopped")
            st.metric("ML Engine", "✅ Active" if status['ml_engine'] else "❌ Inactive")
        with col2:
            st.metric("Total Trades", status['total_trades'])
            st.metric("Total Signals", status['total_signals'])
        
        # Bot Controls
        st.subheader("🎮 Bot Controls")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Start Bot", disabled=status['bot_running']):
                start_bot()
        with col2:
            if st.button("⏹️ Stop Bot", disabled=not status['bot_running']):
                stop_bot()
        
        if st.button("🔄 Restart Bot"):
            restart_bot()
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("📊 Refresh Data"):
            st.rerun()
        
        if st.button("🧠 Retrain ML"):
            retrain_ml_models()
        
        if st.button("💾 Export Data"):
            export_trading_data(dashboard)
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["⚙️ Configuration", "📈 Trading Monitor", "🧠 ML Analytics", "📋 Logs", "📊 Performance"])
    
    with tab1:
        show_configuration_panel(dashboard)
    
    with tab2:
        show_trading_monitor(dashboard)
    
    with tab3:
        show_ml_analytics(dashboard)
    
    with tab4:
        show_logs_panel(dashboard)
    
    with tab5:
        show_performance_panel(dashboard)

def show_configuration_panel(dashboard):
    """Configuration panel for trading parameters"""
    st.header("⚙️ Trading Configuration")
    
    config = dashboard.load_config()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Trading Parameters")
        
        # Scanning parameters
        scan_interval = st.slider(
            "Scan Interval (seconds)",
            min_value=5,
            max_value=300,
            value=config['trading']['scan_interval'],
            step=5,
            help="How often to scan for trading opportunities"
        )
        
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.1,
            max_value=1.0,
            value=config['trading']['confidence_threshold'],
            step=0.05,
            help="Minimum confidence required to open a position"
        )
        
        ratio_threshold = st.slider(
            "Ratio Threshold",
            min_value=1.0,
            max_value=5.0,
            value=config['trading']['ratio_threshold'],
            step=0.1,
            help="Minimum PSC/TON ratio to consider"
        )
        
        max_positions = st.number_input(
            "Max Concurrent Positions",
            min_value=1,
            max_value=20,
            value=config['trading']['max_positions'],
            help="Maximum number of open positions"
        )
        
        position_size = st.number_input(
            "Position Size (USD)",
            min_value=100,
            max_value=10000,
            value=config['trading']['position_size'],
            step=100,
            help="Default position size in USD"
        )
    
    with col2:
        st.subheader("🎢 Superp Leverage Settings")
        
        superp_enabled = st.checkbox(
            "Enable Superp No-Liquidation",
            value=config['superp']['enabled'],
            help="Enable Superp extreme leverage trading"
        )
        
        col2a, col2b = st.columns(2)
        with col2a:
            conservative_max = st.number_input(
                "Conservative Max (x)",
                min_value=1,
                max_value=1000,
                value=config['superp']['conservative_range'][1],
                help="Maximum leverage for conservative trades"
            )
            
            moderate_max = st.number_input(
                "Moderate Max (x)",
                min_value=100,
                max_value=5000,
                value=config['superp']['moderate_range'][1],
                help="Maximum leverage for moderate confidence trades"
            )
        
        with col2b:
            aggressive_max = st.number_input(
                "Aggressive Max (x)",
                min_value=1000,
                max_value=10000,
                value=config['superp']['aggressive_range'][1],
                help="Maximum leverage for aggressive trades"
            )
            
            time_limit = st.number_input(
                "Time Limit (minutes)",
                min_value=1,
                max_value=60,
                value=config['superp']['time_limit_minutes'],
                help="Maximum time to hold Superp positions"
            )
        
        st.subheader("🧠 ML Configuration")
        
        ml_enabled = st.checkbox(
            "Enable ML Predictions",
            value=config['ml']['enabled'],
            help="Use ML engine for trade predictions"
        )
        
        retrain_interval = st.number_input(
            "Retrain Interval",
            min_value=10,
            max_value=200,
            value=config['ml']['retrain_interval'],
            help="Retrain models every N predictions"
        )
    
    # Save configuration
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("💾 Save Configuration"):
            # Update config with new values
            config['trading']['scan_interval'] = scan_interval
            config['trading']['confidence_threshold'] = confidence_threshold
            config['trading']['ratio_threshold'] = ratio_threshold
            config['trading']['max_positions'] = max_positions
            config['trading']['position_size'] = position_size
            
            config['superp']['enabled'] = superp_enabled
            config['superp']['conservative_range'][1] = conservative_max
            config['superp']['moderate_range'][1] = moderate_max
            config['superp']['aggressive_range'][1] = aggressive_max
            config['superp']['time_limit_minutes'] = time_limit
            
            config['ml']['enabled'] = ml_enabled
            config['ml']['retrain_interval'] = retrain_interval
            
            if dashboard.save_config(config):
                st.success("✅ Configuration saved successfully!")
            else:
                st.error("❌ Failed to save configuration")
    
    with col2:
        if st.button("🔄 Load Defaults"):
            default_config = dashboard.get_default_config()
            dashboard.save_config(default_config)
            st.success("✅ Default configuration loaded!")
            st.rerun()

def show_trading_monitor(dashboard):
    """Real-time trading monitor"""
    st.header("📈 Trading Monitor")
    
    data = dashboard.load_trading_data()
    
    # Real-time metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not data['trades'].empty and 'profit_usd' in data['trades'].columns:
            total_profit = data['trades']['profit_usd'].sum()
            st.metric("Total Profit", f"${total_profit:.2f}")
        else:
            st.metric("Total Profit", "$0.00")
    
    with col2:
        if not data['trades'].empty:
            successful_trades = len(data['trades'][data['trades']['successful'] == True]) if 'successful' in data['trades'].columns else 0
            success_rate = (successful_trades / len(data['trades']) * 100) if len(data['trades']) > 0 else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")
        else:
            st.metric("Success Rate", "0%")
    
    with col3:
        active_positions = 0
        if st.session_state.trading_bot:
            try:
                active_positions = len([p for p in st.session_state.trading_bot.open_positions.values() if p.get('status') == 'ACTIVE'])
            except:
                active_positions = 0
        st.metric("Active Positions", active_positions)
    
    with col4:
        if not data['signals'].empty:
            recent_signals = len(data['signals'][data['signals']['timestamp'] > (datetime.now() - timedelta(hours=1)).isoformat()]) if 'timestamp' in data['signals'].columns else 0
            st.metric("Signals (1h)", recent_signals)
        else:
            st.metric("Signals (1h)", 0)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Recent Trades")
        if not data['trades'].empty:
            # Display recent trades table
            recent_trades = data['trades'].tail(10)
            if not recent_trades.empty:
                display_columns = ['timestamp', 'coin', 'profit_pct', 'successful', 'confidence']
                available_columns = [col for col in display_columns if col in recent_trades.columns]
                if available_columns:
                    st.dataframe(recent_trades[available_columns], use_container_width=True)
                else:
                    st.dataframe(recent_trades, use_container_width=True)
        else:
            st.info("No trading data available yet")
    
    with col2:
        st.subheader("🎯 Recent Signals")
        if not data['signals'].empty:
            recent_signals = data['signals'].tail(10)
            if not recent_signals.empty:
                display_columns = ['timestamp', 'coin', 'ratio', 'confidence', 'direction']
                available_columns = [col for col in display_columns if col in recent_signals.columns]
                if available_columns:
                    st.dataframe(recent_signals[available_columns], use_container_width=True)
                else:
                    st.dataframe(recent_signals, use_container_width=True)
        else:
            st.info("No signal data available yet")
    
    # Profit chart
    if not data['trades'].empty and 'timestamp' in data['trades'].columns and 'profit_usd' in data['trades'].columns:
        st.subheader("💰 Cumulative Profit")
        
        # Calculate cumulative profit
        trades_df = data['trades'].copy()
        trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
        trades_df = trades_df.sort_values('timestamp')
        trades_df['cumulative_profit'] = trades_df['profit_usd'].cumsum()
        
        fig = px.line(trades_df, x='timestamp', y='cumulative_profit', title='Cumulative Profit Over Time')
        fig.update_layout(yaxis_title='Profit (USD)', xaxis_title='Time')
        st.plotly_chart(fig, use_container_width=True)

def show_ml_analytics(dashboard):
    """ML engine analytics and performance"""
    st.header("🧠 ML Analytics")
    
    data = dashboard.load_trading_data()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 ML Performance")
        
        if st.session_state.trading_bot and st.session_state.trading_bot.ml_engine:
            try:
                performance = st.session_state.trading_bot.ml_engine.get_model_performance()
                
                st.metric("Total Predictions", performance.get('total_predictions', 0))
                st.metric("Overall Accuracy", f"{performance.get('overall_accuracy', 0):.1%}")
                st.metric("High Confidence Accuracy", f"{performance.get('high_confidence_accuracy', 0):.1%}")
                st.metric("Model Status", performance.get('model_status', 'Unknown'))
                
            except Exception as e:
                st.error(f"Error getting ML performance: {e}")
        else:
            st.info("ML engine not available")
    
    with col2:
        st.subheader("📈 Prediction History")
        
        if data['predictions']:
            pred_df = pd.DataFrame(data['predictions'])
            
            if not pred_df.empty and 'timestamp' in pred_df.columns:
                pred_df['timestamp'] = pd.to_datetime(pred_df['timestamp'])
                recent_predictions = pred_df.tail(10)
                
                display_columns = ['timestamp', 'prediction', 'actual_outcome']
                available_columns = [col for col in display_columns if col in recent_predictions.columns]
                
                if available_columns:
                    st.dataframe(recent_predictions[available_columns], use_container_width=True)
                else:
                    st.dataframe(recent_predictions, use_container_width=True)
        else:
            st.info("No prediction data available")
    
    # ML Controls
    st.subheader("🎛️ ML Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Retrain Models"):
            if st.session_state.trading_bot and st.session_state.trading_bot.ml_engine:
                try:
                    success = st.session_state.trading_bot.ml_engine.retrain_models()
                    if success:
                        st.success("✅ Models retrained successfully!")
                    else:
                        st.warning("⚠️ Not enough data for retraining")
                except Exception as e:
                    st.error(f"❌ Retraining failed: {e}")
            else:
                st.error("ML engine not available")
    
    with col2:
        if st.button("💾 Save Models"):
            if st.session_state.trading_bot and st.session_state.trading_bot.ml_engine:
                try:
                    st.session_state.trading_bot.ml_engine.save_models()
                    st.success("✅ Models saved successfully!")
                except Exception as e:
                    st.error(f"❌ Save failed: {e}")
            else:
                st.error("ML engine not available")
    
    with col3:
        if st.button("📚 Load Models"):
            if st.session_state.trading_bot and st.session_state.trading_bot.ml_engine:
                try:
                    st.session_state.trading_bot.ml_engine.load_models()
                    st.success("✅ Models loaded successfully!")
                except Exception as e:
                    st.error(f"❌ Load failed: {e}")
            else:
                st.error("ML engine not available")

def show_logs_panel(dashboard):
    """System logs and debugging information"""
    st.header("📋 System Logs")
    
    # Log level selector
    log_level = st.selectbox("Log Level", ["INFO", "DEBUG", "WARNING", "ERROR"], index=0)
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto-refresh logs", value=False)
    
    if auto_refresh:
        # Auto-refresh every 5 seconds
        placeholder = st.empty()
        
        for i in range(12):  # 1 minute of auto-refresh
            with placeholder.container():
                display_logs(dashboard, log_level)
            time.sleep(5)
    else:
        display_logs(dashboard, log_level)
    
    # Manual refresh button
    if st.button("🔄 Refresh Logs"):
        st.rerun()

def display_logs(dashboard, log_level):
    """Display system logs"""
    try:
        # Check for log files
        log_files = []
        
        # System log
        system_log = dashboard.logs_dir / "hybrid_system.log"
        if system_log.exists():
            log_files.append(("System Log", system_log))
        
        # Trading log (if exists)
        trading_log = dashboard.logs_dir / "trading.log"
        if trading_log.exists():
            log_files.append(("Trading Log", trading_log))
        
        if not log_files:
            st.info("No log files found")
            return
        
        # Display logs in tabs
        if len(log_files) > 1:
            tabs = st.tabs([name for name, _ in log_files])
            for tab, (name, log_file) in zip(tabs, log_files):
                with tab:
                    show_log_content(log_file, log_level)
        else:
            show_log_content(log_files[0][1], log_level)
            
    except Exception as e:
        st.error(f"Error displaying logs: {e}")

def show_log_content(log_file, log_level):
    """Show content of a specific log file"""
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Filter by log level
        filtered_lines = []
        for line in lines:
            if log_level in line or log_level == "INFO":
                filtered_lines.append(line.strip())
        
        # Show last 100 lines
        recent_lines = filtered_lines[-100:]
        
        if recent_lines:
            log_text = '\n'.join(recent_lines)
            st.text_area("Log Content", value=log_text, height=400, key=f"log_{log_file.name}")
        else:
            st.info(f"No {log_level} level logs found")
            
    except Exception as e:
        st.error(f"Error reading log file: {e}")

def show_performance_panel(dashboard):
    """Performance analytics and statistics"""
    st.header("📊 Performance Analytics")
    
    data = dashboard.load_trading_data()
    
    if data['trades'].empty:
        st.info("No trading data available for performance analysis")
        return
    
    trades_df = data['trades']
    
    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'profit_usd' in trades_df.columns:
            total_profit = trades_df['profit_usd'].sum()
            avg_profit = trades_df['profit_usd'].mean()
            st.metric("Total Profit", f"${total_profit:.2f}")
            st.metric("Avg Profit/Trade", f"${avg_profit:.2f}")
    
    with col2:
        if 'successful' in trades_df.columns:
            win_rate = (trades_df['successful'].sum() / len(trades_df)) * 100
            total_trades = len(trades_df)
            st.metric("Win Rate", f"{win_rate:.1f}%")
            st.metric("Total Trades", total_trades)
    
    with col3:
        if 'profit_pct' in trades_df.columns:
            max_gain = trades_df['profit_pct'].max()
            max_loss = trades_df['profit_pct'].min()
            st.metric("Best Trade", f"{max_gain:.2f}%")
            st.metric("Worst Trade", f"{max_loss:.2f}%")
    
    with col4:
        if 'confidence' in trades_df.columns:
            avg_confidence = trades_df['confidence'].mean()
            high_conf_trades = len(trades_df[trades_df['confidence'] > 0.8])
            st.metric("Avg Confidence", f"{avg_confidence:.1%}")
            st.metric("High Conf Trades", high_conf_trades)
    
    # Performance charts
    col1, col2 = st.columns(2)
    
    with col1:
        if 'profit_pct' in trades_df.columns:
            st.subheader("📈 Profit Distribution")
            fig = px.histogram(trades_df, x='profit_pct', nbins=20, title='Trade Profit Distribution')
            fig.update_layout(xaxis_title='Profit %', yaxis_title='Number of Trades')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'confidence' in trades_df.columns and 'successful' in trades_df.columns:
            st.subheader("🎯 Confidence vs Success")
            fig = px.scatter(trades_df, x='confidence', y='profit_pct', color='successful',
                           title='Confidence vs Profit')
            fig.update_layout(xaxis_title='Confidence', yaxis_title='Profit %')
            st.plotly_chart(fig, use_container_width=True)

# Bot control functions
def start_bot():
    """Start the trading bot"""
    try:
        if not st.session_state.trading_bot:
            st.session_state.trading_bot = PSCTONTradingBot()
        
        st.session_state.bot_running = True
        st.success("✅ Bot started successfully!")
        
    except Exception as e:
        st.error(f"❌ Failed to start bot: {e}")

def stop_bot():
    """Stop the trading bot"""
    try:
        st.session_state.bot_running = False
        st.success("✅ Bot stopped successfully!")
        
    except Exception as e:
        st.error(f"❌ Failed to stop bot: {e}")

def restart_bot():
    """Restart the trading bot"""
    try:
        stop_bot()
        time.sleep(1)
        start_bot()
        st.success("✅ Bot restarted successfully!")
        
    except Exception as e:
        st.error(f"❌ Failed to restart bot: {e}")

def retrain_ml_models():
    """Retrain ML models"""
    try:
        if st.session_state.trading_bot and st.session_state.trading_bot.ml_engine:
            success = st.session_state.trading_bot.ml_engine.retrain_models()
            if success:
                st.success("✅ ML models retrained successfully!")
            else:
                st.warning("⚠️ Not enough data for retraining")
        else:
            st.error("❌ ML engine not available")
            
    except Exception as e:
        st.error(f"❌ Retraining failed: {e}")

def export_trading_data(dashboard):
    """Export trading data"""
    try:
        data = dashboard.load_trading_data()
        
        if not data['trades'].empty:
            csv = data['trades'].to_csv(index=False)
            st.download_button(
                label="📥 Download Trading Data",
                data=csv,
                file_name=f"trading_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No trading data to export")
            
    except Exception as e:
        st.error(f"❌ Export failed: {e}")

if __name__ == "__main__":
    main()
