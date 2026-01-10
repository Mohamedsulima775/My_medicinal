# دليل ربط تطبيق Flutter (Dawaii_Android) مع Frappe (My_medicinal)

## 📋 نظرة عامة

هذا الدليل يشرح كيفية ربط تطبيق Flutter مع خادم Frappe عندما تكون البيئتان على جهازين منفصلين.

### البنية الحالية:
- **Flutter App**: Dawaii_Android على جهاز المطور
- **Frappe Backend**: My_medicinal على جهاز/خادم آخر

---

## 🔧 الجزء الأول: إعداد خادم Frappe

### 1. إعدادات الشبكة

#### أ) تحديد IP Address للخادم

على جهاز Frappe، قم بتشغيل:

```bash
# للحصول على IP Address
ip addr show

# أو
hostname -I
```

ستحصل على IP مثل: `192.168.1.100` أو `10.0.0.5`

#### ب) التأكد من تشغيل Frappe على جميع واجهات الشبكة

افتح ملف `sites/common_site_config.json` وأضف:

```json
{
  "allow_cors": "*",
  "host_name": "http://192.168.1.100:8000",
  "webserver_port": 8000,
  "socketio_port": 9000,
  "serve_default_site": true,
  "allow_tests": true
}
```

**ملاحظة**: استبدل `192.168.1.100` بـ IP الفعلي لخادمك

#### ج) تشغيل Frappe للاستماع على جميع الواجهات

```bash
# بدلاً من
bench start

# استخدم
bench start --host 0.0.0.0
```

### 2. إعدادات CORS (Cross-Origin Resource Sharing)

#### أ) تحديث ملف `.env`

قم بإنشاء ملف `.env` في مجلد المشروع (إذا لم يكن موجوداً):

```bash
# في مجلد My_medicinal
cp .env.example .env
```

ثم حدث إعدادات CORS:

```bash
# CORS Allowed Origins - أضف IP للأجهزة التي ستتصل
ALLOWED_CORS_ORIGINS=http://localhost:3000,http://192.168.1.100:8000,http://192.168.1.101:3000

# أو للسماح بجميع الاتصالات في التطوير (غير آمن للإنتاج!)
ALLOWED_CORS_ORIGINS=*
```

#### ب) التحقق من إعدادات CORS في hooks.py

الإعدادات موجودة بالفعل في `my_medicinal/hooks.py` (السطر 326-327):

```python
_cors_origins = os.getenv("ALLOWED_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:8000")
allow_cors = [origin.strip() for origin in _cors_origins.split(",") if origin.strip()]
```

### 3. إعدادات Firewall

#### أ) السماح بالمنافذ المطلوبة

```bash
# إذا كنت تستخدم UFW على Ubuntu
sudo ufw allow 8000/tcp  # Frappe Web
sudo ufw allow 9000/tcp  # SocketIO
sudo ufw reload

# إذا كنت تستخدم firewalld على CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=9000/tcp
sudo firewall-cmd --reload
```

### 4. اختبار الاتصال

#### من جهاز Flutter، جرّب:

```bash
# اختبار الاتصال
ping 192.168.1.100

# اختبار المنفذ
curl http://192.168.1.100:8000/api/method/ping
```

يجب أن ترى: `{"message": "pong"}`

---

## 📱 الجزء الثاني: إعداد Flutter

### 1. بنية المشروع المقترحة

```
Dawaii_Android/
├── lib/
│   ├── services/
│   │   ├── api_client.dart        # HTTP Client
│   │   ├── auth_service.dart      # Authentication
│   │   └── api_config.dart        # Configuration
│   ├── models/
│   │   ├── patient.dart
│   │   ├── medication.dart
│   │   └── api_response.dart
│   └── main.dart
```

### 2. ملف التكوين (api_config.dart)

```dart
class ApiConfig {
  // استبدل بـ IP الفعلي لخادم Frappe
  static const String baseUrl = 'http://192.168.1.100:8000';

  // API Endpoints
  static const String apiBase = '/api/method/my_medicinal.my_medicinal.api';

  // Endpoints
  static const String register = '$apiBase.patient.register';
  static const String login = '$apiBase.patient.login';
  static const String getProfile = '$apiBase.patient.get_profile';
  static const String updateProfile = '$apiBase.patient.update_profile';
  static const String getMedications = '$apiBase.medication.get_list';
  static const String addMedication = '$apiBase.medication.add';
  static const String logMedication = '$apiBase.medication.log_taken';

  // Timeout settings
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
}
```

