
# -*- coding: utf-8 -*-
# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime, timedelta

class MedicalConsultation(Document):
    def validate(self):
        """Validate consultation data before saving"""
        self.validate_dates()
        self.validate_provider_availability()
        self.set_consultation_fee()
    
    def validate_dates(self):
        """Validate consultation date"""
        if self.consultation_date:
            consultation_dt = frappe.utils.get_datetime(self.consultation_date)
            now = frappe.utils.now_datetime()
            
            # Don't allow booking consultations in the past
            if consultation_dt < now and self.status == "Pending":
                frappe.throw(_("Cannot book consultation in the past"))
    
    def validate_provider_availability(self):
        """Check if provider is available at the requested time"""
        if not self.is_new() and self.has_value_changed("consultation_date"):
            return  # Skip validation if just updating other fields
        
        if self.healthcare_provider and self.consultation_date:
            # Check provider status
            provider = frappe.get_doc("Healthcare Provider", self.healthcare_provider)
            if provider.status != "Active":
                frappe.throw(_("Provider {0} is currently {1}").format(
                    provider.provider_name, provider.status
                ))
            
            # Check if time slot is available
            dt = frappe.utils.get_datetime(self.consultation_date)
            day_name = dt.strftime("%A")
            time_str = dt.strftime("%H:%M:%S")
            
            # Check schedule
            is_available = False
            for schedule in provider.schedule:
                if schedule.day == day_name and schedule.is_available:
                    if schedule.from_time <= time_str <= schedule.to_time:
                        is_available = True
                        break
            
            if not is_available:
                frappe.throw(_("Provider is not available at the selected time"))
            
            # Check for conflicting consultations
            existing = frappe.db.exists(
                "Medical Consultation",
                {
                    "healthcare_provider": self.healthcare_provider,
                    "consultation_date": self.consultation_date,
                    "status": ["in", ["Scheduled", "In Progress"]],
                    "name": ["!=", self.name]
                }
            )
            
            if existing:
                frappe.throw(_("This time slot is already booked"))
    
    def set_consultation_fee(self):
        """Set consultation fee from provider"""
        if self.healthcare_provider and not self.consultation_fee:
            provider = frappe.get_doc("Healthcare Provider", self.healthcare_provider)
            self.consultation_fee = provider.consultation_fee
    
    def on_update(self):
        """Actions after updating consultation"""
        # Send notification if status changed
        if self.has_value_changed("status"):
            self.send_status_notification()
    
    def send_status_notification(self):
        """Send notification when status changes"""
        # This will be implemented with notification system
        pass
    
    def on_cancel(self):
        """Actions when consultation is cancelled"""
        self.status = "Cancelled"


# ============================================
# API Functions
# ============================================

@frappe.whitelist()
def create_consultation(patient, healthcare_provider, consultation_type,consultation_date, priority="Normal", notes=None):
    """
    Create a new consultation
    
    Args:
        patient: Patient ID
        healthcare_provider: Provider ID
        consultation_type: Type of consultation
        consultation_date: Date and time
        priority: Priority level (default: Normal)
        notes: Additional notes
    
    Returns:
        Consultation document
    """
    # Validate patient exists
    if not frappe.db.exists("patient", patient):
        frappe.throw(_("Patient not found"))
    
    # Validate provider exists
    if not frappe.db.exists("Healthcare Provider", healthcare_provider):
        frappe.throw(_("Healthcare Provider not found"))
    
    # Create consultation
    consultation = frappe.get_doc({
        "doctype": "Medical Consultation",
        "patient": patient,
        "healthcare_provider": healthcare_provider,
        "consultation_type": consultation_type,
        "consultation_date": consultation_date,
        "status": "Pending",
        "priority": priority,
        "notes": notes
    })
    
    consultation.insert(ignore_permissions=True)
    frappe.db.commit()
    
    return {
        "message": "Consultation created successfully",
        "consultation_id": consultation.name,
        "consultation": consultation.as_dict()
    }


@frappe.whitelist()
def get_consultations(patient_id=None, provider_id=None, status=None, 
                     from_date=None, to_date=None):
    """
    Get list of consultations with filters
    
    Args:
        patient_id: Filter by patient
        provider_id: Filter by provider
        status: Filter by status
        from_date: Start date filter
        to_date: End date filter
    
    Returns:
        List of consultations
    """
    filters = {}
    
    if patient_id:
        filters["patient"] = patient_id
    
    if provider_id:
        filters["healthcare_provider"] = provider_id
    
    if status:
        filters["status"] = status
    
    if from_date:
        filters["consultation_date"] = [">=", from_date]
    
    if to_date:
        if "consultation_date" in filters:
            filters["consultation_date"] = ["between", [from_date, to_date]]
        else:
            filters["consultation_date"] = ["<=", to_date]
    
    consultations = frappe.get_all(
        "Medical Consultation",
        filters=filters,
        fields=[
            "name",
            "patient",
            "patient_name",
            "healthcare_provider",
            "provider_name",
            "consultation_type",
            "consultation_date",
            "status",
            "priority",
            "consultation_fee",
            "payment_status"
        ],
        order_by="consultation_date desc"
    )
    
    return consultations


