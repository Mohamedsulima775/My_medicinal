/// API Constants for Dawaii Flutter App
/// This file contains all API endpoints for connecting to My_medicinal backend
///
/// Usage:
/// ```dart
/// final url = '${ApiConstants.baseUrl}${ApiConstants.login}';
/// ```

class ApiConstants {
  // ============================================================
  // Environment Configuration
  // ============================================================

  /// Development server URL
  static const String devBaseUrl = 'http://localhost:8000';

  /// Staging server URL
  static const String stagingBaseUrl = 'https://staging.dawaii.com';

  /// Production server URL
  static const String prodBaseUrl = 'https://api.dawaii.com';

  /// Current environment: 'development', 'staging', 'production'
  static const String environment = 'development';

  /// Get current base URL based on environment
  static String get baseUrl {
    switch (environment) {
      case 'production':
        return prodBaseUrl;
      case 'staging':
        return stagingBaseUrl;
      default:
        return devBaseUrl;
    }
  }

  /// API method prefix for Frappe
  static const String apiPrefix = '/api/method/my_medicinal';

  // ============================================================
  // Authentication Endpoints - نقاط المصادقة
  // ============================================================

  /// Register new patient - تسجيل مريض جديد
  /// Method: POST
  /// Body: {mobile, full_name, password, email?, date_of_birth?, gender?, blood_group?}
  /// Mobile format: 05XXXXXXXX (Saudi format)
  static const String register = '$apiPrefix.api.patient.register';

  /// Patient login - تسجيل الدخول
  /// Method: POST
  /// Body: {mobile, password}
  static const String login = '$apiPrefix.api.patient.login';

  /// Get patient profile - جلب الملف الشخصي
  /// Method: GET
  /// Headers: Authorization: token API_KEY:API_SECRET
  static const String getProfile = '$apiPrefix.api.patient.get_profile';

  /// Update patient profile - تحديث الملف الشخصي
  /// Method: POST
  /// Headers: Authorization
  /// Body: {full_name?, email?, date_of_birth?, gender?, blood_group?, allergies?, chronic_diseases?}
  static const String updateProfile = '$apiPrefix.api.patient.update_profile';

  /// Refresh authentication token - تجديد التوكن
  /// Method: POST
  /// Headers: Authorization (with current token)
  static const String refreshToken = '$apiPrefix.api.patient.refresh_token';

  // ============================================================
  // Medication Endpoints - نقاط الأدوية
  // ============================================================

  /// Get patient medications - جلب أدوية المريض
  /// Method: GET
  /// Headers: Authorization
  static const String getPatientMedications =
      '$apiPrefix.api.medication.get_patient_medications';

  /// Get medications due now - جلب الأدوية المستحقة
  /// Method: GET
  /// Headers: Authorization
  static const String getMedicationsDue =
      '$apiPrefix.api.medication_schedule.get_medications_due';

  /// Add new medication - إضافة دواء جديد
  /// Method: POST
  /// Headers: Authorization
  /// Body: {
  ///   medication_name: string,
  ///   dosage: string,
  ///   frequency: string (Once daily, Twice daily, Three times daily, etc.),
  ///   times: [{time: "HH:mm", before_after_meal?: string, notes?: string}],
  ///   stock?: int,
  ///   reorder_level?: int,
  ///   color?: string (hex color)
  /// }
  static const String addMedication = '$apiPrefix.api.medication.add_medication';

  /// Log medication taken/missed/skipped - تسجيل تناول الدواء
  /// Method: POST
  /// Headers: Authorization
  /// Body: {schedule_id, status: "Taken"|"Missed"|"Skipped", taken_time?: "YYYY-MM-DD HH:mm"}
  static const String logMedicationTaken =
      '$apiPrefix.api.medication.log_medication_taken';

  /// Update medication stock - تحديث المخزون
  /// Method: POST
  /// Headers: Authorization
  /// Body: {schedule_id, new_stock: int}
  static const String updateStock = '$apiPrefix.api.medication.update_stock';

  /// Get low stock medications - تنبيهات نفاد المخزون
  /// Method: GET
  /// Headers: Authorization
  static const String getLowStockMedications =
      '$apiPrefix.api.medication.get_low_stock_medications';

  /// Deactivate medication - إلغاء تفعيل الدواء
  /// Method: POST
  /// Headers: Authorization
  /// Body: {schedule_id}
  static const String deactivateMedication =
      '$apiPrefix.api.medication.deactivate_medication';

  // ============================================================
  // Consultation Endpoints - نقاط الاستشارات
  // ============================================================

  /// Create consultation - إنشاء استشارة
  /// Method: POST
  /// Headers: Authorization
  /// Body: {provider_id, subject, message, priority?: "Low"|"Medium"|"High"}
  static const String createConsultation =
      '$apiPrefix.api.consultation.create_consultation';

  /// Get my consultations - جلب استشاراتي
  /// Method: GET
  /// Headers: Authorization
  /// Query: ?status=Pending|In Progress|Completed&limit=20&offset=0
  static const String getMyConsultations =
      '$apiPrefix.api.consultation.get_my_consultations';

  /// Get consultation details - تفاصيل استشارة
  /// Method: GET
  /// Headers: Authorization
  /// Query: ?consultation_id=XXX
  static const String getConsultationDetails =
      '$apiPrefix.api.consultation.get_consultation_details';

  /// Send message in consultation - إرسال رسالة
  /// Method: POST
  /// Headers: Authorization
  /// Body: {consultation_id, message}
  static const String sendMessage = '$apiPrefix.api.consultation.send_message';

  /// Get consultation messages - جلب الرسائل
  /// Method: GET
  /// Headers: Authorization
  /// Query: ?consultation_id=XXX&limit=50&offset=0
  static const String getMessages = '$apiPrefix.api.consultation.get_messages';

