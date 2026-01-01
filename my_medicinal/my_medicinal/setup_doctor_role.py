# -*- coding: utf-8 -*-
"""
Script to setup Healthcare Provider role and permissions
Run: bench --site your-site.local execute my_medicinal.setup_doctor_role
"""

import frappe
from frappe import _

def setup_doctor_role():
    """Create Healthcare Provider role with proper permissions"""
    
    print("🏥 Setting up Healthcare Provider Role...")
    
    # 1. Create Role if not exists
    if not frappe.db.exists("Role", "Healthcare Provider"):
        role = frappe.get_doc({
            "doctype": "Role",
            "role_name": "Healthcare Provider",
            "desk_access": 1,
            "disabled": 0
        })
        role.insert(ignore_permissions=True)
        print("✅ Role 'Healthcare Provider' created")
    else:
        print("ℹ️  Role 'Healthcare Provider' already exists")
    
    # 2. Setup permissions for Healthcare Provider DocType
    setup_doctype_permissions()
    
    # 3. Create default doctor workspace
    create_doctor_workspace()
    
    # 4. Setup doctor dashboard
    setup_doctor_dashboard()
    
    frappe.db.commit()
    print("🎉 Healthcare Provider setup complete!")
    

def setup_doctype_permissions():
    """Setup permissions for Healthcare Provider role"""
    
    print("\n📋 Setting up DocType permissions...")
    
    # Define permissions for each DocType
    permissions_map = {
        # Full access
        "Medical Consultation": {
            "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1,
            "condition": 'doc.provider == frappe.session.user'
        },
        "Consultation Message": {
            "read": 1, "write": 1, "create": 1,
            "condition": 'doc.sender == frappe.session.user'
        },
        "Medical Prescription": {
            "read": 1, "write": 1, "create": 1, "submit": 1,
            "condition": 'doc.provider == frappe.session.user'
        },
        "Prescription Item": {
            "read": 1, "write": 1, "create": 1
        },
        
        # Read only
        "patient": {
            "read": 1, "write": 0, "create": 0
        },
        "Medication Schedule": {
            "read": 1, "write": 0, "create": 0
        },
        "Medication Log": {
            "read": 1, "write": 0, "create": 0
        },
        "Patient Order": {
            "read": 1, "write": 0, "create": 0
        },
        "Adherence Report": {
            "read": 1, "write": 0, "create": 0
        },
        
        # Full access to own profile
        "Healthcare Provider": {
            "read": 1, "write": 1, "create": 0,
            "condition": 'doc.user == frappe.session.user'
        },
        "Provider Schedule": {
            "read": 1, "write": 1, "create": 1,
            "condition": 'doc.provider == frappe.session.user'
        }
    }
    
    for doctype, perms in permissions_map.items():
        if not frappe.db.exists("DocType", doctype):
            print(f"⚠️  DocType '{doctype}' not found, skipping")
            continue
            
        # Clear existing permissions
        frappe.db.delete("Custom DocPerm", {
            "parent": doctype,
            "role": "Healthcare Provider"
        })
        
        # Add new permissions
        perm = frappe.get_doc({
            "doctype": "Custom DocPerm",
            "parent": doctype,
            "parenttype": "DocType",
            "parentfield": "permissions",
            "role": "Healthcare Provider",
            "permlevel": 0,
            "read": perms.get("read", 0),
            "write": perms.get("write", 0),
            "create": perms.get("create", 0),
            "delete": perms.get("delete", 0),
            "submit": perms.get("submit", 0),
            "cancel": perms.get("cancel", 0),
            "amend": perms.get("amend", 0),
            "if_owner": perms.get("if_owner", 0)
        })
        
        # Add condition if specified
        if "condition" in perms:
            perm.update({"condition": perms["condition"]})
        
        perm.insert(ignore_permissions=True)
        print(f"✅ Permissions set for {doctype}")
    
    frappe.db.commit()


