# -*- coding: utf-8 -*-
# Copyright (c) 2024, My Medicinal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, now_datetime, add_days, cint, flt
import json

# ============================================
# MEDICATION SCHEDULE APIs
# ============================================

@frappe.whitelist()
def add_medication(patient_id, medication_data):
    """
    Add medication to patient schedule
    
    Args:
        patient_id: Patient ID
        medication_data: JSON with medication info
    
    Returns:
        Created medication schedule
    """
    try:
        if isinstance(medication_data, str):
            medication_data = json.loads(medication_data)
        
        # Verify patient access
        patient = frappe.get_doc("patient", patient_id)
        if patient.user != frappe.session.user and not frappe.has_permission("medication_schedule", "create"):
            frappe.throw(_("Not authorized"))
        
        # Create schedule
        schedule = frappe.get_doc({
            "doctype": "medication_schedule",
            "patient": patient_id,
            "medication_name": medication_data.get("medication_name"),
            "scientific_name": medication_data.get("scientific_name"),
            "dosage": medication_data.get("dosage"),
            "dosage_unit": medication_data.get("dosage_unit", "???"),
            "frequency": medication_data.get("frequency"),
            "current_stock": medication_data.get("current_stock"),
            "stock_unit": medication_data.get("stock_unit", "Tablet"),
            "is_active": 1,
            "start_date": medication_data.get("start_date", today())
        })
        
        # Add times
        if medication_data.get("times"):
            for time_entry in medication_data.get("times"):
                schedule.append("times", time_entry)
        
        schedule.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": True,
            "message": "Medication added successfully",
            "schedule_id": schedule.name,
            "medication_name": schedule.medication_name,
            "current_stock": schedule.current_stock
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Add Medication Error")
        frappe.throw(_("Failed to add medication: {0}").format(str(e)))


@frappe.whitelist()
def get_patient_medications(patient_id, is_active=1):
    """Get all medications for a patient"""
    try:
        filters = {"patient": patient_id}
        if is_active is not None:
            filters["is_active"] = cint(is_active)
        
        medications = frappe.get_all(
            "medication_schedule",
            filters=filters,
            fields=[
                "name", "medication_name", "scientific_name",
                "dosage", "dosage_unit", "frequency",
                "current_stock", "stock_unit",
                "is_active", "start_date"
            ],
            order_by="creation desc"
        )
        
        # Get times for each medication
        for med in medications:
            times = frappe.get_all(
                "medication_time",
                filters={"parent": med.name},
                fields=["time", "before_after_meal"],
                order_by="time"
            )
            med["times"] = times
        
        return medications
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Medications Error")
        frappe.throw(_("Failed to get medications: {0}").format(str(e)))


@frappe.whitelist()
def log_medication_taken(patient_id, medication_schedule_id, scheduled_date, scheduled_time, actual_datetime=None):
    """Log that medication was taken"""
    try:
        if not actual_datetime:
            actual_datetime = now_datetime()
        
        log = frappe.get_doc({
            "doctype": "medication_log",
            "patient": patient_id,
            "medication_schedule": medication_schedule_id,
            "scheduled_date": scheduled_date,
            "scheduled_time": scheduled_time,
            "actual_datetime": actual_datetime,
            "status": "Taken"
        })
        
        log.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": True,
            "log_id": log.name,
            "status": log.status
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Log Medication Error")
        frappe.throw(_("Failed to log medication: {0}").format(str(e)))


@frappe.whitelist()
def get_todays_schedule(patient_id):
    """Get today's medication schedule"""
    try:
        medications = get_patient_medications(patient_id, is_active=1)
        
        schedule = []
        for med in medications:
            for time_entry in med.get("times", []):
                # Check if already logged
                log = frappe.db.get_value(
                    "medication_log",
                    {
                        "patient": patient_id,
                        "medication_schedule": med.name,
                        "scheduled_date": today(),
                        "scheduled_time": time_entry.time
                    },
                    ["name", "status", "actual_datetime"],
                    as_dict=True
                )
                
                schedule.append({
                    "schedule_id": med.name,
                    "medication_name": med.medication_name,
                    "dosage": med.dosage,
                    "dosage_unit": med.dosage_unit,
                    "time": time_entry.time,
                    "status": log.status if log else "Scheduled",
                    "log_id": log.name if log else None
                })
        
        # Sort by time
        schedule.sort(key=lambda x: x["time"])
        
        return schedule
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Today's Schedule Error")
        frappe.throw(_("Failed to get schedule: {0}").format(str(e)))


@frappe.whitelist()
def get_adherence_stats(patient_id, days=30):
    """Get adherence statistics"""
    try:
        from_date = add_days(today(), -days)
        
        # Total scheduled
        total = frappe.db.count(
            "medication_log",
            {
                "patient": patient_id,
                "scheduled_date": [">=", from_date]
            }
        )
        
        # Taken
        taken = frappe.db.count(
            "medication_log",
            {
                "patient": patient_id,
                "scheduled_date": [">=", from_date],
                "status": "Taken"
            }
        )
        
        # Calculate adherence
        adherence = 0
        if total > 0:
            adherence = round((taken / total) * 100, 2)
        
        return {
            "period_days": days,
            "total": total,
            "taken": taken,
            "missed": total - taken,
            "adherence_percentage": adherence
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Adherence Stats Error")
        frappe.throw(_("Failed to get stats: {0}").format(str(e)))