### 3. API Client (api_client.dart)

```dart
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'api_config.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  late Dio _dio;
  String? _authToken;

  factory ApiClient() {
    return _instance;
  }

  ApiClient._internal() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConfig.baseUrl,
      connectTimeout: ApiConfig.connectionTimeout,
      receiveTimeout: ApiConfig.receiveTimeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // Add interceptors
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        // Add auth token if available
        if (_authToken != null) {
          options.headers['Authorization'] = 'token $_authToken';
        }
        print('Request: ${options.method} ${options.path}');
        return handler.next(options);
      },
      onResponse: (response, handler) {
        print('Response: ${response.statusCode} ${response.data}');
        return handler.next(response);
      },
      onError: (DioException error, handler) {
        print('Error: ${error.message}');
        _handleError(error);
        return handler.next(error);
      },
    ));

    _loadToken();
  }

  // Load saved token
  Future<void> _loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _authToken = prefs.getString('auth_token');
  }

  // Save token
  Future<void> saveToken(String token) async {
    _authToken = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }

  // Clear token
  Future<void> clearToken() async {
    _authToken = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }

  // GET request
  Future<Response> get(String endpoint, {Map<String, dynamic>? params}) async {
    try {
      return await _dio.get(endpoint, queryParameters: params);
    } catch (e) {
      rethrow;
    }
  }

  // POST request
  Future<Response> post(String endpoint, {Map<String, dynamic>? data}) async {
    try {
      return await _dio.post(endpoint, data: data);
    } catch (e) {
      rethrow;
    }
  }

  // PUT request
  Future<Response> put(String endpoint, {Map<String, dynamic>? data}) async {
    try {
      return await _dio.put(endpoint, data: data);
    } catch (e) {
      rethrow;
    }
  }

  // DELETE request
  Future<Response> delete(String endpoint) async {
    try {
      return await _dio.delete(endpoint);
    } catch (e) {
      rethrow;
    }
  }

  // Error handler
  void _handleError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        throw Exception('انتهت مهلة الاتصال. تحقق من اتصالك بالإنترنت.');

      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode;
        if (statusCode == 401) {
          throw Exception('غير مصرح. يرجى تسجيل الدخول مرة أخرى.');
        } else if (statusCode == 403) {
          throw Exception('ممنوع. ليس لديك صلاحية للوصول.');
        } else if (statusCode == 404) {
          throw Exception('غير موجود.');
        } else if (statusCode == 500) {
          throw Exception('خطأ في الخادم.');
        }
        throw Exception('خطأ: ${error.response?.statusMessage}');

      case DioExceptionType.cancel:
        throw Exception('تم إلغاء الطلب.');

      default:
        throw Exception('فشل الاتصال. تحقق من اتصالك بالإنترنت وعنوان IP للخادم.');
    }
  }
}
```

### 4. خدمة المصادقة (auth_service.dart)

```dart
import 'api_client.dart';
import 'api_config.dart';
import '../models/patient.dart';

class AuthService {
  final ApiClient _apiClient = ApiClient();

  // تسجيل مستخدم جديد
  Future<Map<String, dynamic>> register({
    required String patientName,
    required String mobile,
    required String password,
    String? email,
    String? dateOfBirth,
    String? gender,
  }) async {
    try {
      final response = await _apiClient.post(
        ApiConfig.register,
        data: {
          'patient_name': patientName,
          'mobile': mobile,
          'password': password,
          'email': email,
          'date_of_birth': dateOfBirth,
          'gender': gender,
        },
      );

      if (response.data['message']['success'] == true) {
        final token = response.data['message']['token'];
        await _apiClient.saveToken(token);
        return response.data['message'];
      } else {
        throw Exception(response.data['message']['message'] ?? 'فشل التسجيل');
      }
    } catch (e) {
      throw Exception('خطأ في التسجيل: $e');
    }
  }

  // تسجيل الدخول
  Future<Map<String, dynamic>> login({
    required String mobile,
    required String password,
  }) async {
    try {
      final response = await _apiClient.post(
        ApiConfig.login,
        data: {
          'mobile': mobile,
          'password': password,
        },
      );

      if (response.data['message']['success'] == true) {
        final token = response.data['message']['token'];
        await _apiClient.saveToken(token);
        return response.data['message'];
      } else {
        throw Exception(response.data['message']['message'] ?? 'فشل تسجيل الدخول');
      }
    } catch (e) {
      throw Exception('خطأ في تسجيل الدخول: $e');
    }
  }

  // تسجيل الخروج
  Future<void> logout() async {
    await _apiClient.clearToken();
  }

  // الحصول على الملف الشخصي
  Future<Patient> getProfile() async {
    try {
      final response = await _apiClient.get(ApiConfig.getProfile);

      if (response.data['message']['success'] == true) {
        return Patient.fromJson(response.data['message']['patient']);
      } else {
        throw Exception('فشل الحصول على الملف الشخصي');
      }
    } catch (e) {
      throw Exception('خطأ في الحصول على الملف الشخصي: $e');
    }
  }
}
```

