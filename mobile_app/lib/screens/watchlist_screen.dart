import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';
import 'stock_detail_screen.dart';

class WatchlistScreen extends StatefulWidget {
  @override
  _WatchlistScreenState createState() => _WatchlistScreenState();
}

class _WatchlistScreenState extends State<WatchlistScreen> {
  final ApiService _apiService = ApiService();
  List<Map<String, dynamic>> _watchlist = [];
  bool _isLoading = true;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _loadWatchlist();
  }

  Future<void> _loadWatchlist() async {
    try {
      setState(() => _isLoading = true);
      final watchlist = await _apiService.getWatchlist();
      setState(() {
        _watchlist = watchlist;
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
        title: Text('Watchlist'),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _loadWatchlist,
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
              'Error loading watchlist',
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
              onPressed: _loadWatchlist,
              child: Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_watchlist.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.list_alt,
              color: AppTheme.textTertiary,
              size: 64,
            ),
            SizedBox(height: 16),
            Text(
              'No stocks in watchlist',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            SizedBox(height: 8),
            Text(
              'Add stocks to start tracking',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadWatchlist,
      color: AppTheme.primaryColor,
      child: ListView.builder(
        padding: EdgeInsets.all(16),
        itemCount: _watchlist.length,
        itemBuilder: (context, index) {
          final stock = _watchlist[index];
          return _buildStockCard(stock);
        },
      ),
    );
  }

  Widget _buildStockCard(Map<String, dynamic> stock) {
    final symbol = stock['symbol'] ?? '';
    final price = stock['current_price']?.toDouble() ?? 0.0;
    final change = stock['price_change']?.toDouble() ?? 0.0;
    final changePercent = stock['price_change_percent']?.toDouble() ?? 0.0;
    final isPositive = change >= 0;

    return Container(
      margin: EdgeInsets.only(bottom: 12),
      child: Card(
        color: AppTheme.cardColor,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
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
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: EdgeInsets.all(16),
            child: Row(
              children: [
                // Stock Symbol and Name
                Expanded(
                  flex: 2,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        symbol,
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      SizedBox(height: 4),
                      Text(
                        stock['company_name'] ?? symbol,
                        style: Theme.of(context).textTheme.bodyMedium,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                
                // Price and Change
                Expanded(
                  flex: 1,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        '\$${price.toStringAsFixed(2)}',
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      SizedBox(height: 4),
                      Container(
                        padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: isPositive 
                              ? AppTheme.positiveColor.withOpacity(0.1)
                              : AppTheme.negativeColor.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          '${isPositive ? '+' : ''}${changePercent.toStringAsFixed(2)}%',
                          style: TextStyle(
                            color: isPositive ? AppTheme.positiveColor : AppTheme.negativeColor,
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                
                // Arrow Icon
                SizedBox(width: 8),
                Icon(
                  Icons.chevron_right,
                  color: AppTheme.textTertiary,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
