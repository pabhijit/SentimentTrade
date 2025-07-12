import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';
import 'stock_detail_screen.dart';

class NotificationsScreen extends StatefulWidget {
  @override
  _NotificationsScreenState createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  final ApiService _apiService = ApiService();
  List<Map<String, dynamic>> _signals = [];
  bool _isLoading = true;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _loadSignals();
  }

  Future<void> _loadSignals() async {
    try {
      setState(() => _isLoading = true);
      final signals = await _apiService.getSignals(limit: 50);
      setState(() {
        _signals = signals;
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      appBar: AppBar(
        title: Text('Trading Signals'),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _loadSignals,
          ),
        ],
      ),
      body: _buildBody(),
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
              'Error loading signals',
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
              onPressed: _loadSignals,
              child: Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_signals.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.notifications_none,
              color: AppTheme.textTertiary,
              size: 64,
            ),
            SizedBox(height: 16),
            Text(
              'No signals yet',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            SizedBox(height: 8),
            Text(
              'Trading signals will appear here',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadSignals,
      color: AppTheme.primaryColor,
      child: ListView.builder(
        padding: EdgeInsets.all(16),
        itemCount: _signals.length,
        itemBuilder: (context, index) {
          final signal = _signals[index];
          return _buildSignalCard(signal);
        },
      ),
    );
  }

  Widget _buildSignalCard(Map<String, dynamic> signal) {
    final symbol = signal['symbol'] ?? '';
    final action = signal['action'] ?? '';
    final confidence = signal['confidence']?.toDouble() ?? 0.0;
    final currentPrice = signal['current_price']?.toDouble() ?? 0.0;
    final targetPrice = signal['target_price']?.toDouble() ?? 0.0;
    final stopLoss = signal['stop_loss']?.toDouble() ?? 0.0;
    final timestamp = signal['timestamp'] ?? '';
    final reasoning = signal['reasoning'] ?? '';

    final isBuy = action.toLowerCase() == 'buy';
    final actionColor = isBuy ? AppTheme.positiveColor : AppTheme.negativeColor;
    final confidenceColor = confidence >= 0.8 
        ? AppTheme.positiveColor 
        : confidence >= 0.6 
            ? AppTheme.warningColor 
            : AppTheme.negativeColor;

    return Container(
      margin: EdgeInsets.only(bottom: 16),
      child: Card(
        color: AppTheme.cardColor,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        child: InkWell(
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => StockDetailScreen(symbol: symbol),
              ),
            );
          },
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header with symbol and action
                Row(
                  children: [
                    Container(
                      padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: actionColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        action.toUpperCase(),
                        style: TextStyle(
                          color: actionColor,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    SizedBox(width: 12),
                    Text(
                      symbol,
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    Spacer(),
                    Container(
                      padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: confidenceColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        '${(confidence * 100).toStringAsFixed(0)}%',
                        style: TextStyle(
                          color: confidenceColor,
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
                
                SizedBox(height: 16),
                
                // Price information
                Row(
                  children: [
                    Expanded(
                      child: _buildPriceInfo('Current', currentPrice),
                    ),
                    Expanded(
                      child: _buildPriceInfo('Target', targetPrice),
                    ),
                    Expanded(
                      child: _buildPriceInfo('Stop Loss', stopLoss),
                    ),
                  ],
                ),
                
                SizedBox(height: 16),
                
                // Reasoning
                if (reasoning.isNotEmpty) ...[
                  Text(
                    'Analysis',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    reasoning,
                    style: Theme.of(context).textTheme.bodyMedium,
                    maxLines: 3,
                    overflow: TextOverflow.ellipsis,
                  ),
                  SizedBox(height: 12),
                ],
                
                // Timestamp and action button
                Row(
                  children: [
                    Icon(
                      Icons.access_time,
                      color: AppTheme.textTertiary,
                      size: 16,
                    ),
                    SizedBox(width: 4),
                    Text(
                      _formatTimestamp(timestamp),
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    Spacer(),
                    TextButton(
                      onPressed: () => _showTradeDialog(signal),
                      child: Text(
                        'Trade',
                        style: TextStyle(color: AppTheme.primaryColor),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPriceInfo(String label, double price) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall,
        ),
        SizedBox(height: 4),
        Text(
          '\$${price.toStringAsFixed(2)}',
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
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

  void _showTradeDialog(Map<String, dynamic> signal) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.cardColor,
        title: Text(
          'Execute Trade',
          style: TextStyle(color: AppTheme.textPrimary),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '${signal['action']} ${signal['symbol']}',
              style: TextStyle(
                color: AppTheme.textPrimary,
                fontSize: 18,
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(height: 16),
            Text(
              'Current Price: \$${signal['current_price']?.toStringAsFixed(2)}',
              style: TextStyle(color: AppTheme.textSecondary),
            ),
            Text(
              'Target Price: \$${signal['target_price']?.toStringAsFixed(2)}',
              style: TextStyle(color: AppTheme.textSecondary),
            ),
            Text(
              'Stop Loss: \$${signal['stop_loss']?.toStringAsFixed(2)}',
              style: TextStyle(color: AppTheme.textSecondary),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Cancel',
              style: TextStyle(color: AppTheme.textSecondary),
            ),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _executeTrade(signal);
            },
            child: Text('Execute'),
          ),
        ],
      ),
    );
  }

  Future<void> _executeTrade(Map<String, dynamic> signal) async {
    try {
      await _apiService.confirmTrade({
        'symbol': signal['symbol'],
        'action': signal['action'],
        'quantity': 100, // Default quantity
        'price': signal['current_price'],
        'signal_id': signal['id'],
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Trade executed successfully'),
          backgroundColor: AppTheme.positiveColor,
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to execute trade: ${e.toString()}'),
          backgroundColor: AppTheme.negativeColor,
        ),
      );
    }
  }
}