@frappe.whitelist()
def get_consultation_details(consultation_id):
    """
    Get complete consultation details including messages
    
    Args:
        consultation_id: Consultation name/ID
    
    Returns:
        Consultation document with messages
    """
    if not frappe.db.exists("Medical Consultation", consultation_id):
        frappe.throw(_("Consultation not found"))
    
    consultation = frappe.get_doc("Medical Consultation", consultation_id)
    
    # Get unread messages count
    unread_count = 0
    for msg in consultation.messages:
        if not msg.is_read and msg.sender_type == "Provider":
            unread_count += 1
    
    return {
        "name": consultation.name,
        "patient": consultation.patient,
        "patient_name": consultation.patient_name,
        "healthcare_provider": consultation.healthcare_provider,
        "provider_name": consultation.provider_name,
        "consultation_type": consultation.consultation_type,
        "consultation_date": consultation.consultation_date,"status": consultation.status,
        "priority": consultation.priority,
        "consultation_fee": consultation.consultation_fee,
        "payment_status": consultation.payment_status,
        "payment_method": consultation.payment_method,
        "payment_date": consultation.payment_date,
        "notes": consultation.notes,
        "unread_messages": unread_count,
        "messages": [
            {
                "sender_type": msg.sender_type,
                "message": msg.message,
                "timestamp": msg.timestamp,
                "attachment": msg.attachment,
                "is_read": msg.is_read
            }
            for msg in consultation.messages
        ]
    }


@frappe.whitelist()
def send_message(consultation_id, sender_type, message, attachment=None):
    """
    Send a message in consultation chat
    
    Args:
        consultation_id: Consultation name/ID
        sender_type: "Patient" or "Provider"
        message: Message text
        attachment: File attachment (optional)
    
    Returns:
        Success message
    """
    if not frappe.db.exists("Medical Consultation", consultation_id):
        frappe.throw(_("Consultation not found"))
    
    consultation = frappe.get_doc("Medical Consultation", consultation_id)
    
    # Add message
    consultation.append("messages", {
        "sender_type": sender_type,
        "message": message,
        "timestamp": frappe.utils.now_datetime(),
        "attachment": attachment,
        "is_read": 0
    })
    
    consultation.save(ignore_permissions=True)
    frappe.db.commit()
    
    # Send notification to recipient
    # This will be implemented with notification system
    
    return {
        "message": "Message sent successfully",
        "consultation_id": consultation_id
    }


@frappe.whitelist()
def mark_messages_read(consultation_id, sender_type):
    """
    Mark messages as read
    
    Args:
        consultation_id: Consultation name/ID
        sender_type: Mark messages from this sender type as read
    
    Returns:
        Success message
    """
    if not frappe.db.exists("Medical Consultation", consultation_id):
        frappe.throw(_("Consultation not found"))
    
    consultation = frappe.get_doc("Medical Consultation", consultation_id)
    
    updated = 0
    for msg in consultation.messages:
        if msg.sender_type == sender_type and not msg.is_read:
            msg.is_read = 1
            updated += 1
    
    if updated > 0:
        consultation.save(ignore_permissions=True)
        frappe.db.commit()
    
    return {
        "message": f"Marked {updated} messages as read",
        "updated_count": updated
    }


@frappe.whitelist()
def update_consultation_status(consultation_id, new_status):
    """
    Update consultation status
    
    Args:
        consultation_id: Consultation name/ID
        new_status: New status
    
    Returns:
        Success message
    """
    if not frappe.db.exists("Medical Consultation", consultation_id):
        frappe.throw(_("Consultation not found"))
    
    valid_statuses = ["Pending", "Scheduled", "In Progress", "Completed", "Cancelled"]
    if new_status not in valid_statuses:
        frappe.throw(_("Invalid status"))
    
    consultation = frappe.get_doc("Medical Consultation", consultation_id)
    old_status = consultation.status
    consultation.status = new_status
    
    # Auto-update payment status if completed
    if new_status == "Completed" and consultation.payment_status == "Unpaid":
        consultation.payment_status = "Paid"
        consultation.payment_date = frappe.utils.today()
    
    consultation.save(ignore_permissions=True)
    frappe.db.commit()
    
    return {
        "message": f"Status updated from {old_status} to {new_status}",
        "consultation_id": consultation_id,
        "new_status": new_status
    }