### 5. نموذج البيانات (patient.dart)

```dart
class Patient {
  final String patientId;
  final String patientName;
  final String mobile;
  final String email;
  final String? dateOfBirth;
  final String? gender;
  final String? bloodGroup;
  final String? allergies;
  final String? medicalNotes;
  final String status;

  Patient({
    required this.patientId,
    required this.patientName,
    required this.mobile,
    required this.email,
    this.dateOfBirth,
    this.gender,
    this.bloodGroup,
    this.allergies,
    this.medicalNotes,
    required this.status,
  });

  factory Patient.fromJson(Map<String, dynamic> json) {
    return Patient(
      patientId: json['patient_id'],
      patientName: json['patient_name'],
      mobile: json['mobile'],
      email: json['email'],
      dateOfBirth: json['date_of_birth'],
      gender: json['gender'],
      bloodGroup: json['blood_group'],
      allergies: json['allergies'],
      medicalNotes: json['medical_notes'],
      status: json['status'] ?? 'Active',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'patient_id': patientId,
      'patient_name': patientName,
      'mobile': mobile,
      'email': email,
      'date_of_birth': dateOfBirth,
      'gender': gender,
      'blood_group': bloodGroup,
      'allergies': allergies,
      'medical_notes': medicalNotes,
      'status': status,
    };
  }
}
```

### 6. Dependencies في pubspec.yaml

```yaml
dependencies:
  flutter:
    sdk: flutter
  dio: ^5.4.0                    # HTTP client
  shared_preferences: ^2.2.2    # Local storage
  provider: ^6.1.1              # State management (optional)
```

---

## 🧪 الجزء الثالث: اختبار الاتصال

### 1. من Flutter - اختبار بسيط

```dart
import 'package:flutter/material.dart';
import 'services/auth_service.dart';

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _authService = AuthService();
  final _mobileController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  Future<void> _handleLogin() async {
    setState(() => _isLoading = true);

    try {
      final result = await _authService.login(
        mobile: _mobileController.text,
        password: _passwordController.text,
      );

      // نجح تسجيل الدخول
      print('تم تسجيل الدخول: ${result['patient']}');

      // انتقل إلى الشاشة الرئيسية
      Navigator.pushReplacementNamed(context, '/home');

    } catch (e) {
      // فشل تسجيل الدخول
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('خطأ: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('تسجيل الدخول')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: _mobileController,
              decoration: InputDecoration(
                labelText: 'رقم الجوال',
                hintText: '05XXXXXXXX',
              ),
              keyboardType: TextInputType.phone,
            ),
            SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              decoration: InputDecoration(labelText: 'كلمة المرور'),
              obscureText: true,
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: _isLoading ? null : _handleLogin,
              child: _isLoading
                  ? CircularProgressIndicator()
                  : Text('تسجيل الدخول'),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## 🔍 الجزء الرابع: استكشاف الأخطاء

### المشاكل الشائعة والحلول

#### 1. خطأ: "Connection refused" أو "Failed to connect"

**الأسباب المحتملة:**
- خادم Frappe غير مشغل
- Firewall يمنع الاتصال
- IP Address خاطئ

**الحلول:**
```bash
# تحقق من تشغيل Frappe
bench start

# تحقق من المنافذ
sudo netstat -tlnp | grep 8000

