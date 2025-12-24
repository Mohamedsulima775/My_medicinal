

# -*- coding: utf-8 -*-
# Copyright (c) 2025, Your Company
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime, time_diff_in_seconds
from datetime import datetime, timedelta

class MedicationLog(Document):
    def validate(self):
        """Validation on save"""
        self.validate_times()
        self.calculate_time_difference()
        self.determine_on_time_status()
        self.update_medication_stock()
    
    def validate_times(self):
        """Validate scheduled and actual times"""
        if not self.scheduled_time:
            frappe.throw("Scheduled time is required")
        
        scheduled = get_datetime(self.scheduled_time)
        now = now_datetime()
        
        # Cannot schedule in far future (more than 1 day ahead)
        if scheduled > now + timedelta(days=1):
            frappe.throw("Scheduled time cannot be more than 1 day in the future")
        
        # If status is Taken, actual_time is required
        if self.status == "Taken" and not self.actual_time:
            # Set to now if not provided
            self.actual_time = now
        
        # Actual time cannot be in the future
        if self.actual_time:
            actual = get_datetime(self.actual_time)
            if actual > now:
                frappe.throw("Actual time cannot be in the future")
    
    def calculate_time_difference(self):
        """Calculate difference between scheduled and actual time"""
        if self.scheduled_time and self.actual_time:
            scheduled = get_datetime(self.scheduled_time)
            actual = get_datetime(self.actual_time)
            
            # Calculate difference in minutes
            diff_seconds = time_diff_in_seconds(actual, scheduled)
            self.time_difference = int(diff_seconds / 60)
    
    def determine_on_time_status(self):
        """Determine if medication was taken on time"""
        if self.status == "Taken" and self.time_difference is not None:
            # Consider on-time if taken within 30 minutes of scheduled time
            self.was_on_time = abs(self.time_difference) <= 30
        else:
            self.was_on_time = 0
    
    def update_medication_stock(self):
        """Update medication stock when taken"""
        if self.status == "Taken" and not self.is_new():
            # Check if status changed to Taken
            old_doc = self.get_doc_before_save()
            if old_doc and old_doc.status != "Taken" and self.status == "Taken":
                self._decrease_stock()
        elif self.status == "Taken" and self.is_new():
            self._decrease_stock()
    
    def _decrease_stock(self):
        """Decrease stock in Medication Schedule"""
        try:
            med_schedule = frappe.get_doc("Medication Schedule", self.medication_schedule)
            
            if med_schedule.current_stock > 0:
                med_schedule.current_stock -= 1
                med_schedule.save(ignore_permissions=True)
                
                frappe.msgprint(
                    f"Stock updated: {med_schedule.current_stock} {med_schedule.stock_unit} remaining",
                    indicator="green"
                )
            else:
                frappe.msgprint(
                    "Warning: Medication stock is 0",
                    indicator="orange"
                )
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Update Stock Error")
    
    def before_insert(self):
        """Before insert"""
        # Set logged_by to current user
        if not self.logged_by:
            self.logged_by = frappe.session.user
    
    def after_insert(self):
        """After insert"""
        # Create notification if missed
        if self.status == "Missed":
            self.send_missed_notification()
    
    def send_missed_notification(self):
        """Send notification for missed medication"""
        patient = frappe.get_doc("patient", self.patient)
        
        if patient.user:
            frappe.get_doc({
                "doctype": "Notification Log",
                "subject": f"Missed Medication: {self.medication_name}",
                "for_user": patient.user,
                "type": "Alert",
                "document_type": "Medication Log",
                "document_name": self.name,
                "email_content": f"""
                    <p>Dear {patient.patient_name},</p>
                    <p>You missed your medication <strong>{self.medication_name}</strong>.</p>
                    <p>Scheduled time: {self.scheduled_time}</p>
                    <p>Please try to maintain your medication schedule for better health outcomes.</p>
                """
            }).insert(ignore_permissions=True)


# API Functions

