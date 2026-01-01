# 📚 Dawaii API Documentation

**Version:** 1.0  
**Last Updated:** December 26, 2025  
**Base URL:** `https://your-domain.com/api/method`

---

## 📖 **Table of Contents**

1. [Authentication](#authentication)
2. [Patient APIs](#patient-apis)
3. [Medication APIs](#medication-apis)
4. [Product APIs](#product-apis)
5. [Order APIs](#order-apis)
6. [Consultation APIs](#consultation-apis)
7. [Provider APIs](#provider-apis)
8. [Prescription APIs](#prescription-apis)
9. [Notification APIs](#notification-apis)
10. [Background Tasks](#background-tasks)
11. [Error Codes](#error-codes)

---

## 🔐 **Authentication**

### **Overview**

Dawaii uses token-based authentication. After login, you receive an `auth_token` that must be included in all subsequent requests.

### **Header Format**

```http
Authorization: Bearer {auth_token}
Content-Type: application/json
```

---

## 👤 **Patient APIs**

### **1. Register Patient**

Create a new patient account.

**Endpoint:** `POST /my_medicinal.api.patient.register`

**Request Body:**
```json
{
  "patient_name": "أحمد محمد",
  "mobile": "0512345678",
  "email": "ahmed@example.com",
  "password": "SecurePass123!",
  "date_of_birth": "1990-01-01",
  "gender": "Male"
}
```

**Response (Success):**
```json
{
  "message": {
    "status": "success",
    "patient_id": "PAT-00021",
    "auth_token": "a1b2c3d4e5f6...",
    "message": "تم التسجيل بنجاح"
  }
}
```

**Response (Error):**
```json
{
  "exc_type": "ValidationError",
  "message": "رقم الجوال مسجل مسبقاً"
}
```

**Validation Rules:**
- `patient_name`: Required, min 3 characters
- `mobile`: Required, 10 digits, unique
- `email`: Required, valid email format, unique
- `password`: Required, min 8 characters, must contain uppercase, lowercase, number, special char
- `date_of_birth`: Optional, format: YYYY-MM-DD
- `gender`: Optional, values: "Male" or "Female"

---

### **2. Login**

Authenticate existing patient.

**Endpoint:** `POST /my_medicinal.api.patient.login`

**Request Body:**
```json
{
  "mobile": "0512345678",
  "password": "SecurePass123!"
}
```

**Response (Success):**
```json
{
  "message": {
    "status": "success",
    "patient_id": "PAT-00021",
    "patient_name": "أحمد محمد",
    "email": "ahmed@example.com",
    "mobile": "0512345678",
    "auth_token": "a1b2c3d4e5f6...",
    "message": "تم تسجيل الدخول بنجاح"
  }
}
```

**Response (Error):**
```json
{
  "message": "بيانات الدخول غير صحيحة"
}
```

---

### **3. Get Profile**

Retrieve patient profile information.

**Endpoint:** `GET /my_medicinal.api.patient.get_profile`

**Headers:**
```http
Authorization: Bearer {auth_token}
```

**Query Parameters:**
```
patient_id (optional): If not provided, uses authenticated user
```

**Response:**
```json
{
  "message": {
    "patient_id": "PAT-00021",
    "patient_name": "أحمد محمد",
    "email": "ahmed@example.com",
    "mobile": "0512345678",
    "date_of_birth": "1990-01-01",
    "gender": "Male",
    "blood_group": "A+",
    "allergies": "البنسلين",
    "chronic_diseases": ["السكري", "الضغط"],
    "medical_notes": "ملاحظات طبية إضافية",
    "created_at": "2025-12-20 10:30:00"
  }
}
```

---

### **4. Update Profile**

Update patient profile information.

**Endpoint:** `POST /my_medicinal.api.patient.update_profile`

**Headers:**
```http
Authorization: Bearer {auth_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "patient_id": "PAT-00021",
  "profile_data": "{\"patient_name\":\"أحمد محمد علي\",\"blood_group\":\"A+\",\"allergies\":\"البنسلين، الفول السوداني\"}"
}
```

**Response:**
```json
{
  "message": {
    "status": "success",
    "message": "تم تحديث الملف الشخصي بنجاح"
  }
}
```

**Updatable Fields:**
- `patient_name`
- `blood_group`
- `allergies`
- `medical_notes`
- `date_of_birth`
- `gender`

---

## 💊 **Medication APIs**

### **5. Get Medications**

Get all medications for a patient.

**Endpoint:** `GET /my_medicinal.api.medication_schedule.get_medications`

**Headers:**
```http
Authorization: Bearer {auth_token}
```

**Query Parameters:**
```
patient_id (required): Patient ID
active_only (optional, default=1): 1 for active only, 0 for all
```

**Response:**
```json
{
  "message": [
    {
      "name": "MED-أحمد محمد-0001",
      "medication_name": "Glucophage 500mg",
      "scientific_name": "Metformin",
      "dosage": "500mg",
      "frequency": "Twice Daily",
      "current_stock": 60,
      "stock_unit": "Tablet",
      "daily_consumption": 2.0,
      "days_until_depletion": 30,
      "color_code": "#4CAF50",
      "image": "/files/glucophage.jpg",
      "is_active": 1,
      "start_date": "2025-12-01",
      "end_date": null,
      "instructions": "مع الطعام",
      "times": [
        {
          "time": "08:00:00",
          "before_after_meal": "After Meal",
          "notes": "مع وجبة الإفطار"
        },
        {
          "time": "20:00:00",
          "before_after_meal": "After Meal",
          "notes": "مع وجبة العشاء"
        }
      ]
    }
  ]
}
```

---

### **6. Get Medications Due**

Get medications due within a time window.

**Endpoint:** `GET /my_medicinal.api.medication_schedule.get_medications_due`

**Query Parameters:**
```
patient_id (required): Patient ID
time_window (optional, default=30): Minutes before/after current time
```

**Response:**
```json
{
  "message": [
    {
      "schedule_id": "MED-أحمد محمد-0001",
      "medication_name": "Glucophage 500mg",
      "dosage": "500mg",
      "time": "08:00:00",
      "before_after_meal": "After Meal",
      "notes": "مع وجبة الإفطار",
      "current_stock": 60,
      "color_code": "#4CAF50",
      "image": "/files/glucophage.jpg"
    }
  ]
}
```

---

### **7. Add Medication**

Add a new medication schedule.

**Endpoint:** `POST /my_medicinal.api.medication_schedule.add_medication`

**Request Body:**
```json
{
  "patient_id": "PAT-00021",
  "medication_name": "Glucophage 500mg",
  "scientific_name": "Metformin",
  "medication_type": "Tablet",
  "dosage": "500mg",
  "frequency": "Twice Daily",
  "current_stock": 60,
  "stock_unit": "Tablet",
  "instructions": "مع الطعام",
  "color_code": "#4CAF50",
  "times_json": "[{\"time\":\"08:00:00\",\"before_after_meal\":\"After Meal\",\"notes\":\"مع وجبة الإفطار\"},{\"time\":\"20:00:00\",\"before_after_meal\":\"After Meal\",\"notes\":\"مع وجبة العشاء\"}]"
}
```

**Response:**
```json
{
  "message": {
    "message": "Medication added successfully",
    "medication_id": "MED-أحمد محمد-0001",
    "daily_consumption": 2.0,
    "days_until_depletion": 30
  }
}
```

---

### **8. Log Medication Taken**

Log that a medication dose was taken.

**Endpoint:** `POST /my_medicinal.api.medication.log_medication_taken`

**Request Body:**
```json
{
  "patient_id": "PAT-00021",
  "medication_schedule": "MED-أحمد محمد-0001",
  "scheduled_time": "08:00:00",
  "actual_time": "08:15:00",
  "status": "Taken",
  "notes": "تم الأخذ بعد الإفطار"
}
```

**Response:**
```json
{
  "message": {
    "status": "success",
    "log_id": "ML-0001",
    "message": "تم تسجيل تناول الدواء بنجاح"
  }
}
```

**Status Options:**
- `Taken`: تم تناوله
- `Missed`: تم تفويته
- `Skipped`: تم تخطيه

---

### **9. Update Stock**

Update medication stock quantity.

**Endpoint:** `POST /my_medicinal.api.medication_schedule.update_stock`

**Request Body:**
```json
{
  "schedule_id": "MED-أحمد محمد-0001",
  "new_stock": 90
}
```

**Response:**
```json
{
  "message": {
    "message": "Stock updated successfully",
    "current_stock": 90,
    "days_until_depletion": 45
  }
}
```

---

### **10. Deactivate Medication**

Deactivate a medication schedule.

**Endpoint:** `POST /my_medicinal.api.medication_schedule.deactivate_medication`

**Request Body:**
```json
{
  "schedule_id": "MED-أحمد محمد-0001"
}
```

**Response:**
```json
{
  "message": {
    "message": "Medication deactivated"
  }
}
```

---

### **11. Get Low Stock Medications**

Get medications with low stock.

**Endpoint:** `GET /my_medicinal.api.medication_schedule.get_low_stock_medications`

**Query Parameters:**
```
patient_id (required): Patient ID
threshold (optional, default=5): Days threshold
```

**Response:**
```json
{
  "message": [
    {
      "name": "MED-أحمد محمد-0001",
      "medication_name": "Glucophage 500mg",
      "current_stock": 8,
      "stock_unit": "Tablet",
      "days_until_depletion": 4
    }
  ]
}
```

---

## 🛒 **Product APIs**

### **12. Get Products**

Get available products for purchase.

**Endpoint:** `GET /my_medicinal.api.product.get_products`

**Query Parameters:**
```
category (optional): Filter by category
search (optional): Search term
limit (optional, default=50): Results limit
```

**Response:**
```json
{
  "message": [
    {
      "name": "PROD-0001",
      "product_name": "Glucophage 500mg",
      "category": "Diabetes",
      "price": 45.50,
      "stock_available": 1,
      "quantity_in_stock": 500,
      "description": "دواء لعلاج السكري من النوع الثاني",
      "image": "/files/glucophage.jpg"
    }
  ]
}
```

---

### **13. Search Products**

Search for products.

**Endpoint:** `GET /my_medicinal.api.product.search_products`

**Query Parameters:**
```
search_term (required): Search query
```

**Response:**
```json
{
  "message": [
    {
      "name": "PROD-0001",
      "product_name": "Glucophage 500mg",
      "category": "Diabetes",
      "price": 45.50,
      "stock_available": 1
    }
  ]
}
```

---

### **14. Get Product Details**

Get detailed information about a product.

**Endpoint:** `GET /my_medicinal.api.product.get_product_details`

**Query Parameters:**
```
product_id (required): Product ID
```

**Response:**
```json
{
  "message": {
    "name": "PROD-0001",
    "product_name": "Glucophage 500mg",
    "scientific_name": "Metformin HCl",
    "category": "Diabetes",
    "manufacturer": "Merck",
    "price": 45.50,
    "quantity_in_stock": 500,
    "description": "دواء لعلاج السكري من النوع الثاني",
    "dosage_form": "Tablet",
    "strength": "500mg",
    "package_size": "30 Tablets",
    "requires_prescription": 1,
    "side_effects": "غثيان، إسهال، آلام في المعدة",
    "contraindications": "الحساسية للمادة الفعالة، أمراض الكلى الحادة",
    "storage_conditions": "يحفظ في درجة حرارة الغرفة",
    "image": "/files/glucophage.jpg"
  }
}
```

---

## 🛍️ **Order APIs**

### **15. Create Order**

Create a new order.

**Endpoint:** `POST /my_medicinal.api.order.create_order`

**Request Body:**
```json
{
  "patient_id": "PAT-00021",
  "items": "[{\"product\":\"PROD-0001\",\"quantity\":2,\"price\":45.50}]",
  "delivery_address": "الرياض، حي النرجس، شارع الأمير محمد",
  "delivery_phone": "0512345678",
  "payment_method": "Cash on Delivery",
  "notes": "التوصيل بعد المغرب"
}
```

**Response:**
```json
{
  "message": {
    "status": "success",
    "order_id": "ORD-00001",
    "total_amount": 91.00,
    "message": "تم إنشاء الطلب بنجاح"
  }
}
```

---

### **16. Get My Orders**

Get all orders for a patient.

**Endpoint:** `GET /my_medicinal.api.order.get_my_orders`

**Query Parameters:**
```
patient_id (required): Patient ID
status (optional): Filter by status
```

**Response:**
```json
{
  "message": [
    {
      "name": "ORD-00001",
      "order_date": "2025-12-26",
      "status": "Pending",
      "total_amount": 91.00,
      "delivery_address": "الرياض، حي النرجس",
      "payment_method": "Cash on Delivery",
      "items": [
        {
          "product": "PROD-0001",
          "product_name": "Glucophage 500mg",
          "quantity": 2,
          "price": 45.50,
          "total": 91.00
        }
      ]
    }
  ]
}
```

**Status Values:**
- `Pending`: قيد الانتظار
- `Confirmed`: مؤكد
- `Out for Delivery`: في الطريق
- `Delivered`: تم التوصيل
- `Cancelled`: ملغي

---

## 💬 **Consultation APIs**

### **17. Create Consultation**

Request a medical consultation.

**Endpoint:** `POST /my_medicinal.api.consultation.create_consultation`

**Request Body:**
```json
{
  "patient_id": "PAT-00021",
  "consultation_type": "General",
  "chief_complaint": "ألم في الصدر",
  "symptoms": "ألم حاد، ضيق في التنفس",
  "duration": "منذ 3 أيام",
  "severity": "High",
  "attachments": "[]"
}
```

**Response:**
```json
{
  "message": {
    "status": "success",
    "consultation_id": "CONS-00001",
    "message": "تم إنشاء الاستشارة بنجاح"
  }
}
```

**Consultation Types:**
- `General`: استشارة عامة
- `Follow-up`: متابعة
- `Emergency`: طارئة

**Severity Levels:**
- `Low`: منخفضة
- `Medium`: متوسطة
- `High`: عالية

---

### **18. Get My Consultations**

Get all consultations for a patient.

**Endpoint:** `GET /my_medicinal.api.consultation.get_my_consultations`

**Query Parameters:**
```
patient_id (required): Patient ID
status (optional): Filter by status
```

**Response:**
```json
{
  "message": [
    {
      "name": "CONS-00001",
      "consultation_date": "2025-12-26 10:30:00",
      "consultation_type": "General",
      "status": "Pending",
      "chief_complaint": "ألم في الصدر",
      "severity": "High",
      "provider": null,
      "provider_name": null
    }
  ]
}
```

---

### **19. Send Message**

Send a message in a consultation.

**Endpoint:** `POST /my_medicinal.api.consultation.send_message`

**Request Body:**
```json
{
  "consultation_id": "CONS-00001",
  "sender": "PAT-00021",
  "message": "الألم يزداد عند التنفس العميق",
  "attachment": null
}
```

**Response:**
```json
{
  "message": {
    "status": "success",
    "message_id": "MSG-00001",
    "message": "تم إرسال الرسالة بنجاح"
  }
}
```

---

### **20. Get Consultation Messages**

Get all messages in a consultation.

**Endpoint:** `GET /my_medicinal.api.consultation.get_messages`

**Query Parameters:**
```
consultation_id (required): Consultation ID
```

**Response:**
```json
{
  "message": [
    {
      "name": "MSG-00001",
      "sender": "PAT-00021",
      "sender_name": "أحمد محمد",
      "message": "الألم يزداد عند التنفس العميق",
      "sent_at": "2025-12-26 10:35:00",
      "attachment": null
    },
    {
      "name": "MSG-00002",
      "sender": "PROV-00001",
      "sender_name": "د. خالد العتيبي",
      "message": "هل الألم مستمر أم متقطع؟",
      "sent_at": "2025-12-26 10:40:00",
      "attachment": null
    }
  ]
}
```

---

## 👨‍⚕️ **Provider APIs**

### **21. Get Providers**

Get list of available healthcare providers.

**Endpoint:** `GET /my_medicinal.api.provider.get_providers`

**Query Parameters:**
```
specialty (optional): Filter by specialty
available_only (optional, default=1): 1 for available only
```

**Response:**
```json
{
  "message": [
    {
      "name": "PROV-00001",
      "provider_name": "د. خالد العتيبي",
      "specialty": "General Practitioner",
      "qualifications": "بكالوريوس طب، ماجستير طب الأسرة",
      "experience_years": 10,
      "rating": 4.8,
      "is_available": 1,
      "consultation_fee": 150.00,
      "image": "/files/dr_khalid.jpg"
    }
  ]
}
```

---

### **22. Get Provider Schedule**

Get provider's available time slots.

**Endpoint:** `GET /my_medicinal.api.provider.get_schedule`

**Query Parameters:**
```
provider_id (required): Provider ID
date (optional): Specific date (YYYY-MM-DD)
```

**Response:**
```json
{
  "message": [
    {
      "day": "Sunday",
      "slots": [
        {
          "start_time": "09:00:00",
          "end_time": "09:30:00",
          "is_available": 1
        },
        {
          "start_time": "09:30:00",
          "end_time": "10:00:00",
          "is_available": 0
        }
      ]
    }
  ]
}
```

---

## 📋 **Prescription APIs**

### **23. Get My Prescriptions**

Get all prescriptions for a patient.

**Endpoint:** `GET /my_medicinal.api.prescription.get_my_prescriptions`

**Query Parameters:**
```
patient_id (required): Patient ID
```

**Response:**
```json
{
  "message": [
    {
      "name": "PRESC-00001",
      "prescription_date": "2025-12-20",
      "provider": "PROV-00001",
      "provider_name": "د. خالد العتيبي",
      "diagnosis": "السكري من النوع الثاني",
      "notes": "مراجعة بعد شهر",
      "medications": [
        {
          "medication_name": "Glucophage 500mg",
          "dosage": "500mg",
          "frequency": "Twice Daily",
          "duration": "3 months",
          "instructions": "مع الطعام"
        }
      ]
    }
  ]
}
```

---

### **24. Get Prescription Details**

Get detailed prescription information.

**Endpoint:** `GET /my_medicinal.api.prescription.get_prescription_details`

**Query Parameters:**
```
prescription_id (required): Prescription ID
```

**Response:**
```json
{
  "message": {
    "name": "PRESC-00001",
    "prescription_date": "2025-12-20",
    "patient": "PAT-00021",
    "patient_name": "أحمد محمد",
    "provider": "PROV-00001",
    "provider_name": "د. خالد العتيبي",
    "diagnosis": "السكري من النوع الثاني",
    "notes": "مراجعة بعد شهر",
    "medications": [
      {
        "medication_name": "Glucophage 500mg",
        "scientific_name": "Metformin",
        "dosage": "500mg",
        "frequency": "Twice Daily",
        "duration": "3 months",
        "quantity": 180,
        "instructions": "مع الطعام",
        "refills": 2
      }
    ]
  }
}
```

---

## 🔔 **Notification APIs**

### **25. Register Device**

Register device for push notifications.

**Endpoint:** `POST /my_medicinal.my_medicinal.notifications.register_device`

**Headers:**
```http
Authorization: Bearer {auth_token}
```

**Request Body:**
```json
{
  "fcm_token": "eXYz123ABC...",
  "device_type": "Android",
  "device_id": "unique_device_id_12345"
}
```

**Response:**
```json
{
  "message": {
    "success": true,
    "message": "Device registered successfully"
  }
}
```

---

### **26. Send Test Notification**

Send a test push notification.

**Endpoint:** `POST /my_medicinal.my_medicinal.notifications.send_test_notification`

**Request Body:**
```json
{
  "user_id": "ahmed@example.com",
  "title": "اختبار الإشعارات",
  "body": "هذا إشعار تجريبي"
}
```

**Response:**
```json
{
  "message": {
    "push": {
      "success": true,
      "message": "Notification sent",
      "response": "projects/dawaii-app/messages/123456"
    }
  }
}
```

---

### **27. Get My Notifications**

Get user's notifications.

**Endpoint:** `GET /my_medicinal.my_medicinal.notifications.get_my_notifications`

**Query Parameters:**
```
limit (optional, default=20): Number of notifications
```

**Response:**
```json
{
  "message": [
    {
      "name": "NL-00001",
      "subject": "⏰ موعد الدواء",
      "email_content": "<p>حان موعد دوائك: Glucophage 500mg</p>",
      "type": "Alert",
      "read": 0,
      "creation": "2025-12-26 08:00:00"
    }
  ]
}
```

---

### **28. Mark Notification Read**

Mark a notification as read.

**Endpoint:** `POST /my_medicinal.my_medicinal.notifications.mark_notification_read`

**Request Body:**
```json
{
  "notification_id": "NL-00001"
}
```

**Response:**
```json
{
  "message": {
    "success": true
  }
}
```

---

## ⚙️ **Background Tasks**

These tasks run automatically via scheduler.

### **Medication Reminders**

**Schedule:** Every 5 minutes  
**Function:** `my_medicinal.my_medicinal.tasks.send_medication_reminders()`

Checks upcoming medications within 5-minute window and sends notifications.

---

### **Stock Depletion Check**

**Schedule:** Daily at midnight  
**Function:** `my_medicinal.my_medicinal.tasks.check_stock_depletion()`

Checks medication stock levels and sends alerts:
- ≤ 2 days: Critical alert
- ≤ 5 days: Warning alert

---

### **Adherence Reports**

**Schedule:** Daily  
**Function:** `my_medicinal.my_medicinal.tasks.generate_daily_adherence_reports()`

Generates 30-day adherence reports and alerts if <80%.

---

### **Cleanup Old Notifications**

**Schedule:** Weekly  
**Function:** `my_medicinal.my_medicinal.tasks.cleanup_old_notifications()`

Deletes read notifications older than 30 days.

---

## ❌ **Error Codes**

### **HTTP Status Codes**

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Invalid or missing auth token |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Internal server error |

### **Application Error Codes**

| Code | Message | Description |
|------|---------|-------------|
| AUTH_001 | Invalid credentials | Wrong mobile/password |
| AUTH_002 | Token expired | Auth token expired |
| AUTH_003 | Token invalid | Invalid auth token |
| VAL_001 | Validation error | Field validation failed |
| VAL_002 | Required field missing | Required field not provided |
| VAL_003 | Duplicate entry | Unique field already exists |
| MED_001 | Medication not found | Medication schedule not found |
| MED_002 | No stock available | Medication out of stock |
| ORD_001 | Order not found | Order ID not found |
| ORD_002 | Payment failed | Payment processing failed |
| CONS_001 | Consultation not found | Consultation ID not found |
| CONS_002 | Provider unavailable | Provider not available |

### **Error Response Format**

```json
{
  "exc_type": "ValidationError",
  "message": "رقم الجوال يجب أن يكون 10 أرقام",
  "exception": "frappe.exceptions.ValidationError: ...",
  "_server_messages": "[...]"
}
```

---

## 🔧 **Testing**

### **cURL Examples**

**Register:**
```bash
curl -X POST https://your-domain.com/api/method/my_medicinal.api.patient.register \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "أحمد محمد",
    "mobile": "0512345678",
    "email": "ahmed@example.com",
    "password": "SecurePass123!"
  }'
```

**Login:**
```bash
curl -X POST https://your-domain.com/api/method/my_medicinal.api.patient.login \
  -H "Content-Type: application/json" \
  -d '{
    "mobile": "0512345678",
    "password": "SecurePass123!"
  }'
```

**Get Medications (Authenticated):**
```bash
curl -X GET "https://your-domain.com/api/method/my_medicinal.api.medication_schedule.get_medications?patient_id=PAT-00021" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📞 **Support**

For API support or questions:
- **Email:** support@dawaii.com
- **GitHub:** https://github.com/Mohamedsulima775/My_medicinal
- **Documentation:** This file

---

## 📝 **Changelog**

### Version 1.0 (2025-12-26)
- Initial release
- 28 API endpoints
- Authentication system
- Background tasks
- Firebase notifications

---

**Last Updated:** December 26, 2025  
**Maintained by:** Dawaii Development Team