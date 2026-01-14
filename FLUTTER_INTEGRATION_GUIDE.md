# دليل ربط Flutter/Android مع My_medicinal API
## Flutter Integration Guide for Dawaii

---

## المشكلة الحالية (Current Issue)

التطبيق يستخدم APIs تجريبية بدلاً من API الخاص بـ Dawaii:
```
fakestoreapi.com     ❌ API تجريبي
dummyapi.online      ❌ API تجريبي
```

**الحل:** استخدام `my_medicinal` API endpoints:
```
/api/method/my_medicinal.api.*   ✅ API الصحيح
```

---

## 1. إعداد الثوابت (API Constants)

### `lib/core/constants/api_constants.dart`

```dart
class ApiConstants {
  // ==========================================
  // Base Configuration
  // ==========================================

  // Development
  static const String devBaseUrl = 'http://localhost:8000';

  // Production
  static const String prodBaseUrl = 'https://your-production-server.com';

  // Current environment
  static const bool isProduction = false;

  static String get baseUrl => isProduction ? prodBaseUrl : devBaseUrl;

  // API Prefix
  static const String apiPrefix = '/api/method/my_medicinal';

  // ==========================================
  // Authentication Endpoints
  // ==========================================

  /// تسجيل مريض جديد
  /// POST - Body: {mobile, full_name, password, email?, date_of_birth?, gender?, blood_group?}
  static String get register => '$apiPrefix.api.patient.register';

  /// تسجيل الدخول
  /// POST - Body: {mobile, password}
  static String get login => '$apiPrefix.api.patient.login';

  /// الملف الشخصي
  /// GET - Headers: Authorization
  static String get getProfile => '$apiPrefix.api.patient.get_profile';

  /// تحديث الملف الشخصي
  /// POST - Body: {full_name?, email?, date_of_birth?, gender?, blood_group?, allergies?, chronic_diseases?}
  static String get updateProfile => '$apiPrefix.api.patient.update_profile';

  /// تجديد التوكن
  /// POST - Headers: Authorization (old token)
  static String get refreshToken => '$apiPrefix.api.patient.refresh_token';

  // ==========================================
  // Medication Endpoints - الأدوية
  // ==========================================

  /// جلب أدوية المريض
  /// GET - Headers: Authorization
  static String get getPatientMedications => '$apiPrefix.api.medication.get_patient_medications';

  /// جلب الأدوية المستحقة الآن
  /// GET - Headers: Authorization
  static String get getMedicationsDue => '$apiPrefix.api.medication_schedule.get_medications_due';

  /// إضافة دواء جديد
  /// POST - Body: {medication_name, dosage, frequency, times[], stock?, color?}
  static String get addMedication => '$apiPrefix.api.medication.add_medication';

  /// تسجيل تناول الدواء
  /// POST - Body: {schedule_id, status: "Taken"|"Missed"|"Skipped", taken_time?}
  static String get logMedicationTaken => '$apiPrefix.api.medication.log_medication_taken';

  /// تحديث مخزون الدواء
  /// POST - Body: {schedule_id, new_stock}
  static String get updateStock => '$apiPrefix.api.medication.update_stock';

  /// تنبيهات نفاد المخزون
  /// GET - Headers: Authorization
  static String get getLowStockMedications => '$apiPrefix.api.medication.get_low_stock_medications';

  /// إلغاء تفعيل الدواء
  /// POST - Body: {schedule_id}
  static String get deactivateMedication => '$apiPrefix.api.medication.deactivate_medication';

  // ==========================================
  // Consultation Endpoints - الاستشارات
  // ==========================================

  /// إنشاء استشارة جديدة
  /// POST - Body: {provider_id, subject, message, priority?}
  static String get createConsultation => '$apiPrefix.api.consultation.create_consultation';

  /// جلب استشاراتي
  /// GET - Query: ?status=&limit=20&offset=0
  static String get getMyConsultations => '$apiPrefix.api.consultation.get_my_consultations';

  /// تفاصيل استشارة
  /// GET - Query: ?consultation_id=XXX
  static String get getConsultationDetails => '$apiPrefix.api.consultation.get_consultation_details';

  /// إرسال رسالة في استشارة
  /// POST - Body: {consultation_id, message}
  static String get sendMessage => '$apiPrefix.api.consultation.send_message';

  /// جلب رسائل استشارة
  /// GET - Query: ?consultation_id=XXX
  static String get getMessages => '$apiPrefix.api.consultation.get_messages';

  // ==========================================
  // Product/Pharmacy Endpoints - المنتجات
  // ==========================================

  /// جلب المنتجات (بدون مصادقة)
  /// GET - Query: ?category=&limit=20&offset=0
  static String get getProducts => '$apiPrefix.api.product.get_products';

  /// البحث في المنتجات
  /// GET - Query: ?query=XXX
  static String get searchProducts => '$apiPrefix.api.product.search_products';

  /// جلب التصنيفات
  /// GET
  static String get getCategories => '$apiPrefix.api.product.get_categories';

  /// تفاصيل منتج
  /// GET - Query: ?item_code=XXX
  static String get getProductDetails => '$apiPrefix.api.product.get_product_details';

  // ==========================================
  // Order Endpoints - الطلبات
  // ==========================================

  /// إنشاء طلب
  /// POST - Body: {items[], delivery_address, payment_method}
  static String get createOrder => '$apiPrefix.api.order.create_order';

  /// جلب طلباتي
  /// GET - Query: ?status=&limit=20&offset=0
  static String get getMyOrders => '$apiPrefix.api.order.get_my_orders';

  // ==========================================
  // Prescription Endpoints - الوصفات الطبية
  // ==========================================

  /// جلب وصفاتي الطبية
  /// GET - Headers: Authorization
  static String get getMyPrescriptions => '$apiPrefix.api.prescription.get_my_prescriptions';

  /// تفاصيل وصفة طبية
  /// GET - Query: ?prescription_id=XXX
  static String get getPrescriptionDetails => '$apiPrefix.api.prescription.get_prescription_details';

  // ==========================================
  // Notification Endpoints - الإشعارات
  // ==========================================

  /// تسجيل جهاز FCM
  /// POST - Body: {fcm_token, device_type: "android"|"ios", device_id}
  static String get registerDevice => '$apiPrefix.my_medicinal.notifications.register_device';

  /// جلب إشعاراتي
  /// GET - Query: ?limit=20&offset=0
  static String get getMyNotifications => '$apiPrefix.my_medicinal.notifications.get_my_notifications';

  /// تحديد إشعار كمقروء
  /// POST - Body: {notification_id}
  static String get markNotificationRead => '$apiPrefix.my_medicinal.notifications.mark_notification_read';

  // ==========================================
  // Helper Methods
  // ==========================================

  /// Build full URL
  static String buildUrl(String endpoint) => '$baseUrl$endpoint';
}
```

