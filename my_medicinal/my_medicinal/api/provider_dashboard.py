# my_medicinal/my_medicinal/api/provider.py

import frappe
from frappe import _
from datetime import datetime, timedelta

@frappe.whitelist()
def get_dashboard_stats():
    """Get dashboard statistics for healthcare provider"""
    
    provider = frappe.session.user
    
    # Get all stats
    stats = {
        "today": get_today_stats(provider),
        "performance": get_performance_stats(provider),
        "consultations": get_consultation_stats(provider),
        "patients": get_patient_stats(provider)
    }
    
    return stats

@frappe.whitelist()
def get_today_stats(provider=None):
    """Get today's statistics"""
    
    if not provider:
        provider = frappe.session.user
    
    today = datetime.now().date()
    
    # Total patients
    total_patients = frappe.db.count("Patient", {
        "primary_doctor": provider
    })
    
    # Consultations today
    consultations_today = frappe.db.count("Medical Consultation", {
        "provider": provider,
        "creation": [">=", today]
    })
    
    # Prescriptions today
    prescriptions_today = frappe.db.count("Medical Prescription", {
        "provider": provider,
        "creation": [">=", today]
    })
    
    # Appointments today
    appointments_today = frappe.db.count("Provider Schedule", {
        "provider": provider,
        "schedule_date": today
    })
    
    return {
        "total_patients": total_patients,
        "consultations_today": consultations_today,
        "prescriptions_today": prescriptions_today,
        "appointments_today": appointments_today
    }

@frappe.whitelist()
def get_performance_stats(provider=None):
    """Get performance statistics"""
    
    if not provider:
        provider = frappe.session.user
    
    # Average adherence
    avg_adherence = get_average_adherence(provider)
    
    # Improvement rate
    improvement = get_improvement_rate(provider)
    
    # Doctor rating
    rating = get_doctor_rating(provider)
    
    # Activity status
    activity = get_activity_status(provider)
    
    return {
        "avg_adherence": avg_adherence,
        "improvement": improvement,
        "rating": rating,
        "activity": activity
    }

@frappe.whitelist()
def get_average_adherence(provider=None):
    """Calculate average adherence of all patients"""
    
    if not provider:
        provider = frappe.session.user
    
    # Get all patients
    patients = frappe.get_all("Patient", 
        filters={"primary_doctor": provider},
        pluck="name"
    )
    
    if not patients:
        return 0
    
    # Get latest adherence for each patient
    total_adherence = 0
    count = 0
    
    for patient in patients:
        adherence = frappe.db.get_value(
            "Adherence Report",
            {"patient": patient},
            "adherence_percentage",
            order_by="creation desc"
        )
        
        if adherence:
            total_adherence += adherence
            count += 1
    
    if count == 0:
        return 0
    
    avg = round(total_adherence / count, 1)
    
    return {
        "value": avg,
        "label": f"{avg}%",
        "color": "green" if avg >= 80 else "yellow" if avg >= 60 else "red"
    }

@frappe.whitelist()
def get_improvement_rate(provider=None):
    """Calculate month-over-month improvement"""
    
    if not provider:
        provider = frappe.session.user
    
    # This month
    this_month_start = datetime.now().replace(day=1).date()
    this_month_avg = get_period_adherence(provider, this_month_start, datetime.now().date())
    
    # Last month
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    last_month_avg = get_period_adherence(provider, last_month_start, last_month_end)
    
    if last_month_avg == 0:
        return {"value": 0, "label": "0%", "trend": "neutral"}
    
    improvement = ((this_month_avg - last_month_avg) / last_month_avg) * 100
    improvement = round(improvement, 1)
    
    return {
        "value": improvement,
        "label": f"+{improvement}%" if improvement > 0 else f"{improvement}%",
        "trend": "up" if improvement > 0 else "down" if improvement < 0 else "neutral"
    }

def get_period_adherence(provider, start_date, end_date):
    """Get average adherence for a period"""
    
    patients = frappe.get_all("Patient",
        filters={"primary_doctor": provider},
        pluck="name"
    )
    
    if not patients:
        return 0
    
    # Get adherence reports in period
    reports = frappe.get_all("Adherence Report",
        filters={
            "patient": ["in", patients],
            "start_date": [">=", start_date],
            "end_date": ["<=", end_date]
        },
        fields=["adherence_percentage"]
    )
    
    if not reports:
        return 0
    
    total = sum(r.adherence_percentage for r in reports)
    return total / len(reports)