def create_doctor_workspace():
    """Create custom workspace for doctors"""
    
    print("\n🏥 Creating Doctor's Workspace...")
    
    workspace_name = "Healthcare Provider Portal"
    
    # Delete existing workspace if any
    if frappe.db.exists("Workspace", workspace_name):
        frappe.delete_doc("Workspace", workspace_name, force=1)
    
    workspace = frappe.get_doc({
        "doctype": "Workspace",
        "title": workspace_name,
        "module": "My Medicinal",
        "icon": "medical",
        "restrict_to_domain": "",
        "public": 0,
        "is_hidden": 0,
        "for_user": "",
        "content": get_workspace_content()
    })
    
    workspace.insert(ignore_permissions=True)
    
    # Assign to Healthcare Provider role
    workspace.append("roles", {
        "role": "Healthcare Provider"
    })
    workspace.save(ignore_permissions=True)
    
    print(f"✅ Workspace '{workspace_name}' created")
    frappe.db.commit()


def get_workspace_content():
    """Return workspace JSON content"""
    
    import json
    
    content = [
        {
            "type": "Header",
            "data": {
                "text": "لوحة التحكم - الطبيب",
                "col": 12
            }
        },
        {
            "type": "Shortcut",
            "data": {
                "label": "الاستشارات النشطة",
                "type": "DocType",
                "link_to": "Medical Consultation",
                "doc_view": "List",
                "icon": "comments",
                "color": "blue",
                "stats_filter": '{"status": "Active", "provider": ["=", "%(user)s"]}',
                "col": 3
            }
        },
        {
            "type": "Shortcut",
            "data": {
                "label": "الوصفات الطبية",
                "type": "DocType",
                "link_to": "Medical Prescription",
                "doc_view": "List",
                "icon": "file-medical",
                "color": "green",
                "col": 3
            }
        },
        {
            "type": "Shortcut",
            "data": {
                "label": "المرضى",
                "type": "DocType",
                "link_to": "patient",
                "doc_view": "List",
                "icon": "users",
                "color": "orange",
                "col": 3
            }
        },
        {
            "type": "Shortcut",
            "data": {
                "label": "جدول المواعيد",
                "type": "DocType",
                "link_to": "Provider Schedule",
                "doc_view": "List",
                "icon": "calendar",
                "color": "purple",
                "col": 3
            }
        },
        {
            "type": "Header",
            "data": {
                "text": "الاستشارات",
                "col": 12
            }
        },
        {
            "type": "Card",
            "data": {
                "card_name": "استشاراتي",
                "col": 6,
                "links": [
                    {
                        "label": "جميع الاستشارات",
                        "type": "DocType",
                        "name": "Medical Consultation",
                        "description": "عرض جميع الاستشارات"
                    },
                    {
                        "label": "استشارات قيد الانتظار",
                        "type": "DocType",
                        "name": "Medical Consultation",
                        "onboard": 0,
                        "link_type": "List",
                        "link_to": "Medical Consultation",
                        "filters": '{"status": "Pending"}'
                    },
                    {
                        "label": "استشارات اليوم",
                        "type": "DocType",
                        "name": "Medical Consultation",
                        "link_type": "List",
                        "link_to": "Medical Consultation",
                        "filters": '{"consultation_date": [">=", "Today"]}'
                    }
                ]
            }
        },
        {
            "type": "Card",
            "data": {
                "card_name": "الوصفات والمرضى",
                "col": 6,
                "links": [
                    {
                        "label": "كتابة وصفة جديدة",
                        "type": "DocType",
                        "name": "Medical Prescription",
                        "description": "إنشاء وصفة طبية جديدة"
                    },
                    {
                        "label": "عرض المرضى",
                        "type": "DocType",
                        "name": "patient"
                    },
                    {
                        "label": "تقارير الالتزام",
                        "type": "DocType",
                        "name": "Adherence Report"
                    }
                ]
            }
        },
        {
            "type": "Header",
            "data": {
                "text": "الإعدادات",
                "col": 12
            }
        },
        {
            "type": "Card",
            "data": {
                "card_name": "ملفي الشخصي",
                "col": 4,
                "links": [
                    {
                        "label": "معلوماتي الشخصية",
                        "type": "DocType",
                        "name": "Healthcare Provider"
                    },
                    {
                        "label": "جدول مواعيدي",
                        "type": "DocType",
                        "name": "Provider Schedule"
                    }
                ]
            }
        }
    ]
    
    return json.dumps(content)