---

## 2. إعداد HTTP Client مع Dio

### `lib/core/network/api_client.dart`

```dart
import 'package:dio/dio.dart';
import '../constants/api_constants.dart';
import '../storage/secure_storage.dart';

class ApiClient {
  late final Dio _dio;
  final SecureStorage _storage;

  ApiClient(this._storage) {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConstants.baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Language': 'ar',
      },
    ));

    _dio.interceptors.addAll([
      _AuthInterceptor(_storage),
      _LoggingInterceptor(),
    ]);
  }

  // GET Request
  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    return _dio.get<T>(path, queryParameters: queryParameters);
  }

  // POST Request
  Future<Response<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) async {
    return _dio.post<T>(path, data: data, queryParameters: queryParameters);
  }
}

// Auth Interceptor
class _AuthInterceptor extends Interceptor {
  final SecureStorage _storage;

  _AuthInterceptor(this._storage);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    // Skip auth for public endpoints
    final publicEndpoints = [
      ApiConstants.register,
      ApiConstants.login,
      ApiConstants.getProducts,
      ApiConstants.searchProducts,
      ApiConstants.getCategories,
    ];

    final isPublic = publicEndpoints.any((e) => options.path.contains(e));

    if (!isPublic) {
      final apiKey = await _storage.getApiKey();
      final apiSecret = await _storage.getApiSecret();

      if (apiKey != null && apiSecret != null) {
        options.headers['Authorization'] = 'token $apiKey:$apiSecret';
      }
    }

    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    // Handle 401 - Token expired
    if (err.response?.statusCode == 401) {
      // Try to refresh token
      try {
        final refreshed = await _refreshToken();
        if (refreshed) {
          // Retry original request
          final response = await _dio.fetch(err.requestOptions);
          return handler.resolve(response);
        }
      } catch (e) {
        // Logout user
        await _storage.clearAll();
      }
    }
    handler.next(err);
  }

  Future<bool> _refreshToken() async {
    // Implement token refresh logic
    return false;
  }
}

// Logging Interceptor
class _LoggingInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    print('>>> REQUEST: ${options.method} ${options.uri}');
    print('>>> HEADERS: ${options.headers}');
    print('>>> DATA: ${options.data}');
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    print('<<< RESPONSE [${response.statusCode}]: ${response.data}');
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    print('!!! ERROR: ${err.message}');
    print('!!! RESPONSE: ${err.response?.data}');
    handler.next(err);
  }
}
```

