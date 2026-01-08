#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medication API
Handles all medication schedule operations and hooks
"""

import frappe
from frappe import _
import json
from datetime import datetime, timedelta


# ============================================================================
# DOCUMENT HOOKS (Called from hooks.py)
# ============================================================================

def validate(doc, method=None):
    """
    Validate Medication Schedule before save
    Called by hooks.py: doc_events["Medication Schedule"]["validate"]
    """
    try:
        # ?????? ?? ???????? ????????
        if not doc.patient:
            frappe.throw(_("Patient is required"))
        
        if not doc.medication_name:
            frappe.throw(_("Medication name is required"))
        
        # ?????? ?? ???????
        if doc.current_stock and doc.current_stock < 0:
            frappe.throw(_("Current stock cannot be negative"))
        
        # ?????? ?? ????????
        if doc.start_date and doc.end_date:
            if doc.end_date < doc.start_date:
                frappe.throw(_("End date cannot be before start date"))
        
        # ?????? ?? ???? ?????
        if not doc.times or len(doc.times) == 0:
            frappe.throw(_("Please add at least one time for medication"))
        
        frappe.logger().info(f"? Medication Schedule validated: {doc.name}")
        
    except Exception as e:
        frappe.logger().error(f"? Validation error: {str(e)}")
        raise


def before_save(doc, method=None):
    """
    Calculate depletion before saving
    Called by hooks.py: doc_events["Medication Schedule"]["before_save"]
    """
    calculate_depletion(doc, method)


def calculate_depletion(doc, method=None):
    """
    ???? ??? ?????? ??? ???? ??????
    """
    try:
        if not doc.current_stock:
            doc.days_until_depletion = 0
            return
        
        # ???? ????????? ??????
        times_count = len(doc.times) if doc.times else 0
        
        if times_count == 0:
            doc.daily_consumption = 0
            doc.days_until_depletion = 0
            return
        
        # ???? ????????? ?????? ????? ??? ???????
        if doc.frequency == "Once Daily":
            doc.daily_consumption = 1
        elif doc.frequency == "Twice Daily":
            doc.daily_consumption = 2
        elif doc.frequency == "Three Times Daily":
            doc.daily_consumption = 3
        elif doc.frequency == "Four Times Daily":
            doc.daily_consumption = 4
        else:
            # ??????? ??? ?????? ??????
            doc.daily_consumption = times_count
        
        # ???? ??? ??????
        if doc.daily_consumption > 0:
            doc.days_until_depletion = int(doc.current_stock / doc.daily_consumption)
        else:
            doc.days_until_depletion = 0
        
        # ????? last_stock_update
        doc.last_stock_update = frappe.utils.now()
        
        frappe.logger().info(
            f"? Calculated depletion for {doc.medication_name}: "
            f"{doc.days_until_depletion} days "
            f"(Stock: {doc.current_stock}, Daily: {doc.daily_consumption})"
        )
        
    except Exception as e:
        frappe.logger().error(f"? Depletion calculation error: {str(e)}")
        # ?? ???? ?????? ??? ?????
        doc.days_until_depletion = 0


def after_insert(doc, method=None):
    """
    After inserting new medication schedule
    Called by hooks.py: doc_events["Medication Schedule"]["after_insert"]
    """
    try:
        # ????? ????? ??????
        if doc.patient:
            create_notification(
                patient=doc.patient,
                title=_("Medication Added"),
                body=_(f"New medication {doc.medication_name} has been added to your schedule"),
                notification_type="Medication Added"
            )
        
        frappe.logger().info(f"? Medication Schedule created: {doc.name}")
        
    except Exception as e:
        frappe.logger().error(f"? After insert error: {str(e)}")


def on_update(doc, method=None):
    """
    After updating medication schedule
    Called by hooks.py: doc_events["Medication Schedule"]["on_update"]
    """
    try:
        # ?????? ?? ????????? ?? ???????
        if doc.has_value_changed("current_stock"):
            old_stock = doc.get_value("current_stock") or 0
            new_stock = doc.current_stock or 0
            
            # ??? ????? ??????? ??? ????? ?????
            if new_stock <= doc.reorder_level and doc.auto_reorder:
                send_low_stock_alert(doc)
        
        # ?????? ?? ????? ??????
        if doc.has_value_changed("is_active"):
            if not doc.is_active:
                # ????? ????? ?????? ??????
                create_notification(
                    patient=doc.patient,
                    title=_("Medication Deactivated"),
                    body=_(f"Medication {doc.medication_name} has been deactivated"),
                    notification_type="Medication Status Changed"
                )
        
        frappe.logger().info(f"? Medication Schedule updated: {doc.name}")
        
    except Exception as e:
        frappe.logger().error(f"? On update error: {str(e)}")


def update_adherence(doc, method=None):
    """
    Update adherence statistics after logging medication
    Called by hooks.py: doc_events["Medication Log"]["after_insert"]
    """
    try:
        if not doc.medication_schedule:
            return
        
        schedule = frappe.get_doc("Medication Schedule", doc.medication_schedule)
        
        # ????? ??????? ??? ?? ????? ??????
        if doc.status == "Taken" and doc.quantity_taken:
            new_stock = (schedule.current_stock or 0) - doc.quantity_taken
            
            if new_stock < 0:
                frappe.msgprint(_("Warning: Stock is now negative!"), indicator="orange")
                new_stock = 0
            
            schedule.current_stock = new_stock
            schedule.save(ignore_permissions=True)
            
            frappe.logger().info(
                f"? Stock updated for {schedule.medication_name}: "
                f"Old={schedule.current_stock}, New={new_stock}"
            )
        
    except Exception as e:
        frappe.logger().error(f"? Update adherence error: {str(e)}")


# ============================================================================
# API METHODS (Whitelisted for external access)
# ============================================================================

@frappe.whitelist()
def get_patient_medications(patient_id, active_only=1):
    """
    Get all medications for a patient
    """
    try:
        filters = {"patient": patient_id}
        
        if int(active_only):
            filters["is_active"] = 1
        
        medications = frappe.get_all(
            "Medication Schedule",
            filters=filters,
            fields=[
                "name", "medication_name", "scientific_name", 
                "dosage", "dosage_unit", "frequency",
                "current_stock", "stock_unit", "daily_consumption",
                "days_until_depletion", "reorder_level", "auto_reorder",
                "start_date", "end_date", "instructions", "side_effects",
                "image", "color_code", "is_active", "last_refill_date"
            ],
            order_by="creation desc"
        )
        
        # ????? ??????? ??? ????
        for med in medications:
            times = frappe.get_all(
                "Medication Time",
                filters={"parent": med.name},
                fields=["time", "before_after_meal", "notes"],
                order_by="time"
            )
            med["times"] = times
        
        return medications
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Patient Medications Error")
        frappe.throw(_("Error fetching medications: {0}").format(str(e)))


@frappe.whitelist()
def add_medication(patient_id, medication_name, scientific_name=None, 
                   dosage=None, dosage_unit=None, frequency="Once Daily",
                   current_stock=0, stock_unit="Tablet", 
                   start_date=None, end_date=None,
                   instructions=None, side_effects=None,
                   color_code=None, image=None, auto_reorder=1, reorder_level=10,
                   times_json=None):
    """
    Add new medication schedule
    """
    try:
        # ????? Medication Schedule
        med_schedule = frappe.get_doc({
            "doctype": "Medication Schedule",
            "patient": patient_id,
            "medication_name": medication_name,
            "scientific_name": scientific_name,
            "dosage": dosage,
            "dosage_unit": dosage_unit,
            "frequency": frequency,
            "current_stock": current_stock,
            "stock_unit": stock_unit,
            "start_date": start_date or frappe.utils.today(),
            "end_date": end_date,
            "instructions": instructions,
            "side_effects": side_effects,
            "color_code": color_code or "#4CAF50",
            "image": image,
            "auto_reorder": auto_reorder,
            "reorder_level": reorder_level,
            "is_active": 1
        })
        
        # ????? ???????
        if times_json:
            times = json.loads(times_json) if isinstance(times_json, str) else times_json
            
            for time_entry in times:
                med_schedule.append("times", {
                    "time": time_entry.get("time"),
                    "before_after_meal": time_entry.get("before_after_meal", "After Meal"),
                    "notes": time_entry.get("notes")
                })
        
        med_schedule.insert(ignore_permissions=True)
        
        return {
            "message": "Medication added successfully",
            "medication_id": med_schedule.name,
            "daily_consumption": med_schedule.daily_consumption,
            "days_until_depletion": med_schedule.days_until_depletion
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Add Medication Error")
        frappe.throw(_("Error adding medication: {0}").format(str(e)))


@frappe.whitelist()
def log_medication_taken(patient_id, medication_schedule, 
                         scheduled_date=None, scheduled_time=None,
                         actual_datetime=None, status="Taken",
                         quantity_taken=1, notes=None):
    """
    Log that medication was taken
    """
    try:
        log = frappe.get_doc({
            "doctype": "Medication Log",
            "patient": patient_id,
            "medication_schedule": medication_schedule,
            "scheduled_date": scheduled_date or frappe.utils.today(),
            "scheduled_time": scheduled_time,
            "actual_datetime": actual_datetime or frappe.utils.now(),
            "status": status,
            "quantity_taken": quantity_taken if status == "Taken" else 0,
            "notes": notes,
            "logged_by": frappe.session.user,
            "reminder_sent": 0
        })
        
        log.insert(ignore_permissions=True)
        
        # ???? ????? ??????? ???????? ??? hook
        
        return {
            "message": "Medication logged successfully",
            "log_id": log.name
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Log Medication Error")
        frappe.throw(_("Error logging medication: {0}").format(str(e)))


@frappe.whitelist()
def update_stock(medication_schedule, new_stock, reason=None):
    """
    Update medication stock
    """
    try:
        schedule = frappe.get_doc("Medication Schedule", medication_schedule)
        
        old_stock = schedule.current_stock
        schedule.current_stock = new_stock
        schedule.last_refill_date = frappe.utils.today()
        
        if reason:
            schedule.add_comment("Comment", f"Stock updated from {old_stock} to {new_stock}. Reason: {reason}")
        
        schedule.save(ignore_permissions=True)
        
        return {
            "message": "Stock updated successfully",
            "old_stock": old_stock,
            "new_stock": new_stock,
            "days_until_depletion": schedule.days_until_depletion
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update Stock Error")
        frappe.throw(_("Error updating stock: {0}").format(str(e)))


@frappe.whitelist()
def get_low_stock_medications(patient_id=None, threshold=10):
    """
    Get medications with low stock
    """
    try:
        filters = {
            "is_active": 1,
            "days_until_depletion": ["<=", threshold]
        }
        
        if patient_id:
            filters["patient"] = patient_id
        
        medications = frappe.get_all(
            "Medication Schedule",
            filters=filters,
            fields=[
                "name", "patient", "medication_name", 
                "current_stock", "days_until_depletion",
                "reorder_level", "auto_reorder"
            ],
            order_by="days_until_depletion"
        )
        
        return medications
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Low Stock Error")
        frappe.throw(_("Error fetching low stock medications: {0}").format(str(e)))


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def send_low_stock_alert(schedule):
    """
    Send low stock alert to patient
    """
    try:
        create_notification(
            patient=schedule.patient,
            title=_("Low Stock Alert"),
            body=_(f"{schedule.medication_name} stock is low. Only {schedule.days_until_depletion} days remaining."),
            notification_type="Low Stock Alert",
            related_doctype="Medication Schedule",
            related_document=schedule.name
        )
        
        frappe.logger().info(f"? Low stock alert sent for {schedule.medication_name}")
        
    except Exception as e:
        frappe.logger().error(f"? Send low stock alert error: {str(e)}")


def create_notification(patient, title, body, notification_type, 
                       related_doctype=None, related_document=None):
    """
    Create notification log
    """
    try:
        notification = frappe.get_doc({
            "doctype": "Notification Log",
            "patient": patient,
            "type": notification_type,
            "title": title,
            "body": body,
            "status": "Sent",
            "sent_at": frappe.utils.now(),
            "related_doctype": related_doctype,
            "related_document": related_document
        })
        
        notification.insert(ignore_permissions=True)
        
        # ????? FCM notification ??? ??? ??????
        try:
            from my_medicinal.my_medicinal.notifications import send_fcm_notification
            send_fcm_notification(patient, title, body)
        except:
            pass
        
    except Exception as e:
        frappe.logger().error(f"? Create notification error: {str(e)}")































