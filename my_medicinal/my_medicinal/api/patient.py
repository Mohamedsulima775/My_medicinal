# -*- coding: utf-8 -*-
# Copyright (c) 2024, My Medicinal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, today, add_days, now_datetime
import json
from my_medicinal.my_medicinal.rate_limiter import rate_limit, get_mobile_key

# ============================================
# PATIENT REGISTRATION & AUTHENTICATION
# ============================================

@frappe.whitelist(allow_guest=True)
@rate_limit(limit=5, window=300, key_func=get_mobile_key)  # 5 attempts per 5 minutes
def register(patient_name, mobile, password, email=None, date_of_birth=None, gender=None):
    """
    Register a new patient
    
    Args:
        patient_name: Full name
        mobile: Mobile number (05XXXXXXXX)
        password: Password
        email: Optional email
        date_of_birth: Optional DOB
        gender: Optional gender
    
    Returns:
        {"success": True, "patient": {...}, "token": "..."}
    """
    try:
        # Validate mobile
        if not mobile.startswith('05') or len(mobile) != 10:
            frappe.throw(_("Invalid mobile number. Must be 05XXXXXXXX"))
        
        # Check if mobile already exists
        if frappe.db.exists("patient", {"mobile": mobile}):
            frappe.throw(_("Mobile number already registered"))
        
        # Generate email if not provided
        if not email:
            email = f"{mobile}@dawaii.local"
        
        # Check if email exists
        if frappe.db.exists("User", email):
            frappe.throw(_("Email already registered"))
        
        # Create User
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "mobile_no": mobile,
            "first_name": patient_name,
            "enabled": 1,
            "user_type": "Website User",
            "send_welcome_email": 0
        })
        user.insert(ignore_permissions=True)
        
        # Set password
        from frappe.utils.password import update_password
        update_password(user.name, password)
        
        # Add Patient role
        user.add_roles("Patient")
        
        # Create Patient record
        patient = frappe.get_doc({
            "doctype": "patient",
            "patient_name": patient_name,
            "mobile": mobile,
            "email": email,
            "user": user.name,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "status": "Active"
        })
        
        patient.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Generate API key for token
        api_key, api_secret = generate_api_keys(user.name)
        
        return {
            "success": True,
            "message": "Registration successful",
            "patient": {
                "patient_id": patient.name,
                "patient_name": patient.patient_name,
                "mobile": patient.mobile,
                "email": patient.email
            },
            "token": api_key,
            "user": user.name
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Patient Registration Error")
        frappe.throw(_("Registration failed: {0}").format(str(e)))


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=10, window=300, key_func=get_mobile_key)  # 10 attempts per 5 minutes
def login(mobile, password):
    """
    Login patient
    
    Args:
        mobile: Patient mobile number
        password: Account password
    
    Returns:
        {"success": True, "patient": {...}, "token": "..."}
    """
    try:
        # Get user by mobile
        user_email = frappe.db.get_value("User", {"mobile_no": mobile}, "name")
        
        if not user_email:
            frappe.throw(_("Mobile number not registered"))
        
        # Authenticate - check password
        from frappe.utils.password import check_password
        try:
            check_password(user_email, password)
        except frappe.AuthenticationError:
            frappe.throw(_("Invalid mobile number or password"))
        
        # Get patient
        patient_doc = frappe.get_doc("patient", {"user": user_email})
        
        if patient_doc.status != "Active":
            frappe.throw(_("Account is not active"))
        
        # Generate or get API key
        api_key, api_secret = generate_api_keys(user_email)
        
        return {
            "success": True,
            "message": "Login successful",
            "patient": {
                "patient_id": patient_doc.name,
                "patient_name": patient_doc.patient_name,
                "mobile": patient_doc.mobile,
                "email": patient_doc.email,
                "user": user_email
            },
            "token": api_key
        }
        
    except frappe.AuthenticationError:
        frappe.throw(_("Invalid mobile number or password"))
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Patient Login Error")
        frappe.throw(_("Login failed: {0}").format(str(e)))