---

## 3. إعداد التخزين الآمن

### `lib/core/storage/secure_storage.dart`

```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorage {
  final FlutterSecureStorage _storage = const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
  );

  // Keys
  static const _keyApiKey = 'api_key';
  static const _keyApiSecret = 'api_secret';
  static const _keyPatientId = 'patient_id';
  static const _keyExpiresAt = 'expires_at';
  static const _keyFcmToken = 'fcm_token';

  // Save auth tokens
  Future<void> saveAuthTokens({
    required String apiKey,
    required String apiSecret,
    required String patientId,
    required int expiresAt,
  }) async {
    await Future.wait([
      _storage.write(key: _keyApiKey, value: apiKey),
      _storage.write(key: _keyApiSecret, value: apiSecret),
      _storage.write(key: _keyPatientId, value: patientId),
      _storage.write(key: _keyExpiresAt, value: expiresAt.toString()),
    ]);
  }

  // Get tokens
  Future<String?> getApiKey() => _storage.read(key: _keyApiKey);
  Future<String?> getApiSecret() => _storage.read(key: _keyApiSecret);
  Future<String?> getPatientId() => _storage.read(key: _keyPatientId);

  // Check if logged in
  Future<bool> isLoggedIn() async {
    final apiKey = await getApiKey();
    final expiresAt = await _storage.read(key: _keyExpiresAt);

    if (apiKey == null || expiresAt == null) return false;

    final expiry = int.tryParse(expiresAt) ?? 0;
    return DateTime.now().millisecondsSinceEpoch < expiry;
  }

  // Clear all
  Future<void> clearAll() => _storage.deleteAll();

  // FCM Token
  Future<void> saveFcmToken(String token) =>
    _storage.write(key: _keyFcmToken, value: token);
  Future<String?> getFcmToken() => _storage.read(key: _keyFcmToken);
}
```

---

## 4. نماذج البيانات (Models)

### `lib/data/models/auth_response.dart`

```dart
class AuthResponse {
  final bool success;
  final String? apiKey;
  final String? apiSecret;
  final String? patientId;
  final int? expiresAt;
  final String? error;

  AuthResponse({
    required this.success,
    this.apiKey,
    this.apiSecret,
    this.patientId,
    this.expiresAt,
    this.error,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    final message = json['message'] ?? json;
    return AuthResponse(
      success: message['success'] ?? false,
      apiKey: message['api_key'],
      apiSecret: message['api_secret'],
      patientId: message['patient_id'],
      expiresAt: message['expires_at'],
      error: message['error'],
    );
  }
}
```

### `lib/data/models/medication.dart`

```dart
class Medication {
  final String id;
  final String medicationName;
  final String? scientificName;
  final String dosage;
  final String frequency;
  final int currentStock;
  final int? reorderLevel;
  final String? color;
  final bool isActive;
  final List<MedicationTime> times;
  final String? depletionDate;

  Medication({
    required this.id,
    required this.medicationName,
    this.scientificName,
    required this.dosage,
    required this.frequency,
    required this.currentStock,
    this.reorderLevel,
    this.color,
    required this.isActive,
    required this.times,
    this.depletionDate,
  });

  factory Medication.fromJson(Map<String, dynamic> json) {
    return Medication(
      id: json['name'] ?? json['id'],
      medicationName: json['medication_name'],
      scientificName: json['scientific_name'],
      dosage: json['dosage'],
      frequency: json['frequency'],
      currentStock: json['current_stock'] ?? 0,
      reorderLevel: json['reorder_level'],
      color: json['color'],
      isActive: json['is_active'] == 1,
      times: (json['times'] as List? ?? [])
          .map((t) => MedicationTime.fromJson(t))
          .toList(),
      depletionDate: json['estimated_depletion_date'],
    );
  }
}

class MedicationTime {
  final String time; // HH:mm
  final String? beforeAfterMeal;
  final String? notes;

  MedicationTime({
    required this.time,
    this.beforeAfterMeal,
    this.notes,
  });

  factory MedicationTime.fromJson(Map<String, dynamic> json) {
    return MedicationTime(
      time: json['time'],
      beforeAfterMeal: json['before_after_meal'],
      notes: json['notes'],
    );
  }

  Map<String, dynamic> toJson() => {
    'time': time,
    'before_after_meal': beforeAfterMeal,
    'notes': notes,
  };
}
```

