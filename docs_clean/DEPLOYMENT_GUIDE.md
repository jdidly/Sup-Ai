# PSC Trading System - Cloud Deployment Guide

**Target Platforms:** Render, Railway, Heroku  
**System Type:** Python-based trading system with Telegram bot  
**Last Updated:** August 25, 2025  

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Render Deployment (Recommended)](#render-deployment)
3. [Environment Variables](#environment-variables)
4. [Git Setup](#git-setup)
5. [Deployment Process](#deployment-process)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
7. [Alternative Platforms](#alternative-platforms)

---

## Prerequisites

### Required Accounts
- ✅ **GitHub Account**: For code repository
- ✅ **Render Account**: For hosting (render.com)
- ✅ **Telegram Bot**: Bot token and chat ID
- ✅ **Trading API Keys**: For price feeds (optional)

### System Requirements
- **Python**: 3.11+ compatibility
- **Dependencies**: See `requirements.txt`
- **Memory**: Minimum 512MB RAM
- **Storage**: ~100MB for logs and data

---

## Render Deployment (Recommended)

### Why Render?
- ✅ **Free Tier**: $0/month for hobby projects
- ✅ **Auto-Deploy**: GitHub integration with automatic updates
- ✅ **Python Support**: Native Python 3.11+ support
- ✅ **Environment Variables**: Easy configuration management
- ✅ **Health Checks**: Built-in monitoring
- ✅ **Logs**: Real-time log streaming

### Step 1: Prepare Repository
```bash
# Ensure clean requirements.txt (no problematic packages)
# Requirements should include:
pip install -r requirements.txt

# Key packages:
python-telegram-bot>=20.0
aiohttp>=3.8.0
PyYAML>=6.0
pandas>=1.5.0
scikit-learn>=1.3.0
numpy>=1.24.0
```

### Step 2: Create Render Service
1. Go to **Render Dashboard** (render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your **GitHub repository**
4. Configure service settings:
   - **Name**: `superp-trader` (or your preferred name)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python psc_ton_system.py`
   - **Instance Type**: `Free` (for testing)

### Step 3: Configure Environment Variables
Add these in Render's Environment tab:

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Trading Configuration
MIN_SIGNAL_RATIO=1.25
MIN_CONFIDENCE_THRESHOLD=0.6
MAX_POSITIONS=5

# Deployment Controls
DISABLE_TELEGRAM_BOT=false
DISABLE_TIMER_ALERTS=false
DISABLE_TIMER_NOTIFICATIONS=true

# System Configuration
PYTHON_VERSION=3.11.0
PORT=10000
```

---

## Environment Variables

### Core Configuration
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | - | Yes |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | - | Yes |
| `PORT` | Web server port | 10000 | Auto-set |

### Trading Parameters
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MIN_SIGNAL_RATIO` | Minimum PSC ratio for signals | 1.25 | No |
| `MIN_CONFIDENCE_THRESHOLD` | ML confidence threshold | 0.6 | No |
| `MAX_POSITIONS` | Maximum concurrent positions | 5 | No |

### Deployment Controls
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DISABLE_TELEGRAM_BOT` | Disable bot (for multiple deployments) | false | No |
| `DISABLE_TIMER_ALERTS` | Disable timer logging | false | No |
| `DISABLE_TIMER_NOTIFICATIONS` | Disable timer Telegram spam | false | No |

---

## Git Setup

### Initial Repository Setup
```bash
# Initialize repository
git init
git add .
git commit -m "Initial PSC Trading System"

# Create GitHub repository and add remote
git remote add origin https://github.com/yourusername/superp-trader.git
git branch -M main
git push -u origin main
```

### Update Deployment Process
```bash
# Make changes to your code
git add .
git commit -m "Update trading logic"
git push origin main

# Render will automatically detect changes and redeploy
```

### Quick Update Script (Windows)
```batch
@echo off
echo Updating PSC Trading System...
git add .
set /p commit_msg="Enter commit message: "
git commit -m "%commit_msg%"
git push origin main
echo Deployment triggered! Check Render dashboard for status.
pause
```

---

## Deployment Process

### Automatic Deployment Flow
1. **Code Push**: Push changes to GitHub main branch
2. **Trigger**: Render detects repository changes
3. **Build**: Render runs `pip install -r requirements.txt`
4. **Deploy**: Render starts `python psc_ton_system.py`
5. **Health Check**: System responds to `/health` endpoint
6. **Live**: Trading system is operational

### Deployment Status Monitoring
```bash
# Check deployment logs in Render dashboard
# Monitor health endpoint: https://your-app.onrender.com/health
# Check system stats: https://your-app.onrender.com/stats
```

### Health Check Response
```json
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "uptime_hours": 1.0,
  "last_activity": "2025-08-25T10:30:00",
  "memory_usage": 45.2,
  "cpu_usage": 12.5,
  "active_threads": 8,
  "active_positions": 3,
  "monitored_coins": 6
}
```

---

## Monitoring & Troubleshooting

### Real-Time Monitoring
- **Render Logs**: Real-time log streaming in dashboard
- **Health Endpoint**: `https://your-app.onrender.com/health`
- **Stats Endpoint**: `https://your-app.onrender.com/stats`
- **Telegram Commands**: `/status`, `/dashboard`, `/logs`

### Common Issues & Solutions

#### Issue: Build Failures
```bash
# Problem: Package installation fails
# Solution: Check requirements.txt for problematic packages
# Remove: nacl, cryptography, base58 (if causing issues)
# Keep: Core ML and web packages only
```

#### Issue: Memory Limits
```bash
# Problem: Free tier memory exceeded
# Solution: Optimize code or upgrade to paid tier
# Monitor: Check memory usage in /health endpoint
```

#### Issue: Bot Conflicts
```bash
# Problem: Multiple deployments cause bot conflicts
# Solution: Set DISABLE_TELEGRAM_BOT=true for additional instances
# Primary: Keep one deployment with bot enabled
```

#### Issue: Timer Notification Spam
```bash
# Solution: Set DISABLE_TIMER_NOTIFICATIONS=true
# This stops timer alerts while keeping system functional
```

### Debug Commands
```bash
# Check logs via Telegram
/logs - Recent system logs
/status - Current system status
/dashboard - Complete system overview

# Check health via web
curl https://your-app.onrender.com/health
curl https://your-app.onrender.com/stats
```

---

## Alternative Platforms

### Railway Deployment
```yaml
# railway.json
{
  "deploy": {
    "startCommand": "python psc_ton_system.py",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### Heroku Deployment
```
# Procfile
web: python psc_ton_system.py
```

### PythonAnywhere
```python
# For PythonAnywhere, use web app configuration
# Point to psc_ton_system.py as main application
```

---

## Production Optimization

### Performance Settings
```python
# Optimize for production deployment
MONITORING_INTERVAL = 45  # Seconds between ML scans
MAX_CONCURRENT_REQUESTS = 10
CACHE_DURATION = 30  # Seconds for price caching
LOG_LEVEL = "INFO"  # Reduce verbose logging
```

### Scaling Considerations
- **Free Tier**: Suitable for testing and small-scale trading
- **Paid Tier**: Required for high-frequency trading or large positions
- **Multiple Deployments**: Use environment variables to prevent conflicts

### Security Best Practices
- ✅ **Environment Variables**: Never commit tokens to code
- ✅ **Limited Permissions**: Use minimal bot permissions
- ✅ **Regular Updates**: Keep dependencies updated
- ✅ **Monitoring**: Set up alerts for system failures

---

## Conclusion

This deployment guide provides everything needed to run the PSC Trading System in production. The combination of GitHub integration, automatic deployments, and comprehensive monitoring ensures reliable operation with minimal maintenance.

**Recommended Setup**: Render with GitHub auto-deployment for the best balance of features, reliability, and cost.
