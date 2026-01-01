# 🏥 Dawaii - نظام إدارة الأمراض المزمنة

<div dir="rtl">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Frappe](https://img.shields.io/badge/Frappe-v15-orange.svg)](https://frappeframework.com/)
[![Firebase](https://img.shields.io/badge/Firebase-FCM-yellow.svg)](https://firebase.google.com/)

منصة متكاملة لإدارة مرضى الأمراض المزمنة مبنية على Frappe Framework، تربط بين المرضى والأطباء والصيدليات.

</div>

---

## 📖 **جدول المحتويات**

- [نظرة عامة](#-نظرة-عامة)
- [المميزات](#-المميزات)
- [البنية التقنية](#-البنية-التقنية)
- [التثبيت](#-التثبيت)
- [التكوين](#-التكوين)
- [الاستخدام](#-الاستخدام)
- [API Documentation](#-api-documentation)
- [المساهمة](#-المساهمة)
- [الترخيص](#-الترخيص)

---

## 🌟 **نظرة عامة**

<div dir="rtl">

**Dawaii** هو نظام شامل لإدارة المرضى الذين يعانون من أمراض مزمنة، يوفر:

- ✅ **تذكيرات ذكية** للأدوية عبر Firebase Cloud Messaging
- ✅ **إدارة مخزون** آلية مع تنبيهات نفاد الدواء
- ✅ **استشارات طبية** فورية مع أطباء مختصين
- ✅ **طلب وتوصيل** الأدوية من الصيدليات
- ✅ **تقارير الالتزام** بالعلاج (Adherence Reports)
- ✅ **مهام آلية** في الخلفية (Background Jobs)

</div>

---

## ✨ **المميزات**

### **للمرضى 👤**

<div dir="rtl">

- 📱 **جدولة الأدوية** مع تذكيرات ذكية
- 💊 **تتبع المخزون** وتنبيهات النفاد
- 📊 **تقارير الالتزام** بالعلاج
- 💬 **استشارات طبية** مباشرة
- 🛒 **طلب الأدوية** أونلاين
- 📈 **سجل طبي** شامل

</div>

### **للأطباء 👨‍⚕️**

<div dir="rtl">

- 📋 **إدارة الاستشارات** والرسائل
- 💊 **كتابة الوصفات** الطبية
- 📊 **متابعة المرضى** والالتزام
- 📅 **جدول المواعيد**

</div>

### **للصيدليات 💊**

<div dir="rtl">

- 📦 **إدارة المخزون** والمنتجات
- 🛍️ **معالجة الطلبات**
- 📊 **تقارير المبيعات**

</div>

---

## 🏗️ **البنية التقنية**

### **Backend Stack**

```
├─ Frappe Framework v15
├─ Python 3.8+
├─ MariaDB/MySQL
├─ Redis
├─ Firebase Admin SDK
└─ Scheduler (Cron Jobs)
```

### **Architecture**

```
my_medicinal/
├── my_medicinal/
│   ├── doctype/           # 19 DocTypes
│   │   ├── patient/
│   │   ├── medication_schedule/
│   │   ├── medical_consultation/
│   │   ├── patient_order/
│   │   └── ...
│   │
│   ├── api/               # API Layer
│   │   ├── patient.py
│   │   ├── medication.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── consultation.py
│   │   └── ...
│   │
│   ├── tasks.py           # Background Jobs
│   ├── notifications.py   # FCM Integration
│   └── hooks.py           # Scheduler Config
│
├── firebase_credentials.json  # Firebase Config
├── requirements.txt
└── README.md
```

### **DocTypes (19 إجمالي)**

<div dir="rtl">

1. **Patient** - بيانات المريض
2. **Medication Schedule** - جدول الأدوية
3. **Medication Time** - أوقات تناول الأدوية
4. **Medication Log** - سجل تناول الأدوية
5. **Medication Reminder** - تذكيرات الأدوية
6. **Medical Consultation** - الاستشارات الطبية
7. **Consultation Message** - رسائل الاستشارات
8. **Medical Prescription** - الوصفات الطبية
9. **Prescription Item** - أدوية الوصفة
10. **Patient Order** - طلبات المرضى
11. **Order Item** - عناصر الطلب
12. **Medication Item** - قائمة الأدوية
13. **Medication Category** - تصنيفات الأدوية
14. **Healthcare Provider** - الأطباء
15. **Provider Schedule** - جداول الأطباء
16. **Adherence Report** - تقارير الالتزام
17. **Notification Log** - سجل الإشعارات
18. **API Key** - مفاتيح API + FCM Tokens
19. **Chronic Disease** - الأمراض المزمنة

</div>

---

## 🚀 **التثبيت**

### **المتطلبات**

```bash
- Python 3.8+
- Node.js 16+
- MariaDB 10.6+
- Redis
- Git
```

### **1. تثبيت Frappe**

```bash
# Install bench
pip3 install frappe-bench

# Initialize bench
bench init frappe-bench --frappe-branch version-15

# Create site
cd frappe-bench
bench new-site dawaii.local
```

### **2. Clone المشروع**

```bash
# Get app from GitHub
bench get-app https://github.com/Mohamedsulima775/My_medicinal.git

# Install app on site
bench --site dawaii.local install-app my_medicinal
```

### **3. تثبيت Dependencies**

```bash
# Python packages
pip install firebase-admin --break-system-packages

# أو من requirements.txt
pip install -r apps/my_medicinal/requirements.txt --break-system-packages
```

### **4. Firebase Setup**

```bash
# 1. إنشاء Firebase Project على console.firebase.google.com
# 2. تحميل Service Account JSON
# 3. وضعه في:
cp path/to/firebase-key.json apps/my_medicinal/firebase_credentials.json

# 4. إضافة لـ .gitignore
echo "firebase_credentials.json" >> apps/my_medicinal/.gitignore
```

### **5. تفعيل Scheduler**

```bash
# Enable scheduler
bench --site dawaii.local enable-scheduler

# Restart
bench restart
```

---

## ⚙️ **التكوين**

### **1. Database**

```bash
# Migrate database
bench --site dawaii.local migrate
```

### **2. Scheduler Events**

في `hooks.py`:

```python
scheduler_events = {
    "cron": {
        "*/5 * * * *": [
            "my_medicinal.my_medicinal.tasks.send_medication_reminders"
        ]
    },
    "daily": [
        "my_medicinal.my_medicinal.tasks.all"
    ],
    "weekly": [
        "my_medicinal.my_medicinal.tasks.cleanup_old_notifications"
    ]
}
```

### **3. API Configuration**

Base URL:
```
https://your-domain.com/api/method/
```

Authentication:
```http
Authorization: Bearer {token}
```

---

## 💻 **الاستخدام**

### **تشغيل Development Server**

```bash
bench start
```

### **Testing APIs**

```bash
# Register patient
curl -X POST http://localhost:8000/api/method/my_medicinal.api.patient.register \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "أحمد محمد",
    "mobile": "0512345678",
    "email": "ahmed@example.com",
    "password": "SecurePass123!"
  }'

# Login
curl -X POST http://localhost:8000/api/method/my_medicinal.api.patient.login \
  -H "Content-Type: application/json" \
  -d '{
    "mobile": "0512345678",
    "password": "SecurePass123!"
  }'
```

### **Manual Task Testing**

```bash
# Open console
bench --site dawaii.local console

# Test medication reminders
>>> from my_medicinal.my_medicinal.tasks import send_medication_reminders
>>> send_medication_reminders()

# Test stock check
>>> from my_medicinal.my_medicinal.tasks import check_stock_depletion
>>> check_stock_depletion()
```

---

## 📚 **API Documentation**

<div dir="rtl">

التوثيق الكامل لـ APIs متوفر في: **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)**

### **الأقسام الرئيسية:**

- 🔐 **Authentication** (2 endpoints)
- 👤 **Patient APIs** (4 endpoints)
- 💊 **Medication APIs** (7 endpoints)
- 🛒 **Product APIs** (3 endpoints)
- 🛍️ **Order APIs** (2 endpoints)
- 💬 **Consultation APIs** (4 endpoints)
- 👨‍⚕️ **Provider APIs** (2 endpoints)
- 📋 **Prescription APIs** (2 endpoints)
- 🔔 **Notification APIs** (4 endpoints)

**المجموع: 28+ API Endpoint**

</div>

---

## 🔧 **Background Jobs**

### **Automated Tasks**

| Task | Schedule | Description |
|------|----------|-------------|
| Medication Reminders | Every 5 min | إرسال تذكيرات الأدوية |
| Stock Depletion Check | Daily | فحص نفاد المخزون |
| Adherence Reports | Daily | تقارير الالتزام بالعلاج |
| Cleanup Notifications | Weekly | حذف الإشعارات القديمة |

### **Monitoring**

```bash
# Check scheduler status
bench --site dawaii.local scheduler status

# View logs
bench --site dawaii.local scheduler --verbose

# Enable/Disable
bench --site dawaii.local enable-scheduler
bench --site dawaii.local disable-scheduler
```

---

## 🔔 **Notifications**

### **Firebase Cloud Messaging**

<div dir="rtl">

- ✅ Push Notifications للأجهزة المحمولة
- ✅ Topics للإشعارات الجماعية
- ✅ Device registration عبر API
- ✅ تكامل مع Background Tasks

</div>

### **Notification Types**

<div dir="rtl">

- 💊 تذكيرات الأدوية
- 📦 تنبيهات نفاد المخزون
- 💬 رسائل الاستشارات
- 🛍️ تحديثات الطلبات
- 📊 تقارير الالتزام

</div>

---

## 📊 **Features Status**

| Feature | Status | Progress |
|---------|--------|----------|
| Patient Management | ✅ Complete | 100% |
| Medication Schedule | ✅ Complete | 100% |
| Background Jobs | ✅ Complete | 100% |
| FCM Notifications | ✅ Complete | 100% |
| Consultations | ✅ Complete | 100% |
| Orders | ✅ Complete | 100% |
| Products | ✅ Complete | 100% |
| Prescriptions | ✅ Complete | 100% |
| API Documentation | ✅ Complete | 100% |
| **Overall** | **✅ Production Ready** | **95%** |

---

## 🧪 **Testing**

### **Unit Tests**

```bash
# Run tests
bench --site dawaii.local run-tests --app my_medicinal

# Specific doctype
bench --site dawaii.local run-tests --doctype "Medication Schedule"
```

### **Manual Testing Checklist**

<div dir="rtl">

- [ ] تسجيل مريض جديد
- [ ] تسجيل دخول
- [ ] إضافة دواء للجدول
- [ ] تسجيل تناول دواء
- [ ] إنشاء طلب
- [ ] إنشاء استشارة
- [ ] استلام إشعار تذكير
- [ ] فحص تقرير الالتزام

</div>

---

## 🚀 **Deployment**

### **Production Setup**

```bash
# Production config
bench setup production your-user

# SSL
bench setup lets-encrypt dawaii.com

# Start services
sudo systemctl enable nginx
sudo systemctl enable supervisor
```

### **Environment Variables**

```bash
# In site_config.json
{
  "db_name": "dawaii_production",
  "db_password": "secure_password",
  "host_name": "https://dawaii.com",
  "firebase_credentials_path": "/path/to/firebase.json"
}
```

---

## 🤝 **المساهمة**

<div dir="rtl">

نرحب بمساهماتك! يرجى اتباع الخطوات التالية:

1. Fork المشروع
2. إنشاء Branch جديد (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add some AmazingFeature'`)
4. Push للـ Branch (`git push origin feature/AmazingFeature`)
5. فتح Pull Request

</div>

### **Code Style**

- Python: PEP 8
- JavaScript: ESLint
- Commits: Conventional Commits

---

## 📞 **الدعم**

<div dir="rtl">

- **Email:** mohamedsuliman923@gmail.com
- **GitHub Issues:** [Report Issue](https://github.com/Mohamedsulima775/My_medicinal/issues)
- **Documentation:** [Frappe Docs](https://frappeframework.com/docs)

</div>

---

## 📝 **الترخيص**

<div dir="rtl">

هذا المشروع مرخص تحت **MIT License** - انظر ملف [LICENSE](license.txt) للتفاصيل.

</div>

---

## 🙏 **شكر وتقدير**

<div dir="rtl">

- **Frappe Framework** - البنية الأساسية
- **Firebase** - خدمات الإشعارات
- **المساهمون** - جميع من ساهم في المشروع

</div>

---

## 📈 **Roadmap**

### **Version 2.0 (Q1 2026)**

<div dir="rtl">

- [ ] تطبيق Flutter للمرضى
- [ ] لوحة تحكم للأطباء
- [ ] تكامل مع بوابات الدفع
- [ ] تقارير تحليلية متقدمة
- [ ] AI-powered medication recommendations
- [ ] Multi-language support (English)

</div>

---

## 📊 **Statistics**

```
Lines of Code:     ~5,000
API Endpoints:     28+
DocTypes:          19
Background Jobs:   4
Tests:             In Progress
Documentation:     Complete
```

---

## 🏆 **Acknowledgments**

<div dir="rtl">

تم بناء هذا المشروع بـ ❤️ في اليمن

**التطوير:**
- Backend: محمد سليمان حامد الشميري
- Flutter: عبدالرحمن عارف الشميري
- Documentation: Claude AI (Anthropic)

**الإصدار:** 1.0  
**التاريخ:** ديسمبر 2025

</div>

---

<div align="center">

**⭐ إذا أعجبك المشروع، لا تنسى النجمة على GitHub! ⭐**

</div>