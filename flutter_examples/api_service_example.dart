// =============================================================================
// Dawaii Flutter App - Complete API Service Example
// مثال كامل لخدمة API في تطبيق دوائي
// =============================================================================

import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

// =============================================================================
// API Configuration
// =============================================================================

class ApiConfig {
  // ⚠️ IMPORTANT: استبدل هذا الـ IP بعنوان خادم Frappe الخاص بك
  static const String baseUrl = 'http://192.168.1.100:8000';

  // API base path
  static const String apiBase = '/api/method/my_medicinal.my_medicinal.api';

  // Timeout settings
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);

  // Storage keys
  static const String tokenKey = 'auth_token';
  static const String userKey = 'user_data';
}

// =============================================================================
// API Response Models
// =============================================================================

class ApiResponse<T> {
  final bool success;
  final String? message;
  final T? data;
  final dynamic error;

  ApiResponse({
    required this.success,
    this.message,
    this.data,
    this.error,
  });

  factory ApiResponse.fromJson(
    Map<String, dynamic> json,
    T Function(Map<String, dynamic>)? fromJsonT,
  ) {
    final messageData = json['message'];

    if (messageData is Map<String, dynamic>) {
      return ApiResponse(
        success: messageData['success'] ?? false,
        message: messageData['message'],
        data: fromJsonT != null && messageData['patient'] != null
            ? fromJsonT(messageData['patient'])
            : null,
      );
    }

    return ApiResponse(
      success: false,
      message: 'Invalid response format',
      error: json,
    );
  }
}

// =============================================================================
// Patient Model
// =============================================================================

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
      patientId: json['patient_id'] ?? '',
      patientName: json['patient_name'] ?? '',
      mobile: json['mobile'] ?? '',
      email: json['email'] ?? '',
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

// =============================================================================
// Medication Model
// =============================================================================

class Medication {
  final String name;
  final String medicineId;
  final String dosage;
  final String frequency;
  final String? startDate;
  final String? endDate;
  final List<String> timings;
  final String? notes;

  Medication({
    required this.name,
    required this.medicineId,
    required this.dosage,
    required this.frequency,
    this.startDate,
    this.endDate,
    required this.timings,
    this.notes,
  });

  factory Medication.fromJson(Map<String, dynamic> json) {
    return Medication(
      name: json['name'] ?? '',
      medicineId: json['medicine_id'] ?? '',
      dosage: json['dosage'] ?? '',
      frequency: json['frequency'] ?? '',
      startDate: json['start_date'],
      endDate: json['end_date'],
      timings: json['timings'] != null
          ? List<String>.from(json['timings'])
          : [],
      notes: json['notes'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'medicine_id': medicineId,
      'dosage': dosage,
      'frequency': frequency,
      'start_date': startDate,
      'end_date': endDate,
      'timings': timings,
      'notes': notes,
    };
  }
}

// =============================================================================
// API Client - HTTP Client with Dio
// =============================================================================

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

    // Add request/response interceptors
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Add auth token if available
          if (_authToken != null) {
            options.headers['Authorization'] = 'token $_authToken';
          }

          print('📤 Request: ${options.method} ${options.path}');
          print('📦 Data: ${options.data}');

          return handler.next(options);
        },
        onResponse: (response, handler) {
          print('📥 Response: ${response.statusCode}');
          print('📦 Data: ${response.data}');
          return handler.next(response);
        },
        onError: (error, handler) {
          print('❌ Error: ${error.message}');
          _handleError(error);
          return handler.next(error);
        },
      ),
    );

    // Load saved token
    _loadToken();
  }

  // Load token from storage
  Future<void> _loadToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _authToken = prefs.getString(ApiConfig.tokenKey);
      print('🔑 Token loaded: ${_authToken != null ? "Yes" : "No"}');
    } catch (e) {
      print('⚠️ Error loading token: $e');
    }
  }

  // Save token to storage
  Future<void> saveToken(String token) async {
    _authToken = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(ApiConfig.tokenKey, token);
    print('✅ Token saved');
  }

  // Clear token from storage
  Future<void> clearToken() async {
    _authToken = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(ApiConfig.tokenKey);
    await prefs.remove(ApiConfig.userKey);
    print('🗑️ Token cleared');
  }

  // GET request
  Future<Response> get(String endpoint, {Map<String, dynamic>? params}) async {
    return await _dio.get(endpoint, queryParameters: params);
  }

  // POST request
  Future<Response> post(String endpoint, {Map<String, dynamic>? data}) async {
    return await _dio.post(endpoint, data: data);
  }

  // PUT request
  Future<Response> put(String endpoint, {Map<String, dynamic>? data}) async {
    return await _dio.put(endpoint, data: data);
  }

  // DELETE request
  Future<Response> delete(String endpoint) async {
    return await _dio.delete(endpoint);
  }

  // Error handler
  void _handleError(DioException error) {
    String errorMessage;

    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        errorMessage = 'انتهت مهلة الاتصال. تحقق من اتصالك بالإنترنت.';
        break;

      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode;
        if (statusCode == 401) {
          errorMessage = 'غير مصرح. يرجى تسجيل الدخول مرة أخرى.';
        } else if (statusCode == 403) {
          errorMessage = 'ممنوع. ليس لديك صلاحية للوصول.';
        } else if (statusCode == 404) {
          errorMessage = 'غير موجود.';
        } else if (statusCode == 500) {
          errorMessage = 'خطأ في الخادم.';
        } else {
          errorMessage = 'خطأ: ${error.response?.statusMessage}';
        }
        break;

      case DioExceptionType.cancel:
        errorMessage = 'تم إلغاء الطلب.';
        break;

      default:
        errorMessage = 'فشل الاتصال. تحقق من:\n'
            '1. اتصالك بالإنترنت\n'
            '2. عنوان IP للخادم صحيح\n'
            '3. الخادم يعمل';
        break;
    }

    throw Exception(errorMessage);
  }
}