def setup_doctor_dashboard():
    """Create dashboard for doctors"""
    
    print("\n📊 Setting up Doctor Dashboard...")
    
    dashboard_name = "Healthcare Provider Dashboard"
    
    # Delete existing dashboard
    if frappe.db.exists("Dashboard", dashboard_name):
        frappe.delete_doc("Dashboard", dashboard_name, force=1)
    
    dashboard = frappe.get_doc({
        "doctype": "Dashboard",
        "dashboard_name": dashboard_name,
        "module": "My Medicinal",
        "is_default": 0,
        "is_standard": 0
    })
    
    # Add charts
    charts = [
        {
            "chart_name": "الاستشارات الشهرية",
            "chart": get_or_create_chart("consultations_monthly"),
            "width": "Half"
        },
        {
            "chart_name": "حالة الاستشارات",
            "chart": get_or_create_chart("consultations_status"),
            "width": "Half"
        },
        {
            "chart_name": "الوصفات الأسبوعية",
            "chart": get_or_create_chart("prescriptions_weekly"),
            "width": "Half"
        }
    ]
    
    for chart_data in charts:
        dashboard.append("charts", chart_data)
    
    dashboard.insert(ignore_permissions=True)
    print(f"✅ Dashboard '{dashboard_name}' created")
    
    frappe.db.commit()


def get_or_create_chart(chart_type):
    """Create or get existing chart"""
    
    charts_config = {
        "consultations_monthly": {
            "name": "استشارات شهرية - الطبيب",
            "chart_name": "استشارات شهرية",
            "chart_type": "Line",
            "document_type": "Medical Consultation",
            "based_on": "consultation_date",
            "time_interval": "Monthly",
            "timespan": "Last Year",
            "filters_json": '[["Medical Consultation", "provider", "=", "%(user)s"]]'
        },
        "consultations_status": {
            "name": "حالة الاستشارات - الطبيب",
            "chart_name": "حالة الاستشارات",
            "chart_type": "Donut",
            "document_type": "Medical Consultation",
            "based_on": "status",
            "filters_json": '[["Medical Consultation", "provider", "=", "%(user)s"]]'
        },
        "prescriptions_weekly": {
            "name": "وصفات أسبوعية - الطبيب",
            "chart_name": "الوصفات الأسبوعية",
            "chart_type": "Bar",
            "document_type": "Medical Prescription",
            "based_on": "prescription_date",
            "time_interval": "Weekly",
            "timespan": "Last Month",
            "filters_json": '[["Medical Prescription", "provider", "=", "%(user)s"]]'
        }
    }
    
    config = charts_config.get(chart_type)
    if not config:
        return None
    
    chart_name = config["name"]
    
    if frappe.db.exists("Dashboard Chart", chart_name):
        return chart_name
    
    chart = frappe.get_doc({
        "doctype": "Dashboard Chart",
        "chart_name": config["chart_name"],
        "name": chart_name,
        "chart_type": config["chart_type"],
        "document_type": config["document_type"],
        "based_on": config["based_on"],
        "filters_json": config.get("filters_json", "[]"),
        "time_interval": config.get("time_interval"),
        "timespan": config.get("timespan"),
        "is_public": 0
    })
    
    chart.insert(ignore_permissions=True)
    return chart_name


# Main execution
if __name__ == "__main__":
    setup_doctor_role()
