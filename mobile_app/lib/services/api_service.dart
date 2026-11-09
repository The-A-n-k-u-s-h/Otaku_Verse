import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class ApiService {
  ApiService._();

  static final ApiService instance = ApiService._();

  // Chrome uses localhost. The Android emulator uses 10.0.2.2
  // to reach the Flask server running on the development computer.
  static String get baseUrl => kIsWeb
      ? 'http://127.0.0.1:5000'
      : 'http://10.0.2.2:5000';

  String? _sessionCookie;

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Cookie': ?_sessionCookie,
      };

  void _saveCookie(http.Response response) {
    final rawCookie = response.headers['set-cookie'];
    if (rawCookie != null && rawCookie.isNotEmpty) {
      _sessionCookie = rawCookie.split(';').first;
    }
  }

  Map<String, dynamic> _decodeResponse(http.Response response) {
    dynamic decoded;
    try {
      decoded = jsonDecode(response.body);
    } on FormatException {
      throw Exception('The backend returned an invalid JSON response.');
    }

    if (decoded is! Map<String, dynamic>) {
      throw Exception('Unexpected response format from the backend.');
    }

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception(
        decoded['message']?.toString() ??
            'Request failed with status ${response.statusCode}.',
      );
    }

    return decoded;
  }

  Future<Map<String, dynamic>> startGuestSession(int duration) async {
    if (![10, 20, 30].contains(duration)) {
      throw ArgumentError('Guest duration must be 10, 20 or 30 minutes.');
    }

    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl/api/guest/start'),
            headers: _headers,
            body: jsonEncode({'duration': duration}),
          )
          .timeout(const Duration(seconds: 15));

      _saveCookie(response);
      return _decodeResponse(response);
    } on http.ClientException catch (e) {
      throw Exception(
        'Cannot reach Flask. Check that the backend is running and CORS is configured: $e',
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getGuestStatus() async {
    try {
      final response = await http
          .get(
            Uri.parse('$baseUrl/api/guest/status'),
            headers: _headers,
          )
          .timeout(const Duration(seconds: 15));

      _saveCookie(response);
      return _decodeResponse(response);
    } on http.ClientException catch (e) {
      throw Exception('Cannot reach Flask backend: $e');
    }
  }

  Future<void> endGuestSession() async {
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl/api/guest/end'),
            headers: _headers,
          )
          .timeout(const Duration(seconds: 15));

      _saveCookie(response);
      _decodeResponse(response);
      _sessionCookie = null;
    } on http.ClientException catch (e) {
      throw Exception('Cannot reach Flask backend: $e');
    }
  }
}
