# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
import json

# ============================================
# AUTHENTICATION
# ============================================

@frappe.whitelist(allow_guest=True)
def register(patient_name, mobile, email, password, date_of_birth=None, gender=None):
    """????? ???? ????"""
    try:
        # ?????? ?? ??????
        if frappe.db.exists("User", {"mobile_no": mobile}):
            return {
                "success": False,
                "message": "??? ?????? ?????? ??????"
            }
        
        # ?????? ?? ??????
        if frappe.db.exists("User", {"email": email}):
            return {
                "success": False,
                "message": "?????? ?????????? ?????? ??????"
            }
        
        # ????? User
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "mobile_no": mobile,
            "first_name": patient_name,
            "new_password": password,
            "user_type": "Website User",
            "enabled": 1
        })
        user.insert(ignore_permissions=True)
        user.add_roles("Patient")
        
        # ????? Patient
        patient = frappe.get_doc({
            "doctype": "patient",
            "patient_name": patient_name,
            "mobile": mobile,
            "email": email,
            "user": user.name,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "status": "???"
        })
        patient.insert(ignore_permissions=True)
        
        frappe.db.commit()
        
        return {
            "success": True,
            "patient_id": patient.name,
            "patient_name": patient.patient_name,
            "message": "?? ??????? ?????"  
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Register API Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist(allow_guest=True)
def login(mobile, password):
    """????? ????"""
    try:
        # ????? ?? ????????
        user = frappe.db.get_value("User", {"mobile_no": mobile}, "name")
        
        if not user:
            return {
                "success": False,
                "message": "??? ?????? ??? ????"
            }
        
        # ?????? ????? ??????
        frappe.local.login_manager.authenticate(user, password)
        frappe.local.login_manager.post_login()
        
        # ?????? ??? ?????? ??????
        patient = frappe.db.get_value(
            "Patient",
            {"user": user},
            ["name", "patient_name", "mobile", "email"],
            as_dict=True
        )
        
        if not patient:
            return {
                "success": False,
                "message": "?? ??? ?????? ??? ??? ??????"
            }
        
        # ????? token
        token = frappe.generate_hash(length=32)
        
        return {
            "success": True,
            "token": token,
            "patient": patient
        }
        
    except frappe.AuthenticationError:
        return {
            "success": False,
            "message": "???? ?????? ??? ?????"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Login API Error")
        return {
            "success": False,
            "message": str(e)
        }


# ============================================
# MEDICATIONS
# ============================================

@frappe.whitelist()
def get_medications(patient_id):
    """?????? ??? ????? ??????"""
    try:
        medications = frappe.get_all(
            "Medication Schedule",
            filters={"patient": patient_id},
            fields=["*"],
            order_by="creation desc"
        )
        
        return {
            "success": True,
            "data": medications
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Medications Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def add_medication(patient_id, medication_name, dosage, frequency, 
                   current_stock, times_json=None):
    """????? ???? ????"""
    try:
        medication = frappe.get_doc({
            "doctype": "Medication Schedule",
            "patient": patient_id,
            "medication_name": medication_name,
            "dosage": dosage,
            "frequency": frequency,
            "current_stock": current_stock
        })
        
        medication.insert()
        frappe.db.commit()
        
        return {
            "success": True,
            "medication_id": medication.name,
            "message": "?? ????? ?????? ?????"
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Add Medication Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def log_medication_taken(medication_id, status="taken"):
    """????? ????? ??????"""
    try:
        medication = frappe.get_doc("Medication Schedule", medication_id)
        
        log = frappe.get_doc({
            "doctype": "Medication Log",
            "patient": medication.patient,
            "medication_schedule": medication_id,
            "actual_time": frappe.utils.now_datetime(),
            "status": status
        })
        log.insert()
        
        frappe.db.commit()
        
        return {
            "success": True,
            "log_id": log.name
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Log Medication Error")
        return {
            "success": False,
            "message": str(e)
        }


# ============================================
# CONSULTATIONS
# ============================================

@frappe.whitelist()
def get_consultations(patient_id):
    """?????? ??? ???????? ??????"""
    try:
        consultations = frappe.get_all(
            "Medical Consultation",
            filters={"patient": patient_id},
            fields=["*"],
            order_by="creation desc"
        )
        
        return {
            "success": True,
            "data": consultations
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Consultations Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def create_consultation(patient_id, provider_type, subject, description):
    """????? ??????? ?????"""
    try:
        consultation = frappe.get_doc({
            "doctype": "Medical Consultation",
            "patient": patient_id,
            "provider_type": provider_type,
            "subject": subject,
            "description": description,
            "status": "pending"
        })
        consultation.insert()
        frappe.db.commit()
        
        return {
            "success": True,
            "consultation_id": consultation.name,
            "message": "?? ????? ????????? ?????"
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Create Consultation Error")
        return {
            "success": False,
            "message": str(e)
        }
