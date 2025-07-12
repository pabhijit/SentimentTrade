import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';

class BacktestingScreen extends StatefulWidget {
  const BacktestingScreen({Key? key}) : super(key: key);

  @override
  State<BacktestingScreen> createState() => _BacktestingScreenState();
}

class _BacktestingScreenState extends State<BacktestingScreen> {
  final ApiService _apiService = ApiService();
  
  // Strategy Selection
  String _selectedStrategy = 'AI Sentiment';
  final List<String> _strategies = ['AI Sentiment', 'Break & Retest'];
  
  // Asset Selection
  String _selectedAsset = 'SPY';
  final Map<String, Map<String, dynamic>> _assets = {
    'SPY': {'name': 'SPDR S&P 500 ETF', 'years': '31+ years', 'type': 'ETF'},
    'QQQ': {'name': 'Invesco QQQ Trust', 'years': '25+ years', 'type': 'ETF'},
    'NVDA': {'name': 'NVIDIA Corporation', 'years': '15+ years', 'type': 'Stock'},
    'AAPL': {'name': 'Apple Inc.', 'years': '15+ years', 'type': 'Stock'},
    'AMZN': {'name': 'Amazon.com Inc.', 'years': '15+ years', 'type': 'Stock'},
    'MSFT': {'name': 'Microsoft Corporation', 'years': '15+ years', 'type': 'Stock'},
    'GOOGL': {'name': 'Alphabet Inc.', 'years': '15+ years', 'type': 'Stock'},
  };
  
  // AI Sentiment Strategy Parameters
  String _sentimentMode = 'contrarian';
  double _confidenceThreshold = 0.15;
  double _positionSize = 0.02;
  int _lookbackPeriod = 20;
  
  // Break & Retest Strategy Parameters
  double _breakoutStrength = 0.01;
  double _retestTolerance = 0.005;
  int _consolidationPeriod = 10;
  double _riskRewardRatio = 3.0;
  
  // Preset Configurations
  String _selectedPreset = 'Balanced';
  final List<String> _presets = ['Conservative', 'Balanced', 'Aggressive', 'High Frequency'];
  