// =============================================================================
// Authentication Service
// =============================================================================

class AuthService {
  final ApiClient _apiClient = ApiClient();

  // Register new patient
  Future<ApiResponse<Patient>> register({
    required String patientName,
    required String mobile,
    required String password,
    String? email,
    String? dateOfBirth,
    String? gender,
  }) async {
    try {
      final response = await _apiClient.post(
        '${ApiConfig.apiBase}.patient.register',
        data: {
          'patient_name': patientName,
          'mobile': mobile,
          'password': password,
          'email': email,
          'date_of_birth': dateOfBirth,
          'gender': gender,
        },
      );

      final result = response.data['message'];

      if (result['success'] == true) {
        final token = result['token'];
        await _apiClient.saveToken(token);

        final patient = Patient.fromJson(result['patient']);
        await _saveUserData(patient);

        return ApiResponse(
          success: true,
          message: result['message'],
          data: patient,
        );
      } else {
        return ApiResponse(
          success: false,
          message: result['message'] ?? 'فشل التسجيل',
        );
      }
    } catch (e) {
      return ApiResponse(
        success: false,
        message: 'خطأ في التسجيل',
        error: e.toString(),
      );
    }
  }

  // Login
  Future<ApiResponse<Patient>> login({
    required String mobile,
    required String password,
  }) async {
    try {
      final response = await _apiClient.post(
        '${ApiConfig.apiBase}.patient.login',
        data: {
          'mobile': mobile,
          'password': password,
        },
      );

      final result = response.data['message'];

      if (result['success'] == true) {
        final token = result['token'];
        await _apiClient.saveToken(token);

        final patient = Patient.fromJson(result['patient']);
        await _saveUserData(patient);

        return ApiResponse(
          success: true,
          message: result['message'],
          data: patient,
        );
      } else {
        return ApiResponse(
          success: false,
          message: result['message'] ?? 'فشل تسجيل الدخول',
        );
      }
    } catch (e) {
      return ApiResponse(
        success: false,
        message: 'خطأ في تسجيل الدخول',
        error: e.toString(),
      );
    }
  }

  // Logout
  Future<void> logout() async {
    await _apiClient.clearToken();
  }

  // Get profile
  Future<ApiResponse<Patient>> getProfile() async {
    try {
      final response = await _apiClient.get(
        '${ApiConfig.apiBase}.patient.get_profile',
      );

      final result = response.data['message'];

      if (result['success'] == true) {
        final patient = Patient.fromJson(result['patient']);
        return ApiResponse(
          success: true,
          data: patient,
        );
      } else {
        return ApiResponse(
          success: false,
          message: 'فشل الحصول على الملف الشخصي',
        );
      }
    } catch (e) {
      return ApiResponse(
        success: false,
        message: 'خطأ في الحصول على الملف الشخصي',
        error: e.toString(),
      );
    }
  }

  // Update profile
  Future<ApiResponse<Patient>> updateProfile({
    required String patientId,
    required Map<String, dynamic> profileData,
  }) async {
    try {
      final response = await _apiClient.post(
        '${ApiConfig.apiBase}.patient.update_profile',
        data: {
          'patient_id': patientId,
          'profile_data': jsonEncode(profileData),
        },
      );

      final result = response.data['message'];

      if (result['success'] == true) {
        final patient = Patient.fromJson(result['patient']);
        await _saveUserData(patient);

        return ApiResponse(
          success: true,
          message: 'تم تحديث الملف الشخصي بنجاح',
          data: patient,
        );
      } else {
        return ApiResponse(
          success: false,
          message: result['message'] ?? 'فشل تحديث الملف الشخصي',
        );
      }
    } catch (e) {
      return ApiResponse(
        success: false,
        message: 'خطأ في تحديث الملف الشخصي',
        error: e.toString(),
      );
    }
  }