---

## 5. المستودعات (Repositories)

### `lib/data/repositories/auth_repository.dart`

```dart
import '../models/auth_response.dart';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../core/storage/secure_storage.dart';

class AuthRepository {
  final ApiClient _client;
  final SecureStorage _storage;

  AuthRepository(this._client, this._storage);

  /// تسجيل مريض جديد
  Future<AuthResponse> register({
    required String mobile,
    required String fullName,
    required String password,
    String? email,
    String? dateOfBirth,
    String? gender,
    String? bloodGroup,
  }) async {
    try {
      final response = await _client.post(
        ApiConstants.register,
        data: {
          'mobile': mobile, // Format: 05XXXXXXXX
          'full_name': fullName,
          'password': password,
          if (email != null) 'email': email,
          if (dateOfBirth != null) 'date_of_birth': dateOfBirth,
          if (gender != null) 'gender': gender,
          if (bloodGroup != null) 'blood_group': bloodGroup,
        },
      );

      final authResponse = AuthResponse.fromJson(response.data);

      if (authResponse.success) {
        await _storage.saveAuthTokens(
          apiKey: authResponse.apiKey!,
          apiSecret: authResponse.apiSecret!,
          patientId: authResponse.patientId!,
          expiresAt: authResponse.expiresAt!,
        );
      }

      return authResponse;
    } catch (e) {
      return AuthResponse(success: false, error: e.toString());
    }
  }

  /// تسجيل الدخول
  Future<AuthResponse> login({
    required String mobile,
    required String password,
  }) async {
    try {
      final response = await _client.post(
        ApiConstants.login,
        data: {
          'mobile': mobile,
          'password': password,
        },
      );

      final authResponse = AuthResponse.fromJson(response.data);

      if (authResponse.success) {
        await _storage.saveAuthTokens(
          apiKey: authResponse.apiKey!,
          apiSecret: authResponse.apiSecret!,
          patientId: authResponse.patientId!,
          expiresAt: authResponse.expiresAt!,
        );
      }

      return authResponse;
    } catch (e) {
      return AuthResponse(success: false, error: e.toString());
    }
  }

  /// تسجيل الخروج
  Future<void> logout() async {
    await _storage.clearAll();
  }

  /// التحقق من تسجيل الدخول
  Future<bool> isLoggedIn() => _storage.isLoggedIn();
}
```

### `lib/data/repositories/medication_repository.dart`

```dart
import '../models/medication.dart';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';

class MedicationRepository {
  final ApiClient _client;

  MedicationRepository(this._client);

  /// جلب أدوية المريض
  Future<List<Medication>> getPatientMedications() async {
    final response = await _client.get(ApiConstants.getPatientMedications);
    final data = response.data['message'];

    if (data['success'] == true) {
      return (data['medications'] as List)
          .map((m) => Medication.fromJson(m))
          .toList();
    }

    throw Exception(data['error'] ?? 'Failed to fetch medications');
  }

  /// جلب الأدوية المستحقة الآن
  Future<List<Medication>> getMedicationsDue() async {
    final response = await _client.get(ApiConstants.getMedicationsDue);
    final data = response.data['message'];

    if (data['success'] == true) {
      return (data['medications'] as List)
          .map((m) => Medication.fromJson(m))
          .toList();
    }

    throw Exception(data['error'] ?? 'Failed to fetch due medications');
  }

  /// إضافة دواء جديد
  Future<Medication> addMedication({
    required String medicationName,
    required String dosage,
    required String frequency,
    required List<MedicationTime> times,
    int? stock,
    String? color,
  }) async {
    final response = await _client.post(
      ApiConstants.addMedication,
      data: {
        'medication_name': medicationName,
        'dosage': dosage,
        'frequency': frequency,
        'times': times.map((t) => t.toJson()).toList(),
        if (stock != null) 'stock': stock,
        if (color != null) 'color': color,
      },
    );

    final data = response.data['message'];

    if (data['success'] == true) {
      return Medication.fromJson(data['medication']);
    }

    throw Exception(data['error'] ?? 'Failed to add medication');
  }

  /// تسجيل تناول الدواء
  Future<void> logMedicationTaken({
    required String scheduleId,
    required String status, // "Taken", "Missed", "Skipped"
    String? takenTime,
  }) async {
    final response = await _client.post(
      ApiConstants.logMedicationTaken,
      data: {
        'schedule_id': scheduleId,
        'status': status,
        if (takenTime != null) 'taken_time': takenTime,
      },
    );

    final data = response.data['message'];

    if (data['success'] != true) {
      throw Exception(data['error'] ?? 'Failed to log medication');
    }
  }

  /// تحديث المخزون
  Future<void> updateStock({
    required String scheduleId,
    required int newStock,
  }) async {
    final response = await _client.post(
      ApiConstants.updateStock,
      data: {
        'schedule_id': scheduleId,
        'new_stock': newStock,
      },
    );

    final data = response.data['message'];

    if (data['success'] != true) {
      throw Exception(data['error'] ?? 'Failed to update stock');
    }
  }

  /// جلب تنبيهات نفاد المخزون
  Future<List<Medication>> getLowStockMedications() async {
    final response = await _client.get(ApiConstants.getLowStockMedications);
    final data = response.data['message'];

    if (data['success'] == true) {
      return (data['medications'] as List)
          .map((m) => Medication.fromJson(m))
          .toList();
    }

    throw Exception(data['error'] ?? 'Failed to fetch low stock medications');
  }
}
```

