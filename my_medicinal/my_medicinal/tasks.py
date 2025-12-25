# -*- coding: utf-8 -*-
# Copyright (c) 2024, My Medicinal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, now_datetime, add_days, get_datetime, time_diff_in_hours
import json

# ============================================
# SCHEDULED TASKS
# ============================================

def all():
    """Tasks that run every day"""
    check_stock_depletion()
    generate_daily_adherence_reports()
    cleanup_old_notifications()


def hourly():
    """Tasks that run every hour"""
    send_medication_reminders()


# ============================================
# 1. MEDICATION REMINDERS
# ============================================

def send_medication_reminders():
    """
    Check upcoming medications and send reminders
    Runs every hour (or every 5 minutes in production)
    """
    try:
        from datetime import datetime, timedelta
        
        print("\n?? Checking medication reminders...")
        
        # Get current time + 5 minutes window
        now = now_datetime()
        window_end = now + timedelta(minutes=5)
        
        # Get all active medication schedules
        schedules = frappe.get_all(
            "Medication Schedule",
            filters={"is_active": 1},
            fields=["name", "patient", "medication_name", "dosage"]
        )
        
        reminders_sent = 0
        
        for schedule in schedules:
            # Get times for this schedule
            times = frappe.get_all(
                "Medication Time",
                filters={"parent": schedule.name},
                fields=["time"],
                order_by="time"
            )
            
            for time_entry in times:
                # Build scheduled datetime for today
                scheduled_time = get_datetime(f"{today()} {time_entry.time}")
                
                # Check if within reminder window
                if now <= scheduled_time <= window_end:
                    # Check if already reminded today
                    existing_reminder = frappe.db.exists(
                        "Medication Reminder",
                        {
                            "medication_schedule": schedule.name,
                            "reminder_date": today(),
                            "reminder_time": time_entry.time
                        }
                    )
                    
                    if not existing_reminder:
                        # Create reminder
                        reminder = frappe.get_doc({
                            "doctype": "Medication Reminder",
                            "medication_schedule": schedule.name,
                            "patient": schedule.patient,
                            "reminder_date": today(),
                            "reminder_time": time_entry.time,
                            "status": "Pending",
                            "reminder_sent_at": now_datetime()
                        })
                        reminder.insert(ignore_permissions=True)
                        
                        # Send notification
                        send_medication_notification(
                            schedule.patient,
                            schedule.medication_name,
                            schedule.dosage,
                            time_entry.time
                        )
                        
                        reminders_sent += 1
        
        frappe.db.commit()
        print(f"? Sent {reminders_sent} medication reminders")
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Medication Reminders Error")
        print(f"? Error in reminders: {str(e)}")

def send_medication_notification(patient_id, medication_name, dosage, time):
    """Send notification for medication reminder"""
    try:
        # Import FCM function
        from my_medicinal.my_medicinal.notifications import send_medication_notification_fcm
        
        # Send via FCM
        fcm_result = send_medication_notification_fcm(
            patient_id,
            medication_name,
            dosage,
            time
        )
        
        # Also log in DB (fallback)
        patient = frappe.get_doc("patient", patient_id)
        notification = frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"? Medication Time",
            "for_user": patient.user,
            "type": "Alert",
            "document_type": "Medication Schedule",
            "email_content": f"""
                <p>my dear{patient.patient_name},</p>
                <p>it's time for your medication: <strong>{medication_name}</strong></p>
                <p>Dose: {dosage}</p>
                <p>Time: {time}</p>
            """
        })
        notification.insert(ignore_permissions=True)
        
        if fcm_result.get('push', {}).get('success'):
            print(f"? FCM + DB notification sent to {patient.patient_name}")
        else:
            print(f"??  DB notification sent (FCM failed): {patient.patient_name}")
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Send Notification Error")
        print(f"? Notification error: {str(e)}")


# ============================================
# 2. STOCK DEPLETION CHECK
# ============================================

def check_stock_depletion():
    """
    Check medications running low on stock
    Runs daily at midnight
    """
    try:
        print("\n?? Checking medication stock...")
        
        # Get all active schedules
        schedules = frappe.get_all(
            "Medication Schedule",
            filters={"is_active": 1, "current_stock": [">", 0]},
            fields=[
                "name", "patient", "medication_name",
                "current_stock", "dosage", "frequency"
            ]
        )
        
        alerts_sent = 0
        
        for schedule in schedules:
            # Calculate daily consumption
            dosage = float(schedule.dosage.split()[0] if schedule.dosage else 1)
            
            # Frequency mapping
            freq_map = {
                "Once Daily": 1,
                "Twice Daily": 2,
                "Three Times Daily": 3,
                "Four Times Daily": 4
            }
            times_per_day = freq_map.get(schedule.frequency, 1)
            
            daily_consumption = dosage * times_per_day
            
            if daily_consumption > 0:
                days_remaining = int(schedule.current_stock / daily_consumption)
                
                # Update schedule
                frappe.db.set_value(
                    "Medication Schedule",
                    schedule.name,
                    "days_until_depletion",
                    days_remaining
                )
                
                # Send alerts based on days remaining
                if days_remaining <= 2:
                    send_stock_alert(schedule, days_remaining, "Critical")
                    alerts_sent += 1
                elif days_remaining <= 5:
                    send_stock_alert(schedule, days_remaining, "Warning")
                    alerts_sent += 1
        
        frappe.db.commit()
        print(f"? Sent {alerts_sent} stock alerts")
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Stock Depletion Check Error")
        print(f"? Error in stock check: {str(e)}")


