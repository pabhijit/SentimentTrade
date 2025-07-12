import 'dart:convert';
import 'package:http/http.dart' as http;
import 'auth_service.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000'; // Update for production
  final AuthService _authService = AuthService();

  // Existing methods
  Future<List<Map<String, dynamic>>> getWatchlist() async {
    try {
      final headers = await _authService.getAuthHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/watchlist'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.cast<Map<String, dynamic>>();
      } else {
        throw Exception('Failed to load watchlist');
      }
    } catch (e) {
      throw Exception('Network error: ${e.toString()}');
    }
  }

  Future<Map<String, dynamic>> generateSignal(String symbol) async {
    try {
      final headers = await _authService.getAuthHeaders();
      final response = await http.post(
        Uri.parse('$baseUrl/signal'),
        headers: headers,
        body: json.encode({'symbol': symbol}),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to generate signal');
      }
    } catch (e) {
      throw Exception('Network error: ${e.toString()}');
    }
  }

  Future<Map<String, dynamic>> confirmTrade(Map<String, dynamic> tradeData) async {
    try {
      final headers = await _authService.getAuthHeaders();
      final response = await http.post(
        Uri.parse('$baseUrl/trade-confirmation'),
        headers: headers,
        body: json.encode(tradeData),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to confirm trade');
      }
    } catch (e) {
      throw Exception('Network error: ${e.toString()}');
    }
  }

  Future<Map<String, dynamic>> getDashboard() async {
    try {
      final headers = await _authService.getAuthHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/dashboard'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load dashboard');
      }
    } catch (e) {
      throw Exception('Network error: ${e.toString()}');
    }
  }

  Future<List<Map<String, dynamic>>> getSignals({int limit = 20}) async {
    try {
      final headers = await _authService.getAuthHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/signals?limit=$limit'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.cast<Map<String, dynamic>>();
      } else {
        throw Exception('Failed to load signals');
      }
    } catch (e) {
      throw Exception('Network error: ${e.toString()}');
    }
  }

  Future<Map<String, dynamic>> getStockData(String symbol) async {
    try {
      final headers = await _authService.getAuthHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/stock/$symbol'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load stock data');
      }
    } catch (e) {
      throw Exception('Network error: ${e.toString()}');
    }
  }

  Future<Map<String, dynamic>> getTradingPreferences() async {
    try {
      final headers = await _authService.getAuthHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/user/preferences'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load trading preferences');
      }
    } catch (e) {
      throw Exception('Network error: ${e.toString()}');
    }
  }

  Future<Map<String, dynamic>> updateTradingPreferences(Map<String, dynamic> preferences) async {
    try {
      final headers = await _authService.getAuthHeaders();
      final response = await http.put(
        Uri.parse('$baseUrl/user/preferences'),
        headers: headers,
        body: json.encode(preferences),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to update trading preferences');
      }
    } catch (e) {
      throw Exception('Network error: ${e.toString()}');
    }
  }

  // NEW BACKTESTING METHODS

  /// Get available trading strategies with their parameter schemas
  Future<List<Map<String, dynamic>>> getAvailableStrategies() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/strategies'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['strategies']);
      } else {
        throw Exception('Failed to load strategies: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
  
  /// Get available assets with their data ranges
  Future<Map<String, dynamic>> getAvailableAssets() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/assets'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['assets'];
      } else {
        throw Exception('Failed to load assets: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
  
  /// Run a backtest with specified parameters
  Future<Map<String, dynamic>> runBacktest(Map<String, dynamic> parameters) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/backtest'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(parameters),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data;
      } else if (response.statusCode == 202) {
        // Backtest started, return job ID for polling
        final data = json.decode(response.body);
        return await _pollBacktestResults(data['job_id']);
      } else {
        throw Exception('Failed to run backtest: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Backtest error: $e');
    }
  }
  
  /// Poll backtest results for long-running jobs
  Future<Map<String, dynamic>> _pollBacktestResults(String jobId) async {
    const maxAttempts = 60; // 5 minutes with 5-second intervals
    int attempts = 0;
    
    while (attempts < maxAttempts) {
      try {
        final response = await http.get(
          Uri.parse('$baseUrl/api/backtest/results/$jobId'),
          headers: {'Content-Type': 'application/json'},
        );
        
        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          if (data['status'] == 'completed') {
            return data['results'];
          } else if (data['status'] == 'failed') {
            throw Exception('Backtest failed: ${data['error']}');
          }
          // Still running, continue polling
        } else if (response.statusCode == 404) {
          throw Exception('Backtest job not found');
        }
        
        await Future.delayed(const Duration(seconds: 5));
        attempts++;
      } catch (e) {
        if (attempts >= maxAttempts - 1) {
          throw Exception('Backtest timeout: $e');
        }
        await Future.delayed(const Duration(seconds: 5));
        attempts++;
      }
    }
    
    throw Exception('Backtest timeout after ${maxAttempts * 5} seconds');
  }
  
  /// Get preset configurations for strategies
  Future<Map<String, dynamic>> getPresetConfigurations(String strategy) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/strategies/$strategy/presets'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['presets'];
      } else {
        throw Exception('Failed to load presets: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
  
  /// Get historical performance data for comparison
  Future<Map<String, dynamic>> getHistoricalPerformance(String asset, String strategy) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/performance/$asset/$strategy'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data;
      } else {
        throw Exception('Failed to load performance data: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
  
  /// Save backtest results for later comparison
  Future<String> saveBacktestResults(Map<String, dynamic> results) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/backtest/save'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(results),
      );
      
      if (response.statusCode == 201) {
        final data = json.decode(response.body);
        return data['result_id'];
      } else {
        throw Exception('Failed to save results: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Save error: $e');
    }
  }
  
  /// Get saved backtest results
  Future<List<Map<String, dynamic>>> getSavedResults() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/backtest/saved'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['results']);
      } else {
        throw Exception('Failed to load saved results: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
  
  /// Compare multiple backtest results
  Future<Map<String, dynamic>> compareResults(List<String> resultIds) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/backtest/compare'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'result_ids': resultIds}),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data;
      } else {
        throw Exception('Failed to compare results: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Comparison error: $e');
    }
  }
}
