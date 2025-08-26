# ⚙️ System Configuration Guide

**Purpose**: Complete guide to configuring and optimizing the PSC Trading System

---

## 📁 **CONFIGURATION FILE STRUCTURE**

### **Main Configuration (`config/settings.yaml`)**

```yaml
# PSC Trading System Configuration
# Last Updated: August 25, 2025

# Core Trading Parameters
trading:
  # Scanning and timing
  scan_interval: 45                    # ML scanning frequency (seconds)
  timer_interval: 600                  # Trade cycle duration (10 minutes)
  confidence_threshold: 0.65           # Minimum ML confidence for trades
  
  # PSC ratio thresholds
  min_signal_ratio: 1.25              # LONG signal threshold
  max_short_ratio: 0.9                # SHORT signal threshold
  neutral_zone: [0.95, 1.2]          # No-trade zone
  
  # Position management
  max_position_duration: 600           # Maximum position time (seconds)
  entry_window: 180                    # Entry window (0-3 minutes)
  exit_window: 120                     # Exit preparation (8-10 minutes)

# Risk Management
risk_management:
  # Position sizing
  max_position_size: 100               # Maximum position size ($)
  min_position_size: 10                # Minimum position size ($)
  max_daily_positions: 50              # Daily position limit
  portfolio_risk_limit: 0.2           # Maximum portfolio risk (20%)
  
  # Profit/Loss targets
  target_profit_percentage: 0.12      # Primary profit target (0.12%)
  stop_loss_percentage: 0.1           # Stop loss threshold (0.1%)
  break_even_threshold: 0.001         # Break-even point (0.1%)
  
  # Position limits
  max_simultaneous_positions: 5       # Maximum concurrent positions
  cooldown_period: 300                # Seconds between same-asset trades

# Superp Platform Configuration
superp:
  # Default settings
  default_leverage_type: "MODERATE"   # CONSERVATIVE, MODERATE, AGGRESSIVE, EXTREME
  default_buy_in: 25                  # Default position size ($)
  
  # Leverage categories
  leverage_categories:
    CONSERVATIVE: [1, 100]            # 1x-100x leverage
    MODERATE: [100, 1000]             # 100x-1000x leverage
    AGGRESSIVE: [1000, 5000]          # 1000x-5000x leverage
    EXTREME: [5000, 10000]            # 5000x-10000x leverage
  
  # Timer optimization
  timer_efficiency:
    entry_window: 1.0                 # Full efficiency (minutes 0-3)
    mid_timer: 0.8                    # 80% efficiency (minutes 3-6)
    late_timer: 0.6                   # 60% efficiency (minutes 6-8)
    exit_window: 0.4                  # 40% efficiency (minutes 8-10)

# Machine Learning Configuration
ml_engine:
  # Model settings
  confidence_threshold: 0.65           # Minimum confidence for execution
  prediction_timeout: 5                # Seconds to wait for prediction
  fallback_to_heuristic: true         # Use heuristic if ML fails
  
  # Continuous learning
  enable_learning: true               # Enable model updates
  retraining_threshold: 100           # Retrain after N new outcomes
  max_training_samples: 10000         # Maximum samples for training
  
  # Feature engineering
  feature_count: 25                   # Number of input features
  normalize_features: true            # Feature normalization
  include_technical_indicators: true  # Include TA features

# TradingView Integration
tradingview:
  # Analysis settings
  update_interval: 30                 # Update frequency (seconds)
  timeframes: ["1m", "5m", "10m"]    # Timeframes for analysis
  consensus_threshold: 0.6            # Minimum consensus for signal validation
  
  # Indicators
  enabled_indicators:
    - "RSI"
    - "MACD" 
    - "Bollinger Bands"
    - "Moving Averages"
    - "Volume Analysis"
    - "Support/Resistance"
  
  # Signal processing
  signal_weight: 0.3                  # Weight in final decision (30%)
  timeout: 10                         # Seconds to wait for analysis

# Monitoring Configuration
monitoring:
  # Assets to monitor
  cryptocurrencies:
    - "BTCUSDT"
    - "ETHUSDT"
    - "SOLUSDT"
    - "ADAUSDT"
    - "DOTUSDT"
    - "TONUSDT"
  
  # Base currency
  base_currency: "TONUSDT"            # For PSC ratio calculations
  
  # Data collection
  price_update_interval: 5            # Price update frequency (seconds)
  historical_data_retention: 30      # Days to keep historical data

# Telegram Bot Configuration
telegram:
  # Bot settings
  enable_bot: true                    # Enable Telegram integration
  command_prefix: "/"                 # Command prefix
  admin_chat_id: null                 # Admin chat ID (set your chat ID)
  
  # Notifications
  notifications:
    position_opened: true             # Notify when position opens
    position_closed: true             # Notify when position closes
    daily_summary: true               # Send daily performance summary
    error_alerts: true                # Send error notifications
  
  # Available commands
  commands:
    - "status"        # System status
    - "performance"   # Performance metrics
    - "positions"     # Active positions
    - "config"        # Configuration display
    - "logs"          # Recent logs
    - "dashboard"     # Dashboard link

# Logging Configuration
logging:
  # Log levels
  console_level: "INFO"               # Console log level
  file_level: "DEBUG"                 # File log level
  
  # Log files
  main_log: "logs/psc_system.log"
  trade_log: "data/live_trades.csv"
  ml_log: "data/ml/prediction_history.json"
  
  # Retention
  max_log_size_mb: 100                # Maximum log file size
  backup_count: 5                     # Number of backup files
  
  # Performance logging
  log_predictions: true               # Log all ML predictions
  log_technical_analysis: true        # Log TradingView analysis
  log_price_data: false              # Log price updates (verbose)

# Dashboard Configuration
dashboard:
  # Web dashboard
  enable_web_dashboard: true          # Enable Streamlit dashboard
  port: 8501                          # Dashboard port
  auto_refresh: 30                    # Auto-refresh interval (seconds)
  
  # Simple dashboard
  enable_simple_dashboard: true       # Enable parameter dashboard
  simple_port: 8502                   # Simple dashboard port

# Development/Testing Configuration
development:
  # Testing mode
  paper_trading_mode: false           # Enable paper trading only
  simulation_mode: false              # Enable full simulation
  
  # Debug settings
  debug_mode: false                   # Enable debug logging
  verbose_ml: false                   # Verbose ML logging
  mock_apis: false                    # Mock external APIs for testing
  
  # Performance testing
  enable_backtesting: true            # Enable backtesting capabilities
  backtest_data_path: "backtesting/data/"
```

