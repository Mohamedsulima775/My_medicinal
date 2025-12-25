# -*- coding: utf-8 -*-
# Copyright (c) 2024, My Medicinal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, today
import json

# ============================================
# PATIENT REGISTRATION & AUTHENTICATION
# ============================================

@frappe.whitelist(allow_guest=True)
def register(mobile, password, patient_data):
    """
    Register a new patient
    
    Args:
        mobile: Patient mobile number (unique)
        password: Strong password (min 8 chars, mixed case, numbers, symbols)
        patient_data: JSON string or dict with patient info
    
    Returns:
        {
            "success": True,
            "patient": {...},
            "token": "..."
        }
    """
    try:
        # Parse patient_data if string
        if isinstance(patient_data, str):
            patient_data = json.loads(patient_data)
        
        # Check if mobile already exists
        if frappe.db.exists("patient", {"mobile": mobile}):
            frappe.throw(_("Mobile number already registered"))
        
        # Create User
        user = frappe.get_doc({
            "doctype": "User",
            "email": f"{mobile}@dawaii.local",
            "mobile_no": mobile,
            "first_name": patient_data.get("patient_name", "Patient"),
            "user_type": "Website User",
            "send_welcome_email": 0,
            "new_password": password
        })
        user.insert(ignore_permissions=True)
        
        # Add Patient role
        user.add_roles("Patient")
        
        # Create Patient record
        patient = frappe.get_doc({
            "doctype": "patient",
            "patient_name": patient_data.get("patient_name"),
            "mobile": mobile,
            "email": user.email,
            "user": user.name,
            "date_of_birth": patient_data.get("date_of_birth"),
            "gender": patient_data.get("gender"),
            "blood_group": patient_data.get("blood_group"),
            "allergies": patient_data.get("allergies"),
            "medical_notes": patient_data.get("medical_notes"),
            "status": "Active"
        })
        
        patient.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Generate token
        token = generate_token(user.name)
        
        return {
            "success": True,
            "message": "Registration successful",
            "patient": {
                "patient_id": patient.name,
                "patient_name": patient.patient_name,
                "mobile": patient.mobile,
                "email": patient.email
            },
            "token": token
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Patient Registration Error")
        frappe.throw(_("Registration failed: {0}").format(str(e)))


@frappe.whitelist(allow_guest=True)
def login(mobile, password):
    """
    Login patient
    
    Args:
        mobile: Patient mobile number
        password: Account password
    
    Returns:
        {
            "success": True,
            "patient": {...},
            "token": "..."
        }
    """
    try:
        # Get user by mobile
        user_email = frappe.db.get_value("User", {"mobile_no": mobile}, "name")
        
        if not user_email:
            frappe.throw(_("Mobile number not registered"))
        
        # Authenticate
        from frappe.auth import check_password
        check_password(user_email, password)
        
        # Get patient
        patient = frappe.get_doc("patient", {"user": user_email})
        
        if patient.status != "Active":
            frappe.throw(_("Account is not active"))
        
        # Generate token
        token = generate_token(user_email)
        
        return {
            "success": True,
            "message": "Login successful",
            "patient": {
                "patient_id": patient.name,
                "patient_name": patient.patient_name,
                "mobile": patient.mobile,
                "email": patient.email
            },
            "token": token
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
        frappe.log_error(frappe.get_traceback(), "Update Profile Error")
        frappe.throw(_("Failed to update profile: {0}").format(str(e)))


# ============================================
# HELPER FUNCTIONS
# ============================================

def generate_token(user):
    """Generate authentication token"""
    from frappe.utils import cstr
    import hashlib
    import secrets
    
    # Simple token generation
    token_string = f"{user}-{secrets.token_hex(16)}"
    return hashlib.sha256(token_string.encode()).hexdigest()


@frappe.whitelist()
def get_my_patient_id():
    """Get patient ID for current user"""
    patient_id = frappe.db.get_value("patient", {"user": frappe.session.user}, "name")
    if not patient_id:
        frappe.throw(_("Patient record not found"))
    return patient_id