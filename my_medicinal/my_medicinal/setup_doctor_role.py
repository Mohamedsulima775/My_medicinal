# -*- coding: utf-8 -*-
"""
Healthcare Provider Setup Script
=================================
Script to setup Healthcare Provider role, permissions, workspace, and dashboard.

Usage:
    bench --site my_medicinal.local execute my_medicinal.my_medicinal.setup_doctor_role.setup_healthcare_provider

Author: Mohammed Suliman
Date: 2026-01-09
"""

import frappe
from frappe import _
import json


def setup_healthcare_provider():
    """
    Main function to setup Healthcare Provider role and workspace

    This function:
    1. Creates Healthcare Provider role
    2. Sets up permissions for all relevant doctypes
    3. Creates custom workspace for doctors
    4. Sets up dashboard with charts
    """

    try:
        print("=" * 60)
        print("🏥 Starting Healthcare Provider Setup")
        print("=" * 60)

        # Step 1: Create role
        create_healthcare_provider_role()

        # Step 2: Setup permissions
        setup_doctype_permissions()

        # Step 3: Create workspace
        create_doctor_workspace()

        # Step 4: Setup dashboard
        setup_doctor_dashboard()

        frappe.db.commit()

        print("\n" + "=" * 60)
        print("✅ Healthcare Provider setup complete!")
        print("=" * 60)

        return {"success": True, "message": "Setup completed successfully"}

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Healthcare Provider Setup Error")
        print(f"\n❌ Error: {str(e)}")
        print("Check Error Log for details")
        raise


# ============================================================================
# ROLE CREATION
# ============================================================================

def create_healthcare_provider_role():
    """Create Healthcare Provider role if it doesn't exist"""

    print("\n👨‍⚕️ Setting up Healthcare Provider role...")

    role_name = "Healthcare Provider"

    if frappe.db.exists("Role", role_name):
        print(f"ℹ️  Role '{role_name}' already exists")
        return

    try:
        role = frappe.get_doc({
            "doctype": "Role",
            "role_name": role_name,
            "desk_access": 1,
            "is_custom": 1,
            "disabled": 0
        })
        role.insert(ignore_permissions=True)
        print(f"✅ Role '{role_name}' created successfully")

    except Exception as e:
        print(f"❌ Error creating role: {str(e)}")
        raise


# ============================================================================
# PERMISSIONS SETUP
# ============================================================================

def setup_doctype_permissions():
    """Setup permissions for Healthcare Provider role"""

    print("\n📋 Setting up DocType permissions...")

    # Define permissions for each DocType
    permissions_map = {
        # Full access for consultations
        "Medical Consultation": {
            "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1,
            "description": "Full access to consultations"
        },
        "Consultation Message": {
            "read": 1, "write": 1, "create": 1,
            "description": "Manage consultation messages"
        },

        # Prescription management
        "Medical Prescription": {
            "read": 1, "write": 1, "create": 1, "submit": 1,
            "description": "Create and manage prescriptions"
        },
        "Prescription Item": {
            "read": 1, "write": 1, "create": 1,
            "description": "Add prescription items"
        },

        # Read-only access to patient data
        "patient": {
            "read": 1, "write": 0, "create": 0,
            "description": "View patient information"
        },
        "Medication Schedule": {
            "read": 1, "write": 0, "create": 0,
            "description": "View medication schedules"
        },
        "Medication Log": {
            "read": 1, "write": 0, "create": 0,
            "description": "View medication logs"
        },
        "Patient Order": {
            "read": 1, "write": 0, "create": 0,
            "description": "View patient orders"
        },
        "Adherence Report": {
            "read": 1, "write": 0, "create": 0,
            "description": "View adherence reports"
        },

        # Own profile management
        "Healthcare Provider": {
            "read": 1, "write": 1, "create": 0,
            "description": "Manage own profile"
        },
        "Provider Schedule": {
            "read": 1, "write": 1, "create": 1,
            "description": "Manage own schedule"
        }
    }

    success_count = 0
    skip_count = 0

    for doctype, perms in permissions_map.items():
        # Check if doctype exists
        if not frappe.db.exists("DocType", doctype):
            print(f"⚠️  DocType '{doctype}' not found, skipping")
            skip_count += 1
            continue

        try:
            # Check if permission already exists
            existing = frappe.db.exists("Custom DocPerm", {
                "parent": doctype,
                "role": "Healthcare Provider"
            })

            if existing:
                print(f"ℹ️  Permission for '{doctype}' already exists")
                skip_count += 1
                continue

            # Create new permission
            description = perms.pop("description", "")

            perm = frappe.get_doc({
                "doctype": "Custom DocPerm",
                "parent": doctype,
                "parenttype": "DocType",
                "parentfield": "permissions",
                "role": "Healthcare Provider",
                "permlevel": 0,
                **perms
            })

            perm.insert(ignore_permissions=True)
            print(f"✅ Permission set for '{doctype}' - {description}")
            success_count += 1

        except Exception as e:
            print(f"❌ Error setting permission for '{doctype}': {str(e)}")
            continue

    frappe.db.commit()
    print(f"\n📊 Summary: {success_count} created, {skip_count} skipped")