---

## 🎛️ **PARAMETER TUNING GUIDE**

### **Critical Parameters for Performance**

**1. Confidence Threshold (`confidence_threshold: 0.65`)**
```yaml
# Conservative (fewer trades, higher accuracy)
confidence_threshold: 0.7

# Balanced (recommended)
confidence_threshold: 0.65

# Aggressive (more trades, lower accuracy)
confidence_threshold: 0.6
```

**Impact**:
- Higher = Fewer but more reliable trades
- Lower = More trades but higher risk of failures
- Recommended range: 0.6-0.75

**2. PSC Ratio Thresholds**
```yaml
# Conservative settings (stronger signals required)
min_signal_ratio: 1.3      # LONG threshold
max_short_ratio: 0.85      # SHORT threshold

# Balanced settings (recommended)
min_signal_ratio: 1.25
max_short_ratio: 0.9

# Aggressive settings (more opportunities)
min_signal_ratio: 1.2
max_short_ratio: 0.95
```

**3. Scan Interval (`scan_interval: 45`)**
```yaml
# Fast scanning (higher CPU usage)
scan_interval: 30

# Balanced scanning (recommended)
scan_interval: 45

# Slow scanning (lower resource usage)
scan_interval: 60
```

### **Risk Management Optimization**

**Position Sizing Strategy**:
```yaml
# Conservative approach
max_position_size: 50
min_position_size: 10
max_daily_positions: 20

# Balanced approach (recommended)
max_position_size: 100
min_position_size: 10
max_daily_positions: 50

# Aggressive approach
max_position_size: 200
min_position_size: 25
max_daily_positions: 100
```

