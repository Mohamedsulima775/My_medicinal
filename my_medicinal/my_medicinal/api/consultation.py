# -*- coding: utf-8 -*-
# Copyright (c) 2024, My Medicinal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now_datetime
import json

# ============================================
# CONSULTATION APIs
# ============================================

@frappe.whitelist()
def create_consultation(patient_id, subject, description, provider_type="Doctor"):
    """Create new consultation"""
    try:
        patient = frappe.get_doc("patient", patient_id)
        
        consultation = frappe.get_doc({
            "doctype": "medical_consultation",
            "patient": patient_id,
            "patient_name": patient.patient_name,
            "subject": subject,
            "description": description,
            "provider_type": provider_type,
            "status": "Pending",
            "priority": "Normal"
        })
        
        consultation.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": True,
            "consultation_id": consultation.name,
            "subject": consultation.subject,
            "status": consultation.status
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Consultation Error")
        frappe.throw(_("Failed to create consultation: {0}").format(str(e)))


@frappe.whitelist()
def send_message(consultation_id, message, sender_type="Patient"):
    """Send message in consultation"""
    try:
        consultation = frappe.get_doc("medical_consultation", consultation_id)
        
        consultation.append("messages", {
            "sender_id": frappe.session.user,
            "sender_type": sender_type,
            "message": message,
            "timestamp": now_datetime(),
            "is_read": 0
        })
        
        if consultation.status == "Pending":
            consultation.status = "In Progress"
        
        consultation.save(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": True,
            "message": "Message sent"
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Send Message Error")
        frappe.throw(_("Failed to send message: {0}").format(str(e)))


@frappe.whitelist()
def get_my_consultations(patient_id, status=None, limit=20):
    """Get patient consultations"""
    try:
        filters = {"patient": patient_id}
        if status:
            filters["status"] = status
        
        consultations = frappe.get_all(
            "medical_consultation",
            filters=filters,
            fields=[
                "name", "subject", "status", "provider_type",
                "creation", "modified"
            ],
            limit=limit,
            order_by="creation desc"
        )
        
        return consultations
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Consultations Error")
        frappe.throw(_("Failed to get consultations: {0}").format(str(e)))


@frappe.whitelist()
def get_consultation_details(consultation_id):
    """Get consultation with messages"""
    try:
        consultation = frappe.get_doc("medical_consultation", consultation_id)
        
        messages = []
        for msg in consultation.messages:
            messages.append({
                "sender_type": msg.sender_type,
                "message": msg.message,
                "timestamp": msg.timestamp,
                "is_read": msg.is_read
            })
        
        return {
            "consultation_id": consultation.name,
            "subject": consultation.subject,
            "description": consultation.description,
            "status": consultation.status,
            "provider_type": consultation.provider_type,
            "messages": messages
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Consultation Details Error")
        frappe.throw(_("Failed to get details: {0}").format(str(e)))