---

## 6. إعداد Firebase للإشعارات

### `lib/core/services/fcm_service.dart`

```dart
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import '../network/api_client.dart';
import '../constants/api_constants.dart';
import '../storage/secure_storage.dart';

class FCMService {
  final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();
  final ApiClient _client;
  final SecureStorage _storage;

  FCMService(this._client, this._storage);

  Future<void> initialize() async {
    // Request permission
    await _messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    // Initialize local notifications
    await _initLocalNotifications();

    // Get FCM token and register
    final token = await _messaging.getToken();
    if (token != null) {
      await _registerDevice(token);
    }

    // Listen for token refresh
    _messaging.onTokenRefresh.listen(_registerDevice);

    // Handle foreground messages
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

    // Handle background/terminated messages
    FirebaseMessaging.onMessageOpenedApp.listen(_handleMessageClick);
  }

  Future<void> _initLocalNotifications() async {
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings();

    await _localNotifications.initialize(
      const InitializationSettings(
        android: androidSettings,
        iOS: iosSettings,
      ),
      onDidReceiveNotificationResponse: (details) {
        // Handle notification click
      },
    );
  }

  Future<void> _registerDevice(String token) async {
    try {
      await _storage.saveFcmToken(token);

      await _client.post(
        ApiConstants.registerDevice,
        data: {
          'fcm_token': token,
          'device_type': 'android',
          'device_id': await _getDeviceId(),
        },
      );
    } catch (e) {
      print('Failed to register device: $e');
    }
  }

  Future<String> _getDeviceId() async {
    // Implement device ID retrieval
    return 'device_id';
  }

  void _handleForegroundMessage(RemoteMessage message) {
    final notification = message.notification;
    final data = message.data;

    if (notification != null) {
      _localNotifications.show(
        notification.hashCode,
        notification.title,
        notification.body,
        NotificationDetails(
          android: AndroidNotificationDetails(
            'dawaii_channel',
            'Dawaii Notifications',
            importance: Importance.high,
            priority: Priority.high,
            icon: '@mipmap/ic_launcher',
          ),
        ),
        payload: data['type'],
      );
    }
  }

  void _handleMessageClick(RemoteMessage message) {
    final type = message.data['type'];

    switch (type) {
      case 'medication_reminder':
        // Navigate to medication screen
        break;
      case 'consultation_update':
        // Navigate to consultation
        break;
      case 'prescription_ready':
        // Navigate to prescriptions
        break;
    }
  }
}
```

---

## 7. حل مشكلة CORS لـ Flutter Web

### الخيار 1: استخدام Proxy (للتطوير)

قم بتشغيل Flutter Web مع proxy:

```bash
# Create a proxy server with cors-anywhere or similar
# Or use the built-in Flutter Web proxy

flutter run -d chrome --web-browser-flag "--disable-web-security"
```

### الخيار 2: تحديث إعدادات الخادم

تم تحديث `hooks.py` لدعم Flutter Web ports:

```python
# في hooks.py - تم إضافة دعم لـ Flutter ports
allow_cors = [
    "http://localhost:56858",  # Flutter Web port
    "http://localhost:5000",
    "http://localhost:8080",
    # ... المزيد
]
```

