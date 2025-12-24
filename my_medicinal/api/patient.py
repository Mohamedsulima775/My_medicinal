# chronic_disease/chronic_disease/api/patient.py

@frappe.whitelist(allow_guest=True)
def register(mobile, password, patient_name, **kwargs):
    """????? ???? ????"""
    
    # 1. ?????? ?? ??? ???? ??????
    if frappe.db.exists("Patient", {"mobile": mobile}):
        frappe.throw("??? ?????? ?????? ??????")
    
    # 2. ????? User
    user = frappe.get_doc({
        "doctype": "User",
        "email": f"{mobile}@dawaii.local",
        "mobile_no": mobile,
        "first_name": patient_name,
        "new_password": password,
        "user_type": "Website User"
    })
    user.insert(ignore_permissions=True)
    user.add_roles("Patient")
    
    # 3. ????? Patient
    patient = frappe.get_doc({
        "doctype": "Patient",
        "patient_name": patient_name,
        "mobile": mobile,
        "user": user.name,
        **kwargs
    })
    patient.insert(ignore_permissions=True)
    
    # 4. ????? Token
    from frappe.utils import get_secret
    token = frappe.generate_hash(length=32)
    
    return {
        "success": True,
        "token": token,
        "patient_id": patient.name,
        "patient_name": patient.patient_name
    }

@frappe.whitelist()
def get_profile():
    """?????? ??? ??? ??????"""
    user = frappe.session.user
    patient = frappe.get_doc("Patient", {"user": user})
    
    return {
        "patient_id": patient.name,
        "patient_name": patient.patient_name,
        "mobile": patient.mobile,
        "email": patient.email,
        "chronic_diseases": patient.chronic_diseases
    }