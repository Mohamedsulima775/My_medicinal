# -*- coding: utf-8 -*-
"""
Healthcare Provider (Doctor) APIs
APIs for doctors to manage consultations, prescriptions, and patients
"""

import frappe
from frappe import _
import json
from datetime import datetime, timedelta


@frappe.whitelist()
def get_my_consultations(status=None, limit=20):
    """Get consultations for logged-in doctor"""
    try:
        # Get doctor's provider record
        provider = frappe.db.get_value(
            "Healthcare Provider",
            {"user": frappe.session.user},
            "name"
        )
        
        if not provider:
            frappe.throw(_("Healthcare Provider not found for this user"))
        
        filters = {"provider": provider}
        if status:
            filters["status"] = status
        
        consultations = frappe.get_all(
            "Medical Consultation",
            filters=filters,
            fields=[
                "name", "consultation_date", "consultation_type",
                "status", "patient", "patient_name", "chief_complaint",
                "severity", "creation", "modified"
            ],
            order_by="consultation_date desc",
            limit=int(limit)
        )
        
        # Add unread messages count
        for consultation in consultations:
            consultation["unread_messages"] = get_unread_messages_count(
                consultation["name"],
                frappe.session.user
            )
        
        return consultations
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Doctor Consultations Error")
        frappe.throw(str(e))