### الخيار 3: إنشاء Proxy Middleware في Flutter

```dart
// lib/core/network/cors_proxy.dart
class CorsProxy {
  static String proxyUrl(String url) {
    // For development only
    if (kIsWeb && !kReleaseMode) {
      return 'https://cors-anywhere.herokuapp.com/$url';
    }
    return url;
  }
}
```

---

## 8. هيكل المشروع المقترح

```
dawaii_flutter/
├── lib/
│   ├── main.dart
│   ├── app.dart
│   ├── core/
│   │   ├── constants/
│   │   │   └── api_constants.dart
│   │   ├── network/
│   │   │   ├── api_client.dart
│   │   │   └── api_exceptions.dart
│   │   ├── storage/
│   │   │   └── secure_storage.dart
│   │   ├── services/
│   │   │   └── fcm_service.dart
│   │   └── di/
│   │       └── injection.dart
│   ├── data/
│   │   ├── models/
│   │   │   ├── auth_response.dart
│   │   │   ├── patient.dart
│   │   │   ├── medication.dart
│   │   │   ├── consultation.dart
│   │   │   └── product.dart
│   │   └── repositories/
│   │       ├── auth_repository.dart
│   │       ├── medication_repository.dart
│   │       ├── consultation_repository.dart
│   │       └── product_repository.dart
│   ├── presentation/
│   │   ├── auth/
│   │   │   ├── login_screen.dart
│   │   │   └── register_screen.dart
│   │   ├── home/
│   │   │   └── home_screen.dart
│   │   ├── medications/
│   │   │   ├── medications_screen.dart
│   │   │   └── add_medication_screen.dart
│   │   ├── consultations/
│   │   │   └── consultations_screen.dart
│   │   └── profile/
│   │       └── profile_screen.dart
│   └── l10n/
│       ├── app_ar.arb
│       └── app_en.arb
├── android/
├── ios/
├── web/
└── pubspec.yaml
```

---

## 9. Dependencies المطلوبة

```yaml
# pubspec.yaml
dependencies:
  flutter:
    sdk: flutter

  # Networking
  dio: ^5.4.0

  # State Management
  flutter_bloc: ^8.1.3

  # Storage
  flutter_secure_storage: ^9.0.0
  shared_preferences: ^2.2.2

  # Firebase
  firebase_core: ^2.24.2
  firebase_messaging: ^14.7.10

  # Local Notifications
  flutter_local_notifications: ^16.3.0

  # Dependency Injection
  get_it: ^7.6.4
  injectable: ^2.3.2

  # Utils
  intl: ^0.19.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  injectable_generator: ^2.4.1
  build_runner: ^2.4.7
```

---

## 10. خطوات التنفيذ

| # | الخطوة | الأمر |
|---|--------|-------|
| 1 | إنشاء المشروع | `flutter create dawaii_app` |
| 2 | إضافة Dependencies | `flutter pub get` |
| 3 | إعداد Firebase | `flutterfire configure` |
| 4 | إنشاء API Constants | كما في القسم 1 |
| 5 | إنشاء ApiClient | كما في القسم 2 |
| 6 | إنشاء Models | كما في القسم 4 |
| 7 | إنشاء Repositories | كما في القسم 5 |
| 8 | بناء UI | وفقًا للتصميم |
| 9 | اختبار API | استخدام Postman أولاً |
| 10 | تشغيل التطبيق | `flutter run` |

---

## 11. اختبار API باستخدام cURL

```bash
# تسجيل مريض جديد
curl -X POST http://localhost:8000/api/method/my_medicinal.api.patient.register \
  -H "Content-Type: application/json" \
  -d '{
    "mobile": "0500000001",
    "full_name": "أحمد محمد",
    "password": "#@!Gqwe"
  }'

# تسجيل الدخول
curl -X POST http://localhost:8000/api/method/my_medicinal.api.patient.login \
  -H "Content-Type: application/json" \
  -d '{
    "mobile": "0500000001",
    "password": "#@!Gqwe"
  }'

# جلب الأدوية (مع التوكن)
curl -X GET http://localhost:8000/api/method/my_medicinal.api.medication.get_patient_medications \
  -H "Authorization: token API_KEY:API_SECRET"
```

---

**ملاحظة مهمة:** تأكد من تغيير جميع الـ URLs من `fakestoreapi.com` و `dummyapi.online` إلى API الخاص بـ Dawaii كما هو موضح أعلاه.