@frappe.whitelist()
def get_doctor_rating(provider=None):
    """Get doctor's average rating"""
    
    if not provider:
        provider = frappe.session.user
    
    # Get consultations with ratings
    ratings = frappe.db.sql("""
        SELECT AVG(rating) as avg_rating, COUNT(*) as count
        FROM `tabMedical Consultation`
        WHERE provider = %s AND rating > 0
    """, (provider,), as_dict=True)
    
    if not ratings or not ratings[0].count:
        return {"value": 0, "label": "?? ????", "count": 0}
    
    avg_rating = round(ratings[0].avg_rating, 1)
    count = ratings[0].count
    
    return {
        "value": avg_rating,
        "label": f"{avg_rating}/5",
        "count": count,
        "stars": "?" * int(avg_rating)
    }

@frappe.whitelist()
def get_activity_status(provider=None):
    """Get provider's activity status"""
    
    if not provider:
        provider = frappe.session.user
    
    # Check if active today
    today = datetime.now().date()
    
    # Check recent activity (consultations, prescriptions)
    recent_activity = frappe.db.sql("""
        SELECT COUNT(*) as count
        FROM (
            SELECT creation FROM `tabMedical Consultation`
            WHERE provider = %s AND DATE(creation) = %s
            UNION ALL
            SELECT creation FROM `tabMedical Prescription`
            WHERE provider = %s AND DATE(creation) = %s
        ) as activity
    """, (provider, today, provider, today), as_dict=True)
    
    is_active = recent_activity[0].count > 0 if recent_activity else False
    
    return {
        "value": "???" if is_active else "??? ???",
        "color": "green" if is_active else "gray",
        "icon": "?" if is_active else "??"
    }

@frappe.whitelist()
def get_adherence_distribution(provider=None):
    """Get patient distribution by adherence level"""
    
    if not provider:
        provider = frappe.session.user
    
    # Get all patients with latest adherence
    data = frappe.db.sql("""
        SELECT 
            CASE
                WHEN ar.adherence_percentage >= 80 THEN 'High'
                WHEN ar.adherence_percentage >= 50 THEN 'Medium'
                ELSE 'Low'
            END as level,
            COUNT(*) as count
        FROM `tabPatient` p
        LEFT JOIN (
            SELECT patient, adherence_percentage
            FROM `tabAdherence Report` ar1
            WHERE creation = (
                SELECT MAX(creation)
                FROM `tabAdherence Report` ar2
                WHERE ar2.patient = ar1.patient
            )
        ) ar ON ar.patient = p.name
        WHERE p.primary_doctor = %s
        GROUP BY level
    """, (provider,), as_dict=True)
    
    # Format for chart
    high_count = next((d.count for d in data if d.level == "High"), 0)
    medium_count = next((d.count for d in data if d.level == "Medium"), 0)
    low_count = next((d.count for d in data if d.level == "Low"), 0)
    
    total = high_count + medium_count + low_count
    
    return {
        "labels": ["?????? ???? (>80%)", "?????? ????? (50-80%)", "?????? ????? (<50%)"],
        "datasets": [{
            "name": "??? ??????",
            "values": [high_count, medium_count, low_count]
        }],
        "summary": {
            "high": {"count": high_count, "percentage": round(high_count/total*100, 1) if total > 0 else 0},
            "medium": {"count": medium_count, "percentage": round(medium_count/total*100, 1) if total > 0 else 0},
            "low": {"count": low_count, "percentage": round(low_count/total*100, 1) if total > 0 else 0},
            "total": total
        }
    }

