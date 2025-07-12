import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';

class DashboardScreen extends StatefulWidget {
  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final ApiService _apiService = ApiService();
  Map<String, dynamic> _dashboardData = {};
  bool _isLoading = true;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _loadDashboard();
  }

  Future<void> _loadDashboard() async {
    try {
      setState(() => _isLoading = true);
      final data = await _apiService.getDashboard();
      setState(() {
        _dashboardData = data;
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
        title: Text('Dashboard'),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _loadDashboard,
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
              'Error loading dashboard',
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
              onPressed: _loadDashboard,
              child: Text('Retry'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadDashboard,
      color: AppTheme.primaryColor,
      child: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildPortfolioOverview(),
            SizedBox(height: 24),
            _buildPerformanceMetrics(),
            SizedBox(height: 24),
            _buildRecentActivity(),
          ],
        ),
      ),
    );
  }

  Widget _buildPortfolioOverview() {
    final totalValue = _dashboardData['total_portfolio_value']?.toDouble() ?? 0.0;
    final totalGain = _dashboardData['total_gain']?.toDouble() ?? 0.0;
    final totalGainPercent = _dashboardData['total_gain_percent']?.toDouble() ?? 0.0;
    final isPositive = totalGain >= 0;

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
              'Portfolio Value',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            SizedBox(height: 8),
            Text(
              '\$${totalValue.toStringAsFixed(2)}',
              style: Theme.of(context).textTheme.headlineLarge,
            ),
            SizedBox(height: 12),
            Row(
              children: [
                Icon(
                  isPositive ? Icons.trending_up : Icons.trending_down,
                  color: isPositive ? AppTheme.positiveColor : AppTheme.negativeColor,
                  size: 20,
                ),
                SizedBox(width: 8),
                Text(
                  '${isPositive ? '+' : ''}\$${totalGain.toStringAsFixed(2)}',
                  style: TextStyle(
                    color: isPositive ? AppTheme.positiveColor : AppTheme.negativeColor,
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                SizedBox(width: 8),
                Text(
                  '(${isPositive ? '+' : ''}${totalGainPercent.toStringAsFixed(2)}%)',
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

  Widget _buildPerformanceMetrics() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Performance',
          style: Theme.of(context).textTheme.headlineSmall,
        ),
        SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildMetricCard(
                'Win Rate',
                '${(_dashboardData['win_rate']?.toDouble() ?? 0.0).toStringAsFixed(1)}%',
                Icons.check_circle_outline,
                AppTheme.positiveColor,
              ),
            ),
            SizedBox(width: 12),
            Expanded(
              child: _buildMetricCard(
                'Total Trades',
                '${_dashboardData['total_trades'] ?? 0}',
                Icons.swap_horiz,
                AppTheme.primaryColor,
              ),
            ),
          ],
        ),
        SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _buildMetricCard(
                'Avg Return',
                '${(_dashboardData['avg_return']?.toDouble() ?? 0.0).toStringAsFixed(2)}%',
                Icons.trending_up,
                AppTheme.accentColor,
              ),
            ),
            SizedBox(width: 12),
            Expanded(
              child: _buildMetricCard(
                'Best Trade',
                '\$${(_dashboardData['best_trade']?.toDouble() ?? 0.0).toStringAsFixed(2)}',
                Icons.star_outline,
                AppTheme.warningColor,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildMetricCard(String title, String value, IconData icon, Color color) {
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
                Icon(icon, color: color, size: 20),
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
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentActivity() {
    final recentTrades = _dashboardData['recent_trades'] as List<dynamic>? ?? [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Recent Activity',
          style: Theme.of(context).textTheme.headlineSmall,
        ),
        SizedBox(height: 16),
        if (recentTrades.isEmpty)
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
                      Icons.history,
                      color: AppTheme.textTertiary,
                      size: 48,
                    ),
                    SizedBox(height: 12),
                    Text(
                      'No recent trades',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                ),
              ),
            ),
          )
        else
          ...recentTrades.take(5).map((trade) => _buildTradeItem(trade)).toList(),
      ],
    );
  }

  Widget _buildTradeItem(Map<String, dynamic> trade) {
    final symbol = trade['symbol'] ?? '';
    final action = trade['action'] ?? '';
    final quantity = trade['quantity']?.toDouble() ?? 0.0;
    final price = trade['price']?.toDouble() ?? 0.0;
    final profit = trade['profit']?.toDouble() ?? 0.0;
    final isProfit = profit >= 0;

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
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: action.toLowerCase() == 'buy' 
                      ? AppTheme.positiveColor.withOpacity(0.1)
                      : AppTheme.negativeColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  action.toLowerCase() == 'buy' ? Icons.add : Icons.remove,
                  color: action.toLowerCase() == 'buy' 
                      ? AppTheme.positiveColor 
                      : AppTheme.negativeColor,
                ),
              ),
              SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '$action $symbol',
                      style: Theme.of(context).textTheme.bodyLarge,
                    ),
                    Text(
                      '${quantity.toStringAsFixed(0)} shares @ \$${price.toStringAsFixed(2)}',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                ),
              ),
              Text(
                '${isProfit ? '+' : ''}\$${profit.toStringAsFixed(2)}',
                style: TextStyle(
                  color: isProfit ? AppTheme.positiveColor : AppTheme.negativeColor,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
