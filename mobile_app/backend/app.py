from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import uuid
import threading
import time
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path to import our backtesting modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import our existing backtesting components
try:
    from sentiment_trading_strategy import SentimentTradingStrategy
    from break_retest_strategy import BreakRetestSwingStrategy
    from data_loader import load_stock_data
    from backtest_engine import BacktestEngine
    from performance_analyzer import PerformanceAnalyzer
except ImportError as e:
    print(f"Warning: Could not import backtesting modules: {e}")
    print("Make sure the backtesting code is in the parent directory")

app = Flask(__name__)
CORS(app)  # Enable CORS for Flutter app

# In-memory storage for running jobs (use Redis in production)
running_jobs = {}
completed_jobs = {}

# Available assets with their data information
AVAILABLE_ASSETS = {
    'SPY': {
        'name': 'SPDR S&P 500 ETF',
        'type': 'ETF',
        'years': '31+',
        'start_date': '1993-01-01',
        'description': 'Tracks the S&P 500 index'
    },
    'QQQ': {
        'name': 'Invesco QQQ Trust',
        'type': 'ETF', 
        'years': '25+',
        'start_date': '1999-01-01',
        'description': 'Tracks the NASDAQ-100 index'
    },
    'NVDA': {
        'name': 'NVIDIA Corporation',
        'type': 'Stock',
        'years': '15+',
        'start_date': '2009-01-01',
        'description': 'Graphics processing and AI chips'
    },
    'AAPL': {
        'name': 'Apple Inc.',
        'type': 'Stock',
        'years': '15+',
        'start_date': '2009-01-01',
        'description': 'Consumer electronics and services'
    },
    'AMZN': {
        'name': 'Amazon.com Inc.',
        'type': 'Stock',
        'years': '15+',
        'start_date': '2009-01-01',
        'description': 'E-commerce and cloud computing'
    },
    'MSFT': {
        'name': 'Microsoft Corporation',
        'type': 'Stock',
        'years': '15+',
        'start_date': '2009-01-01',
        'description': 'Software and cloud services'
    },
    'GOOGL': {
        'name': 'Alphabet Inc.',
        'type': 'Stock',
        'years': '15+',
        'start_date': '2009-01-01',
        'description': 'Search engine and digital advertising'
    }
}

