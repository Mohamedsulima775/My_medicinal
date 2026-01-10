# Flutter Integration Examples

## 📁 الملفات المتوفرة

### 1. `api_service_example.dart`
ملف كامل يحتوي على:
- **ApiConfig**: إعدادات الاتصال
- **ApiClient**: HTTP client مع Dio
- **Models**: Patient, Medication, ApiResponse
- **AuthService**: خدمة المصادقة (تسجيل، دخول، ملف شخصي)
- **MedicationService**: خدمة الأدوية

## 🚀 كيفية الاستخدام

### 1. نسخ الملفات

```bash
# من مجلد My_medicinal
cp flutter_examples/api_service_example.dart /path/to/Dawaii_Android/lib/services/
```

### 2. تحديث IP Address

افتح `lib/services/api_service_example.dart` وحدث:

```dart
class ApiConfig {
  static const String baseUrl = 'http://YOUR_FRAPPE_IP:8000';
  // استبدل YOUR_FRAPPE_IP بعنوان IP الفعلي
}
```

### 3. تثبيت Dependencies

في `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  dio: ^5.4.0
  shared_preferences: ^2.2.2
```

ثم:
```bash
flutter pub get
```

### 4. استخدام الخدمات

#### تسجيل الدخول
```dart
import 'services/api_service_example.dart';

final authService = AuthService();

final result = await authService.login(
  mobile: '0501234567',
  password: 'password',
);

if (result.success) {
  print('Welcome ${result.data?.patientName}');
}
```

#### الحصول على الأدوية
```dart
final medicationService = MedicationService();

final result = await medicationService.getMedications();

if (result.success) {
  for (var med in result.data!) {
    print('${med.name} - ${med.dosage}');
  }
}
```

## 📋 API Endpoints المتاحة

### Authentication
- ✅ `register()` - تسجيل مستخدم جديد
- ✅ `login()` - تسجيل الدخول
- ✅ `logout()` - تسجيل الخروج
- ✅ `getProfile()` - الحصول على الملف الشخصي
- ✅ `updateProfile()` - تحديث الملف الشخصي

### Medications
- ✅ `getMedications()` - الحصول على قائمة الأدوية
- ✅ `addMedication()` - إضافة دواء جديد
- ✅ `logMedicationTaken()` - تسجيل تناول الدواء

## 🔧 تخصيص الكود

### إضافة خدمة جديدة (مثال: Consultations)

```dart
class ConsultationService {
  final ApiClient _apiClient = ApiClient();

  Future<ApiResponse<List<Consultation>>> getConsultations() async {
    try {
      final response = await _apiClient.get(
        '${ApiConfig.apiBase}.consultation.get_list',
      );

      final result = response.data['message'];

      if (result['success'] == true) {
        final consultations = (result['consultations'] as List)
            .map((json) => Consultation.fromJson(json))
            .toList();

        return ApiResponse(
          success: true,
          data: consultations,
        );
      } else {
        return ApiResponse(
          success: false,
          message: 'فشل الحصول على الاستشارات',
        );
      }
    } catch (e) {
      return ApiResponse(
        success: false,
        message: 'خطأ في الحصول على الاستشارات',
        error: e.toString(),
      );
    }
  }
}
```

## 🧪 اختبار

### اختبار بسيط
```dart
void main() async {
  // Test connection
  final authService = AuthService();

  print('Testing login...');
  final result = await authService.login(
    mobile: '0501234567',
    password: 'test123',
  );

  if (result.success) {
    print('✅ Login successful!');
    print('Patient: ${result.data?.patientName}');
  } else {
    print('❌ Login failed: ${result.message}');
  }
}
```

## 📖 المراجع الإضافية

- [دليل الاتصال الكامل](../FLUTTER_FRAPPE_CONNECTION.md)
- [دليل البداية السريعة](../QUICKSTART_FLUTTER_CONNECTION.md)
- [Dio Documentation](https://pub.dev/packages/dio)
- [Frappe API Docs](https://frappeframework.com/docs/user/en/api)

## ❗ ملاحظات مهمة

1. **IP Address**: تأكد من تحديث IP في `ApiConfig`
2. **CORS**: تأكد من إعداد CORS في خادم Frappe
3. **Firewall**: تأكد من فتح المنافذ المطلوبة
4. **HTTPS**: استخدم HTTPS في الإنتاج (ليس HTTP)
5. **Token Storage**: استخدم `flutter_secure_storage` للأمان الأفضل

## 🆘 المساعدة

إذا واجهت مشاكل:
1. تحقق من IP Address
2. تحقق من اتصال الشبكة
3. قم بتشغيل `test_connection.py` على خادم Frappe
4. تحقق من logs في Frappe

---

**آخر تحديث:** 2026-01-10
