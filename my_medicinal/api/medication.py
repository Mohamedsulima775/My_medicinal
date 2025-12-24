# chronic_disease/chronic_disease/api/medication.py

@frappe.whitelist()
def add_medication(patient_id, medication_data):
    """????? ???? ????"""
    
    # ?????? ?? ????????
    patient = frappe.get_doc("Patient", patient_id)
    if patient.user != frappe.session.user:
        frappe.throw("??? ????")
    
    # ???? ????????? ??????
    times_per_day = len(medication_data.get("times", []))
    dosage_per_time = float(medication_data.get("dosage", "1").split()[0])
    daily_consumption = times_per_day * dosage_per_time
    
    # ???? ?????? ??? ??????
    current_stock = medication_data.get("current_stock", 0)
    days_until_depletion = int(current_stock / daily_consumption) if daily_consumption > 0 else 0
    
    # ????? ??????
    schedule = frappe.get_doc({
        "doctype": "Medication Schedule",
        "patient": patient_id,
        "medication_name": medication_data.get("medication_name"),
        "dosage": medication_data.get("dosage"),
        "frequency": medication_data.get("frequency"),
        "times": medication_data.get("times"),
        "current_stock": current_stock,
        "stock_unit": medication_data.get("stock_unit", "Tablet"),
        "daily_consumption": daily_consumption,
        "days_until_depletion": days_until_depletion,
        "image": medication_data.get("image"),
        "color_code": medication_data.get("color_code")
    })
    schedule.insert()
    
    return {"success": True, "schedule_id": schedule.name}

@frappe.whitelist()
def get_medications(patient_id):
    """?????? ??? ???? ????? ??????"""
    
    schedules = frappe.get_all(
        "Medication Schedule",
        filters={"patient": patient_id, "is_active": 1},
        fields=["*"]
    )
    
    # ????? times ??? schedule
    for schedule in schedules:
        schedule["times"] = frappe.get_all(
            "Medication Time",
            filters={"parent": schedule.name},
            fields=["time", "before_after_meal"]
        )
    
    return schedules

@frappe.whitelist()
def log_medication_taken(medication_schedule_id, scheduled_date, scheduled_time):
    """????? ????? ??????"""
    
    schedule = frappe.get_doc("Medication Schedule", medication_schedule_id)
    
    # ????? ?????
    log = frappe.get_doc({
        "doctype": "Medication Log",
        "patient": schedule.patient,
        "medication_schedule": schedule.name,
        "scheduled_date": scheduled_date,
        "scheduled_time": scheduled_time,
        "actual_datetime": frappe.utils.now_datetime(),
        "status": "Taken"
    })
    log.insert()
    
    # ????? ???????
    dosage_taken = float(schedule.dosage.split()[0])
    schedule.current_stock -= dosage_taken
    
    if schedule.daily_consumption > 0:
        schedule.days_until_depletion = int(schedule.current_stock / schedule.daily_consumption)
    
    schedule.save()
    
    return {
        "success": True,
        "current_stock": schedule.current_stock,
        "days_until_depletion": schedule.days_until_depletion
    }