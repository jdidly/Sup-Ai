"""
Paper Trading Validation System for PSC Trading System

This module tracks all ML predictions, performs paper trades, and validates
outcomes against actual market movements to measure prediction accuracy.

Features:
- Logs all predictions to CSV with timestamp
- Performs paper trades for each prediction
- Tracks outcomes after specified time periods
- Calculates prediction accuracy metrics
- Provides detailed analysis reports
"""

import csv
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PaperTradingValidator:
    """
    Comprehensive paper trading validation system for ML predictions
    """
    
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # CSV files for tracking
        self.predictions_file = self.data_dir / "ml_predictions.csv"
        self.paper_trades_file = self.data_dir / "paper_trades.csv"
        self.validation_results_file = self.data_dir / "prediction_validation.csv"
        
        # In-memory tracking
        self.active_paper_trades = []
        self.completed_validations = []
        
        # Paper trading settings
        self.validation_periods = [
            {'name': '5min', 'minutes': 5},
            {'name': '10min', 'minutes': 10},
            {'name': '15min', 'minutes': 15},
            {'name': '30min', 'minutes': 30}
        ]
        
        # Success thresholds
        self.profit_thresholds = {
            'break_even': 0.001,    # 0.1%
            'min_profit': 0.0012,   # 0.12%
            'good_profit': 0.002,   # 0.20%
            'excellent': 0.005      # 0.50%
        }
        
        self.setup_csv_files()
        self.load_active_paper_trades()
        
        logger.info("📊 Paper Trading Validator initialized")
    
    def setup_csv_files(self):
        """Setup CSV files with headers if they don't exist"""
        
        # ML Predictions CSV
        if not self.predictions_file.exists():
            with open(self.predictions_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'coin', 'prediction_id', 'direction', 'confidence',
                    'entry_price', 'target_price', 'stop_loss', 'psc_ratio',
                    'ml_prediction_value', 'signal_strength', 'market_conditions',
                    'tradingview_sentiment', 'expected_profit_pct'
                ])
        
        # Paper Trades CSV
        if not self.paper_trades_file.exists():
            with open(self.paper_trades_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'prediction_id', 'coin', 'direction', 'entry_time', 'entry_price',
                    'target_price', 'confidence', 'status', 'validation_periods'
                ])
        
        # Validation Results CSV
        if not self.validation_results_file.exists():
            with open(self.validation_results_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'prediction_id', 'coin', 'direction', 'entry_time', 'entry_price',
                    'confidence', 'validation_period', 'exit_time', 'exit_price',
                    'actual_profit_pct', 'target_hit', 'success', 'prediction_accuracy',
                    'profit_category', 'ml_prediction_value'
                ])
    
    def log_prediction(self, coin, direction, confidence, entry_price, target_price, 
                      psc_ratio, ml_prediction_value, signal_strength="MODERATE", 
                      market_conditions="NORMAL", tradingview_sentiment=0.5, 
                      expected_profit_pct=0.0015):
        """
        Log a new ML prediction and start paper trading validation
        
        Returns: prediction_id for tracking
        """
        try:
            # Generate unique prediction ID
            prediction_id = f"{coin}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{direction}"
            
            # Calculate stop loss (opposite direction)
            stop_loss = entry_price * (0.995 if direction == "LONG" else 1.005)  # 0.5% stop
            
            # Log prediction to CSV
            with open(self.predictions_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    coin,
                    prediction_id,
                    direction,
                    f"{confidence:.3f}",
                    f"{entry_price:.8f}",
                    f"{target_price:.8f}",
                    f"{stop_loss:.8f}",
                    f"{psc_ratio:.2f}",
                    f"{ml_prediction_value:.3f}",
                    signal_strength,
                    market_conditions,
                    f"{tradingview_sentiment:.3f}",
                    f"{expected_profit_pct:.5f}"
                ])
            
            # Start paper trade
            self.start_paper_trade(prediction_id, coin, direction, entry_price, 
                                 target_price, confidence)
            
            logger.info(f"📊 Logged prediction {prediction_id}: {direction} {coin} @ {entry_price}")
            return prediction_id
            
        except Exception as e:
            logger.error(f"Error logging prediction: {e}")
            return None
    
    def start_paper_trade(self, prediction_id, coin, direction, entry_price, target_price, confidence):
        """Start a new paper trade for validation"""
        try:
            paper_trade = {
                'prediction_id': prediction_id,
                'coin': coin,
                'direction': direction,
                'entry_time': datetime.now(),
                'entry_price': entry_price,
                'target_price': target_price,
                'confidence': confidence,
                'status': 'ACTIVE',
                'validation_periods': [p['name'] for p in self.validation_periods]
            }
            
            # Add to active trades
            self.active_paper_trades.append(paper_trade)
            
            # Log to CSV
            with open(self.paper_trades_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    prediction_id,
                    coin,
                    direction,
                    paper_trade['entry_time'].isoformat(),
                    f"{entry_price:.8f}",
                    f"{target_price:.8f}",
                    f"{confidence:.3f}",
                    'ACTIVE',
                    ','.join(paper_trade['validation_periods'])
                ])
            
            logger.info(f"🎯 Started paper trade: {prediction_id}")
            
        except Exception as e:
            logger.error(f"Error starting paper trade: {e}")
    
    async def validate_predictions(self):
        """
        Check all active paper trades and validate outcomes
        """
        if not self.active_paper_trades:
            return
        
        logger.info(f"🔍 Validating {len(self.active_paper_trades)} active paper trades")
        
        current_time = datetime.now()
        trades_to_remove = []
        
        for trade in self.active_paper_trades:
            try:
                # Check each validation period
                for period in self.validation_periods:
                    validation_time = trade['entry_time'] + timedelta(minutes=period['minutes'])
                    
                    # If validation period has passed
                    if current_time >= validation_time:
                        await self.validate_trade_at_period(trade, period)
                
                # Remove trade if all validation periods are complete
                max_period = max(self.validation_periods, key=lambda x: x['minutes'])
                final_validation_time = trade['entry_time'] + timedelta(minutes=max_period['minutes'])
                
                if current_time >= final_validation_time:
                    trade['status'] = 'COMPLETED'
                    trades_to_remove.append(trade)
                    
            except Exception as e:
                logger.error(f"Error validating trade {trade['prediction_id']}: {e}")
        
        # Remove completed trades
        for trade in trades_to_remove:
            self.active_paper_trades.remove(trade)
            logger.info(f"✅ Completed validation for {trade['prediction_id']}")
    
    async def validate_trade_at_period(self, trade, period):
        """Validate a single trade at a specific time period"""
        try:
            # Get current price
            current_price = await self.get_current_price(trade['coin'])
            if current_price is None:
                return
            
            # Calculate actual outcome
            entry_price = trade['entry_price']
            direction = trade['direction']
            target_price = trade['target_price']
            
            if direction == "LONG":
                actual_profit_pct = (current_price - entry_price) / entry_price
                target_hit = current_price >= target_price
            else:  # SHORT
                actual_profit_pct = (entry_price - current_price) / entry_price
                target_hit = current_price <= target_price
            
            # Determine success and profit category
            success = actual_profit_pct >= self.profit_thresholds['min_profit']
            profit_category = self.categorize_profit(actual_profit_pct)
            
            # Calculate prediction accuracy
            expected_profit = abs(target_price - entry_price) / entry_price
            prediction_accuracy = max(0, 1 - abs(expected_profit - actual_profit_pct) / expected_profit)
            
            # Log validation result
            with open(self.validation_results_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    trade['prediction_id'],
                    trade['coin'],
                    direction,
                    trade['entry_time'].isoformat(),
                    f"{entry_price:.8f}",
                    f"{trade['confidence']:.3f}",
                    period['name'],
                    datetime.now().isoformat(),
                    f"{current_price:.8f}",
                    f"{actual_profit_pct:.5f}",
                    target_hit,
                    success,
                    f"{prediction_accuracy:.3f}",
                    profit_category,
                    "0.000"  # ML prediction value (to be filled)
                ])
            
            logger.info(f"📊 Validated {trade['prediction_id']} at {period['name']}: "
                       f"{'SUCCESS' if success else 'FAIL'} ({actual_profit_pct:.3f}%)")
            
        except Exception as e:
            logger.error(f"Error validating trade at period {period['name']}: {e}")
    
    async def get_current_price(self, coin):
        """Get current price from Binance API"""
        try:
            symbol = f"{coin}USDT" if not coin.endswith("USDT") else coin
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data['price'])
                    else:
                        logger.warning(f"Failed to get price for {symbol}: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting current price for {coin}: {e}")
            return None
    
    def categorize_profit(self, profit_pct):
        """Categorize profit percentage"""
        if profit_pct >= self.profit_thresholds['excellent']:
            return "EXCELLENT"
        elif profit_pct >= self.profit_thresholds['good_profit']:
            return "GOOD"
        elif profit_pct >= self.profit_thresholds['min_profit']:
            return "PROFITABLE"
        elif profit_pct >= self.profit_thresholds['break_even']:
            return "BREAK_EVEN"
        else:
            return "LOSS"
    
    def load_active_paper_trades(self):
        """Load active paper trades from file on startup"""
        try:
            if self.paper_trades_file.exists():
                with open(self.paper_trades_file, 'r') as f:
                    reader = csv.DictReader(f)
                    current_time = datetime.now()
                    
                    for row in reader:
                        if row['status'] == 'ACTIVE':
                            entry_time = datetime.fromisoformat(row['entry_time'])
                            
                            # Only load trades that are still within validation window
                            max_period = max(self.validation_periods, key=lambda x: x['minutes'])
                            if current_time < entry_time + timedelta(minutes=max_period['minutes']):
                                trade = {
                                    'prediction_id': row['prediction_id'],
                                    'coin': row['coin'],
                                    'direction': row['direction'],
                                    'entry_time': entry_time,
                                    'entry_price': float(row['entry_price']),
                                    'target_price': float(row['target_price']),
                                    'confidence': float(row['confidence']),
                                    'status': 'ACTIVE',
                                    'validation_periods': row['validation_periods'].split(',')
                                }
                                self.active_paper_trades.append(trade)
                
                logger.info(f"📚 Loaded {len(self.active_paper_trades)} active paper trades")
                
        except Exception as e:
            logger.error(f"Error loading active paper trades: {e}")
    
    def get_prediction_accuracy_report(self, days=7):
        """Generate prediction accuracy report"""
        try:
            if not self.validation_results_file.exists():
                return {"error": "No validation data available"}
            
            # Read validation results
            results = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with open(self.validation_results_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    entry_time = datetime.fromisoformat(row['entry_time'])
                    if entry_time >= cutoff_date:
                        results.append(row)
            
            if not results:
                return {"error": f"No validation data in last {days} days"}
            
            # Calculate metrics
            total_predictions = len(results)
            successful_predictions = len([r for r in results if r['success'] == 'True'])
            
            # Direction analysis
            long_results = [r for r in results if r['direction'] == 'LONG']
            short_results = [r for r in results if r['direction'] == 'SHORT']
            
            # Time period analysis
            period_analysis = {}
            for period in self.validation_periods:
                period_results = [r for r in results if r['validation_period'] == period['name']]
                if period_results:
                    period_success = len([r for r in period_results if r['success'] == 'True'])
                    period_analysis[period['name']] = {
                        'total': len(period_results),
                        'successful': period_success,
                        'accuracy': period_success / len(period_results) * 100
                    }
            
            # Profit category analysis
            profit_categories = {}
            for result in results:
                category = result['profit_category']
                if category not in profit_categories:
                    profit_categories[category] = 0
                profit_categories[category] += 1
            
            report = {
                'period': f"Last {days} days",
                'total_predictions': total_predictions,
                'successful_predictions': successful_predictions,
                'overall_accuracy': successful_predictions / total_predictions * 100,
                'direction_analysis': {
                    'long': {
                        'total': len(long_results),
                        'successful': len([r for r in long_results if r['success'] == 'True']),
                        'accuracy': len([r for r in long_results if r['success'] == 'True']) / len(long_results) * 100 if long_results else 0
                    },
                    'short': {
                        'total': len(short_results),
                        'successful': len([r for r in short_results if r['success'] == 'True']),
                        'accuracy': len([r for r in short_results if r['success'] == 'True']) / len(short_results) * 100 if short_results else 0
                    }
                },
                'time_period_analysis': period_analysis,
                'profit_categories': profit_categories
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating accuracy report: {e}")
            return {"error": str(e)}
    
    def get_active_trades_count(self):
        """Get count of active paper trades"""
        return len(self.active_paper_trades)
    
    async def run_validation_loop(self, interval_minutes=5):
        """Run continuous validation loop"""
        logger.info(f"🔄 Starting paper trading validation loop (every {interval_minutes} minutes)")
        
        while True:
            try:
                await self.validate_predictions()
                await asyncio.sleep(interval_minutes * 60)
            except Exception as e:
                logger.error(f"Error in validation loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying


# Integration helper function
async def log_prediction_and_start_paper_trade(validator, coin, direction, confidence, 
                                              entry_price, target_price, psc_ratio, 
                                              ml_prediction_value, **kwargs):
    """
    Helper function to log prediction and start paper trade
    This should be called whenever the ML engine makes a prediction
    """
    return validator.log_prediction(
        coin=coin,
        direction=direction,
        confidence=confidence,
        entry_price=entry_price,
        target_price=target_price,
        psc_ratio=psc_ratio,
        ml_prediction_value=ml_prediction_value,
        **kwargs
    )