# ============================================================================
# WORKSPACE CREATION
# ============================================================================

def create_doctor_workspace():
    """Create custom workspace for Healthcare Providers"""

    print("\n🖥️  Creating Healthcare Provider Workspace...")

    workspace_name = "Healthcare Provider Portal"

    try:
        # Delete existing workspace if any
        if frappe.db.exists("Workspace", workspace_name):
            frappe.delete_doc("Workspace", workspace_name, force=1, ignore_permissions=True)
            print("ℹ️  Deleted existing workspace")

        # Create new workspace
        workspace = frappe.get_doc({
            "doctype": "Workspace",
            "title": workspace_name,
            "module": "my_medicinal",
            "icon": "medical",
            "public": 1,
            "is_hidden": 0,
            "content": json.dumps(get_workspace_content())
        })

        workspace.insert(ignore_permissions=True)
        print(f"✅ Workspace '{workspace_name}' created")

        # Assign to Healthcare Provider role
        assign_workspace_to_role(workspace_name, "Healthcare Provider")

        frappe.db.commit()

    except Exception as e:
        print(f"❌ Error creating workspace: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Workspace Creation Error")
        raise


def assign_workspace_to_role(workspace_name, role_name):
    """Assign workspace to a specific role"""

    try:
        # Check if already assigned
        exists = frappe.db.exists("Has Role", {
            "parent": workspace_name,
            "parenttype": "Workspace",
            "role": role_name
        })

        if exists:
            print(f"ℹ️  Workspace already assigned to '{role_name}'")
            return

        # Create role assignment
        has_role = frappe.get_doc({
            "doctype": "Has Role",
            "parent": workspace_name,
            "parenttype": "Workspace",
            "parentfield": "roles",
            "role": role_name
        })
        has_role.insert(ignore_permissions=True)
        print(f"✅ Workspace assigned to '{role_name}'")

    except Exception as e:
        print(f"⚠️  Could not assign workspace: {str(e)}")


