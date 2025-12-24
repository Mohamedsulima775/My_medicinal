# chronic_disease/chronic_disease/tasks.py

import frappe
from frappe.utils import now_datetime, add_to_date, get_datetime
import requests
import json

def all():
    """???? ?????"""
    check_medication_depletion()
    create_daily_medication_logs()

def hourly():
    """???? ?? ????"""
    send_medication_reminders()

def check_medication_depletion():
    """??? ??????? ??????? ?? ??????"""
    
    # ?????? ??? ??????? ?????? ?????
    schedules = frappe.get_all(
        "Medication Schedule",
        filters={
            "is_active": 1,
            "days_until_depletion": ["<=", 5],
            "days_until_depletion": [">", 0]
        },
        fields=["name", "patient", "medication_name", "days_until_depletion"]
    )
    
    for schedule in schedules:
        # ?????? ?? ??? ????? ????? ?????
        today = frappe.utils.today()
        existing = frappe.db.exists("Notification Log", {
            "user": frappe.db.get_value("Patient", schedule.patient, "user"),
            "notification_type": "Low Stock",
            "creation": [">=", today]
        })
        
        if not existing:
            send_notification(
                patient_id=schedule.patient,
                title=f"?? {schedule.medication_name} ????? ??????",
                message=f"??????? ???? ?? {schedule.days_until_depletion} ???? ???",
                notification_type="Low Stock"
            )

def create_daily_medication_logs():
    """????? ????? ??????? ???????"""
    
    tomorrow = add_to_date(frappe.utils.today(), days=1)
    
    # ?????? ??? ???? ??????? ??????
    schedules = frappe.get_all(
        "Medication Schedule",
        filters={"is_active": 1},
        fields=["name", "patient"]
    )
    
    for schedule_data in schedules:
        schedule = frappe.get_doc("Medication Schedule", schedule_data.name)
        
        # ????? log ??? ????
        for time_row in schedule.times:
            # ?????? ?? ??? ???? log ????
            existing = frappe.db.exists("Medication Log", {
                "medication_schedule": schedule.name,
                "scheduled_date": tomorrow,
                "scheduled_time": time_row.time
            })
            
            if not existing:
                log = frappe.get_doc({
                    "doctype": "Medication Log",
                    "patient": schedule.patient,
                    "medication_schedule": schedule.name,
                    "scheduled_date": tomorrow,
                    "scheduled_time": time_row.time,
                    "status": "Scheduled"
                })
                log.insert(ignore_permissions=True)

def send_medication_reminders():
    """????? ??????? ???????"""
    
    now = now_datetime()
    current_time = now.time()
    today = now.date()
    
    # ?????? ??? ??????? ???????? ?? ?????? ???????
    from datetime import timedelta
    reminder_time = (now + timedelta(minutes=5)).time()
    
    logs = frappe.get_all(
        "Medication Log",
        filters={
            "scheduled_date": today,
            "scheduled_time": ["<=", reminder_time],
            "status": "Scheduled",
            "reminder_sent": 0
        },
        fields=["name", "patient", "medication_schedule", "scheduled_time"]
    )
    
    for log_data in logs:
        log = frappe.get_doc("Medication Log", log_data.name)
        schedule = frappe.get_doc("Medication Schedule", log.medication_schedule)
        
        # ????? ???????
        send_notification(
            patient_id=log.patient,
            title="? ???? ??????!",
            message=f"??? ??? ????? {schedule.medication_name}",
            notification_type="Medication Reminder"
        )
        
        # ????? ??????
        log.reminder_sent = 1
        log.save(ignore_permissions=True)

def send_notification(patient_id, title, message, notification_type):
    """????? ????? ??????"""
    
    patient = frappe.get_doc("Patient", patient_id)
    
    # ??? ???????
    notif = frappe.get_doc({
        "doctype": "Notification Log",
        "user": patient.user,
        "title": title,
        "message": message,
        "notification_type": notification_type,
        "fcm_token": patient.fcm_token,
        "sent_at": now_datetime()
    })
    notif.insert(ignore_permissions=True)
    
    # ????? ??? FCM ??? ??? ???? token
    if patient.fcm_token:
        send_fcm_notification(patient.fcm_token, title, message)

def send_fcm_notification(fcm_token, title, message):
    """????? ????? ??? Firebase"""
    
    # ?????? Server Key ?? Firebase Console
    server_key = frappe.conf.get("fcm_server_key")
    
    if not server_key:
        return
    
    url = "https://fcm.googleapis.com/fcm/send"
    headers = {
        "Authorization": f"key={server_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "to": fcm_token,
        "notification": {
            "title": title,
            "body": message,
            "sound": "default"
        },
        "priority": "high"
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.json()
    except Exception as e:
        frappe.log_error(f"FCM Error: {str(e)}")