@frappe.whitelist()
def get_consultation_details(consultation_id):
    """Get detailed consultation information"""
    try:
        # Verify access
        consultation = frappe.get_doc("Medical Consultation", consultation_id)
        
        provider = frappe.db.get_value(
            "Healthcare Provider",
            {"user": frappe.session.user},
            "name"
        )
        
        if consultation.provider != provider:
            frappe.throw(_("Access denied"))
        
        # Get patient details
        patient = frappe.get_doc("patient", consultation.patient)
        
        # Get messages
        messages = frappe.get_all(
            "Consultation Message",
            filters={"consultation": consultation_id},
            fields=["sender", "sender_name", "message", "sent_at", "attachment"],
            order_by="sent_at asc"
        )
        
        # Get patient's medications
        medications = frappe.get_all(
            "Medication Schedule",
            filters={"patient": consultation.patient, "is_active": 1},
            fields=[
                "name", "medication_name", "dosage", "frequency",
                "current_stock", "days_until_depletion"
            ]
        )
        
        # Get adherence report
        adherence = frappe.db.get_value(
            "Adherence Report",
            {
                "patient": consultation.patient,
                "report_period": "Monthly"
            },
            ["adherence_percentage", "generated_at"],
            as_dict=True
        )
        
        return {
            "consultation": consultation.as_dict(),
            "patient": {
                "name": patient.name,
                "patient_name": patient.patient_name,
                "age": calculate_age(patient.date_of_birth),
                "gender": patient.gender,
                "blood_group": patient.blood_group,
                "allergies": patient.allergies,
                "chronic_diseases": patient.chronic_diseases,
                "medical_notes": patient.medical_notes
            },
            "messages": messages,
            "medications": medications,
            "adherence": adherence
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Consultation Details Error")
        frappe.throw(str(e))


@frappe.whitelist()
def update_consultation(consultation_id, data):
    """Update consultation details"""
    try:
        consultation = frappe.get_doc("Medical Consultation", consultation_id)
        
        # Verify access
        provider = frappe.db.get_value(
            "Healthcare Provider",
            {"user": frappe.session.user},
            "name"
        )
        
        if consultation.provider != provider:
            frappe.throw(_("Access denied"))
        
        # Parse data
        if isinstance(data, str):
            data = json.loads(data)
        
        # Update fields
        allowed_fields = [
            "diagnosis", "notes", "follow_up_date", "status"
        ]
        
        for key, value in data.items():
            if key in allowed_fields:
                setattr(consultation, key, value)
        
        consultation.save(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "status": "success",
            "message": _("Consultation updated successfully")
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Update Consultation Error")
        frappe.throw(str(e))


@frappe.whitelist()
def create_prescription(consultation_id, medications, diagnosis, notes=None):
    """Create prescription for consultation"""
    try:
        # Get consultation
        consultation = frappe.get_doc("Medical Consultation", consultation_id)
        
        # Verify access
        provider = frappe.db.get_value(
            "Healthcare Provider",
            {"user": frappe.session.user},
            "name"
        )
        
        if consultation.provider != provider:
            frappe.throw(_("Access denied"))
        
        # Parse medications if string
        if isinstance(medications, str):
            medications = json.loads(medications)
        
        # Create prescription
        prescription = frappe.get_doc({
            "doctype": "Medical Prescription",
            "patient": consultation.patient,
            "provider": provider,
            "consultation": consultation_id,
            "prescription_date": frappe.utils.today(),
            "diagnosis": diagnosis,
            "notes": notes
        })
        
        # Add medications
        for med in medications:
            prescription.append("medications", {
                "medication_name": med.get("medication_name"),
                "scientific_name": med.get("scientific_name"),
                "dosage": med.get("dosage"),
                "frequency": med.get("frequency"),
                "duration": med.get("duration"),
                "quantity": med.get("quantity"),
                "instructions": med.get("instructions"),
                "refills": med.get("refills", 0)
            })
        
        prescription.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Update consultation
        consultation.status = "Completed"
        consultation.diagnosis = diagnosis
        consultation.save(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "status": "success",
            "prescription_id": prescription.name,
            "message": _("Prescription created successfully")
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Create Prescription Error")
        frappe.throw(str(e))


@frappe.whitelist()
def get_my_prescriptions(limit=20):
    """Get prescriptions created by logged-in doctor"""
    try:
        provider = frappe.db.get_value(
            "Healthcare Provider",
            {"user": frappe.session.user},
            "name"
        )
        
        if not provider:
            frappe.throw(_("Healthcare Provider not found"))
        
        prescriptions = frappe.get_all(
            "Medical Prescription",
            filters={"provider": provider},
            fields=[
                "name", "prescription_date", "patient", "patient_name",
                "diagnosis", "consultation", "creation"
            ],
            order_by="prescription_date desc",
            limit=int(limit)
        )
        
        # Add medications count
        for prescription in prescriptions:
            prescription["medications_count"] = frappe.db.count(
                "Prescription Item",
                {"parent": prescription["name"]}
            )
        
        return prescriptions
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Doctor Prescriptions Error")
        frappe.throw(str(e))


@frappe.whitelist()
def get_my_patients(search=None, limit=50):
    """Get patients who have consulted with logged-in doctor"""
    try:
        provider = frappe.db.get_value(
            "Healthcare Provider",
            {"user": frappe.session.user},
            "name"
        )
        
        if not provider:
            frappe.throw(_("Healthcare Provider not found"))
        
        # Get unique patients from consultations
        sql = """
            SELECT DISTINCT 
                p.name, p.patient_name, p.mobile, p.email,
                p.date_of_birth, p.gender, p.blood_group,
                COUNT(mc.name) as consultations_count,
                MAX(mc.consultation_date) as last_consultation
            FROM `tabpatient` p
            INNER JOIN `tabMedical Consultation` mc ON mc.patient = p.name
            WHERE mc.provider = %(provider)s
        """
        
        if search:
            sql += " AND (p.patient_name LIKE %(search)s OR p.mobile LIKE %(search)s)"
        
        sql += """
            GROUP BY p.name
            ORDER BY MAX(mc.consultation_date) DESC
            LIMIT %(limit)s
        """
        
        patients = frappe.db.sql(sql, {
            "provider": provider,
            "search": f"%{search}%" if search else "%",
            "limit": int(limit)
        }, as_dict=True)
        
        # Add age
        for patient in patients:
            if patient.get("date_of_birth"):
                patient["age"] = calculate_age(patient["date_of_birth"])
        
        return patients
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Doctor Patients Error")
        frappe.throw(str(e))


@frappe.whitelist()
def get_patient_history(patient_id):
    """Get complete patient history for doctor"""
    try:
        # Verify access
        provider = frappe.db.get_value(
            "Healthcare Provider",
            {"user": frappe.session.user},
            "name"
        )
        
        # Check if doctor has consulted this patient
        has_access = frappe.db.exists(
            "Medical Consultation",
            {"patient": patient_id, "provider": provider}
        )
        
        if not has_access:
            frappe.throw(_("Access denied"))
        
        # Get patient details
        patient = frappe.get_doc("patient", patient_id)
        
        # Get consultations
        consultations = frappe.get_all(
            "Medical Consultation",
            filters={"patient": patient_id, "provider": provider},
            fields=["*"],
            order_by="consultation_date desc"
        )
        
        # Get prescriptions
        prescriptions = frappe.get_all(
            "Medical Prescription",
            filters={"patient": patient_id, "provider": provider},
            fields=["*"],
            order_by="prescription_date desc"
        )
        
        # Get medications
        medications = frappe.get_all(
            "Medication Schedule",
            filters={"patient": patient_id, "is_active": 1},
            fields=["*"]
        )
        
        # Get adherence reports
        adherence_reports = frappe.get_all(
            "Adherence Report",
            filters={"patient": patient_id},
            fields=["*"],
            order_by="generated_at desc",
            limit=5
        )
        
        return {
            "patient": patient.as_dict(),
            "consultations": consultations,
            "prescriptions": prescriptions,
            "medications": medications,
            "adherence_reports": adherence_reports
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Patient History Error")
        frappe.throw(str(e))


@frappe.whitelist()
def get_doctor_statistics():
    """Get statistics for logged-in doctor"""
    try:
        provider = frappe.db.get_value(
            "Healthcare Provider",
            {"user": frappe.session.user},
            "name"
        )
        
        if not provider:
            frappe.throw(_("Healthcare Provider not found"))
        
        # Today's consultations
        today_consultations = frappe.db.count(
            "Medical Consultation",
            {
                "provider": provider,
                "consultation_date": frappe.utils.today()
            }
        )
        
        # Pending consultations
        pending_consultations = frappe.db.count(
            "Medical Consultation",
            {
                "provider": provider,
                "status": "Pending"
            }
        )
        
        # Active consultations
        active_consultations = frappe.db.count(
            "Medical Consultation",
            {
                "provider": provider,
                "status": "Active"
            }
        )
        
        # Total patients
        total_patients = frappe.db.sql("""
            SELECT COUNT(DISTINCT patient)
            FROM `tabMedical Consultation`
            WHERE provider = %s
        """, provider)[0][0]
        
        # This month's prescriptions
        this_month_prescriptions = frappe.db.count(
            "Medical Prescription",
            {
                "provider": provider,
                "prescription_date": [">=", frappe.utils.get_first_day(frappe.utils.today())]
            }
        )
        
        # Unread messages
        unread_messages = get_total_unread_messages(provider)
        
        return {
            "today_consultations": today_consultations,
            "pending_consultations": pending_consultations,
            "active_consultations": active_consultations,
            "total_patients": total_patients,
            "this_month_prescriptions": this_month_prescriptions,
            "unread_messages": unread_messages
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Doctor Statistics Error")
        frappe.throw(str(e))


@frappe.whitelist()
def update_my_profile(profile_data):
    """Update doctor's own profile"""
    try:
        provider = frappe.db.get_value(
            "Healthcare Provider",
            {"user": frappe.session.user},
            "name"
        )
        
        if not provider:
            frappe.throw(_("Healthcare Provider not found"))
        
        provider_doc = frappe.get_doc("Healthcare Provider", provider)
        
        # Parse data
        if isinstance(profile_data, str):
            profile_data = json.loads(profile_data)
        
        # Allowed fields
        allowed_fields = [
            "provider_name", "specialty", "qualifications",
            "experience_years", "consultation_fee", "is_available"
        ]
        
        for key, value in profile_data.items():
            if key in allowed_fields:
                setattr(provider_doc, key, value)
        
        provider_doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "status": "success",
            "message": _("Profile updated successfully")
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Update Provider Profile Error")
        frappe.throw(str(e))


# Helper functions

def calculate_age(date_of_birth):
    """Calculate age from date of birth"""
    if not date_of_birth:
        return None
    
    from dateutil.relativedelta import relativedelta
    
    if isinstance(date_of_birth, str):
        date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
    
    today = datetime.now().date()
    age = relativedelta(today, date_of_birth)
    
    return f"{age.years} ???"


def get_unread_messages_count(consultation_id, user):
    """Get count of unread messages in consultation"""
    return frappe.db.count(
        "Consultation Message",
        {
            "consultation": consultation_id,
            "sender": ["!=", user],
            "read": 0
        }
    )


def get_total_unread_messages(provider):
    """Get total unread messages for provider"""
    sql = """
        SELECT COUNT(*)
        FROM `tabConsultation Message` cm
        INNER JOIN `tabMedical Consultation` mc ON mc.name = cm.consultation
        WHERE mc.provider = %s
        AND cm.sender != %s
        AND cm.read = 0
    """
    
    user = frappe.db.get_value("Healthcare Provider", provider, "user")
    result = frappe.db.sql(sql, (provider, user))
    
    return result[0][0] if result else 0