def get_workspace_content():
    """Return workspace content in JSON format"""

    return [
        # Header
        {
            "type": "Header",
            "data": {
                "text": "لوحة تحكم مقدم الرعاية الصحية",
                "col": 12
            }
        },
        {
            "type": "Card Break"
        },

        # Quick shortcuts
        {
            "type": "Shortcut",
            "data": {
                "shortcut_name": "الاستشارات النشطة",
                "label": "الاستشارات النشطة",
                "link_to": "Medical Consultation",
                "type": "DocType",
                "icon": "medical",
                "color": "Green"
            }
        },
        {
            "type": "Shortcut",
            "data": {
                "shortcut_name": "كتابة وصفة",
                "label": "كتابة وصفة جديدة",
                "link_to": "Medical Prescription",
                "type": "DocType",
                "icon": "file",
                "color": "Blue"
            }
        },
        {
            "type": "Shortcut",
            "data": {
                "shortcut_name": "المرضى",
                "label": "عرض المرضى",
                "link_to": "patient",
                "type": "DocType",
                "icon": "users",
                "color": "Orange"
            }
        },
        {
            "type": "Shortcut",
            "data": {
                "shortcut_name": "جدول المواعيد",
                "label": "جدول المواعيد",
                "link_to": "Provider Schedule",
                "type": "DocType",
                "icon": "calendar",
                "color": "Purple"
            }
        },

        {
            "type": "Card Break"
        },

        # Consultations card
        {
            "type": "Card",
            "data": {
                "card_name": "الاستشارات",
                "col": 6,
                "links": [
                    {
                        "label": "جميع الاستشارات",
                        "type": "Link",
                        "link_type": "DocType",
                        "link_to": "Medical Consultation",
                        "is_query_report": 0
                    },
                    {
                        "label": "الاستشارات قيد الانتظار",
                        "type": "Link",
                        "link_type": "DocType",
                        "link_to": "Medical Consultation",
                        "is_query_report": 0
                    },
                    {
                        "label": "استشارات اليوم",
                        "type": "Link",
                        "link_type": "DocType",
                        "link_to": "Medical Consultation",
                        "is_query_report": 0
                    }
                ]
            }
        },

        # Prescriptions & Patients card
        {
            "type": "Card",
            "data": {
                "card_name": "الوصفات والمرضى",
                "col": 6,
                "links": [
                    {
                        "label": "الوصفات الطبية",
                        "type": "Link",
                        "link_type": "DocType",
                        "link_to": "Medical Prescription",
                        "is_query_report": 0
                    },
                    {
                        "label": "المرضى",
                        "type": "Link",
                        "link_type": "DocType",
                        "link_to": "patient",
                        "is_query_report": 0
                    },
                    {
                        "label": "تقارير الالتزام",
                        "type": "Link",
                        "link_type": "DocType",
                        "link_to": "Adherence Report",
                        "is_query_report": 0
                    }
                ]
            }
        }
    ]


# ============================================================================
# DASHBOARD SETUP
# ============================================================================

def setup_doctor_dashboard():
    """Create dashboard for Healthcare Providers"""

    print("\n📊 Setting up Healthcare Provider Dashboard...")

    dashboard_name = "Healthcare Provider Dashboard"

    try:
        # Delete existing dashboard
        if frappe.db.exists("Dashboard", dashboard_name):
            frappe.delete_doc("Dashboard", dashboard_name, force=1, ignore_permissions=True)
            print("ℹ️  Deleted existing dashboard")

        # Create new dashboard
        dashboard = frappe.get_doc({
            "doctype": "Dashboard",
            "dashboard_name": dashboard_name,
            "module": "my_medicinal",
            "is_default": 0,
            "is_standard": 0
        })

        # Add charts
        charts = [
            {
                "chart_name": "الاستشارات الشهرية",
                "chart": create_chart("consultations_monthly"),
                "width": "Half"
            },
            {
                "chart_name": "حالة الاستشارات",
                "chart": create_chart("consultations_status"),
                "width": "Half"
            },
            {
                "chart_name": "الوصفات الأسبوعية",
                "chart": create_chart("prescriptions_weekly"),
                "width": "Half"
            }
        ]

        for chart_data in charts:
            if chart_data["chart"]:  # Only add if chart was created
                dashboard.append("charts", chart_data)

        dashboard.insert(ignore_permissions=True)
        print(f"✅ Dashboard '{dashboard_name}' created with {len(charts)} charts")

        frappe.db.commit()

    except Exception as e:
        print(f"❌ Error creating dashboard: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Dashboard Creation Error")


def create_chart(chart_type):
    """Create or get existing dashboard chart"""

    charts_config = {
        "consultations_monthly": {
            "name": "استشارات شهرية - الطبيب",
            "chart_name": "الاستشارات الشهرية",
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

    # Check if chart already exists
    if frappe.db.exists("Dashboard Chart", chart_name):
        print(f"ℹ️  Chart '{config['chart_name']}' already exists")
        return chart_name

    try:
        chart = frappe.get_doc({
            "doctype": "Dashboard Chart",
            "name": chart_name,
            "chart_name": config["chart_name"],
            "chart_type": config["chart_type"],
            "document_type": config["document_type"],
            "based_on": config["based_on"],
            "filters_json": config.get("filters_json", "[]"),
            "time_interval": config.get("time_interval"),
            "timespan": config.get("timespan"),
            "is_public": 0
        })

        chart.insert(ignore_permissions=True)
        print(f"✅ Chart '{config['chart_name']}' created")
        return chart_name

    except Exception as e:
        print(f"⚠️  Could not create chart '{config['chart_name']}': {str(e)}")
        return None


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    setup_healthcare_provider()