@frappe.whitelist()
def cancel_consultation(consultation_id, reason=None):
    """
    Cancel a consultation
    
    Args:
        consultation_id: Consultation name/ID
        reason: Cancellation reason (optional)
    
    Returns:
        Success message
    """
    if not frappe.db.exists("Medical Consultation", consultation_id):
        frappe.throw(_("Consultation not found"))
    
    consultation = frappe.get_doc("Medical Consultation", consultation_id)
    
    # Only allow cancellation of pending or scheduled consultations
    if consultation.status not in ["Pending", "Scheduled"]:
        frappe.throw(_("Can only cancel Pending or Scheduled consultations"))
    
    consultation.status = "Cancelled"
    
    if reason:
        if consultation.notes:
            consultation.notes += f"\n\nCancellation Reason: {reason}"
        else:
            consultation.notes = f"Cancellation Reason: {reason}"
    
    # Refund if payment was made
    if consultation.payment_status == "Paid":
        consultation.payment_status = "Refunded"
    
    consultation.save(ignore_permissions=True)
    frappe.db.commit()
    
    return {
        "message": "Consultation cancelled successfully",
        "consultation_id": consultation_id
    }


@frappe.whitelist()
def update_payment_status(consultation_id, payment_status, payment_method=None):
    """
    Update payment status
    
    Args:
        consultation_id: Consultation name/ID
        payment_status: New payment status
        payment_method: Payment method (optional)
    
    Returns:
        Success message
    """
    if not frappe.db.exists("Medical Consultation", consultation_id):
        frappe.throw(_("Consultation not found"))
    
    valid_statuses = ["Unpaid", "Paid", "Refunded"]
    if payment_status not in valid_statuses:
        frappe.throw(_("Invalid payment status"))
    
    consultation = frappe.get_doc("Medical Consultation", consultation_id)
    consultation.payment_status = payment_status
    
    if payment_status == "Paid":
        consultation.payment_date = frappe.utils.today()
        if payment_method:
            consultation.payment_method = payment_method
    
    consultation.save(ignore_permissions=True)
    frappe.db.commit()
    
    return {
        "message": f"Payment status updated to {payment_status}",
        "consultation_id": consultation_id,
        "payment_status": payment_status
    }


@frappe.whitelist()
def get_upcoming_consultations(patient_id, days=7):
    """
    Get upcoming consultations for a patient
    
    Args:
        patient_id: Patient ID
        days: Number of days to look ahead (default: 7)
    
    Returns:
        List of upcoming consultations
    """
    if not frappe.db.exists("patient", patient_id):
        frappe.throw(_("Patient not found"))
    
    from_date = frappe.utils.today()
    to_date = frappe.utils.add_days(from_date, days)
    
    consultations = frappe.get_all(
        "Medical Consultation",
        filters={
            "patient": patient_id,
            "consultation_date": ["between", [from_date, to_date]],
            "status": ["in", ["Pending", "Scheduled"]]
        },
        fields=[
            "name",
            "provider_name",
            "consultation_type",
            "consultation_date",
            "status",
            "priority"
        ],
        order_by="consultation_date asc"
    )
    
    return consultations


@frappe.whitelist()
def get_consultation_stats(patient_id):
    """
    Get consultation statistics for a patient
    
    Args:
        patient_id: Patient ID
    
    Returns:
        Statistics dictionary
    """
    if not frappe.db.exists("patient", patient_id):
        frappe.throw(_("Patient not found"))
    
    # Count by status
    total = frappe.db.count("Medical Consultation", {
    "patient": patient_id
    })
    completed = frappe.db.count("Medical Consultation", {
        "patient": patient_id,
        "status": "Completed"
    })
    pending = frappe.db.count("Medical Consultation", {
        "patient": patient_id,
        "status": ["in", ["Pending", "Scheduled"]]
    })
    cancelled = frappe.db.count("Medical Consultation", {
        "patient": patient_id,
        "status": "Cancelled"
    })
    
    # Count by type
    consultations_by_type = frappe.db.sql("""
        SELECT 
            consultation_type,
            COUNT(*) as count
        FROM 
            tabMedical Consultation
        WHERE 
            patient = %(patient)s
        GROUP BY 
            consultation_type
    """, {"patient": patient_id}, as_dict=True)
    
    return {
        "total_consultations": total,
        "completed": completed,
        "pending": pending,
        "cancelled": cancelled,
        "by_type": {ct.consultation_type: ct.count for ct in consultations_by_type}
    }