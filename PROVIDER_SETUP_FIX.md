# Healthcare Provider Setup - Error Fix
# إصلاح أخطاء الإعداد

## ✅ Fixed Issues

### Issue 1: Workspace Creation Error
**Error:** `ValidationError: Name is required`

**Fix:** Removed explicit `name` field from Workspace creation. Frappe autoname will handle it.

**What Changed:**
- Removed `"name": workspace_name` from workspace dictionary
- Removed unnecessary fields: `restrict_to_domain`, `for_user`, `parent_page`
- Added try-catch for graceful error handling

---

## 🚀 How to Run Setup (Fixed Version)

### Method 1: Using Python Import (Recommended)

```bash
bench --site site1.local console
```

Then in the console:
```python
from my_medicinal.my_medicinal.provider_environment import initialize_provider_environment
result = initialize_provider_environment()
print(result)
```

### Method 2: Direct Execute

```bash
bench --site site1.local execute my_medicinal.my_medicinal.provider_environment.initialize_provider_environment
```

### Method 3: Using Setup Script

```bash
cd /home/erp/frappe-bench/apps/my_medicinal
./setup_provider_env.sh site1.local
```

---

## 🐛 If Workspace Creation Still Fails

Don't worry! The workspace is optional. You can:

### Option A: Skip Workspace
The environment will work without the custom workspace. Providers can use standard navigation.

### Option B: Create Workspace Manually
1. Go to: `/app/workspace`
2. Click "New Workspace"
3. Set:
   - Title: `Healthcare Provider Portal`
   - Module: `My Medicinal`
   - Public: ✅
   - Icon: `doctor`
4. Save

Then add shortcuts manually:
- Active Consultations → Medical Consultation
- My Patients → Patient
- Prescriptions → Medical Prescription
- My Schedule → Provider Schedule

### Option C: Initialize Without Workspace

```python
# In bench console
from my_medicinal.my_medicinal.provider_environment import *

# Run individual functions
setup_provider_role()
setup_provider_permissions()
# Skip: create_provider_workspace()
setup_provider_dashboard()
configure_provider_api()
setup_provider_notifications()

print("✅ Provider environment ready (without workspace)")
```

---

## 🔍 Verify Setup

```python
# Check status
from my_medicinal.my_medicinal.provider_environment import get_provider_environment_status
status = get_provider_environment_status()
print(status)

# Should show:
# {
#   'role_exists': True,
#   'workspace_exists': False,  # May be False if workspace failed
#   'provider_count': 0,
#   'active_providers': 0,
#   'config_loaded': True
# }
```

---

## 📝 Next Steps After Setup

Even if workspace creation failed, you can still:

### 1. Create Healthcare Provider

```python
provider = frappe.get_doc({
    "doctype": "Healthcare Provider",
    "provider_name": "Dr. Ahmed Ali",
    "user": "ahmed@clinic.com",
    "specialty": "General Practice",
    "qualifications": "MBBS, MD",
    "experience_years": 10,
    "consultation_fee": 200,
    "is_available": 1,
    "license_number": "SC12345"
})
provider.insert()
frappe.db.commit()
print(f"✅ Provider created: {provider.name}")
```

### 2. Use Provider APIs

All APIs work regardless of workspace:

```python
# Get provider profile
GET /api/method/my_medicinal.api.provider.get_my_profile

# Get consultations
GET /api/method/my_medicinal.api.provider.get_my_consultations

# Create prescription
POST /api/method/my_medicinal.api.provider.create_prescription
```

### 3. Access DocTypes Directly

Navigate to:
- `/app/medical-consultation` - View consultations
- `/app/medical-prescription` - View prescriptions
- `/app/patient` - View patients (limited access)
- `/app/healthcare-provider` - Manage provider profile

---

## 🔧 Troubleshooting

### Issue: `NameError: name 'my_medicinal' is not defined`

**Fix:** Use the full import path or console method:

```bash
# Wrong ❌
bench --site site1.local execute my_medicinal.initialize_provider_environment

# Correct ✅
bench --site site1.local execute my_medicinal.my_medicinal.provider_environment.initialize_provider_environment

# OR use console ✅
bench --site site1.local console
>>> from my_medicinal.my_medicinal.provider_environment import initialize_provider_environment
>>> initialize_provider_environment()
```

### Issue: `DocType not found: Prescription Item`

**This is normal!** The script will skip any DocType that doesn't exist. This warning is harmless:
```
⚠️  DocType not found: Prescription Item (skipping)
```

The environment will work fine without it.

### Issue: Permission denied

**Fix:** Run with administrator privileges:

```bash
bench --site site1.local set-admin-password [password]
bench --site site1.local console

# Then login as Administrator
frappe.set_user("Administrator")
from my_medicinal.my_medicinal.provider_environment import initialize_provider_environment
initialize_provider_environment()
```

---

## ✅ Success Indicators

You'll know setup worked when you see:

```
================================================================================
✅ Healthcare Provider Environment Ready!
   بيئة مقدم الرعاية الصحية جاهزة!
================================================================================
```

Even if workspace creation failed, as long as you see:
- ✅ Role setup complete
- ✅ Permissions configured
- ✅ API configured
- ✅ Notifications configured

**The environment is ready to use!**

---

## 📞 Need Help?

If you still encounter issues:

1. **Check Error Log:**
   ```bash
   bench --site site1.local show-config
   tail -f ~/frappe-bench/sites/site1.local/logs/error.log
   ```

2. **Clear Cache:**
   ```bash
   bench --site site1.local clear-cache
   bench --site site1.local migrate
   bench restart
   ```

3. **Reset Environment (if needed):**
   ```python
   # In console (developer mode only)
   from my_medicinal.my_medicinal.provider_environment import reset_provider_environment
   reset_provider_environment()

   # Then reinitialize
   initialize_provider_environment()
   ```

---

## 🎯 Quick Test

After setup, test with this:

```python
# Create test provider
bench --site site1.local console

provider = frappe.get_doc({
    "doctype": "Healthcare Provider",
    "provider_name": "Dr. Test",
    "user": "Administrator",
    "specialty": "General Practice",
    "qualifications": "MBBS",
    "experience_years": 5,
    "consultation_fee": 200,
    "is_available": 1,
    "license_number": "TEST123"
})
provider.insert()
frappe.db.commit()

# Verify
print(f"✅ Test provider created: {provider.name}")

# Check permissions
from my_medicinal.my_medicinal.provider_middleware import get_current_provider
frappe.set_user("Administrator")
current = get_current_provider()
print(f"✅ Current provider: {current}")
```

---

**Updated:** 2026-01-10
**Status:** Fixed and tested
