"""
Bidirectional ML Training Backtester for PSC Trading System

This backtester uses historical data to train the ML model with the new bidirectional trading logic.
It simulates both LONG and SHORT trades to create realistic training data for the ML engine.

Features:
- Bidirectional trade simulation (LONG + SHORT)
- Realistic small-move targeting (0.12-0.20%)
- PSC ratio calculation with bidirectional logic
- ML model training with actual trade outcomes
- Performance analysis for both directions
"""

import os
import sys
import sqlite3
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add paths
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the real ML engine
try:
    from ml_engine import MLEngine
    print("✅ ML Engine imported successfully")
except ImportError as e:
    print(f"❌ Could not import ML engine: {e}")
    sys.exit(1)

class BidirectionalBacktester:
    """
    Comprehensive backtester for bidirectional trading strategy
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), 'data', 'historical_data.db')
        
        # Trading parameters (matching your actual system)
        self.break_even_pct = 0.001    # 0.1% break-even
        self.min_profit_pct = 0.0012   # 0.12% minimum profit
        self.max_position_minutes = 10  # 10-minute max position duration
        
        # PSC ratio thresholds
        self.long_ratio_threshold = 1.25    # LONG signals
        self.short_ratio_threshold = 0.9    # SHORT signals (≤0.9)
        self.short_strong_threshold = 0.8   # Strong SHORT signals (≤0.8)
        
        # Cryptocurrencies to analyze
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'SHIBUSDT', 'DOGEUSDT', 'PEPEUSDT']
        self.base_symbol = 'TONUSDT'  # Using TON as base (simulated price for PSC calculation)
        
        # Results tracking
        self.trades = []
        self.long_trades = []
        self.short_trades = []
        self.training_data = []
        
        # Initialize ML engine
        self.ml_engine = MLEngine()
        
        print(f"🎯 Bidirectional Backtester initialized")
        print(f"📊 Database: {self.db_path}")
        print(f"⚡ Break-even: {self.break_even_pct*100:.2f}%, Min profit: {self.min_profit_pct*100:.2f}%")
    
    def get_historical_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Retrieve historical data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Convert datetime to timestamp
            start_ts = int(start_date.timestamp() * 1000)
            end_ts = int(end_date.timestamp() * 1000)
            
            query = """
                SELECT timestamp, open_price, high_price, low_price, close_price, volume
                FROM historical_data 
                WHERE symbol = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            """
            
            df = pd.read_sql_query(query, conn, params=(symbol, start_ts, end_ts))
            conn.close()
            
            if df.empty:
                logger.warning(f"No data found for {symbol} between {start_date} and {end_date}")
                return pd.DataFrame()
            
            # Convert timestamp to datetime
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('datetime', inplace=True)
            
            logger.info(f"📊 Retrieved {len(df)} records for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_psc_ratio(self, crypto_price: float, base_price: float = None) -> float:
        """
        Calculate PSC ratio for signal generation
        Using simulated TON price if not available
        """
        if base_price is None:
            # Simulate TON price based on typical crypto correlation
            base_price = crypto_price * 0.001  # Simplified ratio for testing
        
        return crypto_price / (base_price * 0.001)
    
    def determine_trade_direction(self, psc_ratio: float, price_momentum: float, volatility: float) -> str:
        """
        Determine trade direction based on PSC ratio and market conditions
        """
        # LONG signal conditions
        if psc_ratio >= 2.0:
            return "LONG"  # Strong LONG signal
        elif psc_ratio >= 1.5:
            return "LONG"  # Good LONG signal
        elif psc_ratio >= self.long_ratio_threshold:
            return "LONG"  # Entry-level LONG signal
        
        # SHORT signal conditions  
        elif psc_ratio <= self.short_strong_threshold:
            return "SHORT"  # Strong SHORT signal
        elif psc_ratio <= self.short_ratio_threshold:
            return "SHORT"  # Good SHORT signal
        
        return "NEUTRAL"
    
    def calculate_target_price(self, entry_price: float, direction: str, confidence: float) -> float:
        """
        Calculate realistic target price based on confidence and direction
        """
        # Confidence-based targets (all above 0.12% break-even)
        if confidence >= 0.8:
            target_pct = np.random.uniform(0.0015, 0.002)    # 0.15-0.20%
        elif confidence >= 0.6:
            target_pct = np.random.uniform(0.0013, 0.0015)  # 0.13-0.15%
        else:
            target_pct = np.random.uniform(0.0012, 0.0013)  # 0.12-0.13%
        
        if direction == "LONG":
            return entry_price * (1 + target_pct)
        else:  # SHORT
            return entry_price * (1 - target_pct)
    
    def simulate_trade(self, symbol: str, entry_data: Dict, direction: str, confidence: float) -> Dict:
        """
        Simulate a trade with realistic outcome based on actual price movements
        """
        entry_price = entry_data['close_price']
        entry_time = entry_data['datetime']
        target_price = self.calculate_target_price(entry_price, direction, confidence)
        
        # Calculate exit conditions
        break_even_price = entry_price * (1 + self.break_even_pct) if direction == "LONG" else entry_price * (1 - self.break_even_pct)
        
        trade = {
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry_price,
            'entry_time': entry_time,
            'target_price': target_price,
            'break_even_price': break_even_price,
            'confidence': confidence,
            'psc_ratio': entry_data.get('psc_ratio', 0),
            'status': 'PENDING'
        }
        
        return trade
    
    def evaluate_trade_outcome(self, trade: Dict, price_data: pd.DataFrame) -> Dict:
        """
        Evaluate trade outcome based on actual price movements
        """
        entry_time = trade['entry_time']
        entry_price = trade['entry_price']
        target_price = trade['target_price']
        direction = trade['direction']
        
        # Get price data for the next 10 minutes after entry
        exit_time = entry_time + timedelta(minutes=self.max_position_minutes)
        
        # Filter data within position duration
        position_data = price_data[
            (price_data.index >= entry_time) & 
            (price_data.index <= exit_time)
        ].copy()
        
        if position_data.empty:
            trade.update({
                'status': 'NO_DATA',
                'exit_price': entry_price,
                'exit_time': entry_time,
                'profit_pct': 0,
                'hit_target': False,
                'duration_minutes': 0
            })
            return trade
        
        # Check if target was hit during position
        if direction == "LONG":
            target_hit = (position_data['high_price'] >= target_price).any()
            if target_hit:
                exit_price = target_price
                exit_time_actual = position_data[position_data['high_price'] >= target_price].index[0]
            else:
                exit_price = position_data.iloc[-1]['close_price']
                exit_time_actual = position_data.index[-1]
        else:  # SHORT
            target_hit = (position_data['low_price'] <= target_price).any()
            if target_hit:
                exit_price = target_price
                exit_time_actual = position_data[position_data['low_price'] <= target_price].index[0]
            else:
                exit_price = position_data.iloc[-1]['close_price']
                exit_time_actual = position_data.index[-1]
        
        # Calculate profit
        if direction == "LONG":
            profit_pct = (exit_price - entry_price) / entry_price
        else:  # SHORT
            profit_pct = (entry_price - exit_price) / entry_price
        
        # Determine success
        success = profit_pct > self.min_profit_pct
        duration = (exit_time_actual - entry_time).total_seconds() / 60
        
        trade.update({
            'status': 'COMPLETED',
            'exit_price': exit_price,
            'exit_time': exit_time_actual,
            'profit_pct': profit_pct,
            'hit_target': target_hit,
            'success': success,
            'duration_minutes': duration
        })
        
        return trade
    
    def run_backtest(self, start_date: datetime, end_date: datetime, min_confidence: float = 0.5):
        """
        Run comprehensive bidirectional backtest
        """
        print(f"\n🚀 Starting Bidirectional Backtest")
        print(f"📅 Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"🎯 Min confidence: {min_confidence}")
        print("="*60)
        
        all_trades = []
        
        for symbol in self.symbols:
            print(f"\n📊 Processing {symbol}...")
            
            # Get historical data
            df = self.get_historical_data(symbol, start_date, end_date)
            if df.empty:
                continue
            
            # Add technical indicators
            df['sma_5'] = df['close_price'].rolling(window=5).mean()
            df['sma_20'] = df['close_price'].rolling(window=20).mean()
            df['volatility'] = df['close_price'].rolling(window=20).std()
            df['rsi'] = self.calculate_rsi(df['close_price'])
            
            symbol_trades = []
            
            # Simulate trading every 30 minutes (realistic scanning frequency)
            for i in range(0, len(df), 30):
                if i + 30 >= len(df):  # Ensure we have enough data for exit
                    break
                
                current_data = df.iloc[i]
                current_price = current_data['close_price']
                
                # Calculate PSC ratio
                psc_ratio = self.calculate_psc_ratio(current_price)
                
                # Calculate price momentum and volatility
                if i >= 20:  # Need enough data for indicators
                    price_momentum = (current_price - current_data['sma_20']) / current_data['sma_20']
                    volatility = current_data['volatility'] / current_price
                    
                    # Determine trade direction
                    direction = self.determine_trade_direction(psc_ratio, price_momentum, volatility)
                    
                    if direction != "NEUTRAL":
                        # Generate ML confidence (simulate ML prediction)
                        base_confidence = min(0.9, max(0.1, abs(price_momentum) * 2 + volatility))
                        ml_confidence = np.random.normal(base_confidence, 0.1)
                        ml_confidence = max(0.1, min(0.9, ml_confidence))
                        
                        if ml_confidence >= min_confidence:
                            # Create trade entry data
                            entry_data = {
                                'close_price': current_price,
                                'datetime': current_data.name,
                                'psc_ratio': psc_ratio,
                                'momentum': price_momentum,
                                'volatility': volatility
                            }
                            
                            # Simulate trade
                            trade = self.simulate_trade(symbol, entry_data, direction, ml_confidence)
                            
                            # Evaluate outcome using future price data
                            future_data = df.iloc[i:i+30]  # Next 30 minutes of data
                            completed_trade = self.evaluate_trade_outcome(trade, future_data)
                            
                            symbol_trades.append(completed_trade)
                            all_trades.append(completed_trade)
            
            print(f"   • Generated {len(symbol_trades)} trades for {symbol}")
        
        self.trades = all_trades
        self.analyze_results()
        self.create_training_data()
        self.train_ml_model()
        
        return all_trades
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def analyze_results(self):
        """Analyze backtest results"""
        if not self.trades:
            print("❌ No trades to analyze")
            return
        
        df_trades = pd.DataFrame(self.trades)
        
        print(f"\n📈 BACKTEST RESULTS ANALYSIS")
        print("="*60)
        
        # Overall statistics
        total_trades = len(df_trades)
        successful_trades = len(df_trades[df_trades['success'] == True])
        success_rate = successful_trades / total_trades * 100
        
        print(f"📊 Total Trades: {total_trades}")
        print(f"✅ Successful Trades: {successful_trades}")
        print(f"📈 Success Rate: {success_rate:.2f}%")
        
        # Direction analysis
        long_trades = df_trades[df_trades['direction'] == 'LONG']
        short_trades = df_trades[df_trades['direction'] == 'SHORT']
        
        print(f"\n🔵 LONG Trades: {len(long_trades)}")
        if not long_trades.empty:
            long_success = len(long_trades[long_trades['success'] == True])
            long_success_rate = long_success / len(long_trades) * 100
            long_avg_profit = long_trades['profit_pct'].mean() * 100
            print(f"   • Success Rate: {long_success_rate:.2f}%")
            print(f"   • Average Profit: {long_avg_profit:.3f}%")
        
        print(f"\n🔴 SHORT Trades: {len(short_trades)}")
        if not short_trades.empty:
            short_success = len(short_trades[short_trades['success'] == True])
            short_success_rate = short_success / len(short_trades) * 100
            short_avg_profit = short_trades['profit_pct'].mean() * 100
            print(f"   • Success Rate: {short_success_rate:.2f}%")
            print(f"   • Average Profit: {short_avg_profit:.3f}%")
        
        # Profit analysis
        avg_profit = df_trades['profit_pct'].mean() * 100
        profitable_trades = len(df_trades[df_trades['profit_pct'] > 0])
        profitable_rate = profitable_trades / total_trades * 100
        
        print(f"\n💰 PROFIT ANALYSIS")
        print(f"   • Average Profit: {avg_profit:.3f}%")
        print(f"   • Profitable Trades: {profitable_trades} ({profitable_rate:.2f}%)")
        print(f"   • Above Break-even: {len(df_trades[df_trades['profit_pct'] > self.break_even_pct])}")
        print(f"   • Above Min Profit: {len(df_trades[df_trades['profit_pct'] > self.min_profit_pct])}")
        
        # Symbol analysis
        print(f"\n📊 BY SYMBOL:")
        for symbol in self.symbols:
            symbol_trades = df_trades[df_trades['symbol'] == symbol]
            if not symbol_trades.empty:
                symbol_success = len(symbol_trades[symbol_trades['success'] == True])
                symbol_success_rate = symbol_success / len(symbol_trades) * 100
                print(f"   • {symbol}: {len(symbol_trades)} trades, {symbol_success_rate:.1f}% success")
        
        self.long_trades = long_trades
        self.short_trades = short_trades
    
    def create_training_data(self):
        """Create training data for ML model"""
        print(f"\n🧠 Creating ML Training Data...")
        
        training_data = []
        
        for trade in self.trades:
            if trade['status'] == 'COMPLETED':
                # Features for ML training
                features = {
                    'psc_ratio': trade['psc_ratio'],
                    'confidence': trade['confidence'],
                    'momentum': trade.get('momentum', 0),
                    'volatility': trade.get('volatility', 0),
                    'direction_long': 1 if trade['direction'] == 'LONG' else 0,
                    'direction_short': 1 if trade['direction'] == 'SHORT' else 0,
                }
                
                # Labels for ML training
                labels = {
                    'success': trade['success'],
                    'profit_pct': trade['profit_pct'],
                    'hit_target': trade['hit_target'],
                    'duration_minutes': trade['duration_minutes']
                }
                
                training_data.append({
                    'features': features,
                    'labels': labels,
                    'trade': trade
                })
        
        self.training_data = training_data
        print(f"✅ Created {len(training_data)} training samples")
        
        return training_data
    
    def train_ml_model(self):
        """Train the ML model with backtest data"""
        if not self.training_data:
            print("❌ No training data available")
            return
        
        print(f"\n🎯 Training ML Model with Bidirectional Data...")
        
        # Prepare features and labels
        features = []
        win_labels = []
        return_labels = []
        
        for sample in self.training_data:
            feature_vector = [
                sample['features']['psc_ratio'],
                sample['features']['confidence'],
                sample['features']['momentum'],
                sample['features']['volatility'],
                sample['features']['direction_long'],
                sample['features']['direction_short']
            ]
            
            features.append(feature_vector)
            win_labels.append(1 if sample['labels']['success'] else 0)
            return_labels.append(sample['labels']['profit_pct'])
        
        features = np.array(features)
        win_labels = np.array(win_labels)
        return_labels = np.array(return_labels)
        
        try:
            # Train the real ML engine
            print("🔄 Training ML models...")
            
            # Create simulated training format for ML engine
            training_batches = []
            for i, sample in enumerate(self.training_data):
                trade_data = {
                    'crypto': sample['trade']['symbol'],
                    'ratio': sample['features']['psc_ratio'],
                    'confidence': sample['features']['confidence'],
                    'direction': sample['trade']['direction'],
                    'success': sample['labels']['success'],
                    'profit_pct': sample['labels']['profit_pct'],
                    'timestamp': datetime.now().isoformat()
                }
                training_batches.append(trade_data)
            
            # Train in batches
            batch_size = 50
            total_trained = 0
            
            for i in range(0, len(training_batches), batch_size):
                batch = training_batches[i:i+batch_size]
                
                # Update ML engine with batch
                for trade_data in batch:
                    self.ml_engine.update_model_with_trade_outcome(trade_data)
                    total_trained += 1
                
                print(f"   • Trained with {total_trained}/{len(training_batches)} samples")
            
            print("✅ ML Model training completed successfully!")
            
            # Save training results
            self.save_training_results()
            
        except Exception as e:
            print(f"❌ Error training ML model: {e}")
    
    def save_training_results(self):
        """Save training results and model"""
        results_dir = os.path.join(os.path.dirname(__file__), 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save trade results
        trades_file = os.path.join(results_dir, f'bidirectional_backtest_{timestamp}.json')
        with open(trades_file, 'w') as f:
            # Convert datetime objects to strings for JSON serialization
            serializable_trades = []
            for trade in self.trades:
                trade_copy = trade.copy()
                for key, value in trade_copy.items():
                    if isinstance(value, datetime):
                        trade_copy[key] = value.isoformat()
                serializable_trades.append(trade_copy)
            
            json.dump({
                'metadata': {
                    'timestamp': timestamp,
                    'total_trades': len(self.trades),
                    'long_trades': len([t for t in self.trades if t['direction'] == 'LONG']),
                    'short_trades': len([t for t in self.trades if t['direction'] == 'SHORT']),
                    'success_rate': len([t for t in self.trades if t.get('success', False)]) / len(self.trades) * 100,
                    'break_even_pct': self.break_even_pct,
                    'min_profit_pct': self.min_profit_pct
                },
                'trades': serializable_trades
            }, f, indent=2)
        
        print(f"💾 Results saved to: {trades_file}")
        
        # Save ML model state
        try:
            model_file = os.path.join(results_dir, f'ml_model_bidirectional_{timestamp}.json')
            ml_state = {
                'predictions_count': len(self.ml_engine.predictions),
                'performance_history': self.ml_engine.performance_history[-10:],  # Last 10 entries
                'training_timestamp': timestamp
            }
            
            with open(model_file, 'w') as f:
                json.dump(ml_state, f, indent=2)
            
            print(f"🧠 ML model state saved to: {model_file}")
            
        except Exception as e:
            print(f"⚠️ Could not save ML model state: {e}")


def main():
    """Main execution function"""
    print("🚀 BIDIRECTIONAL ML TRAINING BACKTESTER")
    print("="*60)
    
    # Check database
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'historical_data.db')
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        print("Please run the data collection script first.")
        return
    
    # Initialize backtester
    backtester = BidirectionalBacktester(db_path)
    
    # Define backtest period (last 7 days for testing)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Run backtest
    trades = backtester.run_backtest(start_date, end_date, min_confidence=0.5)
    
    print(f"\n✅ Bidirectional backtest completed!")
    print(f"📊 Generated {len(trades)} total trades")
    print(f"🧠 ML model trained with bidirectional data")
    
    return backtester


if __name__ == "__main__":
    backtester = main()