# تحقق من Firewall
sudo ufw status
```

#### 2. خطأ: "CORS policy" أو "Access-Control-Allow-Origin"

**الحل:**
```bash
# في ملف .env
ALLOWED_CORS_ORIGINS=*

# أعد تشغيل Frappe
bench restart
```

#### 3. خطأ: "401 Unauthorized"

**الحل:**
- تأكد من صحة token
- تحقق من انتهاء صلاحية token (90 يوم)
- استخدم endpoint لتجديد token

#### 4. الاتصال يعمل على localhost لكن ليس من جهاز آخر

**الحل:**
```bash
# تأكد من تشغيل Frappe على 0.0.0.0
bench start --host 0.0.0.0

# تحقق من common_site_config.json
{
  "host_name": "http://0.0.0.0:8000"
}
```

---

## 📊 الجزء الخامس: API Endpoints المتاحة

### Authentication APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/method/my_medicinal.my_medicinal.api.patient.register` | POST | تسجيل مريض جديد |
| `/api/method/my_medicinal.my_medicinal.api.patient.login` | POST | تسجيل الدخول |
| `/api/method/my_medicinal.my_medicinal.api.patient.get_profile` | GET | الحصول على الملف الشخصي |
| `/api/method/my_medicinal.my_medicinal.api.patient.update_profile` | POST | تحديث الملف الشخصي |

### Medication APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/method/my_medicinal.my_medicinal.api.medication.get_list` | GET | قائمة الأدوية |
| `/api/method/my_medicinal.my_medicinal.api.medication.add` | POST | إضافة دواء |
| `/api/method/my_medicinal.my_medicinal.api.medication.log_taken` | POST | تسجيل تناول دواء |

### Consultation APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/method/my_medicinal.my_medicinal.api.consultation.create` | POST | إنشاء استشارة |
| `/api/method/my_medicinal.my_medicinal.api.consultation.get_list` | GET | قائمة الاستشارات |

### Order APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/method/my_medicinal.my_medicinal.api.order.create` | POST | إنشاء طلب |
| `/api/method/my_medicinal.my_medicinal.api.order.get_list` | GET | قائمة الطلبات |

### Product APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/method/my_medicinal.my_medicinal.api.product.get_products` | GET | قائمة المنتجات |
| `/api/method/my_medicinal.my_medicinal.api.product.search` | GET | البحث عن منتجات |

---

## 🔐 الجزء السادس: الأمان

### 1. HTTPS للإنتاج

**لا تستخدم HTTP في الإنتاج!** استخدم HTTPS مع SSL Certificate.

```bash
# باستخدام Let's Encrypt
sudo bench setup lets-encrypt [site-name]
```

### 2. تأمين API Keys

```dart
// لا تضع API keys في الكود مباشرة
// استخدم environment variables أو secure storage

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

final storage = FlutterSecureStorage();

// حفظ token
await storage.write(key: 'auth_token', value: token);

// قراءة token
String? token = await storage.read(key: 'auth_token');
```

### 3. Rate Limiting

الإعدادات موجودة في `hooks.py`:
```python
rate_limit = {
    "limit": 100,  # 100 طلب
    "window": 60   # في دقيقة واحدة
}
```

---

## ✅ قائمة التحقق النهائية

### على خادم Frappe:
- [ ] تحديد IP Address للخادم
- [ ] تحديث `common_site_config.json`
- [ ] تحديث ملف `.env` مع CORS origins
- [ ] فتح المنافذ في Firewall (8000, 9000)
- [ ] تشغيل Frappe مع `--host 0.0.0.0`
- [ ] اختبار endpoint: `/api/method/ping`

### على جهاز Flutter:
- [ ] تحديث `ApiConfig` مع IP الصحيح
- [ ] إضافة dependencies في `pubspec.yaml`
- [ ] إنشاء API Client
- [ ] إنشاء Auth Service
- [ ] اختبار الاتصال من التطبيق

---

## 📞 الدعم والمساعدة

إذا واجهت أي مشاكل:

1. تحقق من logs:
```bash
# Frappe logs
bench --site [site-name] console

# أو
tail -f sites/[site-name]/logs/web.error.log
```

2. اختبر API من المتصفح أو Postman أولاً

3. تحقق من اتصال الشبكة بين الجهازين

---

**تم إنشاؤه بواسطة:** Claude
**التاريخ:** 2026-01-10
**الإصدار:** 1.0