**Profit/Loss Targets**:
```yaml
# Tight targets (higher win rate, smaller profits)
target_profit_percentage: 0.10    # 0.10%
stop_loss_percentage: 0.08       # 0.08%

# Balanced targets (recommended)
target_profit_percentage: 0.12    # 0.12%
stop_loss_percentage: 0.10       # 0.10%

# Wide targets (lower win rate, larger profits)
target_profit_percentage: 0.15    # 0.15%
stop_loss_percentage: 0.12       # 0.12%
```

---

## 🔧 **ENVIRONMENT CONFIGURATION**

### **Environment Variables**

Create `.env` file in project root:
```bash
# API Keys
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TRADINGVIEW_API_KEY=your_tradingview_api_key_here

# Superp Configuration
TON_WALLET_ADDRESS=your_ton_wallet_address
TON_PRIVATE_KEY=your_ton_private_key

# Exchange APIs (if needed)
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key

# Database Configuration
DATABASE_URL=sqlite:///data/psc_trading.db

# Development Settings
DEBUG_MODE=false
PAPER_TRADING=false
LOG_LEVEL=INFO
```

### **Python Environment Setup**

**Required Python Version**: 3.8+

**Virtual Environment Setup**:
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Key Dependencies** (`requirements.txt`):
```txt
# Core libraries
scikit-learn>=1.3.0
pandas>=1.5.0
numpy>=1.24.0
requests>=2.28.0
pyyaml>=6.0

# Telegram integration
python-telegram-bot>=20.0

# Web dashboard
streamlit>=1.25.0
plotly>=5.15.0

# Async support
asyncio>=3.4.3
aiohttp>=3.8.0

# Data processing
sqlite3
json5>=0.9.0

# Optional (for enhanced features)
ta-lib>=0.4.0  # Technical analysis
ccxt>=3.0.0    # Exchange integration
```

---

## 📊 **MONITORING & ALERTING SETUP**

### **Telegram Bot Configuration**

**1. Create Telegram Bot**:
```bash
# Message @BotFather on Telegram
/newbot
# Follow prompts to create bot
# Save the bot token to .env file
```

**2. Get Your Chat ID**:
```python
# Run this script to get your chat ID
import requests

bot_token = "your_bot_token"
url = f"https://api.telegram.org/bot{bot_token}/getUpdates"

# Send a message to your bot first
response = requests.get(url)
data = response.json()

# Your chat ID will be in the response
chat_id = data['result'][0]['message']['chat']['id']
print(f"Your chat ID: {chat_id}")
```

**3. Update Configuration**:
```yaml
telegram:
  admin_chat_id: 123456789  # Your chat ID here
```

### **Performance Monitoring Setup**

**Custom Metrics Configuration**:
```yaml
monitoring:
  metrics:
    # Trading performance
    win_rate_target: 0.5              # Target 50% win rate
    daily_profit_target: 0.02         # Target 2% daily profit
    max_drawdown_limit: 0.1           # Maximum 10% drawdown
    
    # Technical performance
    ml_accuracy_target: 0.55          # Target 55% ML accuracy
    api_response_time_limit: 5        # Maximum 5 seconds
    system_uptime_target: 0.99        # 99% uptime target
    
    # Risk metrics
    portfolio_risk_limit: 0.2         # 20% maximum portfolio risk
    position_duration_avg: 300        # Average 5-minute positions
    leverage_efficiency_min: 0.7      # Minimum 70% leverage efficiency
```

