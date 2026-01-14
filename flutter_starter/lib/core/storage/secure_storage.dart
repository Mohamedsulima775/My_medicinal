import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Secure Storage for Dawaii App
///
/// Handles secure storage of authentication tokens and user data.
/// Uses flutter_secure_storage for encrypted storage on device.
///
/// Usage:
/// ```dart
/// final storage = SecureStorage();
///
/// // Save tokens after login
/// await storage.saveAuthTokens(
///   apiKey: 'xxx',
///   apiSecret: 'yyy',
///   patientId: 'PT-00001',
///   expiresAt: DateTime.now().add(Duration(days: 90)).millisecondsSinceEpoch,
/// );
///
/// // Check if logged in
/// if (await storage.isLoggedIn()) {
///   final apiKey = await storage.getApiKey();
/// }
/// ```
class SecureStorage {
  // Use encrypted shared preferences on Android
  final FlutterSecureStorage _storage = const FlutterSecureStorage(
    aOptions: AndroidOptions(
      encryptedSharedPreferences: true,
    ),
    iOptions: IOSOptions(
      accessibility: KeychainAccessibility.first_unlock_this_device,
    ),
  );

  // Storage Keys
  static const String _keyApiKey = 'dawaii_api_key';
  static const String _keyApiSecret = 'dawaii_api_secret';
  static const String _keyPatientId = 'dawaii_patient_id';
  static const String _keyPatientName = 'dawaii_patient_name';
  static const String _keyExpiresAt = 'dawaii_expires_at';
  static const String _keyFcmToken = 'dawaii_fcm_token';
  static const String _keyDeviceId = 'dawaii_device_id';
  static const String _keyIsFirstLaunch = 'dawaii_is_first_launch';
  static const String _keyLanguage = 'dawaii_language';

  // ============================================================
  // Authentication Token Management
  // ============================================================

  /// Save authentication tokens after successful login/register
  Future<void> saveAuthTokens({
    required String apiKey,
    required String apiSecret,
    required String patientId,
    required int expiresAt,
    String? patientName,
  }) async {
    await Future.wait([
      _storage.write(key: _keyApiKey, value: apiKey),
      _storage.write(key: _keyApiSecret, value: apiSecret),
      _storage.write(key: _keyPatientId, value: patientId),
      _storage.write(key: _keyExpiresAt, value: expiresAt.toString()),
      if (patientName != null)
        _storage.write(key: _keyPatientName, value: patientName),
    ]);
  }

  /// Get API Key
  Future<String?> getApiKey() => _storage.read(key: _keyApiKey);

  /// Get API Secret
  Future<String?> getApiSecret() => _storage.read(key: _keyApiSecret);

  /// Get Patient ID
  Future<String?> getPatientId() => _storage.read(key: _keyPatientId);

  /// Get Patient Name
  Future<String?> getPatientName() => _storage.read(key: _keyPatientName);

  /// Get token expiration timestamp
  Future<int?> getExpiresAt() async {
    final value = await _storage.read(key: _keyExpiresAt);
    return value != null ? int.tryParse(value) : null;
  }

  /// Check if user is logged in with valid token
  Future<bool> isLoggedIn() async {
    final apiKey = await getApiKey();
    final expiresAt = await getExpiresAt();

    if (apiKey == null || expiresAt == null) {
      return false;
    }

    // Check if token is expired
    final now = DateTime.now().millisecondsSinceEpoch;
    return now < expiresAt;
  }

  /// Check if token is about to expire (within 7 days)
  Future<bool> isTokenExpiringSoon() async {
    final expiresAt = await getExpiresAt();
    if (expiresAt == null) return false;

    final now = DateTime.now().millisecondsSinceEpoch;
    final sevenDaysInMs = 7 * 24 * 60 * 60 * 1000;

    return (expiresAt - now) < sevenDaysInMs;
  }

  /// Clear authentication data (logout)
  Future<void> clearAuth() async {
    await Future.wait([
      _storage.delete(key: _keyApiKey),
      _storage.delete(key: _keyApiSecret),
      _storage.delete(key: _keyPatientId),
      _storage.delete(key: _keyPatientName),
      _storage.delete(key: _keyExpiresAt),
    ]);
  }

  // ============================================================
  // FCM Token Management
  // ============================================================

  /// Save FCM token
  Future<void> saveFcmToken(String token) =>
      _storage.write(key: _keyFcmToken, value: token);

  /// Get FCM token
  Future<String?> getFcmToken() => _storage.read(key: _keyFcmToken);

  /// Save device ID
  Future<void> saveDeviceId(String deviceId) =>
      _storage.write(key: _keyDeviceId, value: deviceId);

  /// Get device ID
  Future<String?> getDeviceId() => _storage.read(key: _keyDeviceId);

  // ============================================================
  // App Settings
  // ============================================================

  /// Check if this is first app launch
  Future<bool> isFirstLaunch() async {
    final value = await _storage.read(key: _keyIsFirstLaunch);
    return value == null;
  }

  /// Mark first launch as completed
  Future<void> setFirstLaunchCompleted() =>
      _storage.write(key: _keyIsFirstLaunch, value: 'false');

  /// Get saved language preference
  Future<String> getLanguage() async {
    final value = await _storage.read(key: _keyLanguage);
    return value ?? 'ar'; // Default to Arabic
  }

  /// Save language preference
  Future<void> saveLanguage(String languageCode) =>
      _storage.write(key: _keyLanguage, value: languageCode);

  // ============================================================
  // Clear All Data
  // ============================================================

  /// Clear all stored data (for logout or app reset)
  Future<void> clearAll() => _storage.deleteAll();

  // ============================================================
  // Debug Helpers
  // ============================================================

  /// Print all stored keys (debug only)
  Future<void> debugPrintAll() async {
    final all = await _storage.readAll();
    print('=== Secure Storage Contents ===');
    all.forEach((key, value) {
      // Mask sensitive values
      if (key.contains('secret') || key.contains('key')) {
        print('$key: ${value?.substring(0, 8)}...');
      } else {
        print('$key: $value');
      }
    });
    print('==============================');
  }
}
