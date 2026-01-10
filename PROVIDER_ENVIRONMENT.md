# Healthcare Provider Environment
# بيئة مقدم الرعاية الصحية

Complete guide for setting up and using the Healthcare Provider environment in My Medicinal (Dawaii).

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Environment Configuration](#environment-configuration)
4. [Initialization](#initialization)
5. [Features](#features)
6. [Security](#security)
7. [API Endpoints](#api-endpoints)
8. [Troubleshooting](#troubleshooting)
9. [Arabic Guide](#arabic-guide)

---

## 🎯 Overview

The Healthcare Provider Environment is a dedicated, secure workspace for doctors and healthcare professionals to:

- Manage patient consultations
- Write and manage prescriptions
- Access patient medical histories
- View schedules and appointments
- Monitor patient adherence to treatment plans
- Generate reports and analytics

### Key Features

✅ **Dedicated Portal** - Custom workspace with provider-specific tools
✅ **Enhanced Security** - Extended sessions, IP whitelisting, 2FA support
✅ **Role-Based Access** - Granular permissions for patient data
✅ **Activity Audit** - Complete logging of all provider activities
✅ **Higher Rate Limits** - 500 requests/minute (vs 100 for patients)
✅ **Video Consultations** - Integrated telemedicine support
✅ **Digital Signatures** - E-prescription with digital signature validation
✅ **Multi-language** - Full Arabic and English support

---

## 🚀 Quick Start

### Step 1: Copy Environment File

```bash
cd /home/user/My_medicinal
cp .env.provider.example .env.provider
```

### Step 2: Configure Settings

Edit `.env.provider` and set your desired configuration:

```bash
# Essential settings to configure
PROVIDER_PORTAL_ENABLED=1
PROVIDER_SESSION_TIMEOUT=28800  # 8 hours
PROVIDER_2FA_REQUIRED=1         # Enable 2FA
VIDEO_CONSULTATION_ENABLED=1    # Enable video calls
```

### Step 3: Initialize Environment

```bash
# Using bench command
bench --site [your-site-name] execute my_medicinal.my_medicinal.provider_environment.initialize_provider_environment

# Example:
bench --site my_medicinal.local execute my_medicinal.my_medicinal.provider_environment.initialize_provider_environment
```

### Step 4: Create Healthcare Provider

```bash
# Via bench console
bench --site [your-site-name] console

# Then in console:
provider = frappe.get_doc({
    "doctype": "Healthcare Provider",
    "provider_name": "Dr. Ahmed Ali",
    "user": "ahmed@example.com",  # Must be existing user
    "specialty": "Cardiology",
    "qualifications": "MBBS, MD (Cardiology)",
    "experience_years": 10,
    "consultation_fee": 300,
    "is_available": 1,
    "license_number": "SC-12345"
})
provider.insert()
frappe.db.commit()
```

### Step 5: Access Provider Portal

Navigate to: `http://localhost:8000/app/healthcare-provider-portal`

---

## ⚙️ Environment Configuration

### Core Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `PROVIDER_PORTAL_ENABLED` | `1` | Enable/disable provider portal |
| `PROVIDER_PORTAL_URL` | `/provider` | Portal URL path |
| `PROVIDER_DASHBOARD_REFRESH_INTERVAL` | `30` | Dashboard refresh (seconds) |

### Authentication & Security

| Variable | Default | Description |
|----------|---------|-------------|
| `PROVIDER_SESSION_TIMEOUT` | `28800` | Session timeout (8 hours) |
| `PROVIDER_2FA_REQUIRED` | `1` | Require two-factor auth |
| `PROVIDER_RATE_LIMIT_MAX_REQUESTS` | `500` | Rate limit per window |
| `PROVIDER_RATE_LIMIT_WINDOW` | `60` | Rate limit window (seconds) |
| `PROVIDER_IP_WHITELIST` | `` | Allowed IPs (comma-separated) |
| `PROVIDER_LOGIN_AUDIT_ENABLED` | `1` | Log all login attempts |

### Consultation Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `PROVIDER_AUTO_ACCEPT_CONSULTATIONS` | `0` | Auto-accept requests |
| `CONSULTATION_TIMEOUT` | `30` | Timeout (minutes) |
| `VIDEO_CONSULTATION_ENABLED` | `1` | Enable video calls |
| `MAX_SIMULTANEOUS_CONSULTATIONS` | `5` | Max concurrent consultations |

### Prescription Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `PRESCRIPTION_DIGITAL_SIGNATURE_REQUIRED` | `1` | Require digital signature |
| `PRESCRIPTION_VALIDITY_DAYS` | `30` | Prescription validity period |
| `CONTROLLED_SUBSTANCES_ALLOWED` | `0` | Allow controlled substances |
| `PRESCRIPTION_AUDIT_TRAIL_ENABLED` | `1` | Log all prescriptions |

### Schedule Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `PROVIDER_SELF_SCHEDULE_ENABLED` | `1` | Self-manage schedule |
| `DEFAULT_SLOT_DURATION` | `30` | Appointment slot (minutes) |
| `DEFAULT_WORKING_HOURS_START` | `09:00` | Work day start time |
| `DEFAULT_WORKING_HOURS_END` | `17:00` | Work day end time |
| `DEFAULT_WORKING_DAYS` | `0,1,2,3,4` | Working days (Sun-Thu) |

### Notification Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `PROVIDER_NOTIFICATION_EMAIL` | `1` | Email notifications |
| `PROVIDER_NOTIFICATION_SMS` | `1` | SMS notifications |
| `PROVIDER_NOTIFICATION_PUSH` | `1` | Push notifications |
| `NOTIFY_NEW_CONSULTATION_REQUEST` | `1` | Notify on new requests |
| `NOTIFY_PATIENT_MESSAGE` | `1` | Notify on patient messages |

---

## 🔧 Initialization

### Automated Initialization

The initialization script sets up:

1. ✅ Healthcare Provider role
2. ✅ Granular permissions for all doctypes
3. ✅ Custom workspace with shortcuts
4. ✅ Dashboard with charts and analytics
5. ✅ API configurations and rate limits
6. ✅ Notification rules
7. ✅ Sample test data (if test mode enabled)

### Manual Initialization

You can also initialize components individually:

```python
import frappe
from my_medicinal.my_medicinal.provider_environment import *

# Initialize specific components
setup_provider_role()
setup_provider_permissions()
create_provider_workspace()
setup_provider_dashboard()
```

### Check Status

```python
from my_medicinal.my_medicinal.provider_environment import get_provider_environment_status

status = get_provider_environment_status()
print(status)
```

Output:
```json
{
  "role_exists": true,
  "workspace_exists": true,
  "provider_count": 5,
  "active_providers": 3,
  "config_loaded": true
}
```

---

## 🎨 Features

### 1. Provider Dashboard

**Location:** `/app/healthcare-provider-portal`

**Widgets:**
- Today's consultations
- Pending consultation requests
- Total patients managed
- Monthly consultation stats
- Patient adherence metrics
- Revenue analytics (if billing enabled)

### 2. Consultation Management

**Features:**
- View pending consultation requests
- Accept/reject consultations
- Conduct video consultations
- Exchange messages with patients
- View patient medical history
- Close consultations with diagnosis

**API Endpoints:**
```python
# Get my consultations
GET /api/method/my_medicinal.api.provider.get_my_consultations

# Get consultation details
GET /api/method/my_medicinal.api.provider.get_consultation_details
    ?consultation_id=CONS-00001

# Update consultation status
POST /api/method/my_medicinal.api.provider.update_consultation
    consultation_id: CONS-00001
    status: "In Progress"
```

### 3. Prescription Management

**Features:**
- Create digital prescriptions
- Add medications with dosage instructions
- Digital signature validation
- Auto-send to patient
- Track prescription fulfillment
- View prescription history

**API Endpoints:**
```python
# Create prescription
POST /api/method/my_medicinal.api.provider.create_prescription
    consultation_id: CONS-00001
    patient: PAT-00001
    medications: [
        {
            "medication": "Aspirin 100mg",
            "dosage": "1 tablet",
            "frequency": "Once daily",
            "duration": "30 days"
        }
    ]

# Get my prescriptions
GET /api/method/my_medicinal.api.provider.get_my_prescriptions
```

### 4. Patient Management

**Features:**
- View patient list (only consulted patients)
- Access patient medical history
- View medication schedules
- Check adherence reports
- Patient search functionality

**API Endpoints:**
```python
# Get my patients
GET /api/method/my_medicinal.api.provider.get_my_patients

# Get patient details
GET /api/method/my_medicinal.api.provider.get_patient_details
    ?patient_id=PAT-00001
```

### 5. Schedule Management

**Features:**
- Set working hours
- Define available time slots
- Block specific dates/times
- View appointment calendar
- Manage recurring schedules

**API Endpoints:**
```python
# Get my schedule
GET /api/method/my_medicinal.api.provider.get_my_schedule

# Update schedule
POST /api/method/my_medicinal.api.provider.update_schedule
    working_days: [0,1,2,3,4]  # Sunday to Thursday
    start_time: "09:00"
    end_time: "17:00"
    slot_duration: 30
```

---

## 🔒 Security

### Authentication

**Session Management:**
- Extended 8-hour sessions for providers
- Auto-refresh on activity
- Secure cookie handling

**Two-Factor Authentication:**
```bash
# Enable 2FA requirement in .env.provider
PROVIDER_2FA_REQUIRED=1
```

### Authorization

**Role-Based Access Control:**
- Providers can only access patients they've consulted
- No access to other providers' data
- Read-only access to patient demographic data
- Full access to own consultations and prescriptions

**Permission Matrix:**

| DocType | Read | Write | Create | Delete | Submit |
|---------|------|-------|--------|--------|--------|
| Medical Consultation | ✅ Own | ✅ Own | ✅ | ❌ | ✅ Own |
| Medical Prescription | ✅ Own | ✅ Own | ✅ | ❌ | ✅ Own |
| Patient | ✅ Limited | ❌ | ❌ | ❌ | ❌ |
| Healthcare Provider | ✅ Own | ✅ Own | ❌ | ❌ | ❌ |

### Activity Auditing

**Logged Activities:**
- Login/logout events
- Patient data access
- Consultation actions
- Prescription creation
- Schedule changes

**View Audit Log:**
```python
@frappe.whitelist()
def get_my_activity_log(days=7):
    """Returns last 7 days of activity"""
    pass

# API call
GET /api/method/my_medicinal.my_medicinal.provider_middleware.get_my_activity_log
    ?days=30
```

### Data Privacy

**HIPAA Compliance Mode:**
```bash
HIPAA_COMPLIANCE_MODE=1
AUDIT_ALL_PATIENT_DATA_ACCESS=1
PATIENT_NOTES_ENCRYPTION_ENABLED=1
```

**Data Retention:**
```bash
PATIENT_DATA_RETENTION_YEARS=10
CONSULTATION_RECORD_RETENTION_YEARS=7
PROVIDER_ACTIVITY_LOG_RETENTION_DAYS=180
```

### IP Whitelisting

**Configuration:**
```bash
# Restrict access to specific IPs
PROVIDER_IP_WHITELIST=192.168.1.100,192.168.1.101,10.0.0.50

# Leave empty to allow all IPs
PROVIDER_IP_WHITELIST=
```

---

## 🔌 API Endpoints

### Provider Profile

```python
# Get my profile
GET /api/method/my_medicinal.api.provider.get_my_profile

# Update my profile
POST /api/method/my_medicinal.api.provider.update_my_profile
    consultation_fee: 350
    is_available: 1
    availability_note: "Available Mon-Thu 9AM-5PM"
```

### Consultations

```python
# Get pending requests
GET /api/method/my_medicinal.api.provider.get_pending_consultation_requests

# Accept consultation
POST /api/method/my_medicinal.api.provider.accept_consultation
    consultation_id: CONS-00001

# Reject consultation
POST /api/method/my_medicinal.api.provider.reject_consultation
    consultation_id: CONS-00001
    reason: "Schedule conflict"

# Start consultation
POST /api/method/my_medicinal.api.provider.start_consultation
    consultation_id: CONS-00001

# Complete consultation
POST /api/method/my_medicinal.api.provider.complete_consultation
    consultation_id: CONS-00001
    diagnosis: "Hypertension - Stage 1"
    notes: "Patient counseled on lifestyle modifications"
```

### Prescriptions

```python
# Get my prescriptions
GET /api/method/my_medicinal.api.provider.get_my_prescriptions
    ?status=active&limit=20

# Get prescription details
GET /api/method/my_medicinal.api.provider.get_prescription_details
    ?prescription_id=PRESC-00001

# Create prescription
POST /api/method/my_medicinal.api.provider.create_prescription
    {
        "consultation_id": "CONS-00001",
        "patient": "PAT-00001",
        "medications": [
            {
                "medication_item": "Aspirin 100mg",
                "dosage": "1 tablet",
                "frequency": "Once daily after breakfast",
                "duration_days": 30,
                "quantity": 30,
                "instructions": "Take with food"
            }
        ],
        "notes": "Follow up in 2 weeks"
    }
```

### Analytics

```python
# Get dashboard statistics
GET /api/method/my_medicinal.api.provider.get_my_statistics

Response:
{
    "total_consultations": 156,
    "active_consultations": 8,
    "total_patients": 92,
    "total_prescriptions": 134,
    "avg_rating": 4.7,
    "this_month_consultations": 24,
    "patient_adherence_avg": 85.3
}

# Get consultation analytics
GET /api/method/my_medicinal.api.provider.get_consultation_analytics
    ?period=month

# Get patient adherence report
GET /api/method/my_medicinal.api.provider.get_adherence_report
    ?patient_id=PAT-00001
```

---

## 🐛 Troubleshooting

### Issue: Cannot access provider portal

**Solution:**
1. Verify user has Healthcare Provider role:
   ```python
   frappe.get_roles(frappe.session.user)
   ```
2. Check Healthcare Provider record exists:
   ```python
   frappe.db.exists("Healthcare Provider", {"user": "user@example.com"})
   ```
3. Verify environment is initialized:
   ```python
   from my_medicinal.my_medicinal.provider_environment import get_provider_environment_status
   status = get_provider_environment_status()
   ```

### Issue: Rate limit exceeded

**Solution:**
Increase rate limits in `.env.provider`:
```bash
PROVIDER_RATE_LIMIT_MAX_REQUESTS=1000
PROVIDER_RATE_LIMIT_WINDOW=60
```

### Issue: Session expires too quickly

**Solution:**
Increase session timeout:
```bash
PROVIDER_SESSION_TIMEOUT=43200  # 12 hours
```

### Issue: Cannot access patient data

**Solution:**
1. Provider can only access patients they've consulted with
2. Check consultation exists:
   ```python
   frappe.db.exists("Medical Consultation", {
       "healthcare_provider": "PROV-00001",
       "patient": "PAT-00001"
   })
   ```

### Issue: Workspace not showing

**Solution:**
1. Clear cache:
   ```bash
   bench --site [site-name] clear-cache
   ```
2. Rebuild workspace:
   ```python
   from my_medicinal.my_medicinal.provider_environment import create_provider_workspace
   create_provider_workspace()
   ```

---

## 🇸🇦 Arabic Guide / الدليل بالعربية

### نظرة عامة

بيئة مقدم الرعاية الصحية هي منصة مخصصة وآمنة للأطباء والمهنيين الصحيين لإدارة:

- استشارات المرضى
- الوصفات الطبية
- السجلات الطبية
- المواعيد والجداول
- تقارير الالتزام بالعلاج

### التثبيت السريع

#### 1. نسخ ملف البيئة

```bash
cp .env.provider.example .env.provider
```

#### 2. تهيئة الإعدادات

عدّل ملف `.env.provider` وقم بضبط الإعدادات:

```bash
PROVIDER_PORTAL_ENABLED=1              # تفعيل بوابة مقدم الخدمة
PROVIDER_SESSION_TIMEOUT=28800         # مدة الجلسة (8 ساعات)
PROVIDER_2FA_REQUIRED=1                # تفعيل المصادقة الثنائية
VIDEO_CONSULTATION_ENABLED=1           # تفعيل الاستشارات المرئية
PROVIDER_PORTAL_LANGUAGE=ar            # اللغة العربية
```

#### 3. تهيئة البيئة

```bash
bench --site [اسم-الموقع] execute my_medicinal.my_medicinal.provider_environment.initialize_provider_environment
```

#### 4. إنشاء سجل مقدم خدمة

```bash
bench --site [اسم-الموقع] console
```

```python
provider = frappe.get_doc({
    "doctype": "Healthcare Provider",
    "provider_name": "د. أحمد علي",
    "user": "ahmed@example.com",
    "specialty": "أمراض القلب",
    "qualifications": "بكالوريوس طب وجراحة، دكتوراه في أمراض القلب",
    "experience_years": 10,
    "consultation_fee": 300,
    "is_available": 1,
    "license_number": "SC-12345"
})
provider.insert()
frappe.db.commit()
```

### الوصول إلى البوابة

```
http://localhost:8000/app/healthcare-provider-portal
```

### الميزات الرئيسية

#### 1. لوحة المعلومات
- استشارات اليوم
- الطلبات المعلقة
- إحصائيات المرضى
- تحليلات الإيرادات

#### 2. إدارة الاستشارات
- قبول/رفض الطلبات
- إجراء استشارات مرئية
- التواصل مع المرضى
- عرض السجل الطبي

#### 3. إدارة الوصفات
- كتابة وصفات رقمية
- التوقيع الإلكتروني
- إرسال تلقائي للمريض
- تتبع صرف الوصفة

#### 4. إدارة الجدول
- تحديد ساعات العمل
- إدارة المواعيد
- حجز الأوقات

### الأمان

#### المصادقة الثنائية
```bash
PROVIDER_2FA_REQUIRED=1
```

#### تسجيل الأنشطة
جميع الأنشطة يتم تسجيلها للتدقيق:
- تسجيل الدخول/الخروج
- الوصول لبيانات المرضى
- إنشاء الوصفات
- تحديث الاستشارات

#### الامتثال للأنظمة
```bash
MOH_INTEGRATION_ENABLED=1              # التكامل مع وزارة الصحة
SCFHS_LICENSE_VERIFICATION=1           # التحقق من ترخيص الهيئة السعودية
HIPAA_COMPLIANCE_MODE=1                # وضع الامتثال للخصوصية
```

### نقاط الاتصال API

#### الملف الشخصي
```
GET /api/method/my_medicinal.api.provider.get_my_profile
POST /api/method/my_medicinal.api.provider.update_my_profile
```

#### الاستشارات
```
GET /api/method/my_medicinal.api.provider.get_my_consultations
POST /api/method/my_medicinal.api.provider.accept_consultation
POST /api/method/my_medicinal.api.provider.complete_consultation
```

#### الوصفات
```
GET /api/method/my_medicinal.api.provider.get_my_prescriptions
POST /api/method/my_medicinal.api.provider.create_prescription
```

### الدعم الفني

للمساعدة أو الإبلاغ عن مشاكل:
- GitHub: https://github.com/mohamedsulima775/my_medicinal
- Email: support@dawaii.com

---

## 📚 Additional Resources

- [Main README](./README.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Frappe Framework Docs](https://frappeframework.com/docs)
- [Healthcare Provider DocType](./my_medicinal/my_medicinal/doctype/healthcare_provider/)

---

## 📝 License

This project is licensed under the MIT License.

---

## 👥 Support

For issues or questions:
- Create an issue on GitHub
- Email: support@dawaii.com
- Documentation: https://docs.dawaii.com

---

**Last Updated:** 2026-01-10
**Version:** 1.0.0
**Author:** Mohammed Suliman