@frappe.whitelist()
def log_medication(
    patient_id,
    medication_schedule_id,
    scheduled_time,
    status="Taken",
    actual_time=None,
    skip_reason=None,
    notes=None
):
    """Log medication intake"""
    
    try:
        log = frappe.get_doc({
            "doctype": "Medication Log",
            "patient": patient_id,
            "medication_schedule": medication_schedule_id,
            "scheduled_time": scheduled_time,
            "actual_time": actual_time or now_datetime(),
            "status": status,
            "skip_reason": skip_reason,
            "notes": notes,
            "logged_by": frappe.session.user
        })
        
        log.insert()
        
        return {
            "success": True,
            "message": "Medication logged successfully",
            "log_id": log.name,
            "was_on_time": log.was_on_time,
            "time_difference": log.time_difference
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Log Medication Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def get_medication_history(patient_id, medication_schedule_id=None, days=30):
    """Get medication log history"""
    
    from datetime import datetime, timedelta
    
    filters = {
        "patient": patient_id,
        "scheduled_time": [">=", (datetime.now() - timedelta(days=int(days))).strftime("%Y-%m-%d")]
    }
    
    if medication_schedule_id:
        filters["medication_schedule"] = medication_schedule_id
    
    logs = frappe.get_all("Medication Log",
        filters=filters,
        fields=[
            "name", "medication_name", "scheduled_time",
            "actual_time", "status", "was_on_time",
            "time_difference", "skip_reason", "notes"
        ],
        order_by="scheduled_time desc"
    )
    
    return logs


@frappe.whitelist()
def get_adherence_stats(patient_id, days=30):
    """Calculate adherence statistics"""
    
    from datetime import datetime, timedelta
    
    # Get logs from last X days
    start_date = (datetime.now() - timedelta(days=int(days))).strftime("%Y-%m-%d")
    
    logs = frappe.get_all("Medication Log",
        filters={
            "patient": patient_id,
            "scheduled_time": [">=", start_date]
        },
        fields=["status", "was_on_time"]
    )
    
    if not logs:
        return {
            "total_doses": 0,
            "taken": 0,
            "missed": 0,
            "skipped": 0,
            "adherence_rate": 0,
            "on_time_rate": 0
        }
    
    total = len(logs)
    taken = len([l for l in logs if l.status == "Taken"])
    missed = len([l for l in logs if l.status == "Missed"])
    skipped = len([l for l in logs if l.status == "Skipped"])
    on_time = len([l for l in logs if l.was_on_time])
    
    adherence_rate = (taken / total * 100) if total > 0 else 0
    on_time_rate = (on_time / taken * 100) if taken > 0 else 0
    
    return {
        "total_doses": total,
        "taken": taken,
        "missed": missed,
        "skipped": skipped,
        "adherence_rate": round(adherence_rate, 2),
        "on_time_rate": round(on_time_rate, 2)
    }


@frappe.whitelist()
def get_missed_doses(patient_id):
    """Get missed doses that need to be logged"""
    
    from datetime import datetime, timedelta
    
    # Get active medications
    medications = frappe.get_all("Medication Schedule",
        filters={
            "patient": patient_id,
            "is_active": 1
        },
        fields=["name", "medication_name", "times"]
    )
    
    missed_doses = []
    now = datetime.now()
    
    for med in medications:
        # Get times for this medication
        times = frappe.get_all("Medication Time",
            filters={"parent": med.name},
            fields=["time"]
        )
        
        for time_obj in times:
            # Parse time
            time_parts = time_obj.time.split(":")
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            
            # Create scheduled datetime for today
            scheduled = datetime(now.year, now.month, now.day, hour, minute)
            
            # If time has passed and not logged
            if scheduled < now:
                # Check if already logged
                existing_log = frappe.db.exists("Medication Log", {
                    "medication_schedule": med.name,
                    "scheduled_time": scheduled.strftime("%Y-%m-%d %H:%M:%S")
                })
                
                if not existing_log:
                    missed_doses.append({
                        "medication_schedule": med.name,
                        "medication_name": med.medication_name,
                        "scheduled_time": scheduled.strftime("%Y-%m-%d %H:%M:%S"),
                        "hours_ago": int((now - scheduled).total_seconds() / 3600)
                    })
    
    return missed_doses


@frappe.whitelist()
def auto_log_missed_doses():
    """Automatically log doses as missed after 2 hours (Background Job)"""
    
    from datetime import datetime, timedelta
    
    # Get all patients with active medications
    patients = frappe.get_all("patient",
        filters={"status": "Active"},
        fields=["name"]
    )
    
    logged_count = 0
    
    for patient in patients:
        missed = get_missed_doses(patient.name)
        
        for dose in missed:
            # If more than 2 hours late, auto-log as missed
            if dose["hours_ago"] >= 2:
                try:
                    log_medication(
                        patient_id=patient.name,
                        medication_schedule_id=dose["medication_schedule"],
                        scheduled_time=dose["scheduled_time"],
                        status="Missed",
                        notes="Auto-logged as missed after 2 hours"
                    )
                    logged_count += 1
                except:
                    pass
    
    return {
        "message": f"Auto-logged {logged_count} missed doses"
    }


@frappe.whitelist()
def update_log_status(log_id, new_status, notes=None):
    """Update medication log status"""
    
    log = frappe.get_doc("Medication Log", log_id)
    log.status = new_status
    
    if notes:
        log.notes = notes
    
    log.save()
    
    return {
        "success": True,
        "message": "Log updated successfully"
    }


@frappe.whitelist()
def get_weekly_adherence_chart(patient_id):
    """Get adherence data for weekly chart"""
    
    from datetime import datetime, timedelta
    
    data = []
    
    for i in range(7):
        date = (datetime.now() - timedelta(days=6-i)).date()
        
        # Count logs for this date
        logs = frappe.get_all("Medication Log",
            filters={
                "patient": patient_id,
                "scheduled_time": ["between", [
                    f"{date} 00:00:00",
                    f"{date} 23:59:59"
                ]]
            },
            fields=["status"]
        )
        
        total = len(logs)
        taken = len([l for l in logs if l.status == "Taken"])
        adherence = (taken / total * 100) if total > 0 else 0
        
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "day": date.strftime("%A")[:3],  # Mon, Tue, etc.
            "total": total,
            "taken": taken,
            "adherence": round(adherence, 1)
        })
    
    return data