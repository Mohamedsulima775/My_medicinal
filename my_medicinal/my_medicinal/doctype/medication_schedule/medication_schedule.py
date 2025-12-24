# -*- coding: utf-8 -*-
# Copyright (c) 2025, Your Company
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, add_days
import json

class MedicationSchedule(Document):
    def validate(self):
        """Validation on save"""
        self.validate_times()
        self.validate_dates()
        self.validate_stock()
        self.calculate_daily_consumption()
        self.calculate_days_until_depletion()

    def validate_times(self):
        """Validate medication times"""
        if not self.times or len(self.times) == 0:
            frappe.throw("Please add at least one medication time")

        # ?????? ?? ??? ????? ????? ?????? ??????
        times_list = [t.time for t in self.times]
        if len(times_list) != len(set(times_list)):
            frappe.throw("Duplicate medication times found")

    def validate_dates(self):
        """Validate start and end dates"""
        if self.start_date:
            start = getdate(self.start_date)
            today_date = getdate(today())
            #?????? ?? ???? ??? ??????? ?????? ????  ?? ???
            if start > add_days(today_date, 365):
                frappe.throw("Start date cannot be more than 1 year in the future")

        if self.start_date and self.end_date:
            start = getdate(self.start_date)
            end = getdate(self.end_date)
   #?????? ?? ????  ????? ???????? ?? ?????? ??? ????? ?????
            if end < start:
                frappe.throw("End date cannot be before start date")

    def validate_stock(self):
    #?????? ??????? ?? ???? ??? ?? 0
        """Validate stock values"""
        if self.current_stock < 0:
            frappe.throw("Current stock cannot be negative")
        #?????? ??????? ?? ???? ???? ?? 1000
        if self.current_stock > 1000:
            frappe.throw("Current stock seems unrealistic. Please check the value.")

    #----------------------------------------------
    # ???? ????????? ?????? ????? ??? ?????


    #-------------------------------------------------
    def calculate_daily_consumption(self):
        """Calculate daily consumption based on dosage and frequency"""
        # Parse dosage (e.g., "500mg" -> 1 tablet)
        # For simplicity, we assume 1 dose per time
        dosage_per_time = 1

        # Parse dosage if it contains a number
        import re
        if self.dosage:
            numbers = re.findall(r'\d+', self.dosage)
            if numbers:
                dosage_per_time = float(numbers[0]) / float(numbers[0])  # Normalize to 1

        # Calculate based on number of times per day
        times_per_day = len(self.times) if self.times else 0

        self.daily_consumption = dosage_per_time * times_per_day

    #____________________________________________________


    def calculate_days_until_depletion(self):
        """Calculate how many days until medication runs out"""
        if self.daily_consumption and self.daily_consumption > 0:
            self.days_until_depletion = int(self.current_stock / self.daily_consumption)
        else:
            self.days_until_depletion = 0


    #-------------------------------

    def after_insert(self):
        """After insert"""
        # Schedule reminders
        self.schedule_reminders()

    def on_update(self):
        """On update"""
        # Check if we need to send low stock alert
        if self.days_until_depletion <= 5 and self.is_active:
            self.send_low_stock_alert()

    def schedule_reminders(self):
        """Schedule medication reminders"""
        if not self.is_active:
            return

        # This will be handled by background jobs
        # For now, just log
        frappe.logger().info(f"Reminders scheduled for {self.medication_name}")

    def send_low_stock_alert(self):
        """Send low stock alert"""
        patient = frappe.get_doc("patient", self.patient)

        # Create notification
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"Low Stock Alert: {self.medication_name}",
            "for_user": patient.user,
            "type": "Alert",
            "document_type": "Medication Schedule",
            "document_name": self.name,
            "email_content": f"""
                <p>Dear {patient.patient_name},</p>
                <p>Your medication <strong>{self.medication_name}</strong> is running low.</p>
                <p>Current stock: {self.current_stock} {self.stock_unit}</p>
                <p>Days remaining: {self.days_until_depletion} days</p>
                <p>Please order more medication soon.</p>
            """
        }).insert(ignore_permissions=True)

    def refill_stock(self, quantity):
        """Refill medication stock"""
        self.current_stock += quantity
        self.calculate_days_until_depletion()
        self.save()

        return {
            "message": "Stock refilled successfully",
            "new_stock": self.current_stock,
            "days_until_depletion": self.days_until_depletion
        }

    def consume_medication(self):
        """Consume one dose of medication"""
        if self.current_stock <= 0:
            frappe.throw("No stock available")

        self.current_stock -= 1
        self.calculate_days_until_depletion()
        self.save()

        return {
            "message": "Medication consumed",
            "remaining_stock": self.current_stock,
            "days_until_depletion": self.days_until_depletion
        }


# API Functions

