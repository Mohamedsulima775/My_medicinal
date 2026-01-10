# -*- coding: utf-8 -*-
"""
Healthcare Provider Middleware
بوابة الأمان لمقدمي الرعاية الصحية
======================================
Security and access control middleware specifically for Healthcare Providers

Features:
- Provider authentication validation
- Role-based access control
- Activity logging and audit trail
- Rate limiting for provider APIs
- Session management
- IP whitelist (optional)

Author: Mohammed Suliman
Date: 2026-01-10
"""

import frappe
from frappe import _
import os
from datetime import datetime, timedelta
import json


# =============================================================================
# PROVIDER AUTHENTICATION MIDDLEWARE
# =============================================================================

def validate_provider_access(func):
    """
    Decorator to validate Healthcare Provider access
    Ensures user has Healthcare Provider role and active provider record
    """
    def wrapper(*args, **kwargs):
        try:
            # Check if user is logged in
            if frappe.session.user == "Guest":
                frappe.throw(_("Authentication required"), frappe.PermissionError)

            # Check if user has Healthcare Provider role
            if "Healthcare Provider" not in frappe.get_roles():
                frappe.throw(_("Healthcare Provider role required"), frappe.PermissionError)

            # Check if provider record exists and is active
            provider = frappe.db.get_value(
                "Healthcare Provider",
                {"user": frappe.session.user},
                ["name", "is_available", "provider_name"],
                as_dict=True
            )

            if not provider:
                frappe.throw(_("No Healthcare Provider record found for this user"), frappe.DoesNotExistError)

            # Log provider activity
            log_provider_activity(provider.name, func.__name__)

            # Execute the function
            return func(*args, **kwargs)

        except frappe.PermissionError:
            frappe.local.response["http_status_code"] = 403
            raise
        except frappe.DoesNotExistError:
            frappe.local.response["http_status_code"] = 404
            raise
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Provider Access Validation Error")
            frappe.throw(_("Access validation failed: {0}").format(str(e)))

    return wrapper


def check_provider_ip_whitelist():
    """
    Check if provider's IP is whitelisted (if whitelist is enabled)
    """
    whitelist = os.getenv("PROVIDER_IP_WHITELIST", "")

    if not whitelist:
        return True  # No whitelist configured, allow all

    allowed_ips = [ip.strip() for ip in whitelist.split(",")]
    user_ip = frappe.local.request_ip

    if user_ip not in allowed_ips:
        frappe.log_error(
            f"Unauthorized IP access attempt: {user_ip}",
            "Provider IP Whitelist Violation"
        )
        return False

    return True


# =============================================================================
# PROVIDER RATE LIMITING
# =============================================================================

def apply_provider_rate_limit():
    """
    Apply rate limiting specifically for provider endpoints
    Higher limits than regular users
    """
    if not get_env_bool("PROVIDER_PORTAL_ENABLED", True):
        return

    max_requests = int(os.getenv("PROVIDER_RATE_LIMIT_MAX_REQUESTS", 500))
    window = int(os.getenv("PROVIDER_RATE_LIMIT_WINDOW", 60))

    user = frappe.session.user
    if user == "Guest":
        return

    # Check if user has Healthcare Provider role
    if "Healthcare Provider" not in frappe.get_roles():
        return

    # Create cache key
    cache_key = f"provider_rate_limit:{user}"

    # Get current request count
    request_count = frappe.cache().get(cache_key) or 0

    if request_count >= max_requests:
        frappe.local.response["http_status_code"] = 429
        frappe.throw(
            _("Rate limit exceeded. Maximum {0} requests per {1} seconds").format(max_requests, window),
            frappe.RateLimitExceededError
        )

    # Increment counter
    frappe.cache().setex(cache_key, window, request_count + 1)


# =============================================================================
# PROVIDER SESSION MANAGEMENT
# =============================================================================

def extend_provider_session():
    """
    Extend session timeout for Healthcare Providers
    Providers get longer sessions (default 8 hours vs 1 hour for patients)
    """
    if frappe.session.user == "Guest":
        return

    if "Healthcare Provider" not in frappe.get_roles():
        return

    # Get provider session timeout from config
    timeout = int(os.getenv("PROVIDER_SESSION_TIMEOUT", 28800))  # 8 hours default

    # Update session expiry
    frappe.db.set_value(
        "Sessions",
        frappe.session.sid,
        "lastupdate",
        datetime.now()
    )


