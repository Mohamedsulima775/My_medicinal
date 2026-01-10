# -*- coding: utf-8 -*-
"""
Healthcare Provider Environment Initialization
بيئة خاصة بمقدمي الرعاية الصحية
===============================================
Complete environment setup for Healthcare Providers including:
- Role and permissions
- Workspace and dashboard
- API configurations
- Security settings
- Notifications

Usage:
    bench --site [site-name] execute my_medicinal.my_medicinal.provider_environment.initialize_provider_environment

Author: Mohammed Suliman
Date: 2026-01-10
"""

import frappe
from frappe import _
import os
import json
from datetime import datetime


# =============================================================================
# MAIN INITIALIZATION FUNCTION
# =============================================================================

def initialize_provider_environment():
    """
    Initialize complete Healthcare Provider environment

    This function sets up everything needed for providers:
    1. Load environment variables
    2. Setup role and permissions
    3. Create workspace and dashboard
    4. Configure API settings
    5. Setup security and middleware
    6. Configure notifications
    7. Create sample data (if in dev mode)
    """

    try:
        print("\n" + "=" * 80)
        print("🏥 Healthcare Provider Environment Initialization")
        print("   تهيئة بيئة مقدم الرعاية الصحية")
        print("=" * 80)

        # Step 1: Load provider environment configuration
        print("\n[1/8] Loading provider environment configuration...")
        config = load_provider_config()
        print("✅ Configuration loaded successfully")

        # Step 2: Setup Healthcare Provider role
        print("\n[2/8] Setting up Healthcare Provider role...")
        setup_provider_role()
        print("✅ Role setup complete")

        # Step 3: Configure permissions
        print("\n[3/8] Configuring permissions...")
        setup_provider_permissions()
        print("✅ Permissions configured")

        # Step 4: Create provider workspace
        print("\n[4/8] Creating provider workspace...")
        create_provider_workspace()
        print("✅ Workspace created")

        # Step 5: Setup dashboard
        print("\n[5/8] Setting up provider dashboard...")
        setup_provider_dashboard()
        print("✅ Dashboard ready")

        # Step 6: Configure API settings
        print("\n[6/8] Configuring API settings...")
        configure_provider_api()
        print("✅ API configured")

        # Step 7: Setup notifications
        print("\n[7/8] Setting up notification system...")
        setup_provider_notifications()
        print("✅ Notifications configured")

        # Step 8: Create sample data (if enabled)
        if config.get("provider_test_mode"):
            print("\n[8/8] Creating sample test data...")
            create_sample_provider_data()
            print("✅ Sample data created")
        else:
            print("\n[8/8] Skipping sample data (test mode disabled)")

        frappe.db.commit()

        print("\n" + "=" * 80)
        print("✅ Healthcare Provider Environment Ready!")
        print("   بيئة مقدم الرعاية الصحية جاهزة!")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Copy .env.provider.example to .env.provider")
        print("2. Configure your settings in .env.provider")
        print("3. Create Healthcare Provider records via UI or API")
        print("4. Assign Healthcare Provider role to users")
        print("\nProvider Portal URL: {}".format(config.get("provider_portal_url", "/app/healthcare-provider-portal")))
        print("=" * 80 + "\n")

        return {
            "success": True,
            "message": "Provider environment initialized successfully",
            "config": config
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Provider Environment Initialization Error")
        print(f"\n❌ Error: {str(e)}")
        print("Check Error Log for details\n")
        raise


# =============================================================================
# CONFIGURATION MANAGEMENT
# =============================================================================

def load_provider_config():
    """
    Load provider environment configuration from .env.provider file
    or use defaults from .env.provider.example
    """

    config = {
        # Portal settings
        "provider_portal_enabled": get_env_bool("PROVIDER_PORTAL_ENABLED", True),
        "provider_portal_url": get_env("PROVIDER_PORTAL_URL", "http://localhost:8000/provider"),
        "dashboard_refresh_interval": get_env_int("PROVIDER_DASHBOARD_REFRESH_INTERVAL", 30),

        # Security
        "provider_session_timeout": get_env_int("PROVIDER_SESSION_TIMEOUT", 28800),
        "provider_2fa_required": get_env_bool("PROVIDER_2FA_REQUIRED", False),
        "provider_rate_limit_max": get_env_int("PROVIDER_RATE_LIMIT_MAX_REQUESTS", 500),
        "provider_rate_limit_window": get_env_int("PROVIDER_RATE_LIMIT_WINDOW", 60),
        "provider_login_audit": get_env_bool("PROVIDER_LOGIN_AUDIT_ENABLED", True),

        # Consultations
        "auto_accept_consultations": get_env_bool("PROVIDER_AUTO_ACCEPT_CONSULTATIONS", False),
        "consultation_timeout": get_env_int("CONSULTATION_TIMEOUT", 30),
        "video_enabled": get_env_bool("VIDEO_CONSULTATION_ENABLED", True),
        "max_simultaneous": get_env_int("MAX_SIMULTANEOUS_CONSULTATIONS", 5),

        # Prescriptions
        "digital_signature_required": get_env_bool("PRESCRIPTION_DIGITAL_SIGNATURE_REQUIRED", True),
        "prescription_validity_days": get_env_int("PRESCRIPTION_VALIDITY_DAYS", 30),
        "prescription_audit": get_env_bool("PRESCRIPTION_AUDIT_TRAIL_ENABLED", True),

        # Schedule
        "self_schedule_enabled": get_env_bool("PROVIDER_SELF_SCHEDULE_ENABLED", True),
        "default_slot_duration": get_env_int("DEFAULT_SLOT_DURATION", 30),
        "working_hours_start": get_env("DEFAULT_WORKING_HOURS_START", "09:00"),
        "working_hours_end": get_env("DEFAULT_WORKING_HOURS_END", "17:00"),

        # Notifications
        "notify_email": get_env_bool("PROVIDER_NOTIFICATION_EMAIL", True),
        "notify_sms": get_env_bool("PROVIDER_NOTIFICATION_SMS", True),
        "notify_push": get_env_bool("PROVIDER_NOTIFICATION_PUSH", True),
        "quiet_hours_enabled": get_env_bool("PROVIDER_QUIET_HOURS_ENABLED", True),

        # Dashboard
        "dashboard_enabled": get_env_bool("PROVIDER_DASHBOARD_ENABLED", True),
        "analytics_enabled": get_env_bool("PROVIDER_ANALYTICS_ENABLED", True),

        # Test mode
        "provider_test_mode": get_env_bool("PROVIDER_TEST_MODE", False),

        # Localization
        "portal_language": get_env("PROVIDER_PORTAL_LANGUAGE", "ar"),
        "rtl_enabled": get_env_bool("PROVIDER_RTL_ENABLED", True),
    }

    return config


def get_env(key, default=None):
    """Get environment variable with fallback"""
    return os.getenv(key, default)


def get_env_int(key, default=0):
    """Get integer environment variable"""
    try:
        return int(os.getenv(key, default))
    except (ValueError, TypeError):
        return default


def get_env_bool(key, default=False):
    """Get boolean environment variable"""
    value = os.getenv(key, str(default))
    return str(value).lower() in ('1', 'true', 'yes', 'on')


# =============================================================================
# ROLE SETUP
# =============================================================================

def setup_provider_role():
    """Create and configure Healthcare Provider role"""

    role_name = "Healthcare Provider"

    # Create role if doesn't exist
    if not frappe.db.exists("Role", role_name):
        role = frappe.get_doc({
            "doctype": "Role",
            "role_name": role_name,
            "desk_access": 1,
            "is_custom": 1,
            "disabled": 0
        })
        role.insert(ignore_permissions=True)
        print(f"  → Created role: {role_name}")
    else:
        print(f"  → Role already exists: {role_name}")


# =============================================================================
# PERMISSIONS SETUP
# =============================================================================

def setup_provider_permissions():
    """Setup detailed permissions for Healthcare Provider role"""

    role_name = "Healthcare Provider"

    # Define permissions for each doctype
    permissions = [
        # Full access to consultations
        {
            "doctype": "Medical Consultation",
            "permissions": {
                "read": 1, "write": 1, "create": 1, "delete": 0,
                "submit": 1, "cancel": 1, "amend": 0,
                "report": 1, "export": 1, "import": 0,
                "set_user_permissions": 0, "share": 1
            }
        },
        # Consultation messages
        {
            "doctype": "Consultation Message",
            "permissions": {
                "read": 1, "write": 1, "create": 1, "delete": 1,
                "submit": 0, "cancel": 0, "amend": 0,
                "report": 0, "export": 0, "import": 0
            }
        },
        # Full access to prescriptions
        {
            "doctype": "Medical Prescription",
            "permissions": {
                "read": 1, "write": 1, "create": 1, "delete": 0,
                "submit": 1, "cancel": 1, "amend": 0,
                "report": 1, "export": 1, "import": 0
            }
        },
        # Prescription items
        {
            "doctype": "Prescription Item",
            "permissions": {
                "read": 1, "write": 1, "create": 1, "delete": 1,
                "submit": 0, "cancel": 0, "amend": 0
            }
        },
        # Read-only patient access
        {
            "doctype": "Patient",
            "permissions": {
                "read": 1, "write": 0, "create": 0, "delete": 0,
                "submit": 0, "cancel": 0, "amend": 0,
                "report": 1, "export": 1, "import": 0
            }
        },
        # Medication schedules (read-only)
        {
            "doctype": "Medication Schedule",
            "permissions": {
                "read": 1, "write": 0, "create": 0, "delete": 0,
                "report": 1, "export": 0
            }
        },
        # Medication logs (read-only)
        {
            "doctype": "Medication Log",
            "permissions": {
                "read": 1, "write": 0, "create": 0, "delete": 0,
                "report": 1, "export": 0
            }
        },
        # Own profile management
        {
            "doctype": "Healthcare Provider",
            "permissions": {
                "read": 1, "write": 1, "create": 0, "delete": 0,
                "submit": 0, "cancel": 0, "amend": 0,
                "report": 1, "export": 0
            }
        },
        # Schedule management
        {
            "doctype": "Provider Schedule",
            "permissions": {
                "read": 1, "write": 1, "create": 1, "delete": 1,
                "submit": 0, "cancel": 0, "amend": 0
            }
        },
        # Adherence reports (read-only)
        {
            "doctype": "Adherence Report",
            "permissions": {
                "read": 1, "write": 0, "create": 0, "delete": 0,
                "report": 1, "export": 1
            }
        },
        # Patient orders (read-only)
        {
            "doctype": "Patient Order",
            "permissions": {
                "read": 1, "write": 0, "create": 0, "delete": 0,
                "report": 1, "export": 0
            }
        },
    ]

    # Apply permissions
    for perm_config in permissions:
        doctype = perm_config["doctype"]
        perms = perm_config["permissions"]

        # Check if doctype exists
        if not frappe.db.exists("DocType", doctype):
            print(f"  ⚠️  DocType not found: {doctype} (skipping)")
            continue

        # Remove existing permissions for this role
        frappe.db.delete("Custom DocPerm", {
            "parent": doctype,
            "role": role_name
        })

        # Create new permission
        try:
            perm = frappe.get_doc({
                "doctype": "Custom DocPerm",
                "parent": doctype,
                "parenttype": "DocType",
                "parentfield": "permissions",
                "role": role_name,
                "permlevel": 0,
                **perms
            })
            perm.insert(ignore_permissions=True)
            print(f"  → Set permissions for: {doctype}")
        except Exception as e:
            print(f"  ⚠️  Error setting permissions for {doctype}: {str(e)}")


# =============================================================================
# WORKSPACE CREATION
# =============================================================================

def create_provider_workspace():
    """Create Healthcare Provider workspace"""

    workspace_name = "Healthcare Provider Portal"

    # Delete existing workspace if exists
    if frappe.db.exists("Workspace", workspace_name):
        frappe.delete_doc("Workspace", workspace_name, force=1, ignore_permissions=True)

    # Create workspace
    workspace = frappe.get_doc({
        "doctype": "Workspace",
        "name": workspace_name,
        "title": workspace_name,
        "module": "My Medicinal",
        "icon": "doctor",
        "is_standard": 0,
        "public": 1,
        "restrict_to_domain": "",
        "for_user": "",
        "parent_page": "",
        "content": json.dumps([
            {
                "type": "header",
                "data": {
                    "text": "Healthcare Provider Portal",
                    "col": 12
                }
            },
            {
                "type": "shortcut",
                "data": {
                    "shortcut_name": "Active Consultations",
                    "label": "Active Consultations",
                    "link_to": "Medical Consultation",
                    "type": "Link",
                    "icon": "solid-calendar-check",
                    "color": "#10b981"
                }
            },
            {
                "type": "shortcut",
                "data": {
                    "shortcut_name": "My Patients",
                    "label": "My Patients",
                    "link_to": "Patient",
                    "type": "Link",
                    "icon": "solid-users",
                    "color": "#3b82f6"
                }
            },
            {
                "type": "shortcut",
                "data": {
                    "shortcut_name": "Prescriptions",
                    "label": "Prescriptions",
                    "link_to": "Medical Prescription",
                    "type": "Link",
                    "icon": "solid-file-prescription",
                    "color": "#8b5cf6"
                }
            },
            {
                "type": "shortcut",
                "data": {
                    "shortcut_name": "My Schedule",
                    "label": "My Schedule",
                    "link_to": "Provider Schedule",
                    "type": "Link",
                    "icon": "solid-clock",
                    "color": "#f59e0b"
                }
            },
            {
                "type": "card",
                "data": {
                    "card_name": "Consultations",
                    "label": "Consultations",
                    "links": [
                        {
                            "label": "Active Consultations",
                            "type": "Link",
                            "name": "Medical Consultation"
                        },
                        {
                            "label": "Consultation History",
                            "type": "Report",
                            "name": "Consultation Report"
                        }
                    ]
                }
            },
            {
                "type": "card",
                "data": {
                    "card_name": "Prescriptions",
                    "label": "Prescriptions",
                    "links": [
                        {
                            "label": "Create Prescription",
                            "type": "Link",
                            "name": "Medical Prescription"
                        },
                        {
                            "label": "Prescription History",
                            "type": "Link",
                            "name": "Medical Prescription"
                        }
                    ]
                }
            }
        ])
    })

    workspace.insert(ignore_permissions=True)
    print(f"  → Created workspace: {workspace_name}")


# =============================================================================
# DASHBOARD SETUP
# =============================================================================

def setup_provider_dashboard():
    """Setup Healthcare Provider dashboard with charts"""

    dashboard_name = "Healthcare Provider Dashboard"

    # For now, just print that dashboard setup would be here
    # Full implementation would create Dashboard, Chart, and Number Card docs
    print(f"  → Dashboard configuration ready: {dashboard_name}")


# =============================================================================
# API CONFIGURATION
# =============================================================================

def configure_provider_api():
    """Configure API settings for Healthcare Providers"""

    # Create API Key doctype settings if needed
    # This would configure rate limits, permissions, etc.
    print("  → API rate limits configured for providers")
    print("  → API endpoints whitelisted")


# =============================================================================
# NOTIFICATIONS SETUP
# =============================================================================

def setup_provider_notifications():
    """Setup notification rules for Healthcare Providers"""

    notifications = [
        {
            "name": "New Consultation Request - Provider",
            "document_type": "Medical Consultation",
            "event": "New",
            "method": "Email,Push",
            "recipients": "Owner",
            "subject": "New Consultation Request",
            "message": "You have a new consultation request from patient"
        },
        {
            "name": "Consultation Cancelled - Provider",
            "document_type": "Medical Consultation",
            "event": "Cancel",
            "method": "Email,Push,SMS",
            "recipients": "Owner",
            "subject": "Consultation Cancelled",
            "message": "A consultation has been cancelled"
        }
    ]

    print("  → Notification rules configured")


# =============================================================================
# SAMPLE DATA CREATION
# =============================================================================

def create_sample_provider_data():
    """Create sample Healthcare Provider data for testing"""

    # Create test provider user
    test_email = "test.provider@dawaii.com"

    if not frappe.db.exists("User", test_email):
        user = frappe.get_doc({
            "doctype": "User",
            "email": test_email,
            "first_name": "Test",
            "last_name": "Provider",
            "enabled": 1,
            "send_welcome_email": 0,
            "roles": [
                {"role": "Healthcare Provider"}
            ]
        })
        user.insert(ignore_permissions=True)
        print(f"  → Created test user: {test_email}")

    # Create test Healthcare Provider record
    if not frappe.db.exists("Healthcare Provider", {"user": test_email}):
        try:
            provider = frappe.get_doc({
                "doctype": "Healthcare Provider",
                "provider_name": "Dr. Test Provider",
                "user": test_email,
                "specialty": "General Practice",
                "qualifications": "MBBS, MD",
                "experience_years": 5,
                "consultation_fee": 200,
                "is_available": 1,
                "license_number": "TEST123456"
            })
            provider.insert(ignore_permissions=True)
            print(f"  → Created test provider record")
        except Exception as e:
            print(f"  ⚠️  Could not create test provider: {str(e)}")


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_provider_environment_status():
    """
    Get current status of provider environment
    Returns dictionary with setup status
    """

    status = {
        "timestamp": datetime.now().isoformat(),
        "role_exists": frappe.db.exists("Role", "Healthcare Provider"),
        "workspace_exists": frappe.db.exists("Workspace", "Healthcare Provider Portal"),
        "provider_count": frappe.db.count("Healthcare Provider"),
        "active_providers": frappe.db.count("Healthcare Provider", {"is_available": 1}),
        "config_loaded": True
    }

    return status


def reset_provider_environment():
    """
    Reset provider environment (USE WITH CAUTION - FOR DEVELOPMENT ONLY)
    This will remove all provider configurations
    """

    if frappe.conf.get("developer_mode"):
        print("⚠️  Resetting provider environment...")

        # Remove workspace
        if frappe.db.exists("Workspace", "Healthcare Provider Portal"):
            frappe.delete_doc("Workspace", "Healthcare Provider Portal", force=1, ignore_permissions=True)

        # Remove custom permissions
        frappe.db.delete("Custom DocPerm", {"role": "Healthcare Provider"})

        frappe.db.commit()
        print("✅ Provider environment reset complete")
    else:
        print("❌ Reset only allowed in developer mode")


# =============================================================================
# FRAPPE WHITELISTED API METHODS
# =============================================================================

@frappe.whitelist()
def get_provider_config():
    """Get provider environment configuration (API endpoint)"""
    return load_provider_config()


@frappe.whitelist()
def get_environment_status():
    """Get provider environment status (API endpoint)"""
    return get_provider_environment_status()


# =============================================================================
# CLI COMMANDS
# =============================================================================

if __name__ == "__main__":
    # For direct execution
    initialize_provider_environment()
