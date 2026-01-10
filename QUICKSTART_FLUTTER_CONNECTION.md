# 🚀 دليل البداية السريعة - ربط Flutter مع Frappe

## الخطوات الأساسية (5 دقائق)

### على خادم Frappe (جهاز 1):

#### 1. تحديد IP Address
```bash
hostname -I
# مثال: 192.168.1.100
```

#### 2. تحديث CORS في `.env`
```bash
# إنشاء ملف .env إذا لم يكن موجوداً
cp .env.example .env

# حرر الملف
nano .env
```

أضف/حدث السطر التالي:
```bash
ALLOWED_CORS_ORIGINS=*
```

#### 3. تشغيل Frappe
```bash
# في مجلد bench
bench start --host 0.0.0.0
```

#### 4. فتح Firewall (إذا لزم الأمر)
```bash
# Ubuntu/Debian
sudo ufw allow 8000/tcp
sudo ufw reload

# أو CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

#### 5. اختبار الاتصال
```bash
# قم بتشغيل سكريبت الاختبار
python3 test_connection.py
```

---

### على جهاز Flutter (جهاز 2):

#### 1. تثبيت Dependencies
في `pubspec.yaml`:
```yaml
dependencies:
  dio: ^5.4.0
  shared_preferences: ^2.2.2
```

ثم:
```bash
flutter pub get
```

#### 2. نسخ ملفات API
انسخ الملفات من `flutter_examples/` إلى مشروع Flutter:
- `api_service_example.dart` → `lib/services/`

#### 3. تحديث IP في ApiConfig
افتح `lib/services/api_service_example.dart` وحدث:
```dart
class ApiConfig {
  // استبدل بـ IP الفعلي لخادم Frappe
  static const String baseUrl = 'http://192.168.1.100:8000';
  // ...
}
```

#### 4. اختبار الاتصال
```dart
import 'services/api_service_example.dart';

void testConnection() async {
  final authService = AuthService();

  try {
    final result = await authService.login(
      mobile: '0501234567',
      password: 'test123',
    );

    if (result.success) {
      print('✅ تم الاتصال بنجاح');
      print('Patient: ${result.data?.patientName}');
    }
  } catch (e) {
    print('❌ فشل الاتصال: $e');
  }
}
```

---

## 🧪 اختبار سريع

### من Terminal على جهاز Flutter:
```bash
# اختبار ping
ping 192.168.1.100

# اختبار API
curl http://192.168.1.100:8000/api/method/ping
```

يجب أن تحصل على:
```json
{"message": "pong"}
```

---

## ❓ المشاكل الشائعة

### ❌ "Connection refused"
**الحل:**
1. تأكد من تشغيل Frappe: `bench start --host 0.0.0.0`
2. تحقق من IP Address صحيح
3. تحقق من Firewall

### ❌ "CORS error"
**الحل:**
1. في `.env`: `ALLOWED_CORS_ORIGINS=*`
2. أعد تشغيل: `bench restart`

### ❌ "401 Unauthorized"
**الحل:**
1. قم بالتسجيل أولاً أو تسجيل الدخول
2. تحقق من صحة token

---

## 📱 مثال تطبيق كامل

```dart
import 'package:flutter/material.dart';
import 'services/api_service_example.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Dawaii',
      home: LoginPage(),
    );
  }
}

class LoginPage extends StatefulWidget {
  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _authService = AuthService();
  final _mobileController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  String? _message;

  Future<void> _login() async {
    setState(() {
      _isLoading = true;
      _message = null;
    });

    try {
      final result = await _authService.login(
        mobile: _mobileController.text,
        password: _passwordController.text,
      );

      setState(() {
        _isLoading = false;
        if (result.success) {
          _message = '✅ تم تسجيل الدخول بنجاح';
        } else {
          _message = '❌ ${result.message}';
        }
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _message = '❌ خطأ: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('دوائي - تسجيل الدخول')),
      body: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: _mobileController,
              decoration: InputDecoration(
                labelText: 'رقم الجوال',
                hintText: '05XXXXXXXX',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.phone,
            ),
            SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              decoration: InputDecoration(
                labelText: 'كلمة المرور',
                border: OutlineInputBorder(),
              ),
              obscureText: true,
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: _isLoading ? null : _login,
              child: _isLoading
                  ? CircularProgressIndicator(color: Colors.white)
                  : Text('تسجيل الدخول'),
              style: ElevatedButton.styleFrom(
                minimumSize: Size(double.infinity, 50),
              ),
            ),
            if (_message != null) ...[
              SizedBox(height: 16),
              Text(
                _message!,
                style: TextStyle(
                  color: _message!.contains('✅')
                      ? Colors.green
                      : Colors.red,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
```

---

## 🎯 الخطوات التالية

بعد نجاح الاتصال:

1. ✅ قم بتطبيق باقي الـ endpoints (Medications, Orders, إلخ)
2. ✅ أضف State Management (Provider, Riverpod, Bloc)
3. ✅ أضف Error Handling أفضل
4. ✅ أضف Offline Support مع local database
5. ✅ استخدم HTTPS في الإنتاج

---

## 📚 المراجع

- [دليل كامل](./FLUTTER_FRAPPE_CONNECTION.md) - دليل شامل مفصل
- [أمثلة Flutter](./flutter_examples/) - أمثلة كود كاملة
- [سكريبت الاختبار](./test_connection.py) - اختبار الاتصال

---

**تمت آخر مراجعة:** 2026-01-10