@frappe.whitelist()
def get_medications(patient_id, active_only=1):
    """Get all medications for a patient"""
    filters = {"patient": patient_id}

    if int(active_only):
        filters["is_active"] = 1

    medications = frappe.get_all("Medication Schedule",
        filters=filters,
        fields=[
            "name", "medication_name", "scientific_name",
            "dosage", "frequency", "current_stock", "stock_unit",
            "daily_consumption", "days_until_depletion",
            "color_code", "image", "is_active",
            "start_date", "end_date", "instructions"
        ],
        order_by="medication_name"
    )

    # Get times for each medication
    for med in medications:
        med['times'] = frappe.get_all("Medication Time",
            filters={"parent": med.name},
            fields=["time", "before_after_meal", "notes"],
            order_by="time"
        )

    return medications


@frappe.whitelist()
def get_medications_due(patient_id, time_window=30):
    """Get medications due within time window (minutes)"""
    from datetime import datetime, timedelta

    now = datetime.now()
    window_start = now - timedelta(minutes=int(time_window))
    window_end = now + timedelta(minutes=int(time_window))

    # Get active medications
    medications = frappe.get_all("Medication Schedule",
        filters={
            "patient": patient_id,
            "is_active": 1
        },
        fields=[
            "name", "medication_name", "dosage",
            "current_stock", "color_code", "image"
        ]
    )

    due_medications = []

    for med in medications:
        # Get times for this medication
        times = frappe.get_all("Medication Time",
            filters={"parent": med.name},
            fields=["time", "before_after_meal", "notes"]
        )

        for time_obj in times:
            med_time = datetime.strptime(time_obj.time, "%H:%M:%S")
            med_datetime = now.replace(
                hour=med_time.hour,
                minute=med_time.minute,
                second=0,
                microsecond=0
            )

            if window_start <= med_datetime <= window_end:
                due_medications.append({
                    "schedule_id": med.name,
                    "medication_name": med.medication_name,
                    "dosage": med.dosage,
                    "time": time_obj.time,
                    "before_after_meal": time_obj.before_after_meal,
                    "notes": time_obj.notes,
                    "current_stock": med.current_stock,
                    "color_code": med.color_code,
                    "image": med.image
                })

    return due_medications


@frappe.whitelist()
def add_medication(
    patient_id,
    medication_name,
    dosage,
    frequency,
    times_json,
    current_stock,
    stock_unit="Tablet",
    scientific_name=None,
    medication_type="Tablet",
    instructions=None,
    color_code=None
):
    """Add new medication schedule"""

    # Parse times
    times = json.loads(times_json) if isinstance(times_json, str) else times_json

    # Create medication schedule
    med_schedule = frappe.get_doc({
        "doctype": "Medication Schedule",
        "patient": patient_id,
        "medication_name": medication_name,
        "scientific_name": scientific_name,
        "medication_type": medication_type,
        "dosage": dosage,
        "frequency": frequency,
        "current_stock": int(current_stock),
        "stock_unit": stock_unit,
        "instructions": instructions,
        "color_code": color_code,
        "is_active": 1,
        "start_date": today()
    })

    # Add times
    for time_obj in times:
        med_schedule.append("times", {
            "time": time_obj.get("time"),
            "before_after_meal": time_obj.get("before_after_meal"),
            "notes": time_obj.get("notes")
        })

    med_schedule.insert()

    return {
        "message": "Medication added successfully",
        "medication_id": med_schedule.name,
        "daily_consumption": med_schedule.daily_consumption,
        "days_until_depletion": med_schedule.days_until_depletion
    }


@frappe.whitelist()
def update_stock(schedule_id, new_stock):
    """Update medication stock"""
    med_schedule = frappe.get_doc("Medication Schedule", schedule_id)
    med_schedule.current_stock = int(new_stock)
    med_schedule.save()

    return {
        "message": "Stock updated successfully",
        "current_stock": med_schedule.current_stock,
        "days_until_depletion": med_schedule.days_until_depletion
    }


@frappe.whitelist()
def deactivate_medication(schedule_id):
    """Deactivate medication schedule"""
    med_schedule = frappe.get_doc("Medication Schedule", schedule_id)
    med_schedule.is_active = 0
    med_schedule.end_date = today()
    med_schedule.save()

    return {"message": "Medication deactivated"}


@frappe.whitelist()
def get_low_stock_medications(patient_id, threshold=5):
    """Get medications with low stock"""
    medications = frappe.get_all("Medication Schedule",
        filters={
            "patient": patient_id,
            "is_active": 1,
            "days_until_depletion": ["<=", int(threshold)]
        },
        fields=[
            "name", "medication_name", "current_stock",
            "stock_unit", "days_until_depletion"
        ],
        order_by="days_until_depletion"
    )

    return medications