**Alert Thresholds**:
```yaml
alerts:
  # Performance alerts
  low_win_rate: 0.4                   # Alert if win rate < 40%
  high_drawdown: 0.08                 # Alert if drawdown > 8%
  system_error: true                  # Alert on any system errors
  
  # Trading alerts
  no_trades_timeout: 3600             # Alert if no trades for 1 hour
  high_loss_streak: 5                 # Alert after 5 consecutive losses
  api_failures: 3                     # Alert after 3 API failures
```

---

## 🔄 **CONFIGURATION MANAGEMENT**

### **Dynamic Configuration Updates**

**Real-time Parameter Updates**:
```python
# Simple dashboard allows real-time updates without restart
python simple_dashboard.py

# Access at http://localhost:8502
# Modify parameters and apply immediately
```

**Configuration Validation**:
```python
def validate_configuration(config):
    """Validate configuration parameters"""
    validation_rules = {
        'confidence_threshold': (0.5, 0.9),      # Valid range
        'scan_interval': (10, 300),              # 10 seconds to 5 minutes
        'max_position_size': (5, 500),           # $5 to $500
        'target_profit_percentage': (0.05, 0.5), # 0.05% to 0.5%
    }
    
    errors = []
    for param, (min_val, max_val) in validation_rules.items():
        value = config.get(param)
        if value is None:
            errors.append(f"Missing required parameter: {param}")
        elif not (min_val <= value <= max_val):
            errors.append(f"{param} must be between {min_val} and {max_val}")
    
    return len(errors) == 0, errors
```

### **Configuration Backup & Recovery**

**Automatic Backup**:
```yaml
backup:
  # Backup settings
  enable_auto_backup: true
  backup_interval_hours: 24           # Daily backups
  backup_location: "config/backups/"
  max_backup_files: 30                # Keep 30 days of backups
  
  # What to backup
  include_files:
    - "config/settings.yaml"
    - "data/live_trades.csv"
    - "data/ml/models/*.pkl"
    - ".env"
```

**Configuration Restore**:
```python
# Restore from backup
python scripts/restore_config.py --date 2025-08-24
```

---

## 🎯 **OPTIMIZATION STRATEGIES**

### **Performance Optimization**

**High-Performance Settings**:
```yaml
# For systems with good hardware
performance:
  scan_interval: 30                   # Faster scanning
  parallel_processing: true          # Enable parallel ML predictions
  cache_predictions: true            # Cache recent predictions
  async_operations: true             # Enable async processing
  
  # Resource allocation
  max_worker_threads: 4               # CPU cores for processing
  prediction_cache_size: 1000        # Cache recent predictions
  price_data_buffer: 500             # Buffer price updates
```

**Low-Resource Settings**:
```yaml
# For lower-end systems
performance:
  scan_interval: 60                   # Slower scanning
  parallel_processing: false         # Single-threaded processing
  cache_predictions: false           # No caching to save memory
  async_operations: false            # Synchronous processing
  
  # Reduced resource usage
  max_worker_threads: 1               # Single thread
  prediction_cache_size: 100         # Smaller cache
  price_data_buffer: 50              # Smaller buffer
```

### **Trading Strategy Optimization**

**Conservative Strategy**:
```yaml
strategy_conservative:
  confidence_threshold: 0.75
  min_signal_ratio: 1.4
  max_short_ratio: 0.8
  max_position_size: 50
  target_profit_percentage: 0.10
  max_daily_positions: 20
```

**Balanced Strategy** (Recommended):
```yaml
strategy_balanced:
  confidence_threshold: 0.65
  min_signal_ratio: 1.25
  max_short_ratio: 0.9
  max_position_size: 100
  target_profit_percentage: 0.12
  max_daily_positions: 50
```

**Aggressive Strategy**:
```yaml
strategy_aggressive:
  confidence_threshold: 0.6
  min_signal_ratio: 1.2
  max_short_ratio: 0.95
  max_position_size: 200
  target_profit_percentage: 0.15
  max_daily_positions: 100
```

---

**🔗 Navigation**: Continue to `06_TESTING_VALIDATION.md` for testing and validation procedures.