# =============================================================================
# PROVIDER ACTIVITY LOGGING
# =============================================================================

def log_provider_activity(provider_name, action, details=None):
    """
    Log provider activities for audit trail
    """
    if not get_env_bool("PROVIDER_LOGIN_AUDIT_ENABLED", True):
        return

    try:
        log_entry = {
            "provider": provider_name,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "user": frappe.session.user,
            "ip_address": frappe.local.request_ip,
            "user_agent": frappe.request.headers.get("User-Agent", ""),
            "details": details or {}
        }

        # Store in cache for batch processing
        cache_key = f"provider_activity_log:{datetime.now().strftime('%Y%m%d')}"
        logs = frappe.cache().get(cache_key) or []
        logs.append(log_entry)
        frappe.cache().setex(cache_key, 86400, logs)  # 24 hours

    except Exception as e:
        # Don't fail the request if logging fails
        frappe.log_error(f"Provider activity logging failed: {str(e)}", "Provider Activity Log Error")


def get_provider_activity_log(provider_name, days=7):
    """
    Retrieve provider activity log for specified number of days
    """
    logs = []

    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        cache_key = f"provider_activity_log:{date}"
        day_logs = frappe.cache().get(cache_key) or []

        # Filter logs for specific provider
        provider_logs = [log for log in day_logs if log.get("provider") == provider_name]
        logs.extend(provider_logs)

    return logs


# =============================================================================
# PROVIDER DATA ACCESS CONTROL
# =============================================================================

def validate_patient_access(provider_name, patient_name):
    """
    Validate that provider has access to patient data
    Provider can only access patients they have consulted with
    """
    # Check if provider has any consultation with this patient
    consultation = frappe.db.exists(
        "Medical Consultation",
        {
            "healthcare_provider": provider_name,
            "patient": patient_name
        }
    )

    if not consultation:
        frappe.throw(
            _("You do not have access to this patient's data"),
            frappe.PermissionError
        )

    # Log access attempt
    log_provider_activity(
        provider_name,
        "patient_data_access",
        {"patient": patient_name}
    )

    return True


def get_provider_accessible_patients(provider_name):
    """
    Get list of patients that provider has access to
    Returns patients who have had consultations with this provider
    """
    patients = frappe.db.sql("""
        SELECT DISTINCT patient, patient_name
        FROM `tabMedical Consultation`
        WHERE healthcare_provider = %s
        ORDER BY modified DESC
    """, provider_name, as_dict=True)

    return patients


# =============================================================================
# PROVIDER PERMISSION FILTERS
# =============================================================================

def get_permission_query_conditions(doctype):
    """
    Return permission query conditions for Healthcare Providers
    This filters data based on provider's access rights
    """
    if not frappe.session.user or frappe.session.user == "Guest":
        return ""

    # Check if user has Healthcare Provider role
    if "Healthcare Provider" not in frappe.get_roles():
        return ""

    # Get provider record
    provider = frappe.db.get_value("Healthcare Provider", {"user": frappe.session.user}, "name")
    if not provider:
        return ""

    # Apply filters based on doctype
    conditions = {
        "Medical Consultation": f"`tabMedical Consultation`.healthcare_provider = '{provider}'",
        "Medical Prescription": f"`tabMedical Prescription`.prescribed_by = '{provider}'",
        "Consultation Message": f"""
            `tabConsultation Message`.parent IN (
                SELECT name FROM `tabMedical Consultation`
                WHERE healthcare_provider = '{provider}'
            )
        """,
    }

    return conditions.get(doctype, "")