  // Backtest State
  bool _isRunning = false;
  double _progress = 0.0;
  Map<String, dynamic>? _results;
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Strategy Backtesting'),
        backgroundColor: Theme.of(context).primaryColor,
        elevation: 0,
      ),
      body: _isRunning ? _buildRunningView() : _buildConfigurationView(),
    );
  }
  
  Widget _buildConfigurationView() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildStrategySelection(),
          const SizedBox(height: 24),
          _buildAssetSelection(),
          const SizedBox(height: 24),
          _buildPresetSelection(),
          const SizedBox(height: 24),
          _buildParameterControls(),
          const SizedBox(height: 32),
          _buildRunButton(),
          if (_results != null) ...[
            const SizedBox(height: 32),
            _buildResultsSection(),
          ],
        ],
      ),
    );
  }
  
  Widget _buildStrategySelection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Strategy Selection',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: _selectedStrategy,
              decoration: const InputDecoration(
                labelText: 'Trading Strategy',
                border: OutlineInputBorder(),
              ),
              items: _strategies.map((strategy) {
                return DropdownMenuItem(
                  value: strategy,
                  child: Text(strategy),
                );
              }).toList(),
              onChanged: (value) {
                setState(() {
                  _selectedStrategy = value!;
                });
              },
            ),
            const SizedBox(height: 8),
            Text(
              _getStrategyDescription(),
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildAssetSelection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Asset Selection',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: _selectedAsset,
              decoration: const InputDecoration(
                labelText: 'Stock/ETF',
                border: OutlineInputBorder(),
              ),
              items: _assets.entries.map((entry) {
                return DropdownMenuItem(
                  value: entry.key,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text('${entry.key} - ${entry.value['name']}'),
                      Text(
                        '${entry.value['type']} • ${entry.value['years']} of data',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
              onChanged: (value) {
                setState(() {
                  _selectedAsset = value!;
                });
              },
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildPresetSelection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Preset Configurations',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              children: _presets.map((preset) {
                return ChoiceChip(
                  label: Text(preset),
                  selected: _selectedPreset == preset,
                  onSelected: (selected) {
                    if (selected) {
                      setState(() {
                        _selectedPreset = preset;
                        _applyPreset(preset);
                      });
                    }
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 8),
            Text(
              _getPresetDescription(),
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildParameterControls() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Strategy Parameters',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            if (_selectedStrategy == 'AI Sentiment') ..._buildAISentimentParameters(),
            if (_selectedStrategy == 'Break & Retest') ..._buildBreakRetestParameters(),
          ],
        ),
      ),
    );
  }
  
  List<Widget> _buildAISentimentParameters() {
    return [
      // Sentiment Mode
      const Text('Sentiment Mode', style: TextStyle(fontWeight: FontWeight.w500)),
      const SizedBox(height: 8),
      SegmentedButton<String>(
        segments: const [
          ButtonSegment(value: 'momentum', label: Text('Momentum')),
          ButtonSegment(value: 'contrarian', label: Text('Contrarian')),
        ],
        selected: {_sentimentMode},
        onSelectionChanged: (Set<String> selection) {
          setState(() {
            _sentimentMode = selection.first;
          });
        },
      ),
      const SizedBox(height: 16),
      
      // Confidence Threshold
      Text('Confidence Threshold: ${_confidenceThreshold.toStringAsFixed(2)}'),
      Slider(
        value: _confidenceThreshold,
        min: 0.05,
        max: 0.50,
        divisions: 45,
        onChanged: (value) {
          setState(() {
            _confidenceThreshold = value;
          });
        },
      ),
      const SizedBox(height: 16),
      
      // Position Size
      Text('Position Size: ${(_positionSize * 100).toStringAsFixed(1)}%'),
      Slider(
        value: _positionSize,
        min: 0.01,
        max: 0.10,
        divisions: 90,
        onChanged: (value) {
          setState(() {
            _positionSize = value;
          });
        },
      ),
      const SizedBox(height: 16),
      
      // Lookback Period
      Text('Lookback Period: $_lookbackPeriod days'),
      Slider(
        value: _lookbackPeriod.toDouble(),
        min: 5,
        max: 50,
        divisions: 45,
        onChanged: (value) {
          setState(() {
            _lookbackPeriod = value.round();
          });
        },
      ),
    ];
  }
  
  List<Widget> _buildBreakRetestParameters() {
    return [
      // Breakout Strength
      Text('Breakout Strength: ${(_breakoutStrength * 100).toStringAsFixed(1)}%'),
      Slider(
        value: _breakoutStrength,
        min: 0.005,
        max: 0.05,
        divisions: 45,
        onChanged: (value) {
          setState(() {
            _breakoutStrength = value;
          });
        },
      ),
      const SizedBox(height: 16),
      
      // Retest Tolerance
      Text('Retest Tolerance: ${(_retestTolerance * 100).toStringAsFixed(2)}%'),
      Slider(
        value: _retestTolerance,
        min: 0.001,
        max: 0.02,
        divisions: 19,
        onChanged: (value) {
          setState(() {
            _retestTolerance = value;
          });
        },
      ),
      const SizedBox(height: 16),
      
      // Consolidation Period
      Text('Consolidation Period: $_consolidationPeriod days'),
      Slider(
        value: _consolidationPeriod.toDouble(),
        min: 5,
        max: 30,
        divisions: 25,
        onChanged: (value) {
          setState(() {
            _consolidationPeriod = value.round();
          });
        },
      ),
      const SizedBox(height: 16),
      
      // Risk-Reward Ratio
      Text('Risk-Reward Ratio: 1:${_riskRewardRatio.toStringAsFixed(1)}'),
      Slider(
        value: _riskRewardRatio,
        min: 1.0,
        max: 5.0,
        divisions: 40,
        onChanged: (value) {
          setState(() {
            _riskRewardRatio = value;
          });
        },
      ),
    ];
  }
  
  Widget _buildRunButton() {
    return SizedBox(
      width: double.infinity,
      height: 50,
      child: ElevatedButton(
        onPressed: _isRunning ? null : _runBacktest,
        style: ElevatedButton.styleFrom(
          backgroundColor: Theme.of(context).primaryColor,
          foregroundColor: Colors.white,
        ),
        child: const Text(
          'Run Backtest',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
  
  Widget _buildRunningView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(strokeWidth: 6),
            const SizedBox(height: 24),
            Text(
              'Running Backtest...',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            Text(
              'Strategy: $_selectedStrategy\nAsset: $_selectedAsset\nPreset: $_selectedPreset',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey[600]),
            ),
            const SizedBox(height: 24),
            LinearProgressIndicator(
              value: _progress,
              backgroundColor: Colors.grey[300],
            ),
            const SizedBox(height: 8),
            Text('${(_progress * 100).toStringAsFixed(0)}% Complete'),
          ],
        ),
      ),
    );
  }
  
  Widget _buildResultsSection() {
    if (_results == null) return const SizedBox.shrink();
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Backtest Results',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildPerformanceMetrics(),
            const SizedBox(height: 16),
            _buildEquityCurveChart(),
            const SizedBox(height: 16),
            _buildTradeStatistics(),
          ],
        ),
      ),
    );
  }
  
  Widget _buildPerformanceMetrics() {
    return Row(
      children: [
        Expanded(
          child: _buildMetricCard(
            'Total Return',
            '${_results!['total_return']?.toStringAsFixed(1) ?? 'N/A'}%',
            _getReturnColor(_results!['total_return']),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildMetricCard(
            'Annual Return',
            '${_results!['annual_return']?.toStringAsFixed(1) ?? 'N/A'}%',
            _getReturnColor(_results!['annual_return']),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildMetricCard(
            'Sharpe Ratio',
            _results!['sharpe_ratio']?.toStringAsFixed(2) ?? 'N/A',
            _getSharpeColor(_results!['sharpe_ratio']),
          ),
        ),
      ],
    );
  }
  
  Widget _buildMetricCard(String title, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Text(
            title,
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildEquityCurveChart() {
    // Placeholder for equity curve chart
    return Container(
      height: 200,
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(8),
      ),
      child: const Center(
        child: Text('Equity Curve Chart\n(Implementation pending)'),
      ),
    );
  }
  
  Widget _buildTradeStatistics() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Trade Statistics',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Total Trades: ${_results!['total_trades'] ?? 'N/A'}'),
            Text('Win Rate: ${_results!['win_rate']?.toStringAsFixed(1) ?? 'N/A'}%'),
          ],
        ),
        const SizedBox(height: 4),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Max Drawdown: ${_results!['max_drawdown']?.toStringAsFixed(1) ?? 'N/A'}%'),
            Text('Avg Trade: ${_results!['avg_trade']?.toStringAsFixed(2) ?? 'N/A'}%'),
          ],
        ),
      ],
    );
  }
  
  String _getStrategyDescription() {
    switch (_selectedStrategy) {
      case 'AI Sentiment':
        return 'Uses market sentiment analysis with momentum or contrarian approaches. Best performance: NVDA +5,928% (contrarian)';
      case 'Break & Retest':
        return 'Identifies support/resistance breakouts with retest confirmation. Swing trading focused with risk management.';
      default:
        return '';
    }
  }
  
  String _getPresetDescription() {
    switch (_selectedPreset) {
      case 'Conservative':
        return 'Lower risk parameters, fewer trades, higher win rate';
      case 'Balanced':
        return 'Moderate risk-reward balance, tested configuration';
      case 'Aggressive':
        return 'Higher risk parameters, more frequent trading';
      case 'High Frequency':
        return 'Maximum trade frequency, requires active monitoring';
      default:
        return '';
    }
  }
  
  void _applyPreset(String preset) {
    // Apply preset configurations based on our optimization results
    switch (preset) {
      case 'Conservative':
        if (_selectedStrategy == 'AI Sentiment') {
          _confidenceThreshold = 0.25;
          _positionSize = 0.015;
          _lookbackPeriod = 30;
        } else {
          _breakoutStrength = 0.015;
          _retestTolerance = 0.008;
          _consolidationPeriod = 15;
          _riskRewardRatio = 3.5;
        }
        break;
      case 'Balanced':
        if (_selectedStrategy == 'AI Sentiment') {
          _confidenceThreshold = 0.15;
          _positionSize = 0.02;
          _lookbackPeriod = 20;
        } else {
          _breakoutStrength = 0.01;
          _retestTolerance = 0.005;
          _consolidationPeriod = 10;
          _riskRewardRatio = 3.0;
        }
        break;
      case 'Aggressive':
        if (_selectedStrategy == 'AI Sentiment') {
          _confidenceThreshold = 0.10;
          _positionSize = 0.03;
          _lookbackPeriod = 15;
        } else {
          _breakoutStrength = 0.008;
          _retestTolerance = 0.003;
          _consolidationPeriod = 8;
          _riskRewardRatio = 2.5;
        }
        break;
      case 'High Frequency':
        if (_selectedStrategy == 'AI Sentiment') {
          _confidenceThreshold = 0.08;
          _positionSize = 0.025;
          _lookbackPeriod = 10;
        } else {
          _breakoutStrength = 0.005;
          _retestTolerance = 0.002;
          _consolidationPeriod = 5;
          _riskRewardRatio = 2.0;
        }
        break;
    }
  }
  
  Color _getReturnColor(double? value) {
    if (value == null) return Colors.grey;
    return value >= 0 ? Colors.green : Colors.red;
  }
  
  Color _getSharpeColor(double? value) {
    if (value == null) return Colors.grey;
    if (value >= 1.0) return Colors.green;
    if (value >= 0.5) return Colors.orange;
    return Colors.red;
  }
  
  Future<void> _runBacktest() async {
    setState(() {
      _isRunning = true;
      _progress = 0.0;
    });
    
    try {
      // Prepare parameters based on selected strategy
      Map<String, dynamic> parameters = {};
      
      if (_selectedStrategy == 'AI Sentiment') {
        parameters = {
          'strategy': 'ai_sentiment',
          'sentiment_mode': _sentimentMode,
          'confidence_threshold': _confidenceThreshold,
          'position_size': _positionSize,
          'lookback_period': _lookbackPeriod,
        };
      } else {
        parameters = {
          'strategy': 'break_retest',
          'breakout_strength': _breakoutStrength,
          'retest_tolerance': _retestTolerance,
          'consolidation_period': _consolidationPeriod,
          'risk_reward_ratio': _riskRewardRatio,
        };
      }
      
      parameters['asset'] = _selectedAsset;
      parameters['preset'] = _selectedPreset;
      
      // Simulate progress updates
      for (int i = 0; i <= 100; i += 10) {
        await Future.delayed(const Duration(milliseconds: 200));
        setState(() {
          _progress = i / 100.0;
        });
      }
      
      // Run the actual backtest
      final results = await _apiService.runBacktest(parameters);
      
      setState(() {
        _results = results;
        _isRunning = false;
        _progress = 1.0;
      });
      
    } catch (e) {
      setState(() {
        _isRunning = false;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Backtest failed: ${e.toString()}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
}
