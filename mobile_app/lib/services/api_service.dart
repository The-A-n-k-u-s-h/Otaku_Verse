import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

class ApiService {
  ApiService._();

  static final ApiService instance = ApiService._();

  static const String _configuredBaseUrl =
      String.fromEnvironment('API_BASE_URL');

  static String get baseUrl {
    if (_configuredBaseUrl.isNotEmpty) return _configuredBaseUrl;
    return kIsWeb ? 'http://127.0.0.1:5000' : 'http://10.0.2.2:5000';
  }

  static const FlutterSecureStorage _secureStorage = FlutterSecureStorage();
  static const String _cookieStorageKey = 'otakuverse_flask_session_cookie';

  String? _sessionCookie;
  Future<void>? _initialization;

  Future<void> _ensureInitialized() {
    _initialization ??= _loadSavedCookie();
    return _initialization!;
  }

  Future<void> _loadSavedCookie() async {
    try {
      _sessionCookie = await _secureStorage.read(key: _cookieStorageKey);
    } catch (error) {
      // Requests can still proceed as a guest if secure storage is unavailable.
      debugPrint('Could not read saved session cookie: $error');
    }
  }

  Future<void> _saveCookie(http.Response response) async {
    final rawCookie = response.headers['set-cookie'];
    if (rawCookie == null || rawCookie.isEmpty) return;

    // Flask's session cookie is the first name=value segment before attributes.
    final cookie = rawCookie.split(';').first.trim();
    if (cookie.isEmpty) return;

    _sessionCookie = cookie;
    try {
      await _secureStorage.write(key: _cookieStorageKey, value: cookie);
    } catch (error) {
      debugPrint('Could not persist session cookie securely: $error');
    }
  }

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        if (_sessionCookie != null && _sessionCookie!.isNotEmpty)
          'Cookie': _sessionCookie!,
      };

  Map<String, dynamic> _decodeResponse(http.Response response) {
    dynamic decoded;
    try {
      decoded = jsonDecode(response.body);
    } on FormatException {
      throw Exception(
        'The backend returned invalid JSON (HTTP ${response.statusCode}).',
      );
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

  Future<Map<String, dynamic>> getJson(String path) async {
    await _ensureInitialized();
    try {
      final response = await http
          .get(Uri.parse('$baseUrl$path'), headers: _headers)
          .timeout(const Duration(seconds: 20));
      await _saveCookie(response);
      return _decodeResponse(response);
    } on http.ClientException catch (error) {
      throw Exception('Cannot reach Flask at $baseUrl. '
          'Check the backend, device network and API_BASE_URL. $error');
    }
  }

  Future<Map<String, dynamic>> postJson(
    String path,
    Map<String, dynamic> body,
  ) async {
    await _ensureInitialized();
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl$path'),
            headers: _headers,
            body: jsonEncode(body),
          )
          .timeout(const Duration(seconds: 20));
      await _saveCookie(response);
      return _decodeResponse(response);
    } on http.ClientException catch (error) {
      throw Exception('Cannot reach Flask at $baseUrl. '
          'Check the backend, device network and API_BASE_URL. $error');
    }
  }

  Future<Map<String, dynamic>> deleteJson(String path) async {
    await _ensureInitialized();
    try {
      final response = await http
          .delete(Uri.parse('$baseUrl$path'), headers: _headers)
          .timeout(const Duration(seconds: 20));
      await _saveCookie(response);
      return _decodeResponse(response);
    } on http.ClientException catch (error) {
      throw Exception('Cannot reach Flask at $baseUrl. '
          'Check the backend, device network and API_BASE_URL. $error');
    }
  }

  Future<Map<String, dynamic>> startGuestSession(int duration) async {
    if (![10, 20, 30].contains(duration)) {
      throw ArgumentError('Guest duration must be 10, 20 or 30 minutes.');
    }
    return postJson('/api/guest/start', {'duration': duration});
  }

  Future<Map<String, dynamic>> getGuestStatus() =>
      getJson('/api/guest/status');

  Future<void> endGuestSession() async {
    await postJson('/api/guest/end', {});
    await clearSavedSession();
  }

  Future<void> clearSavedSession() async {
    _sessionCookie = null;
    try {
      await _secureStorage.delete(key: _cookieStorageKey);
    } catch (error) {
      debugPrint('Could not clear saved session cookie: $error');
    }
  }
}
