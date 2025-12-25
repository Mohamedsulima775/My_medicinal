# -*- coding: utf-8 -*-
# Copyright (c) 2024, My Medicinal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today
import json

# ============================================
# PRESCRIPTION APIs
# ============================================

@frappe.whitelist()
def get_my_prescriptions(patient_id, status="Active", limit=20):
    """Get patient prescriptions"""
    try:
        filters = {"patient": patient_id}
        if status:
            filters["status"] = status
        
        prescriptions = frappe.get_all(
            "medical_prescription",
            filters=filters,
            fields=[
                "name", "prescription_date", "doctor_name",
                "diagnosis", "status", "follow_up_date"
            ],
            limit=limit,
            order_by="prescription_date desc"
        )
        
        return prescriptions
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Prescriptions Error")
        frappe.throw(_("Failed to get prescriptions: {0}").format(str(e)))


@frappe.whitelist()
def get_prescription_details(prescription_id):
    """Get prescription with medications"""
    try:
        prescription = frappe.get_doc("medical_prescription", prescription_id)
        
        medications = []
        for med in prescription.medications:
            medications.append({
                "medication_name": med.medication_name,
                "dosage": med.dosage,
                "frequency": med.frequency,
                "duration": med.duration,
                "quantity": med.quantity,
                "instructions": med.instructions
            })
        
        return {
            "prescription_id": prescription.name,
            "prescription_date": prescription.prescription_date,
            "doctor_name": prescription.doctor_name,
            "diagnosis": prescription.diagnosis,
            "instructions": prescription.instructions,
            "medications": medications,
            "status": prescription.status
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Prescription Details Error")
        frappe.throw(_("Failed to get prescription: {0}").format(str(e)))