def send_stock_alert(schedule, days_remaining, priority):
    """Send stock depletion alert"""
    try:
        patient = frappe.get_doc("patient", schedule.patient)
        
        if days_remaining <= 0:
            title = "?? ??? ??????!"
            message = f"{schedule.medication_name} ??? ??????. ???? ????!"
        elif days_remaining <= 2:
            title = "?? ????? ????"
            message = f"{schedule.medication_name} ????? ???? {days_remaining} ???"
        else:
            title = "?? ?????"
            message = f"{schedule.medication_name} ????? ???? {days_remaining} ????"
        
        # Create notification
        notification = frappe.get_doc({
            "doctype": "Notification Log",
            "subject": title,
            "for_user": patient.user,
            "type": "Alert",
            "document_type": "Medication Schedule",
            "document_name": schedule.name,
            "email_content": f"""
                <p>????? {patient.patient_name},</p>
                <p>{message}</p>
                <p>??????? ??????: {schedule.current_stock}</p>
            """
        })
        notification.insert(ignore_permissions=True)
        
        print(f"?? Stock alert sent for {schedule.medication_name}")
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Send Stock Alert Error")


# ============================================
# 3. ADHERENCE REPORTS
# ============================================

def generate_daily_adherence_reports():
    """
    Generate adherence reports for active patients
    Runs daily
    """
    try:
        print("\n?? Generating adherence reports...")
        
        # Get all active patients with medications
        patients = frappe.db.sql("""
            SELECT DISTINCT patient
            FROM `tabMedication Schedule`
            WHERE is_active = 1
        """, as_dict=True)
        
        reports_generated = 0
        
        for patient_row in patients:
            patient_id = patient_row.patient
            
            # Calculate adherence for last 30 days
            from_date = add_days(today(), -30)
            
            # Get total scheduled doses
            total_logs = frappe.db.count(
                "Medication Log",
                {
                    "patient": patient_id,
                    "scheduled_date": [">=", from_date]
                }
            )
            
            if total_logs > 0:
                # Get taken doses
                taken_logs = frappe.db.count(
                    "Medication Log",
                    {
                        "patient": patient_id,
                        "scheduled_date": [">=", from_date],
                        "status": "Taken"
                    }
                )
                
                # Calculate adherence
                adherence = round((taken_logs / total_logs) * 100, 2)
                
                # Create/update adherence report
                existing_report = frappe.db.get_value(
                    "Adherence Report",
                    {
                        "patient": patient_id,
                        "report_period": "Monthly",
                        "start_date": from_date
                    },
                    "name"
                )
                
                if existing_report:
                    # Update existing
                    report = frappe.get_doc("Adherence Report", existing_report)
                else:
                    # Create new
                    report = frappe.get_doc({
                        "doctype": "Adherence Report",
                        "patient": patient_id,
                        "report_period": "Monthly",
                        "start_date": from_date,
                        "end_date": today()
                    })
                
                report.total_doses_scheduled = total_logs
                report.doses_taken = taken_logs
                report.doses_missed = total_logs - taken_logs
                report.adherence_percentage = adherence
                report.generated_at = now_datetime()
                
                if existing_report:
                    report.save(ignore_permissions=True)
                else:
                    report.insert(ignore_permissions=True)
                
                reports_generated += 1
                
                # Send notification if adherence is low
                if adherence < 80:
                    send_adherence_alert(patient_id, adherence)
        
        frappe.db.commit()
        print(f"? Generated {reports_generated} adherence reports")
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Adherence Reports Error")
        print(f"? Error in adherence reports: {str(e)}")


def send_adherence_alert(patient_id, adherence):
    """Send low adherence alert"""
    try:
        patient = frappe.get_doc("patient", patient_id)
        
        notification = frappe.get_doc({
            "doctype": "Notification Log",
            "subject": "?? ???? ???????? ??????",
            "for_user": patient.user,
            "type": "Alert",
            "email_content": f"""
                <p>????? {patient.patient_name},</p>
                <p>???? ??????? ??????? {adherence}%</p>
                <p>???? ????? ??????? ?????? ??? ???? ???????!</p>
            """
        })
        notification.insert(ignore_permissions=True)
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Send Adherence Alert Error")


# ============================================
# 4. CLEANUP
# ============================================

def cleanup_old_notifications():
    """
    Delete old read notifications (older than 30 days)
    Runs weekly
    """
    try:
        print("\n?? Cleaning up old notifications...")
        
        cutoff_date = add_days(today(), -30)
        
        # Delete old read notifications
        frappe.db.sql("""
            DELETE FROM `tabNotification Log`
            WHERE read = 1
            AND creation < %(cutoff_date)s
        """, {"cutoff_date": cutoff_date})
        
        frappe.db.commit()
        print(f"? Deleted old notifications")
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Cleanup Error")
        print(f"? Error in cleanup: {str(e)}")


# ============================================
# MANUAL TRIGGERS (for testing)
# ============================================

@frappe.whitelist()
def trigger_reminders_manually():
    """Manual trigger for testing"""
    send_medication_reminders()
    return "Reminders sent"


@frappe.whitelist()
def trigger_stock_check_manually():
    """Manual trigger for testing"""
    check_stock_depletion()
    return "Stock check completed"


@frappe.whitelist()
def trigger_adherence_reports_manually():
    """Manual trigger for testing"""
    generate_daily_adherence_reports()
    return "Reports generated"