  // Save user data to local storage
  Future<void> _saveUserData(Patient patient) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(ApiConfig.userKey, jsonEncode(patient.toJson()));
  }

  // Get saved user data
  Future<Patient?> getSavedUserData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final userData = prefs.getString(ApiConfig.userKey);

      if (userData != null) {
        return Patient.fromJson(jsonDecode(userData));
      }
      return null;
    } catch (e) {
      print('⚠️ Error loading user data: $e');
      return null;
    }
  }
}

// =============================================================================
// Medication Service
// =============================================================================

class MedicationService {
  final ApiClient _apiClient = ApiClient();

  // Get patient medications
  Future<ApiResponse<List<Medication>>> getMedications() async {
    try {
      final response = await _apiClient.get(
        '${ApiConfig.apiBase}.medication.get_list',
      );

      final result = response.data['message'];

      if (result['success'] == true) {
        final medicationsJson = result['medications'] as List;
        final medications = medicationsJson
            .map((json) => Medication.fromJson(json))
            .toList();

        return ApiResponse(
          success: true,
          data: medications,
        );
      } else {
        return ApiResponse(
          success: false,
          message: 'فشل الحصول على قائمة الأدوية',
        );
      }
    } catch (e) {
      return ApiResponse(
        success: false,
        message: 'خطأ في الحصول على قائمة الأدوية',
        error: e.toString(),
      );
    }
  }

  // Add medication
  Future<ApiResponse<Medication>> addMedication({
    required String medicineId,
    required String dosage,
    required String frequency,
    required List<String> timings,
    String? startDate,
    String? endDate,
    String? notes,
  }) async {
    try {
      final response = await _apiClient.post(
        '${ApiConfig.apiBase}.medication.add',
        data: {
          'medicine_id': medicineId,
          'dosage': dosage,
          'frequency': frequency,
          'timings': timings,
          'start_date': startDate,
          'end_date': endDate,
          'notes': notes,
        },
      );

      final result = response.data['message'];

      if (result['success'] == true) {
        final medication = Medication.fromJson(result['medication']);
        return ApiResponse(
          success: true,
          message: 'تمت إضافة الدواء بنجاح',
          data: medication,
        );
      } else {
        return ApiResponse(
          success: false,
          message: result['message'] ?? 'فشل إضافة الدواء',
        );
      }
    } catch (e) {
      return ApiResponse(
        success: false,
        message: 'خطأ في إضافة الدواء',
        error: e.toString(),
      );
    }
  }

  // Log medication taken
  Future<ApiResponse<void>> logMedicationTaken({
    required String medicationScheduleId,
    required String takenTime,
    String? notes,
  }) async {
    try {
      final response = await _apiClient.post(
        '${ApiConfig.apiBase}.medication.log_taken',
        data: {
          'medication_schedule_id': medicationScheduleId,
          'taken_time': takenTime,
          'notes': notes,
        },
      );

      final result = response.data['message'];

      if (result['success'] == true) {
        return ApiResponse(
          success: true,
          message: 'تم تسجيل تناول الدواء بنجاح',
        );
      } else {
        return ApiResponse(
          success: false,
          message: result['message'] ?? 'فشل تسجيل تناول الدواء',
        );
      }
    } catch (e) {
      return ApiResponse(
        success: false,
        message: 'خطأ في تسجيل تناول الدواء',
        error: e.toString(),
      );
    }
  }
}

// =============================================================================
// Usage Example
// =============================================================================

/*
void main() async {
  // Initialize
  final authService = AuthService();
  final medicationService = MedicationService();

  // Register
  final registerResult = await authService.register(
    patientName: 'أحمد محمد',
    mobile: '0501234567',
    password: 'password123',
    email: 'ahmed@example.com',
    gender: 'Male',
  );

  if (registerResult.success) {
    print('تم التسجيل بنجاح: ${registerResult.data?.patientName}');
  } else {
    print('فشل التسجيل: ${registerResult.message}');
  }

  // Login
  final loginResult = await authService.login(
    mobile: '0501234567',
    password: 'password123',
  );

  if (loginResult.success) {
    print('تم تسجيل الدخول: ${loginResult.data?.patientName}');

    // Get medications
    final medicationsResult = await medicationService.getMedications();

    if (medicationsResult.success) {
      print('عدد الأدوية: ${medicationsResult.data?.length}');
    }
  }
}
*/