  // ============================================================
  // Product/Pharmacy Endpoints - نقاط المنتجات (بدون مصادقة)
  // ============================================================

  /// Get products list - جلب المنتجات
  /// Method: GET
  /// Query: ?category=&limit=20&offset=0
  static const String getProducts = '$apiPrefix.api.product.get_products';

  /// Search products - البحث في المنتجات
  /// Method: GET
  /// Query: ?query=XXX
  static const String searchProducts = '$apiPrefix.api.product.search_products';

  /// Get categories - جلب التصنيفات
  /// Method: GET
  static const String getCategories = '$apiPrefix.api.product.get_categories';

  /// Get product details - تفاصيل منتج
  /// Method: GET
  /// Query: ?item_code=XXX
  static const String getProductDetails =
      '$apiPrefix.api.product.get_product_details';

  // ============================================================
  // Order Endpoints - نقاط الطلبات
  // ============================================================

  /// Create order - إنشاء طلب
  /// Method: POST
  /// Headers: Authorization
  /// Body: {
  ///   items: [{item_code, quantity}],
  ///   delivery_address: string,
  ///   payment_method: "Cash"|"Card"|"Apple Pay"
  /// }
  static const String createOrder = '$apiPrefix.api.order.create_order';

  /// Get my orders - جلب طلباتي
  /// Method: GET
  /// Headers: Authorization
  /// Query: ?status=&limit=20&offset=0
  static const String getMyOrders = '$apiPrefix.api.order.get_my_orders';

  // ============================================================
  // Prescription Endpoints - نقاط الوصفات الطبية
  // ============================================================

  /// Get my prescriptions - جلب وصفاتي
  /// Method: GET
  /// Headers: Authorization
  static const String getMyPrescriptions =
      '$apiPrefix.api.prescription.get_my_prescriptions';

  /// Get prescription details - تفاصيل وصفة
  /// Method: GET
  /// Headers: Authorization
  /// Query: ?prescription_id=XXX
  static const String getPrescriptionDetails =
      '$apiPrefix.api.prescription.get_prescription_details';

  // ============================================================
  // Notification Endpoints - نقاط الإشعارات
  // ============================================================

  /// Register FCM device - تسجيل جهاز للإشعارات
  /// Method: POST
  /// Headers: Authorization
  /// Body: {fcm_token, device_type: "android"|"ios", device_id}
  static const String registerDevice =
      '$apiPrefix.my_medicinal.notifications.register_device';

  /// Test notification - إرسال إشعار تجريبي
  /// Method: POST
  /// Headers: Authorization
  static const String sendTestNotification =
      '$apiPrefix.my_medicinal.notifications.send_test_notification';

  /// Get my notifications - جلب إشعاراتي
  /// Method: GET
  /// Headers: Authorization
  /// Query: ?limit=20&offset=0
  static const String getMyNotifications =
      '$apiPrefix.my_medicinal.notifications.get_my_notifications';

  /// Mark notification as read - تحديد إشعار كمقروء
  /// Method: POST
  /// Headers: Authorization
  /// Body: {notification_id}
  static const String markNotificationRead =
      '$apiPrefix.my_medicinal.notifications.mark_notification_read';

  // ============================================================
  // Helper Methods
  // ============================================================

  /// Build full URL from endpoint
  static String buildUrl(String endpoint) => '$baseUrl$endpoint';

  /// Build URL with query parameters
  static String buildUrlWithParams(
      String endpoint, Map<String, dynamic> params) {
    final uri = Uri.parse('$baseUrl$endpoint').replace(queryParameters: params);
    return uri.toString();
  }

  // ============================================================
  // API Response Keys
  // ============================================================

  static const String keyMessage = 'message';
  static const String keySuccess = 'success';
  static const String keyError = 'error';
  static const String keyData = 'data';
  static const String keyApiKey = 'api_key';
  static const String keyApiSecret = 'api_secret';
  static const String keyPatientId = 'patient_id';
  static const String keyExpiresAt = 'expires_at';

  // ============================================================
  // Medication Frequencies
  // ============================================================

  static const List<String> medicationFrequencies = [
    'Once daily',
    'Twice daily',
    'Three times daily',
    'Four times daily',
    'Every 6 hours',
    'Every 8 hours',
    'Every 12 hours',
    'As needed',
    'Weekly',
  ];

  // ============================================================
  // Medication Frequencies (Arabic)
  // ============================================================

  static const List<String> medicationFrequenciesAr = [
    'مرة يومياً',
    'مرتين يومياً',
    'ثلاث مرات يومياً',
    'أربع مرات يومياً',
    'كل 6 ساعات',
    'كل 8 ساعات',
    'كل 12 ساعة',
    'عند الحاجة',
    'أسبوعياً',
  ];

  // ============================================================
  // Meal Options
  // ============================================================

  static const List<String> mealOptions = [
    'Before meal',
    'After meal',
    'With meal',
    'Empty stomach',
    'Any time',
  ];

  static const List<String> mealOptionsAr = [
    'قبل الأكل',
    'بعد الأكل',
    'مع الأكل',
    'على معدة فارغة',
    'في أي وقت',
  ];

  // ============================================================
  // Status Values
  // ============================================================

  static const String statusTaken = 'Taken';
  static const String statusMissed = 'Missed';
  static const String statusSkipped = 'Skipped';

  static const String consultationPending = 'Pending';
  static const String consultationInProgress = 'In Progress';
  static const String consultationCompleted = 'Completed';

  static const String priorityLow = 'Low';
  static const String priorityMedium = 'Medium';
  static const String priorityHigh = 'High';
}
