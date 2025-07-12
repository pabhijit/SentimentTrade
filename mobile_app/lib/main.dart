import 'package:flutter/material.dart';
import 'screens/main_navigation.dart';
import 'screens/login_screen.dart';
import 'utils/theme.dart';

void main() {
  runApp(const SentimentTradeApp());
}

class SentimentTradeApp extends StatelessWidget {
  const SentimentTradeApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SentimentTrade',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: const LoginScreen(),
      routes: {
        '/login': (context) => const LoginScreen(),
        '/main': (context) => const MainNavigation(),
      },
    );
  }
}