# Strategy configurations
STRATEGY_CONFIGS = {
    'ai_sentiment': {
        'name': 'AI Sentiment Strategy',
        'description': 'Uses market sentiment analysis with momentum or contrarian approaches',
        'parameters': {
            'sentiment_mode': {'type': 'select', 'options': ['momentum', 'contrarian'], 'default': 'contrarian'},
            'confidence_threshold': {'type': 'float', 'min': 0.05, 'max': 0.50, 'default': 0.15},
            'position_size': {'type': 'float', 'min': 0.01, 'max': 0.10, 'default': 0.02},
            'lookback_period': {'type': 'int', 'min': 5, 'max': 50, 'default': 20}
        },
        'presets': {
            'Conservative': {
                'confidence_threshold': 0.25,
                'position_size': 0.015,
                'lookback_period': 30,
                'sentiment_mode': 'contrarian'
            },
            'Balanced': {
                'confidence_threshold': 0.15,
                'position_size': 0.02,
                'lookback_period': 20,
                'sentiment_mode': 'contrarian'
            },
            'Aggressive': {
                'confidence_threshold': 0.10,
                'position_size': 0.03,
                'lookback_period': 15,
                'sentiment_mode': 'momentum'
            },
            'High Frequency': {
                'confidence_threshold': 0.08,
                'position_size': 0.025,
                'lookback_period': 10,
                'sentiment_mode': 'momentum'
            }
        }
    },
    'break_retest': {
        'name': 'Break & Retest Strategy',
        'description': 'Identifies support/resistance breakouts with retest confirmation',
        'parameters': {
            'breakout_strength': {'type': 'float', 'min': 0.005, 'max': 0.05, 'default': 0.01},
            'retest_tolerance': {'type': 'float', 'min': 0.001, 'max': 0.02, 'default': 0.005},
            'consolidation_period': {'type': 'int', 'min': 5, 'max': 30, 'default': 10},
            'risk_reward_ratio': {'type': 'float', 'min': 1.0, 'max': 5.0, 'default': 3.0}
        },
        'presets': {
            'Conservative': {
                'breakout_strength': 0.015,
                'retest_tolerance': 0.008,
                'consolidation_period': 15,
                'risk_reward_ratio': 3.5
            },
            'Balanced': {
                'breakout_strength': 0.01,
                'retest_tolerance': 0.005,
                'consolidation_period': 10,
                'risk_reward_ratio': 3.0
            },
            'Aggressive': {
                'breakout_strength': 0.008,
                'retest_tolerance': 0.003,
                'consolidation_period': 8,
                'risk_reward_ratio': 2.5
            },
            'High Frequency': {
                'breakout_strength': 0.005,
                'retest_tolerance': 0.002,
                'consolidation_period': 5,
                'risk_reward_ratio': 2.0
            }
        }
    }
}

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get available trading strategies"""
    return jsonify({
        'strategies': STRATEGY_CONFIGS,
        'status': 'success'
    })

@app.route('/api/assets', methods=['GET'])
def get_assets():
    """Get available assets for backtesting"""
    return jsonify({
        'assets': AVAILABLE_ASSETS,
        'status': 'success'
    })

@app.route('/api/strategies/<strategy_name>/presets', methods=['GET'])
def get_strategy_presets(strategy_name):
    """Get preset configurations for a specific strategy"""
    if strategy_name not in STRATEGY_CONFIGS:
        return jsonify({'error': 'Strategy not found'}), 404
    
    return jsonify({
        'presets': STRATEGY_CONFIGS[strategy_name]['presets'],
        'status': 'success'
    })

@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """Run a backtest with specified parameters"""
    try:
        data = request.get_json()
        
        # Validate required parameters
        required_params = ['strategy', 'asset']
        for param in required_params:
            if param not in data:
                return jsonify({'error': f'Missing required parameter: {param}'}), 400
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Store job info
        running_jobs[job_id] = {
            'status': 'running',
            'started_at': datetime.now(),
            'parameters': data,
            'progress': 0
        }
        
        # Start backtest in background thread
        thread = threading.Thread(target=_run_backtest_async, args=(job_id, data))
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'started',
            'message': 'Backtest started successfully'
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backtest/results/<job_id>', methods=['GET'])
def get_backtest_results(job_id):
    """Get backtest results by job ID"""
    if job_id in completed_jobs:
        return jsonify({
            'status': 'completed',
            'results': completed_jobs[job_id]['results'],
            'completed_at': completed_jobs[job_id]['completed_at'].isoformat()
        })
    elif job_id in running_jobs:
        return jsonify({
            'status': 'running',
            'progress': running_jobs[job_id]['progress'],
            'started_at': running_jobs[job_id]['started_at'].isoformat()
        })
    else:
        return jsonify({'error': 'Job not found'}), 404

@app.route('/api/performance/<asset>/<strategy>', methods=['GET'])
def get_historical_performance(asset, strategy):
    """Get historical performance data for comparison"""
    # This would return our pre-computed optimization results
    # Based on our conversation summary data
    
    historical_data = {
        'SPY': {
            'ai_sentiment': {
                'total_return': 383.8,
                'annual_return': 5.2,
                'sharpe_ratio': 0.23,
                'max_drawdown': -15.2,
                'win_rate': 52.3,
                'total_trades': 156
            },
            'break_retest': {
                'total_return': -12.9,
                'annual_return': -0.4,
                'sharpe_ratio': -0.389,
                'max_drawdown': -25.1,
                'win_rate': 33.3,
                'total_trades': 45
            }
        },
        'QQQ': {
            'ai_sentiment': {
                'total_return': 126.1,
                'annual_return': 3.3,
                'sharpe_ratio': 0.23,
                'max_drawdown': -18.7,
                'win_rate': 48.9,
                'total_trades': 142
            }
        },
        'NVDA': {
            'ai_sentiment': {
                'total_return': 5928.0,
                'annual_return': 32.1,
                'sharpe_ratio': 1.45,
                'max_drawdown': -35.2,
                'win_rate': 58.7,
                'total_trades': 89
            }
        }
    }
    
    if asset in historical_data and strategy in historical_data[asset]:
        return jsonify({
            'performance': historical_data[asset][strategy],
            'status': 'success'
        })
    else:
        return jsonify({
            'performance': None,
            'message': 'No historical data available for this combination'
        })

def _run_backtest_async(job_id, parameters):
    """Run backtest asynchronously"""
    try:
        # Update progress
        running_jobs[job_id]['progress'] = 10
        
        # Load data
        asset = parameters['asset']
        strategy_name = parameters['strategy']
        
        # Simulate data loading (replace with actual data loading)
        time.sleep(1)
        running_jobs[job_id]['progress'] = 30
        
        # Initialize strategy
        if strategy_name == 'ai_sentiment':
            strategy = _create_ai_sentiment_strategy(parameters)
        elif strategy_name == 'break_retest':
            strategy = _create_break_retest_strategy(parameters)
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        running_jobs[job_id]['progress'] = 50
        
        # Run backtest (simulate for now)
        time.sleep(2)
        running_jobs[job_id]['progress'] = 80
        
        # Generate results (mock results based on our historical data)
        results = _generate_mock_results(asset, strategy_name, parameters)
        
        running_jobs[job_id]['progress'] = 100
        
        # Move to completed jobs
        completed_jobs[job_id] = {
            'results': results,
            'completed_at': datetime.now(),
            'parameters': parameters
        }
        
        # Remove from running jobs
        del running_jobs[job_id]
        
    except Exception as e:
        # Handle error
        completed_jobs[job_id] = {
            'error': str(e),
            'completed_at': datetime.now(),
            'parameters': parameters
        }
        if job_id in running_jobs:
            del running_jobs[job_id]

def _create_ai_sentiment_strategy(parameters):
    """Create AI sentiment strategy with parameters"""
    # This would create the actual strategy instance
    # For now, return mock strategy
    return {
        'type': 'ai_sentiment',
        'sentiment_mode': parameters.get('sentiment_mode', 'contrarian'),
        'confidence_threshold': parameters.get('confidence_threshold', 0.15),
        'position_size': parameters.get('position_size', 0.02),
        'lookback_period': parameters.get('lookback_period', 20)
    }

def _create_break_retest_strategy(parameters):
    """Create break & retest strategy with parameters"""
    # This would create the actual strategy instance
    return {
        'type': 'break_retest',
        'breakout_strength': parameters.get('breakout_strength', 0.01),
        'retest_tolerance': parameters.get('retest_tolerance', 0.005),
        'consolidation_period': parameters.get('consolidation_period', 10),
        'risk_reward_ratio': parameters.get('risk_reward_ratio', 3.0)
    }

def _generate_mock_results(asset, strategy, parameters):
    """Generate mock results based on our historical performance data"""
    # Use our actual optimization results from the conversation summary
    
    base_results = {
        'SPY': {
            'ai_sentiment': {'total_return': 383.8, 'annual_return': 5.2, 'sharpe_ratio': 0.23, 'win_rate': 52.3, 'total_trades': 156, 'max_drawdown': -15.2},
            'break_retest': {'total_return': -12.9, 'annual_return': -0.4, 'sharpe_ratio': -0.389, 'win_rate': 33.3, 'total_trades': 45, 'max_drawdown': -25.1}
        },
        'QQQ': {
            'ai_sentiment': {'total_return': 126.1, 'annual_return': 3.3, 'sharpe_ratio': 0.23, 'win_rate': 48.9, 'total_trades': 142, 'max_drawdown': -18.7}
        },
        'NVDA': {
            'ai_sentiment': {'total_return': 5928.0, 'annual_return': 32.1, 'sharpe_ratio': 1.45, 'win_rate': 58.7, 'total_trades': 89, 'max_drawdown': -35.2}
        },
        'AAPL': {
            'ai_sentiment': {'total_return': 545.0, 'annual_return': 13.2, 'sharpe_ratio': 0.89, 'win_rate': 54.2, 'total_trades': 78, 'max_drawdown': -22.1}
        },
        'AMZN': {
            'ai_sentiment': {'total_return': 449.0, 'annual_return': 11.8, 'sharpe_ratio': 0.76, 'win_rate': 51.8, 'total_trades': 82, 'max_drawdown': -28.5}
        }
    }
    
    if asset in base_results and strategy in base_results[asset]:
        results = base_results[asset][strategy].copy()
        
        # Add some variation based on parameters
        preset = parameters.get('preset', 'Balanced')
        if preset == 'Conservative':
            results['total_return'] *= 0.8
            results['annual_return'] *= 0.8
            results['win_rate'] *= 1.1
            results['max_drawdown'] *= 0.7
        elif preset == 'Aggressive':
            results['total_return'] *= 1.2
            results['annual_return'] *= 1.2
            results['win_rate'] *= 0.9
            results['max_drawdown'] *= 1.3
        
        # Add additional metrics
        results.update({
            'avg_trade': results['total_return'] / results['total_trades'] if results['total_trades'] > 0 else 0,
            'profit_factor': 1.8 if results['total_return'] > 0 else 0.6,
            'calmar_ratio': results['annual_return'] / abs(results['max_drawdown']) if results['max_drawdown'] != 0 else 0,
            'backtest_period': f"{AVAILABLE_ASSETS[asset]['years']} years",
            'strategy_name': strategy,
            'asset_name': asset,
            'parameters': parameters
        })
        
        return results
    else:
        # Return default results for unknown combinations
        return {
            'total_return': 0.0,
            'annual_return': 0.0,
            'sharpe_ratio': 0.0,
            'win_rate': 50.0,
            'total_trades': 0,
            'max_drawdown': 0.0,
            'avg_trade': 0.0,
            'profit_factor': 1.0,
            'calmar_ratio': 0.0,
            'backtest_period': f"{AVAILABLE_ASSETS[asset]['years']} years",
            'strategy_name': strategy,
            'asset_name': asset,
            'parameters': parameters
        }

if __name__ == '__main__':
    print("🚀 Starting SentimentTrade Backtesting API Server...")
    print("📊 Available Strategies: AI Sentiment, Break & Retest")
    print("📈 Available Assets: SPY, QQQ, NVDA, AAPL, AMZN, MSFT, GOOGL")
    print("🔧 Server running on http://localhost:8000")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
