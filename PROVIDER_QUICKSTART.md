# Healthcare Provider Environment - Quick Start
# دليل البدء السريع - بيئة مقدم الرعاية الصحية

## 🚀 Quick Setup (3 Minutes)

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
./setup_provider_env.sh my_medicinal.local
```

The script will:
- ✅ Create `.env.provider` configuration file
- ✅ Validate all Python files
- ✅ Initialize Healthcare Provider role
- ✅ Setup permissions and workspace
- ✅ Configure dashboard and notifications

### Option 2: Manual Setup

```bash
# 1. Copy environment file
cp .env.provider.example .env.provider

# 2. Edit configuration (optional)
nano .env.provider

# 3. Initialize environment
bench --site my_medicinal.local execute \
  my_medicinal.my_medicinal.provider_environment.initialize_provider_environment
```

---

## 👨‍⚕️ Create Your First Healthcare Provider

### Method 1: Using Bench Console

```bash
bench --site my_medicinal.local console
```

```python
# Create provider
provider = frappe.get_doc({
    "doctype": "Healthcare Provider",
    "provider_name": "Dr. Ahmed Ali",
    "user": "ahmed@clinic.com",  # Must exist in User
    "specialty": "Cardiology",
    "qualifications": "MBBS, MD",
    "experience_years": 10,
    "consultation_fee": 300,
    "is_available": 1,
    "license_number": "SC-12345"
})
provider.insert()
frappe.db.commit()
print(f"✅ Provider created: {provider.name}")
```

### Method 2: Using UI

1. Go to: `/app/healthcare-provider`
2. Click "New"
3. Fill in:
   - Provider Name
   - User (select existing user)
   - Specialty
   - Qualifications
   - Experience Years
   - Consultation Fee
   - License Number
4. Save

---

## 🔐 Assign Role to User

```python
# In bench console
user = frappe.get_doc("User", "ahmed@clinic.com")
user.append("roles", {"role": "Healthcare Provider"})
user.save()
frappe.db.commit()
```

Or via UI:
1. Go to User List
2. Select user
3. Add role "Healthcare Provider"
4. Save

---

## 🌐 Access Provider Portal

**URL:** `http://localhost:8000/app/healthcare-provider-portal`

