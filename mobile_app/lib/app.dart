
import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

class OtakuVerseApp extends StatefulWidget {
  const OtakuVerseApp({super.key});

  @override
  State<OtakuVerseApp> createState() => _OtakuVerseAppState();
}

class _OtakuVerseAppState extends State<OtakuVerseApp> {
  ThemeMode _themeMode = ThemeMode.dark;

  void _toggleTheme() {
    setState(() {
      _themeMode = _themeMode == ThemeMode.dark
          ? ThemeMode.light
          : ThemeMode.dark;
    });
  }

  @override
  Widget build(BuildContext context) {
    const purple = Color(0xFFA879FF);

    return MaterialApp(
      title: 'OtakuVerse',
      debugShowCheckedModeBanner: false,
      themeMode: _themeMode,

      // Light Theme
      theme: ThemeData(
        brightness: Brightness.light,
        scaffoldBackgroundColor: const Color(0xFFF7F4FC),
        fontFamily: 'Roboto',
        colorScheme: ColorScheme.fromSeed(
          seedColor: purple,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),

      // Dark Theme
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0B0A12),
        fontFamily: 'Roboto',
        colorScheme: ColorScheme.fromSeed(
          seedColor: purple,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),

      home: HomeScreen(
        isDark: _themeMode == ThemeMode.dark,
        onToggleTheme: _toggleTheme,
      ),
    );
  }
}
