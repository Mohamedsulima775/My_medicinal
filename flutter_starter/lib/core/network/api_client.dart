import 'dart:convert';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import '../constants/api_constants.dart';
import '../storage/secure_storage.dart';

/// API Client for Dawaii - My_medicinal Backend
///
/// Handles all HTTP communications with proper authentication and error handling.
///
/// Usage:
/// ```dart
/// final client = ApiClient(SecureStorage());
/// await client.initialize();
///
/// // Login
/// final response = await client.post(ApiConstants.login, body: {
///   'mobile': '0500000001',
///   'password': 'password123',
/// });
/// ```
class ApiClient {
  final SecureStorage _storage;
  String? _apiKey;
  String? _apiSecret;

  ApiClient(this._storage);

  /// Initialize client and load stored credentials
  Future<void> initialize() async {
    _apiKey = await _storage.getApiKey();
    _apiSecret = await _storage.getApiSecret();
  }

  /// Update stored credentials after login/register
  void updateCredentials(String apiKey, String apiSecret) {
    _apiKey = apiKey;
    _apiSecret = apiSecret;
  }

  /// Clear credentials on logout
  void clearCredentials() {
    _apiKey = null;
    _apiSecret = null;
  }

  /// Check if user is authenticated
  bool get isAuthenticated => _apiKey != null && _apiSecret != null;

  /// Build headers with optional authentication
  Map<String, String> _buildHeaders({bool requireAuth = true}) {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Accept-Language': 'ar',
    };

    if (requireAuth && isAuthenticated) {
      headers['Authorization'] = 'token $_apiKey:$_apiSecret';
    }

    return headers;
  }

  /// GET request
  Future<ApiResponse> get(
    String endpoint, {
    Map<String, dynamic>? queryParams,
    bool requireAuth = true,
  }) async {
    try {
      final uri = _buildUri(endpoint, queryParams);
      final response = await http.get(
        uri,
        headers: _buildHeaders(requireAuth: requireAuth),
      );
      return _handleResponse(response);
    } catch (e) {
      return ApiResponse.error(_handleError(e));
    }
  }

  /// POST request
  Future<ApiResponse> post(
    String endpoint, {
    Map<String, dynamic>? body,
    Map<String, dynamic>? queryParams,
    bool requireAuth = true,
  }) async {
    try {
      final uri = _buildUri(endpoint, queryParams);
      final response = await http.post(
        uri,
        headers: _buildHeaders(requireAuth: requireAuth),
        body: body != null ? jsonEncode(body) : null,
      );
      return _handleResponse(response);
    } catch (e) {
      return ApiResponse.error(_handleError(e));
    }
  }

  /// Build URI with query parameters
  Uri _buildUri(String endpoint, Map<String, dynamic>? queryParams) {
    final baseUri = Uri.parse('${ApiConstants.baseUrl}$endpoint');

    if (queryParams != null && queryParams.isNotEmpty) {
      return baseUri.replace(
        queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString())),
      );
    }

    return baseUri;
  }

  /// Handle HTTP response
  ApiResponse _handleResponse(http.Response response) {
    final statusCode = response.statusCode;
    final body = response.body.isNotEmpty ? jsonDecode(response.body) : {};

    if (kDebugMode) {
      print('<<< RESPONSE [$statusCode]: $body');
    }

    if (statusCode >= 200 && statusCode < 300) {
      return ApiResponse.success(body);
    } else if (statusCode == 401) {
      clearCredentials();
      return ApiResponse.unauthorized('Session expired. Please login again.');
    } else if (statusCode == 403) {
      return ApiResponse.forbidden(body['message'] ?? 'Access denied');
    } else if (statusCode == 404) {
      return ApiResponse.notFound(body['message'] ?? 'Resource not found');
    } else if (statusCode == 429) {
      return ApiResponse.rateLimited('Too many requests. Please wait.');
    } else {
      return ApiResponse.error(
        body['message'] ?? body['exc'] ?? 'Server error',
      );
    }
  }

  /// Handle exceptions
  String _handleError(dynamic error) {
    if (error is SocketException) {
      return 'No internet connection';
    } else if (error is HttpException) {
      return 'HTTP error occurred';
    } else if (error is FormatException) {
      return 'Invalid response format';
    }
    return error.toString();
  }
}

/// API Response wrapper
class ApiResponse {
  final bool success;
  final int? statusCode;
  final dynamic data;
  final String? error;
  final ApiResponseType type;

  ApiResponse._({
    required this.success,
    this.statusCode,
    this.data,
    this.error,
    required this.type,
  });

  factory ApiResponse.success(dynamic data) {
    return ApiResponse._(
      success: true,
      statusCode: 200,
      data: data,
      type: ApiResponseType.success,
    );
  }

  factory ApiResponse.error(String error) {
    return ApiResponse._(
      success: false,
      error: error,
      type: ApiResponseType.error,
    );
  }

  factory ApiResponse.unauthorized(String error) {
    return ApiResponse._(
      success: false,
      statusCode: 401,
      error: error,
      type: ApiResponseType.unauthorized,
    );
  }

  factory ApiResponse.forbidden(String error) {
    return ApiResponse._(
      success: false,
      statusCode: 403,
      error: error,
      type: ApiResponseType.forbidden,
    );
  }

  factory ApiResponse.notFound(String error) {
    return ApiResponse._(
      success: false,
      statusCode: 404,
      error: error,
      type: ApiResponseType.notFound,
    );
  }

  factory ApiResponse.rateLimited(String error) {
    return ApiResponse._(
      success: false,
      statusCode: 429,
      error: error,
      type: ApiResponseType.rateLimited,
    );
  }

  /// Get the message object from Frappe response
  dynamic get message => data?['message'];

  /// Check if the API operation was successful
  bool get isApiSuccess => message?['success'] == true;

  /// Get error from API response
  String? get apiError => message?['error']?.toString();

  @override
  String toString() {
    if (success) {
      return 'ApiResponse.success: $data';
    }
    return 'ApiResponse.${type.name}: $error';
  }
}

enum ApiResponseType {
  success,
  error,
  unauthorized,
  forbidden,
  notFound,
  rateLimited,
}

/// Example usage:
///
/// ```dart
/// void main() async {
///   final storage = SecureStorage();
///   final client = ApiClient(storage);
///   await client.initialize();
///
///   // Login
///   final loginResponse = await client.post(
///     ApiConstants.login,
///     body: {'mobile': '0500000001', 'password': 'password'},
///     requireAuth: false,
///   );
///
///   if (loginResponse.isApiSuccess) {
///     final apiKey = loginResponse.message['api_key'];
///     final apiSecret = loginResponse.message['api_secret'];
///     client.updateCredentials(apiKey, apiSecret);
///     await storage.saveAuthTokens(apiKey: apiKey, apiSecret: apiSecret, ...);
///   }
///
///   // Get medications (authenticated)
///   final medsResponse = await client.get(ApiConstants.getPatientMedications);
///   if (medsResponse.isApiSuccess) {
///     final medications = medsResponse.message['medications'];
///   }
/// }
/// ```