@frappe.whitelist()
def get_profile(patient_id=None):
    """
    Get patient profile
    
    Args:
        patient_id: Optional, uses current user if not provided
    
    Returns:
        Patient profile dict
    """
    try:
        if not patient_id:
            # Get patient from current user
            patient_id = frappe.db.get_value("patient", {"user": frappe.session.user}, "name")
            if not patient_id:
                frappe.throw(_("Patient record not found"))
        
        patient = frappe.get_doc("patient", patient_id)
        
        # Check permission
        if patient.user != frappe.session.user and not frappe.has_permission("patient", "read", patient_id):
            frappe.throw(_("Not authorized"))
        
        return {
            "success": True,
            "patient": {
                "patient_id": patient.name,
                "patient_name": patient.patient_name,
                "mobile": patient.mobile,
                "email": patient.email,
                "date_of_birth": patient.date_of_birth,
                "gender": patient.gender,
                "blood_group": patient.blood_group,
                "allergies": patient.allergies,
                "medical_notes": patient.medical_notes,
                "status": patient.status
            }
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Profile Error")
        frappe.throw(_("Failed to get profile: {0}").format(str(e)))


@frappe.whitelist()
def update_profile(patient_id, profile_data):
    """
    Update patient profile
    
    Args:
        patient_id: Patient ID
        profile_data: JSON string or dict with fields to update
    
    Returns:
        Updated profile
    """
    try:
        if isinstance(profile_data, str):
            profile_data = json.loads(profile_data)
        
        patient = frappe.get_doc("patient", patient_id)
        
        # Check permission
        if patient.user != frappe.session.user and not frappe.has_permission("patient", "write", patient_id):
            frappe.throw(_("Not authorized"))
        
        # Update allowed fields
        allowed_fields = [
            "patient_name", "date_of_birth", "gender", "blood_group",
            "allergies", "medical_notes"
        ]
        
        for field in allowed_fields:
            if field in profile_data:
                setattr(patient, field, profile_data[field])
        
        patient.save(ignore_permissions=True)
        frappe.db.commit()
        
        return get_profile(patient_id)
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Update Profile Error")
        frappe.throw(_("Failed to update profile: {0}").format(str(e)))


# ============================================
# HELPER FUNCTIONS
# ============================================

def generate_api_keys(user):
    """
    Generate or get existing valid API keys for user
    Uses API Key doctype with 90-day expiration

    Returns:
        (api_key, api_secret) tuple
    """
    try:
        # Check if user already has a valid (non-expired, active) API key
        existing_key = frappe.db.get_value(
            "API Key",
            {
                "user": user,
                "is_active": 1,
                "expires_at": [">", now_datetime()]
            },
            ["api_key", "api_secret"],
            as_dict=True
        )

        if existing_key and existing_key.api_key:
            return (existing_key.api_key, existing_key.api_secret)

        # Deactivate old keys for this user
        frappe.db.sql("""
            UPDATE `tabAPI Key`
            SET is_active = 0
            WHERE user = %s
        """, (user,))

        # Generate new keys with secure length (32 characters)
        api_key = frappe.generate_hash(length=32)
        api_secret = frappe.generate_hash(length=32)

        # Set expiration date to 90 days from now
        expires_at = add_days(now_datetime(), 90)

        # Create new API Key document
        api_key_doc = frappe.get_doc({
            "doctype": "API Key",
            "user": user,
            "api_key": api_key,
            "api_secret": api_secret,
            "is_active": 1,
            "expires_at": expires_at,
            "last_used": now_datetime()
        })
        api_key_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return (api_key, api_secret)

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Generate API Keys Error")
        # Return simple token as fallback
        import hashlib
        import secrets
        token = hashlib.sha256(f"{user}-{secrets.token_hex(16)}".encode()).hexdigest()
        return (token, token)


def validate_api_key(api_key):
    """
    Validate API key and check expiration
    Updates last_used timestamp if valid

    Args:
        api_key: API key to validate

    Returns:
        User email if valid, None otherwise
    """
    try:
        api_key_doc = frappe.db.get_value(
            "API Key",
            {
                "api_key": api_key,
                "is_active": 1
            },
            ["user", "expires_at", "name"],
            as_dict=True
        )

        if not api_key_doc:
            return None

        # Check if expired
        if api_key_doc.expires_at and api_key_doc.expires_at < now_datetime():
            # Deactivate expired key
            frappe.db.set_value("API Key", api_key_doc.name, "is_active", 0)
            frappe.db.commit()
            return None

        # Update last_used timestamp
        frappe.db.set_value("API Key", api_key_doc.name, "last_used", now_datetime())
        frappe.db.commit()

        return api_key_doc.user

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Validate API Key Error")
        return None


@frappe.whitelist()
def refresh_token(old_api_key):
    """
    Refresh an expired or about-to-expire token

    Args:
        old_api_key: Current API key

    Returns:
        New token if successful
    """
    try:
        # Validate the old key and get user
        user = validate_api_key(old_api_key)

        if not user:
            frappe.throw(_("Invalid or expired token"))

        # Generate new API keys
        api_key, api_secret = generate_api_keys(user)

        return {
            "success": True,
            "message": "Token refreshed successfully",
            "token": api_key,
            "expires_in_days": 90
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Refresh Token Error")
        frappe.throw(_("Failed to refresh token: {0}").format(str(e)))


@frappe.whitelist()
def get_my_patient_id():
    """Get patient ID for current user"""
    patient_id = frappe.db.get_value("patient", {"user": frappe.session.user}, "name")
    if not patient_id:
        frappe.throw(_("Patient record not found"))
    return patient_id


# ============================================
# HOOKS FUNCTIONS (for doc_events)
# ============================================

def validate_patient(doc, method):
    """
    Validate patient before save
    Called from hooks.py doc_events
    """
    # Validate mobile number
    if doc.mobile and not doc.mobile.startswith('05'):
        frappe.throw(_("Mobile number must start with 05"))
    
    # Check email uniqueness
    if doc.email and doc.is_new():
        if frappe.db.exists("patient", {"email": doc.email, "name": ["!=", doc.name]}):
            frappe.throw(_("Email already exists"))


def send_welcome_notification(doc, method):
    """
    Send welcome notification after patient insert
    Called from hooks.py doc_events
    """
    try:
        frappe.logger().info(f"Welcome notification for: {doc.patient_name}")
        # TODO: Add FCM notification here
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Welcome Notification Error")


def on_update(doc, method):
    """
    Called when patient is updated
    Called from hooks.py doc_events
    """
    try:
        frappe.logger().info(f"Patient updated: {doc.name}")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Patient Update Error")


@frappe.whitelist()
def logout():
    """Logout current user"""
    frappe.local.login_manager.logout()
    return {"success": True, "message": "Logged out successfully"}