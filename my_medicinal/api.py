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
        # ?????? ?? ??? ??? ??????
        if len(mobile) != 10:
            return {
                "success": False,
                "message": f"??? ?????? ??? ?? ???? 10 ????? (??????: {len(mobile)})"
            }
        
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
        
        # ????? gender ??? ??????
        gender_map = {
            "male": "???",
            "female": "????",
            "???": "???",
            "????": "????"
        }
        gender = gender_map.get(gender, gender) if gender else None
        
        # ????? User
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "mobile_no": mobile,
            "first_name": patient_name,
            "user_type": "Website User",
            "enabled": 1,
            "send_welcome_email": 0
        })
        
        user.flags.ignore_password_policy = True
        user.insert(ignore_permissions=True)
        
        # ????? ???? ??????
        from frappe.utils.password import update_password
        update_password(user.name, password, logout_all_sessions=False)
        
        # ????? ???
        user.add_roles("patient")
        
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
            "user_id": user.name,
            "message": "Registration successful"
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
        # ????? ?? ???????? ???????
        user_data = frappe.db.get_value(
            "User",
            {"mobile_no": mobile},
            ["name", "enabled"],
            as_dict=True
        )
        
        if not user_data:
            return {
                "success": False,
                "message": "??? ?????? ??? ????"
            }
        
        if not user_data.enabled:
            return {
                "success": False,
                "message": "?????? ????"
            }
        
        # ?????? ?? ???? ??????
        from frappe.utils.password import check_password
        
        try:
            check_password(user_data.name, password)
        except frappe.AuthenticationError:
            return {
                "success": False,
                "message": "???? ?????? ??? ?????"
            }
        
        # ?????? ??? Patient - ??????? ???????
        patient = frappe.db.get_value(
            "patient",
            {"user": user_data.name},
            ["name", "patient_name", "mobile", "email", "status"],
            as_dict=True
        )
        
        # ??? ?? ????? ??? ????? ????
        if not patient:
            patient_list = frappe.get_all(
                "patient",
                filters={"user": user_data.name},
                fields=["name", "patient_name", "mobile", "email", "status"],
                limit=1
            )
            
            if patient_list:
                patient = patient_list[0]
            else:
                return {
                    "success": False,
                    "message": "?? ??? ?????? ??? ??? ??????"
                }
        
        # ?????? ?? ???? ??????
        if patient.get("status") == "?????":
            return {
                "success": False,
                "message": "?? ??? ??????"
            }
        
        # ????? token
        token = frappe.generate_hash(length=32)
        
        # ????? ??? ???? (???????)
        try:
            frappe.db.set_value("patient", patient.get("name"), "last_login", frappe.utils.now())
            frappe.db.commit()
        except:
            pass  # ????? ??? ?? ??? ??? last_login ?????
        
        return {
            "success": True,
            "token": token,
            "patient": {
                "id": patient.get("name"),
                "name": patient.get("patient_name"),
                "mobile": patient.get("mobile"),
                "email": patient.get("email"),
                "status": patient.get("status")
            },
            "message": "?? ????? ?????? ?????"
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
            "data": medications,
            "count": len(medications)
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Medications Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def get_medication_detail(medication_id):
    """?????? ???? ????"""
    try:
        medication = frappe.get_doc("Medication Schedule", medication_id)
        
        # ?????? ??? ??? ????? ???????
        logs = frappe.get_all(
            "Medication Log",
            filters={"medication_schedule": medication_id},
            fields=["*"],
            order_by="creation desc",
            limit=10
        )
        
        return {
            "success": True,
            "data": medication.as_dict(),
            "recent_logs": logs
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Medication Detail Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def add_medication(patient_id, medication_name, dosage, frequency, 
                   current_stock, times_json=None, before_after_meal=None,
                   duration=None, notes=None):
    """????? ???? ????"""
    try:
        # ???? ????????? ??????
        daily_consumption = calculate_daily_consumption(dosage, frequency)
        
        medication = frappe.get_doc({
            "doctype": "Medication Schedule",
            "patient": patient_id,
            "medication_name": medication_name,
            "dosage": dosage,
            "frequency": frequency,
            "current_stock": int(current_stock),
            "daily_consumption": daily_consumption,
            "before_after_meal": before_after_meal,
            "duration": duration,
            "notes": notes
        })
        
        medication.insert(ignore_permissions=True)
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
def log_medication_taken(medication_id, status="taken", skip_reason=None):
    """????? ????? ??????"""
    try:
        medication = frappe.get_doc("Medication Schedule", medication_id)
        
        # ????? ???
        log = frappe.get_doc({
            "doctype": "Medication Log",
            "patient": medication.patient,
            "medication_schedule": medication_id,
            "scheduled_time": frappe.utils.now(),
            "actual_time": frappe.utils.now_datetime(),
            "status": status,
            "skip_reason": skip_reason
        })
        log.insert(ignore_permissions=True)
        
        # ????? ??????? ??? ?? ???????
        if status == "taken":
            new_stock = int(medication.current_stock) - int(medication.dosage)
            frappe.db.set_value("Medication Schedule", medication_id, "current_stock", new_stock)
        
        frappe.db.commit()
        
        return {
            "success": True,
            "log_id": log.name,
            "remaining_stock": medication.current_stock,
            "message": "?? ????? ???????"
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Log Medication Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def get_adherence_stats(patient_id, days=30):
    """???????? ????????"""
    try:
        from datetime import timedelta
        from_date = frappe.utils.now_datetime() - timedelta(days=days)
        
        total = frappe.db.count("Medication Log", {
            "patient": patient_id,
            "creation": [">=", from_date]
        })
        
        if total == 0:
            return {
                "success": True,
                "adherence_rate": 0,
                "total_doses": 0,
                "taken": 0,
                "missed": 0,
                "skipped": 0
            }
        
        taken = frappe.db.count("Medication Log", {
            "patient": patient_id,
            "status": "taken",
            "creation": [">=", from_date]
        })
        
        missed = frappe.db.count("Medication Log", {
            "patient": patient_id,
            "status": "missed",
            "creation": [">=", from_date]
        })
        
        skipped = frappe.db.count("Medication Log", {
            "patient": patient_id,
            "status": "skipped",
            "creation": [">=", from_date]
        })
        
        adherence_rate = round((taken / total) * 100, 2)
        
        return {
            "success": True,
            "adherence_rate": adherence_rate,
            "total_doses": total,
            "taken": taken,
            "missed": missed,
            "skipped": skipped,
            "period_days": days
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Adherence Stats Error")
        return {
            "success": False,
            "message": str(e)
        }


def calculate_daily_consumption(dosage, frequency):
    """???? ????????? ??????"""
    try:
        dosage_num = float(dosage)
        
        frequency_map = {
            "???": 1,
            "?????": 2,
            "???? ????": 3,
            "???? ????": 4,
            "once": 1,
            "twice": 2,
            "three times": 3,
            "four times": 4
        }
        
        frequency_num = frequency_map.get(frequency, 1)
        
        return dosage_num * frequency_num
        
    except:
        return 1


# ============================================
# CONSULTATIONS
# ============================================

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
        consultation.insert(ignore_permissions=True)
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


@frappe.whitelist()
def get_consultations(patient_id, status=None):
    """?????? ??? ???????? ??????"""
    try:
        filters = {"patient": patient_id}
        if status:
            filters["status"] = status
        
        consultations = frappe.get_all(
            "Medical Consultation",
            filters=filters,
            fields=["*"],
            order_by="creation desc"
        )
        
        return {
            "success": True,
            "data": consultations,
            "count": len(consultations)
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Consultations Error")
        return {
            "success": False,
            "message": str(e)
        }


# ============================================
# PRESCRIPTIONS
# ============================================

@frappe.whitelist()
def get_prescriptions(patient_id):
    """?????? ??? ????? ??????"""
    try:
        prescriptions = frappe.get_all(
            "Medical Prescription",
            filters={"patient": patient_id},
            fields=["*"],
            order_by="prescription_date desc"
        )
        
        return {
            "success": True,
            "data": prescriptions,
            "count": len(prescriptions)
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Prescriptions Error")
        return {
            "success": False,
            "message": str(e)
        }


# ============================================
# SHOP / ORDERS
# ============================================

@frappe.whitelist()
def get_products(category=None, search=None):
    """?????? ??? ????????"""
    try:
        filters = {"disabled": 0}
        
        if category:
            filters["item_group"] = category
        
        if search:
            filters["item_name"] = ["like", f"%{search}%"]
        
        products = frappe.get_all(
            "Item",
            filters=filters,
            fields=["name", "item_name", "item_group", "standard_rate", "image"],
            limit=50
        )
        
        return {
            "success": True,
            "data": products,
            "count": len(products)
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Products Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def create_order(patient_id, items_json, delivery_address):
    """????? ??? ????"""
    try:
        items = json.loads(items_json) if isinstance(items_json, str) else items_json
        
        # ????? Sales Order
        order = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": patient_id,
            "delivery_date": frappe.utils.add_days(None, 2),
            "items": []
        })
        
        for item in items:
            order.append("items", {
                "item_code": item["item_code"],
                "qty": item["qty"],
                "rate": item.get("rate", 0)
            })
        
        order.insert(ignore_permissions=True)
        order.submit()
        
        frappe.db.commit()
        
        return {
            "success": True,
            "order_id": order.name,
            "message": "?? ????? ????? ?????"
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Create Order Error")
        return {
            "success": False,
            "message": str(e)
        }