# 💊 My Medicinal (Dawaii) - نظام إدارة الأمراض المزمنة

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Framework](https://img.shields.io/badge/framework-Frappe-orange.svg)
![API](https://img.shields.io/badge/API-REST-brightgreen.svg)
![Security](https://img.shields.io/badge/security-80%25-yellow.svg)

**نظام شامل لإدارة الأمراض المزمنة مع تذكيرات ذكية ومتابعة طبية**

</div>

---

## 📋 جدول المحتويات

- [نظرة عامة](#-overview)
- [المميزات](#-features)
- [متطلبات النظام](#-requirements)
- [التثبيت](#-installation)
- [الإعداد](#-configuration)
- [الأمان](#-security)
- [الاختبارات](#-testing)
- [المساهمة](#-contributing)
- [الترخيص](#-license)

---

## 🔍 Overview

**My Medicinal (Dawaii)** هو نظام متكامل لإدارة الأمراض المزمنة يوفر:

- ✅ **إدارة المرضى**: تسجيل ومتابعة معلومات المرضى
- ✅ **تذكيرات الأدوية**: إشعارات ذكية لمواعيد الأدوية (كل 5 دقائق)
- ✅ **الاستشارات الطبية**: منصة للتواصل بين المرضى والأطباء
- ✅ **متابعة الالتزام**: تتبع التزام المرضى بالعلاج
- ✅ **صيدلية إلكترونية**: طلب وتوصيل الأدوية
- ✅ **تقارير وإحصائيات**: تحليلات شاملة للأداء

### 🏗️ البنية التقنية

```
Technology Stack:
├── Backend: Frappe Framework (Python/Flask)
├── Database: MariaDB/MySQL
├── Cache: Redis
├── Push Notifications: Firebase Cloud Messaging (FCM)
├── SMS: Twilio/Unifonic
├── Payment: Stripe/PayFort/PayTabs
└── API: RESTful API with Token Authentication (32+ char tokens, 90-day expiry)
```

---

## ✨ Features

### 👥 إدارة المرضى

- تسجيل مرضى جدد بمعلومات شاملة
- ملفات طبية إلكترونية
- تتبع الأمراض المزمنة والحساسيات
- تحديث ملفات المرضى بسهولة

### 💊 إدارة الأدوية

- جداول أدوية مخصصة لكل مريض
- تذكيرات تلقائية (كل 5 دقائق)
- تتبع المخزون والكميات المتبقية
- تنبيهات نقص المخزون

### 👨‍⚕️ الاستشارات الطبية

- حجز استشارات مع الأطباء
- محادثات مباشرة
- سجل استشارات شامل
- متابعة حالة المريض

### 📊 التقارير والإحصائيات

- تقارير التزام المرضى بالعلاج
- إحصائيات الأطباء
- تحليلات شهرية
- لوحة تحكم تفاعلية

### 🔔 نظام الإشعارات

- إشعارات فورية (FCM)
- رسائل SMS
- بريد إلكتروني
- إشعارات داخل التطبيق

### 🛒 الصيدلية الإلكترونية

- تصفح الأدوية المتاحة
- البحث المتقدم
- الطلب والدفع الإلكتروني
- تتبع الطلبات

---

## 💻 Requirements

### متطلبات النظام الأساسية

```bash
- Python 3.10+
- Node.js 14+
- MariaDB 10.6+ / MySQL 8.0+
- Redis 6.0+
- Git
```

### المتطلبات الاختيارية

```bash
- Nginx (للإنتاج)
- Supervisor (لإدارة العمليات)
- Docker (للتوزيع)
```

---

## 🚀 Installation

### 1. تثبيت Frappe Framework

```bash
# Install frappe-bench
pip3 install frappe-bench

# Create a new bench
bench init my-bench --frappe-branch version-15

# Navigate to bench directory
cd my-bench
```

### 2. إنشاء Site جديد

```bash
# Create new site
bench new-site my_medicinal.local

# Use site
bench use my_medicinal.local
```

### 3. تثبيت التطبيق

```bash
# Get the app from GitHub
bench get-app https://github.com/Mohamedsulima775/My_medicinal.git

# Install app on site
bench --site my_medicinal.local install-app my_medicinal

# Migrate database
bench --site my_medicinal.local migrate
```

### 4. تشغيل الخادم

```bash
# Start development server
bench start
```

الموقع متاح على: `http://localhost:8000`

---

## ⚙️ Configuration

### 1. نسخ ملف البيئة

```bash
cp .env.example .env
```

### 2. تعديل المتغيرات البيئية

راجع [.env.example](./.env.example) للقائمة الكاملة. أهم الإعدادات:

```bash
# Database
DB_NAME=my_medicinal
DB_PASSWORD=your_secure_password

# Security
SECRET_KEY=your_32_char_secret_key
ALLOWED_CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Firebase (FCM)
FCM_ENABLED=1
FCM_SERVER_KEY=your_fcm_server_key

# SMS (Twilio)
SMS_ENABLED=1
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token

# Rate Limiting
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
API_LOGGING_ENABLED=1
```

---

## 🔒 Security

### التحسينات الأمنية المنفذة

#### ✅ Token Authentication (Phase 1)

- **طول Token**: 32+ حرف (آمن من Brute Force)
- **انتهاء الصلاحية**: 90 يوم تلقائياً
- **تجديد Token**: عبر `/api/method/refresh_token`
- **حماية**: حذف حقل password من Patient doctype

#### ✅ Rate Limiting (Phase 1)

```python
# تطبيق على:
- Login: 10 محاولات / 5 دقائق
- Registration: 5 محاولات / 5 دقائق
- قابل للتخصيص عبر .env
```

#### ✅ Security Headers (Phase 2)

```
✓ X-Content-Type-Options: nosniff
✓ X-Frame-Options: SAMEORIGIN
✓ X-XSS-Protection: 1; mode=block
✓ Strict-Transport-Security (Production)
✓ Content-Security-Policy
✓ Referrer-Policy
✓ Permissions-Policy
```

#### ✅ Request Validation (Phase 2)

- التحقق من Content-Type
- تصفية Path Traversal
- حماية من XSS
- إخفاء البيانات الحساسة من السجلات

#### ✅ Request/Response Logging (Phase 2)

- تسجيل جميع الطلبات في `API Request Log`
- إخفاء البيانات الحساسة (passwords, tokens)
- إحصائيات الأداء
- تتبع الأخطاء

### API Readiness: 80%+

---

## 🧪 Testing

### تشغيل الاختبارات

```bash
# جميع الاختبارات
bench --site my_medicinal.local run-tests --app my_medicinal

# اختبار محدد
bench --site my_medicinal.local run-tests my_medicinal.my_medicinal.doctype.patient.test_patient

# مع تقرير التغطية
bench --site my_medicinal.local run-tests --app my_medicinal --coverage
```

### الاختبارات المتاحة

#### ✅ Authentication Tests (15 tests)

- Registration (success, duplicate, invalid)
- Login (success, wrong password, non-existent)
- Token validation/expiration
- Token refresh
- Profile management
- Security tests

**التغطية**: 90%+

للمزيد: راجع [API_Documentation.md](./my_medicinal/API_Documentation.md)

---

## 🤝 Contributing

نرحب بالمساهمات!

1. Fork المشروع
2. أنشئ branch (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. افتح Pull Request

---

## 📄 License

MIT License - Copyright (c) 2024 Mohammed Suliman

---

## 📞 Contact

- **المطور**: Mohammed Suliman
- **Email**: mohamedsuliman923@gmail.com
- **GitHub**: [@Mohamedsulima775](https://github.com/Mohamedsulima775)

---

<div align="center">

**صنع بـ ❤️ في السعودية**

[![GitHub stars](https://img.shields.io/github/stars/Mohamedsulima775/My_medicinal?style=social)](https://github.com/Mohamedsulima775/My_medicinal)

</div>