**Login:**
- Email: ahmed@clinic.com
- Password: [user's password]

---

## 📊 What You Get

### Dashboard Features
- 📅 Today's consultations
- 📝 Pending requests
- 👥 Total patients
- 📈 Monthly statistics
- 💊 Prescriptions overview

### Core Features
- ✅ Accept/manage consultations
- ✅ Video consultations
- ✅ Write digital prescriptions
- ✅ View patient histories
- ✅ Manage schedule
- ✅ Generate reports

---

## ⚙️ Essential Configuration

Edit `.env.provider` for these key settings:

```bash
# Portal
PROVIDER_PORTAL_ENABLED=1

# Security
PROVIDER_SESSION_TIMEOUT=28800  # 8 hours
PROVIDER_2FA_REQUIRED=1         # Require 2FA

# Consultations
VIDEO_CONSULTATION_ENABLED=1
MAX_SIMULTANEOUS_CONSULTATIONS=5

# Prescriptions
PRESCRIPTION_DIGITAL_SIGNATURE_REQUIRED=1
PRESCRIPTION_VALIDITY_DAYS=30

# Schedule
PROVIDER_SELF_SCHEDULE_ENABLED=1
DEFAULT_SLOT_DURATION=30
DEFAULT_WORKING_HOURS_START=09:00
DEFAULT_WORKING_HOURS_END=17:00

# Language
PROVIDER_PORTAL_LANGUAGE=ar  # ar or en
PROVIDER_RTL_ENABLED=1       # Right-to-left
```

---

## 🧪 Test Mode

Enable test mode for sample data:

```bash
# In .env.provider
PROVIDER_TEST_MODE=1
```

Then run initialization again to create:
- Test provider account
- Sample consultations
- Sample prescriptions

---

## ✅ Verify Setup

```bash
bench --site my_medicinal.local console
```

```python
# Check status
from my_medicinal.my_medicinal.provider_environment import get_provider_environment_status
status = get_provider_environment_status()
print(status)

# Expected output:
# {
#   "role_exists": True,
#   "workspace_exists": True,
#   "provider_count": 1,
#   "active_providers": 1,
#   "config_loaded": True
# }
```

---

## 🔧 Common Tasks

### Update Provider Availability

```python
# Via API
POST /api/method/my_medicinal.api.provider.update_my_profile
{
    "is_available": 1,
    "availability_note": "Available Mon-Thu 9AM-5PM"
}
```

### Create Consultation

Consultations are created by patients, providers can:
- Accept/reject requests
- Start consultation
- Send messages
- Write prescription
- Close with diagnosis

### Write Prescription

```python
POST /api/method/my_medicinal.api.provider.create_prescription
{
    "consultation_id": "CONS-00001",
    "patient": "PAT-00001",
    "medications": [
        {
            "medication_item": "Aspirin 100mg",
            "dosage": "1 tablet",
            "frequency": "Once daily",
            "duration_days": 30
        }
    ]
}
```

---

## 📱 Mobile Access

The provider portal is mobile-responsive:
- Works on tablets and phones
- Touch-optimized interface
- Supports biometric login (if configured)

---

## 🔒 Security Best Practices

1. **Enable 2FA:** `PROVIDER_2FA_REQUIRED=1`
2. **Use strong passwords:** Minimum 12 characters
3. **Whitelist IPs (if applicable):** `PROVIDER_IP_WHITELIST=x.x.x.x`
4. **Review audit logs regularly**
5. **Keep license information updated**

---

## 🐛 Quick Troubleshooting

### Cannot login?
```bash
# Check user has role
bench --site my_medicinal.local console
frappe.get_roles("user@email.com")
```

### Portal not showing?
```bash
# Clear cache
bench --site my_medicinal.local clear-cache

# Rebuild
bench --site my_medicinal.local build
```

### Permission errors?
```bash
# Re-run initialization
bench --site my_medicinal.local execute \
  my_medicinal.my_medicinal.provider_environment.initialize_provider_environment
```

---

## 📚 Full Documentation

For complete documentation, see:
- [PROVIDER_ENVIRONMENT.md](./PROVIDER_ENVIRONMENT.md) - Complete guide
- [README.md](./README.md) - Main project README
- [API Documentation](./API_DOCUMENTATION.md) - API reference

---

## 🇸🇦 البدء السريع بالعربية

### التثبيت

```bash
# تشغيل سكريبت التثبيت
./setup_provider_env.sh my_medicinal.local
```

### إنشاء مقدم خدمة

```python
provider = frappe.get_doc({
    "doctype": "Healthcare Provider",
    "provider_name": "د. أحمد علي",
    "user": "ahmed@clinic.com",
    "specialty": "أمراض القلب",
    "qualifications": "بكالوريوس طب وجراحة، دكتوراه",
    "experience_years": 10,
    "consultation_fee": 300,
    "is_available": 1,
    "license_number": "SC-12345"
})
provider.insert()
frappe.db.commit()
```

### الوصول للبوابة

```
http://localhost:8000/app/healthcare-provider-portal
```

### الإعدادات الأساسية

```bash
PROVIDER_PORTAL_ENABLED=1              # تفعيل البوابة
PROVIDER_PORTAL_LANGUAGE=ar            # اللغة العربية
PROVIDER_RTL_ENABLED=1                 # الكتابة من اليمين لليسار
VIDEO_CONSULTATION_ENABLED=1           # الاستشارات المرئية
```

---

## 💬 Support

- **Documentation:** See PROVIDER_ENVIRONMENT.md
- **Issues:** GitHub Issues
- **Email:** support@dawaii.com

---

**Setup Time:** ~3 minutes
**Version:** 1.0.0
**Last Updated:** 2026-01-10
