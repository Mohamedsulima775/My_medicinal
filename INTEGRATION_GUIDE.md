# 🔗 دليل ربط التطبيقات مع My_medicinal / Dawaii

## 📋 جدول المحتويات
1. [نظرة عامة](#نظرة-عامة)
2. [إعداد Backend](#إعداد-backend)
3. [ربط تطبيق موبايل](#ربط-تطبيق-موبايل)
4. [ربط تطبيق ويب](#ربط-تطبيق-ويب)
5. [المصادقة والتوثيق](#المصادقة-والتوثيق)
6. [أمثلة عملية](#أمثلة-عملية)
7. [استكشاف الأخطاء](#استكشاف-الأخطاء)

---

## 🎯 نظرة عامة

My_medicinal يوفر **RESTful API** يمكن ربطه مع أي تطبيق خارجي:

- ✅ **تطبيقات موبايل**: iOS (Swift/SwiftUI), Android (Kotlin/Java), Flutter, React Native
- ✅ **تطبيقات ويب**: React, Vue.js, Angular, Next.js
- ✅ **أنظمة خارجية**: أي نظام يدعم HTTP REST API

### البنية المعمارية

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                      │
│  (Mobile: iOS/Android/Flutter | Web: React/Vue/Angular)    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTPS REST API
                         │ Authorization: Bearer {token}
                         │
┌────────────────────────▼────────────────────────────────────┐
│              My_medicinal Backend (Frappe)                  │
│                  Base URL: https://your-domain.com          │
│                  Endpoint: /api/method/...                  │
├─────────────────────────────────────────────────────────────┤
│  • Authentication APIs   • Medication APIs                  │
│  • Patient APIs          • Consultation APIs                │
│  • Prescription APIs     • Order APIs                       │
│  • Notification APIs     • Provider APIs                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              MariaDB/MySQL + Redis + Firebase               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 إعداد Backend

### 1️⃣ تشغيل الخادم

```bash
# الانتقال إلى مجلد Frappe Bench
cd my-bench

# تشغيل الخادم
bench start

# أو تشغيل في الخلفية
bench start &
```

**النتيجة:**
- Backend متاح على: `http://localhost:8000`
- API Endpoint: `http://localhost:8000/api/method/{endpoint_name}`

### 2️⃣ إعداد CORS (للسماح بالاتصالات الخارجية)

افتح ملف الإعدادات:

```bash
# فتح ملف site_config.json
nano sites/my_medicinal.local/site_config.json
```

أضف إعدادات CORS:

```json
{
  "db_name": "...",
  "db_password": "...",
  "allow_cors": "*",
  "cors_allowed_origins": [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://192.168.1.100:3000",
    "https://your-mobile-app.com"
  ],
  "cors_allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  "cors_allowed_headers": ["Content-Type", "Authorization"]
}
```

**⚠️ للإنتاج:** استبدل `"*"` بالدومينات المحددة لتطبيقك.

### 3️⃣ تفعيل إعدادات Firebase (للإشعارات الفورية)

```bash
# نسخ ملف Firebase Credentials
cp firebase_credentials.json sites/my_medicinal.local/

# التأكد من المتغيرات البيئية
nano .env
```

تأكد من وجود:

```env
FCM_ENABLED=1
FCM_CREDENTIALS_PATH=./firebase_credentials.json
```

### 4️⃣ اختبار الاتصال

```bash
# اختبار الاتصال بالAPI
curl http://localhost:8000/api/method/my_medicinal.api.patient.login \
  -H "Content-Type: application/json" \
  -d '{"mobile":"0512345678","password":"test123"}'
```

إذا كانت النتيجة JSON، فالخادم يعمل بنجاح! ✅

---

## 📱 ربط تطبيق موبايل

### A. Flutter (مثال)

#### 1. إعداد المشروع

```yaml
# pubspec.yaml
dependencies:
  http: ^1.1.0
  shared_preferences: ^2.2.2
  firebase_messaging: ^14.7.9
```

#### 2. إنشاء API Service

```dart
// lib/services/api_service.dart
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // استبدل بعنوان الخادم الخاص بك
  static const String baseUrl = 'http://192.168.1.100:8000';
  static const String apiPath = '/api/method';

  String? _authToken;

  // الحصول على Token المحفوظ
  Future<String?> getAuthToken() async {
    final prefs = await SharedPreferences.getInstance();
    _authToken = prefs.getString('auth_token');
    return _authToken;
  }

  // حفظ Token بعد تسجيل الدخول
  Future<void> saveAuthToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
    _authToken = token;
  }

  // رؤوس HTTP الأساسية
  Future<Map<String, String>> _getHeaders() async {
    await getAuthToken();
    return {
      'Content-Type': 'application/json',
      if (_authToken != null) 'Authorization': 'Bearer $_authToken',
    };
  }

  // 1. تسجيل مريض جديد
  Future<Map<String, dynamic>> register({
    required String patientName,
    required String mobile,
    required String email,
    required String password,
    String? dateOfBirth,
    String? gender,
  }) async {
    final url = Uri.parse('$baseUrl$apiPath/my_medicinal.api.patient.register');

    final response = await http.post(
      url,
      headers: await _getHeaders(),
      body: jsonEncode({
        'patient_name': patientName,
        'mobile': mobile,
        'email': email,
        'password': password,
        'date_of_birth': dateOfBirth,
        'gender': gender,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final authToken = data['message']['auth_token'];
      await saveAuthToken(authToken);
      return data['message'];
    } else {
      throw Exception('فشل التسجيل: ${response.body}');
    }
  }

  // 2. تسجيل الدخول
  Future<Map<String, dynamic>> login(String mobile, String password) async {
    final url = Uri.parse('$baseUrl$apiPath/my_medicinal.api.patient.login');

    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'mobile': mobile,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final authToken = data['message']['auth_token'];
      await saveAuthToken(authToken);
      return data['message'];
    } else {
      throw Exception('فشل تسجيل الدخول: ${response.body}');
    }
  }

  // 3. الحصول على الملف الشخصي
  Future<Map<String, dynamic>> getProfile(String patientId) async {
    final url = Uri.parse(
      '$baseUrl$apiPath/my_medicinal.api.patient.get_profile?patient_id=$patientId'
    );

    final response = await http.get(url, headers: await _getHeaders());

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['message'];
    } else {
      throw Exception('فشل جلب البيانات: ${response.body}');
    }
  }

  // 4. جلب الأدوية
  Future<List<dynamic>> getMedications(String patientId) async {
    final url = Uri.parse(
      '$baseUrl$apiPath/my_medicinal.api.medication_schedule.get_medications?patient_id=$patientId'
    );

    final response = await http.get(url, headers: await _getHeaders());

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['message'];
    } else {
      throw Exception('فشل جلب الأدوية: ${response.body}');
    }
  }

  // 5. تسجيل أخذ الدواء
  Future<Map<String, dynamic>> logMedication({
    required String patientId,
    required String scheduleId,
    required String status, // "Taken", "Missed", "Skipped"
    String? notes,
  }) async {
    final url = Uri.parse(
      '$baseUrl$apiPath/my_medicinal.api.medication_schedule.log_medication_taken'
    );

    final response = await http.post(
      url,
      headers: await _getHeaders(),
      body: jsonEncode({
        'patient_id': patientId,
        'schedule_id': scheduleId,
        'status': status,
        'notes': notes,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['message'];
    } else {
      throw Exception('فشل تسجيل الدواء: ${response.body}');
    }
  }

  // 6. تسجيل FCM Token للإشعارات
  Future<bool> registerDevice(String fcmToken) async {
    final url = Uri.parse(
      '$baseUrl$apiPath/my_medicinal.my_medicinal.notifications.register_device'
    );

    final response = await http.post(
      url,
      headers: await _getHeaders(),
      body: jsonEncode({
        'fcm_token': fcmToken,
        'device_type': 'mobile',
      }),
    );

    return response.statusCode == 200;
  }
}
```

#### 3. استخدام API في التطبيق

```dart
// lib/screens/login_screen.dart
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _mobileController = TextEditingController();
  final _passwordController = TextEditingController();
  final _apiService = ApiService();
  bool _isLoading = false;

  Future<void> _login() async {
    setState(() => _isLoading = true);

    try {
      final result = await _apiService.login(
        _mobileController.text,
        _passwordController.text,
      );

      // الانتقال إلى الشاشة الرئيسية
      Navigator.pushReplacementNamed(context, '/home');

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['message'] ?? 'تم تسجيل الدخول')),
      );
    } catch (e) {
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
        padding: EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _mobileController,
              decoration: InputDecoration(labelText: 'رقم الجوال'),
              keyboardType: TextInputType.phone,
            ),
            TextField(
              controller: _passwordController,
              decoration: InputDecoration(labelText: 'كلمة المرور'),
              obscureText: true,
            ),
            SizedBox(height: 20),
            _isLoading
                ? CircularProgressIndicator()
                : ElevatedButton(
                    onPressed: _login,
                    child: Text('دخول'),
                  ),
          ],
        ),
      ),
    );
  }
}
```

---

### B. React Native (مثال)

#### 1. إنشاء API Service

```javascript
// services/api.js
import AsyncStorage from '@react-native-async-storage/async-storage';

const BASE_URL = 'http://192.168.1.100:8000';
const API_PATH = '/api/method';

class ApiService {
  constructor() {
    this.authToken = null;
  }

  // الحصول على Token
  async getAuthToken() {
    if (!this.authToken) {
      this.authToken = await AsyncStorage.getItem('auth_token');
    }
    return this.authToken;
  }

  // حفظ Token
  async saveAuthToken(token) {
    this.authToken = token;
    await AsyncStorage.setItem('auth_token', token);
  }

  // رؤوس HTTP
  async getHeaders() {
    await this.getAuthToken();
    return {
      'Content-Type': 'application/json',
      ...(this.authToken && { 'Authorization': `Bearer ${this.authToken}` }),
    };
  }

  // تسجيل الدخول
  async login(mobile, password) {
    const response = await fetch(`${BASE_URL}${API_PATH}/my_medicinal.api.patient.login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mobile, password }),
    });

    const data = await response.json();

    if (response.ok) {
      await this.saveAuthToken(data.message.auth_token);
      return data.message;
    } else {
      throw new Error(data.message || 'فشل تسجيل الدخول');
    }
  }

  // جلب الأدوية
  async getMedications(patientId) {
    const response = await fetch(
      `${BASE_URL}${API_PATH}/my_medicinal.api.medication_schedule.get_medications?patient_id=${patientId}`,
      {
        method: 'GET',
        headers: await this.getHeaders(),
      }
    );

    const data = await response.json();

    if (response.ok) {
      return data.message;
    } else {
      throw new Error('فشل جلب الأدوية');
    }
  }
}

export default new ApiService();
```

#### 2. استخدام في Component

```javascript
// screens/LoginScreen.js
import React, { useState } from 'react';
import { View, TextInput, Button, Alert } from 'react-native';
import ApiService from '../services/api';

export default function LoginScreen({ navigation }) {
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    try {
      const result = await ApiService.login(mobile, password);
      Alert.alert('نجح', result.message);
      navigation.replace('Home');
    } catch (error) {
      Alert.alert('خطأ', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <TextInput
        placeholder="رقم الجوال"
        value={mobile}
        onChangeText={setMobile}
        keyboardType="phone-pad"
      />
      <TextInput
        placeholder="كلمة المرور"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <Button
        title={loading ? "جاري التحميل..." : "دخول"}
        onPress={handleLogin}
        disabled={loading}
      />
    </View>
  );
}
```

---

## 🌐 ربط تطبيق ويب

### React.js (مثال)

#### 1. إنشاء API Service

```javascript
// src/services/api.js
const BASE_URL = 'http://localhost:8000';
const API_PATH = '/api/method';

class ApiService {
  constructor() {
    this.authToken = localStorage.getItem('auth_token');
  }

  setAuthToken(token) {
    this.authToken = token;
    localStorage.setItem('auth_token', token);
  }

  getHeaders() {
    return {
      'Content-Type': 'application/json',
      ...(this.authToken && { 'Authorization': `Bearer ${this.authToken}` }),
    };
  }

  async login(mobile, password) {
    const response = await fetch(`${BASE_URL}${API_PATH}/my_medicinal.api.patient.login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mobile, password }),
    });

    const data = await response.json();

    if (response.ok) {
      this.setAuthToken(data.message.auth_token);
      return data.message;
    } else {
      throw new Error(data.message || 'فشل تسجيل الدخول');
    }
  }

  async getProfile(patientId) {
    const response = await fetch(
      `${BASE_URL}${API_PATH}/my_medicinal.api.patient.get_profile?patient_id=${patientId}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    const data = await response.json();

    if (response.ok) {
      return data.message;
    } else {
      throw new Error('فشل جلب الملف الشخصي');
    }
  }

  async getMedications(patientId) {
    const response = await fetch(
      `${BASE_URL}${API_PATH}/my_medicinal.api.medication_schedule.get_medications?patient_id=${patientId}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    const data = await response.json();

    if (response.ok) {
      return data.message;
    } else {
      throw new Error('فشل جلب الأدوية');
    }
  }
}

export default new ApiService();
```

#### 2. استخدام في Component

```jsx
// src/components/Login.jsx
import React, { useState } from 'react';
import ApiService from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const result = await ApiService.login(mobile, password);
      console.log('تم تسجيل الدخول:', result);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h2>تسجيل الدخول</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="tel"
          placeholder="رقم الجوال"
          value={mobile}
          onChange={(e) => setMobile(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="كلمة المرور"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {error && <p style={{color: 'red'}}>{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? 'جاري التحميل...' : 'دخول'}
        </button>
      </form>
    </div>
  );
}
```

---

## 🔐 المصادقة والتوثيق

### آلية Token-Based Authentication

```
1. المستخدم يسجل دخول
   ↓
2. Backend يرجع auth_token (32+ حرف)
   ↓
3. التطبيق يحفظ Token (LocalStorage/AsyncStorage/SharedPreferences)
   ↓
4. كل طلب لاحق يرسل Token في Header
   Authorization: Bearer {auth_token}
   ↓
5. Backend يتحقق من Token ويسمح بالوصول
```

### مثال على Header الكامل

```http
POST /api/method/my_medicinal.api.medication_schedule.add_medication HTTP/1.1
Host: your-domain.com
Content-Type: application/json
Authorization: Bearer a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### إدارة Token Expiry

```javascript
// التعامل مع Token منتهي الصلاحية
async function refreshToken() {
  const response = await fetch(`${BASE_URL}/api/method/my_medicinal.api.patient.refresh_token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${oldToken}`,
    },
  });

  const data = await response.json();

  if (response.ok) {
    // حفظ Token الجديد
    localStorage.setItem('auth_token', data.message.new_token);
    return data.message.new_token;
  } else {
    // تسجيل خروج وإعادة للدخول
    window.location.href = '/login';
  }
}

// Interceptor للتعامل مع 401 Unauthorized
fetch(url, options)
  .then(response => {
    if (response.status === 401) {
      // Token منتهي الصلاحية
      return refreshToken().then(newToken => {
        // إعادة المحاولة بالToken الجديد
        options.headers.Authorization = `Bearer ${newToken}`;
        return fetch(url, options);
      });
    }
    return response;
  });
```

---

## 📚 أمثلة عملية

### مثال 1: تطبيق كامل للأدوية

```javascript
// Medication Dashboard Component
import React, { useState, useEffect } from 'react';
import ApiService from '../services/api';

export default function MedicationDashboard({ patientId }) {
  const [medications, setMedications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMedications();
  }, []);

  const loadMedications = async () => {
    try {
      const data = await ApiService.getMedications(patientId);
      setMedications(data);
    } catch (error) {
      console.error('خطأ:', error);
    } finally {
      setLoading(false);
    }
  };

  const takeMedication = async (scheduleId) => {
    try {
      await ApiService.logMedication({
        patient_id: patientId,
        schedule_id: scheduleId,
        status: 'Taken',
      });
      alert('تم تسجيل تناول الدواء');
      loadMedications(); // إعادة تحميل القائمة
    } catch (error) {
      alert('خطأ: ' + error.message);
    }
  };

  if (loading) return <div>جاري التحميل...</div>;

  return (
    <div className="medication-dashboard">
      <h2>أدويتي</h2>
      {medications.map(med => (
        <div key={med.name} className="medication-card">
          <h3>{med.medication_name}</h3>
          <p>الجرعة: {med.dosage}</p>
          <p>المتبقي: {med.current_stock} {med.stock_unit}</p>
          <p>أيام حتى النفاد: {med.days_until_depletion}</p>

          <div className="times">
            {med.times.map((time, idx) => (
              <div key={idx}>
                <span>{time.time}</span>
                <span>{time.before_after_meal}</span>
              </div>
            ))}
          </div>

          <button onClick={() => takeMedication(med.name)}>
            ✓ تم تناول الدواء
          </button>
        </div>
      ))}
    </div>
  );
}
```

### مثال 2: نظام الإشعارات (Firebase)

```javascript
// Firebase Setup (React)
import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, onMessage } from 'firebase/messaging';
import ApiService from './api';

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

// طلب صلاحية الإشعارات وتسجيل Token
export async function requestNotificationPermission() {
  try {
    const permission = await Notification.requestPermission();

    if (permission === 'granted') {
      const token = await getToken(messaging, {
        vapidKey: 'YOUR_VAPID_KEY'
      });

      console.log('FCM Token:', token);

      // تسجيل Token في Backend
      await ApiService.registerDevice(token);

      return token;
    } else {
      console.log('تم رفض صلاحية الإشعارات');
    }
  } catch (error) {
    console.error('خطأ في تسجيل الإشعارات:', error);
  }
}

// الاستماع للإشعارات الواردة
export function listenForMessages(callback) {
  onMessage(messaging, (payload) => {
    console.log('إشعار وارد:', payload);

    // عرض الإشعار
    if (callback) callback(payload);

    // أو عرض notification
    new Notification(payload.notification.title, {
      body: payload.notification.body,
      icon: '/icon.png'
    });
  });
}
```

---

## 🔧 استكشاف الأخطاء

### المشكلة 1: CORS Error

**الخطأ:**
```
Access to fetch at 'http://localhost:8000/api/method/...' from origin 'http://localhost:3000'
has been blocked by CORS policy
```

**الحل:**
```bash
# افتح site_config.json
nano sites/my_medicinal.local/site_config.json

# أضف:
{
  "allow_cors": "*",
  "cors_allowed_origins": ["http://localhost:3000"]
}

# أعد تشغيل الخادم
bench restart
```

### المشكلة 2: 401 Unauthorized

**السبب:** Token منتهي الصلاحية أو غير موجود

**الحل:**
```javascript
// تحقق من وجود Token
const token = localStorage.getItem('auth_token');
if (!token) {
  // أعد التوجيه لصفحة تسجيل الدخول
  window.location.href = '/login';
}

// أو جدد Token
await refreshToken();
```

### المشكلة 3: الخادم لا يستجيب

**الخطوات:**
```bash
# 1. تحقق من تشغيل الخادم
bench start

# 2. تحقق من المنفذ
netstat -tulpn | grep 8000

# 3. تحقق من السجلات
tail -f sites/my_medicinal.local/logs/web.log
```

### المشكلة 4: Firebase Notifications لا تعمل

**الحل:**
```bash
# 1. تحقق من وجود ملف Credentials
ls -la sites/my_medicinal.local/firebase_credentials.json

# 2. تحقق من صلاحيات الملف
chmod 600 firebase_credentials.json

# 3. فعّل FCM في .env
FCM_ENABLED=1
```

---

## 📝 ملاحظات مهمة

### للتطوير (Development)
- استخدم `http://localhost:8000` أو `http://192.168.1.X:8000` (IP الجهاز)
- فعّل CORS لجميع المصادر: `"allow_cors": "*"`
- استخدم `console.log` لمراقبة Responses

### للإنتاج (Production)
- ✅ استخدم HTTPS (`https://your-domain.com`)
- ✅ حدد CORS Domains بشكل دقيق
- ✅ فعّل Rate Limiting
- ✅ استخدم Environment Variables لل API URLs
- ✅ فعّل API Logging
- ✅ أضف Error Tracking (Sentry)

### أمان إضافي
```javascript
// تشفير البيانات الحساسة قبل الحفظ
const encryptToken = (token) => {
  // استخدم مكتبة مثل crypto-js
  return CryptoJS.AES.encrypt(token, 'secret-key').toString();
};

const decryptToken = (encryptedToken) => {
  const bytes = CryptoJS.AES.decrypt(encryptedToken, 'secret-key');
  return bytes.toString(CryptoJS.enc.Utf8);
};
```

---

## 📞 الدعم

إذا واجهت أي مشاكل:
1. راجع [API Documentation](./API_Documentation.md)
2. تحقق من السجلات: `tail -f sites/my_medicinal.local/logs/web.log`
3. اختبر Endpoints عبر Postman أو cURL
4. تواصل عبر: mohamedsuliman923@gmail.com

---

✅ **الآن تطبيقك جاهز للربط مع My_medicinal Backend!**