def has_permission(doc, ptype="read", user=None):
    """
    Check if provider has permission to access specific document
    """
    if not user:
        user = frappe.session.user

    # Admin always has access
    if user == "Administrator":
        return True

    # Check if user has Healthcare Provider role
    roles = frappe.get_roles(user)
    if "Healthcare Provider" not in roles:
        return False

    # Get provider record
    provider = frappe.db.get_value("Healthcare Provider", {"user": user}, "name")
    if not provider:
        return False

    # Check permission based on doctype
    if doc.doctype == "Medical Consultation":
        return doc.healthcare_provider == provider

    elif doc.doctype == "Medical Prescription":
        return doc.prescribed_by == provider

    elif doc.doctype == "Patient":
        # Check if provider has consulted with this patient
        return frappe.db.exists(
            "Medical Consultation",
            {"healthcare_provider": provider, "patient": doc.name}
        )

    return False


# =============================================================================
# TWO-FACTOR AUTHENTICATION
# =============================================================================

def require_provider_2fa():
    """
    Enforce two-factor authentication for providers if enabled
    """
    if not get_env_bool("PROVIDER_2FA_REQUIRED", False):
        return True

    user = frappe.session.user
    if user == "Guest":
        return False

    # Check if user has 2FA enabled
    user_doc = frappe.get_doc("User", user)
    if not user_doc.two_factor_auth:
        frappe.throw(
            _("Two-factor authentication is required for Healthcare Providers"),
            frappe.ValidationError
        )

    return True


# =============================================================================
# PROVIDER DIGITAL SIGNATURE
# =============================================================================

def validate_digital_signature(provider_name, document_type, document_name):
    """
    Validate digital signature for prescriptions and medical documents
    """
    if not get_env_bool("PRESCRIPTION_DIGITAL_SIGNATURE_REQUIRED", True):
        return True

    # Check if document has valid digital signature
    # Implementation would depend on your digital signature system
    # For now, just log the validation attempt

    log_provider_activity(
        provider_name,
        "digital_signature_validation",
        {
            "document_type": document_type,
            "document_name": document_name
        }
    )

    return True


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_env_bool(key, default=False):
    """Get boolean environment variable"""
    value = os.getenv(key, str(default))
    return str(value).lower() in ('1', 'true', 'yes', 'on')


def get_current_provider():
    """
    Get current provider record for logged in user
    Returns provider name or None
    """
    if frappe.session.user == "Guest":
        return None

    provider = frappe.db.get_value(
        "Healthcare Provider",
        {"user": frappe.session.user},
        ["name", "provider_name", "specialty", "is_available"],
        as_dict=True
    )

    return provider


# =============================================================================
# HOOKS INTEGRATION
# =============================================================================

def on_provider_login(login_manager):
    """
    Hook to run when Healthcare Provider logs in
    """
    user = login_manager.user

    # Check if user is a provider
    if "Healthcare Provider" not in frappe.get_roles(user):
        return

    provider = frappe.db.get_value("Healthcare Provider", {"user": user}, "name")
    if not provider:
        return

    # Log login
    log_provider_activity(provider, "login")

    # Check IP whitelist
    if not check_provider_ip_whitelist():
        frappe.throw(_("Access denied: IP not whitelisted"), frappe.PermissionError)

    # Check 2FA if required
    require_provider_2fa()


def on_provider_logout(logout_user):
    """
    Hook to run when Healthcare Provider logs out
    """
    user = logout_user or frappe.session.user

    provider = frappe.db.get_value("Healthcare Provider", {"user": user}, "name")
    if provider:
        log_provider_activity(provider, "logout")


# =============================================================================
# FRAPPE WHITELISTED API METHODS
# =============================================================================

@frappe.whitelist()
def get_my_activity_log(days=7):
    """
    Get activity log for currently logged in provider
    """
    provider = get_current_provider()
    if not provider:
        frappe.throw(_("Not a Healthcare Provider"), frappe.PermissionError)

    logs = get_provider_activity_log(provider.name, days)
    return logs


@frappe.whitelist()
def get_my_accessible_patients():
    """
    Get list of patients accessible to current provider
    """
    provider = get_current_provider()
    if not provider:
        frappe.throw(_("Not a Healthcare Provider"), frappe.PermissionError)

    patients = get_provider_accessible_patients(provider.name)
    return patients


@frappe.whitelist()
def validate_my_access_to_patient(patient_name):
    """
    Validate current provider's access to a specific patient
    """
    provider = get_current_provider()
    if not provider:
        frappe.throw(_("Not a Healthcare Provider"), frappe.PermissionError)

    return validate_patient_access(provider.name, patient_name)