@frappe.whitelist()
def get_my_patients_detailed(filter_by=None, sort_by="adherence"):
    """Get detailed patient list with adherence"""
    
    provider = frappe.session.user
    
    # Build filters
    filters = {"primary_doctor": provider}
    
    # Get patients
    patients = frappe.db.sql("""
        SELECT 
            p.name as patient_id,
            p.patient_name,
            p.mobile,
            p.email,
            p.date_of_birth,
            p.gender,
            GROUP_CONCAT(pcd.chronic_disease SEPARATOR ', ') as chronic_diseases,
            ar.adherence_percentage,
            ar.report_period,
            COUNT(DISTINCT ms.name) as medication_count,
            MAX(mc.creation) as last_consultation
        FROM `tabPatient` p
        LEFT JOIN `tabPatient Chronic Disease` pcd ON pcd.parent = p.name
        LEFT JOIN (
            SELECT patient, adherence_percentage, report_period
            FROM `tabAdherence Report` ar1
            WHERE creation = (
                SELECT MAX(creation)
                FROM `tabAdherence Report` ar2
                WHERE ar2.patient = ar1.patient
            )
        ) ar ON ar.patient = p.name
        LEFT JOIN `tabMedication Schedule` ms ON ms.patient = p.name AND ms.is_active = 1
        LEFT JOIN `tabMedical Consultation` mc ON mc.patient = p.name
        WHERE p.primary_doctor = %s
        GROUP BY p.name
    """, (provider,), as_dict=True)
    
    # Apply filters
    if filter_by == "high_adherence":
        patients = [p for p in patients if p.adherence_percentage and p.adherence_percentage >= 80]
    elif filter_by == "low_adherence":
        patients = [p for p in patients if p.adherence_percentage and p.adherence_percentage < 70]
    elif filter_by == "new":
        thirty_days_ago = (datetime.now() - timedelta(days=30)).date()
        patients = [p for p in patients if p.creation and p.creation.date() >= thirty_days_ago]
    
    # Add color coding
    for patient in patients:
        adherence = patient.adherence_percentage or 0
        
        if adherence >= 80:
            patient.adherence_color = "green"
            patient.adherence_label = "?????"
        elif adherence >= 60:
            patient.adherence_color = "yellow"
            patient.adherence_label = "???"
        else:
            patient.adherence_color = "red"
            patient.adherence_label = "????? ??????"
            patient.alert = True
        
        # Format last consultation
        if patient.last_consultation:
            days_ago = (datetime.now() - patient.last_consultation).days
            if days_ago == 0:
                patient.last_consultation_text = "?????"
            elif days_ago == 1:
                patient.last_consultation_text = "???"
            elif days_ago < 7:
                patient.last_consultation_text = f"??? {days_ago} ????"
            else:
                patient.last_consultation_text = f"??? {days_ago//7} ??????"
        else:
            patient.last_consultation_text = "?? ????"
    
    # Sort
    if sort_by == "adherence":
        patients.sort(key=lambda x: x.adherence_percentage or 0, reverse=True)
    elif sort_by == "name":
        patients.sort(key=lambda x: x.patient_name)
    elif sort_by == "last_consultation":
        patients.sort(key=lambda x: x.last_consultation or datetime.min, reverse=True)
    
    return patients

@frappe.whitelist()
def get_pending_consultations_detailed():
    """Get pending consultations with full details and priority"""
    
    provider = frappe.session.user
    
    consultations = frappe.db.sql("""
        SELECT 
            c.name,
            c.subject,
            c.description,
            c.creation,
            c.priority,
            c.status,
            p.patient_name,
            p.mobile,
            p.name as patient_id,
            TIMESTAMPDIFF(HOUR, c.creation, NOW()) as hours_ago
        FROM `tabMedical Consultation` c
        LEFT JOIN `tabPatient` p ON c.patient = p.name
        WHERE c.provider = %s
        AND c.status = 'Pending'
        ORDER BY 
            FIELD(c.priority, 'High', 'Medium', 'Low'),
            c.creation ASC
    """, (provider,), as_dict=True)
    
    # Add formatting
    for cons in consultations:
        # Priority colors and icons
        if cons.priority == "High":
            cons.color = "red"
            cons.icon = "??"
            cons.priority_label = "????"
        elif cons.priority == "Medium":
            cons.color = "yellow"
            cons.icon = "??"
            cons.priority_label = "?????"
        else:
            cons.color = "green"
            cons.icon = "??"
            cons.priority_label = "????"
        
        # Format time
        hours = cons.hours_ago
        if hours < 1:
            cons.time_text = f"{int(hours * 60)} ?????"
        elif hours < 24:
            cons.time_text = f"{int(hours)} ????"
        else:
            days = int(hours / 24)
            cons.time_text = f"{days} ???" if days == 1 else f"{days} ????"
    
    return consultations