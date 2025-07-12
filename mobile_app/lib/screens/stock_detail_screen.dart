import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';

class StockDetailScreen extends StatefulWidget {
  final String symbol;

  const StockDetailScreen({Key? key, required this.symbol}) : super(key: key);

  @override
  _StockDetailScreenState createState() => _StockDetailScreenState();
}

class _StockDetailScreenState extends State<StockDetailScreen> {
  final ApiService _apiService = ApiService();
  Map<String, dynamic> _stockData = {};
  bool _isLoading = true;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _loadStockData();
  }

  Future<void> _loadStockData() async {
    try {
      setState(() => _isLoading = true);
      final data = await _apiService.getStockData(widget.symbol);
      setState(() {
        _stockData = data;
        _isLoading = false;
        _error = '';
      });
    } catch (e) {
      setState(() {
        _error = e.toString().replaceAll('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  Future<void> _generateSignal() async {
    try {
      final signal = await _apiService.generateSignal(widget.symbol);
      _showSignalDialog(signal);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to generate signal: ${e.toString()}'),
          backgroundColor: AppTheme.negativeColor,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      appBar: AppBar(
        title: Text(widget.symbol),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _loadStockData,
          ),
        ],
      ),
      body: _buildBody(),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _generateSignal,
        backgroundColor: AppTheme.primaryColor,
        icon: Icon(Icons.analytics),
        label: Text('Generate Signal'),
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return Center(
        child: CircularProgressIndicator(color: AppTheme.primaryColor),
      );
    }

    if (_error.isNotEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              color: AppTheme.negativeColor,
              size: 64,
            ),
            SizedBox(height: 16),
            Text(
              'Error loading stock data',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            SizedBox(height: 8),
            Text(
              _error,
              style: Theme.of(context).textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: _loadStockData,
              child: Text('Retry'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadStockData,
      color: AppTheme.primaryColor,
      child: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildPriceHeader(),
            SizedBox(height: 24),
            _buildChartPlaceholder(),
            SizedBox(height: 24),
            _buildKeyMetrics(),
            SizedBox(height: 24),
            _buildRecentSignals(),
          ],
        ),
      ),
    );
  }

  Widget _buildPriceHeader() {
    final price = _stockData['current_price']?.toDouble() ?? 0.0;
    final change = _stockData['price_change']?.toDouble() ?? 0.0;
    final changePercent = _stockData['price_change_percent']?.toDouble() ?? 0.0;
    final isPositive = change >= 0;

    return Card(
      color: AppTheme.cardColor,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              widget.symbol,
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            Text(
              _stockData['company_name'] ?? widget.symbol,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            SizedBox(height: 16),
            Text(
              '\$${price.toStringAsFixed(2)}',
              style: Theme.of(context).textTheme.headlineLarge,
            ),
            SizedBox(height: 8),
            Row(
              children: [
                Icon(
                  isPositive ? Icons.trending_up : Icons.trending_down,
                  color: isPositive ? AppTheme.positiveColor : AppTheme.negativeColor,
                  size: 20,
                ),
                SizedBox(width: 8),
                Text(
                  '${isPositive ? '+' : ''}\$${change.toStringAsFixed(2)}',
                  style: TextStyle(
                    color: isPositive ? AppTheme.positiveColor : AppTheme.negativeColor,
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                SizedBox(width: 8),
                Text(
                  '(${isPositive ? '+' : ''}${changePercent.toStringAsFixed(2)}%)',
                  style: TextStyle(
                    color: isPositive ? AppTheme.positiveColor : AppTheme.negativeColor,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChartPlaceholder() {
    return Card(
      color: AppTheme.cardColor,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Container(
        height: 200,
        width: double.infinity,
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.show_chart,
                color: AppTheme.textTertiary,
                size: 48,
              ),
              SizedBox(height: 12),
              Text(
                'Price Chart',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  color: AppTheme.textTertiary,
                ),
              ),
              SizedBox(height: 8),
              Text(
                'Chart integration coming soon',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildKeyMetrics() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Key Metrics',
          style: Theme.of(context).textTheme.headlineSmall,
        ),
        SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildMetricCard(
                'Volume',
                '${_stockData['volume'] ?? 'N/A'}',
                Icons.bar_chart,
              ),
            ),
            SizedBox(width: 12),
            Expanded(
              child: _buildMetricCard(
                'Market Cap',
                _stockData['market_cap'] ?? 'N/A',
                Icons.account_balance,
              ),
            ),
          ],
        ),
        SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _buildMetricCard(
                '52W High',
                '\$${(_stockData['high_52w']?.toDouble() ?? 0.0).toStringAsFixed(2)}',
                Icons.trending_up,
              ),
            ),
            SizedBox(width: 12),
            Expanded(
              child: _buildMetricCard(
                '52W Low',
                '\$${(_stockData['low_52w']?.toDouble() ?? 0.0).toStringAsFixed(2)}',
                Icons.trending_down,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildMetricCard(String title, String value, IconData icon) {
    return Card(
      color: AppTheme.cardColor,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: AppTheme.primaryColor, size: 20),
                SizedBox(width: 8),
                Text(
                  title,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ],
            ),
            SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentSignals() {
    final recentSignals = _stockData['recent_signals'] as List<dynamic>? ?? [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Recent Signals',
          style: Theme.of(context).textTheme.headlineSmall,
        ),
        SizedBox(height: 16),
        if (recentSignals.isEmpty)
          Card(
            color: AppTheme.cardColor,
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: Padding(
              padding: EdgeInsets.all(20),
              child: Center(
                child: Column(
                  children: [
                    Icon(
                      Icons.signal_cellular_alt,
                      color: AppTheme.textTertiary,
                      size: 48,
                    ),
                    SizedBox(height: 12),
                    Text(
                      'No recent signals',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                ),
              ),
            ),
          )
        else
          ...recentSignals.take(3).map((signal) => _buildSignalItem(signal)).toList(),
      ],
    );
  }

  Widget _buildSignalItem(Map<String, dynamic> signal) {
    final action = signal['action'] ?? '';
    final confidence = signal['confidence']?.toDouble() ?? 0.0;
    final timestamp = signal['timestamp'] ?? '';
    final isBuy = action.toLowerCase() == 'buy';

    return Container(
      margin: EdgeInsets.only(bottom: 8),
      child: Card(
        color: AppTheme.cardColor,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: isBuy 
                      ? AppTheme.positiveColor.withOpacity(0.1)
                      : AppTheme.negativeColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  action.toUpperCase(),
                  style: TextStyle(
                    color: isBuy ? AppTheme.positiveColor : AppTheme.negativeColor,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Confidence: ${(confidence * 100).toStringAsFixed(0)}%',
                      style: Theme.of(context).textTheme.bodyLarge,
                    ),
                    Text(
                      _formatTimestamp(timestamp),
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatTimestamp(String timestamp) {
    try {
      final dateTime = DateTime.parse(timestamp);
      final now = DateTime.now();
      final difference = now.difference(dateTime);
      
      if (difference.inMinutes < 60) {
        return '${difference.inMinutes}m ago';
      } else if (difference.inHours < 24) {
        return '${difference.inHours}h ago';
      } else {
        return '${difference.inDays}d ago';
      }
    } catch (e) {
      return timestamp;
    }
  }

  void _showSignalDialog(Map<String, dynamic> signal) {
    final action = signal['action'] ?? '';
    final confidence = signal['confidence']?.toDouble() ?? 0.0;
    final reasoning = signal['reasoning'] ?? '';

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.cardColor,
        title: Text(
          'New Signal Generated',
          style: TextStyle(color: AppTheme.textPrimary),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: action.toLowerCase() == 'buy' 
                        ? AppTheme.positiveColor.withOpacity(0.1)
                        : AppTheme.negativeColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    action.toUpperCase(),
                    style: TextStyle(
                      color: action.toLowerCase() == 'buy' 
                          ? AppTheme.positiveColor 
                          : AppTheme.negativeColor,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                SizedBox(width: 12),
                Text(
                  '${(confidence * 100).toStringAsFixed(0)}% Confidence',
                  style: TextStyle(
                    color: AppTheme.textPrimary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            SizedBox(height: 16),
            if (reasoning.isNotEmpty) ...[
              Text(
                'Analysis:',
                style: TextStyle(
                  color: AppTheme.textPrimary,
                  fontWeight: FontWeight.w600,
                ),
              ),
              SizedBox(height: 8),
              Text(
                reasoning,
                style: TextStyle(color: AppTheme.textSecondary),
              ),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Close',
              style: TextStyle(color: AppTheme.textSecondary),
            ),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              // Navigate to notifications screen to see all signals
              Navigator.pop(context);
            },
            child: Text('View All Signals'),
          ),
        ],
      ),
    );
  }
}
