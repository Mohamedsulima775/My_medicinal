from . import __version__ as app_version
import os

app_name = "my_medicinal"
app_title = "Dawaii"
app_publisher = "mohammedsuliman"
app_description = "Chronic Disease Management System"
app_email = "mohamedsuliman923@gmail.com"
app_license = "MIT"
app_color = "#2D6A4F"


fixtures = ["Custom Field"]





doctype_js = {
    "medicineprofile": "public/js/medicine_profile.js",
    "prescription": "public/js/prescription.js",
    "patientmedication": "public/js/patient_medication.js",
}



#website_context = {
 #   "brand_html": """
 #      <img src="/files/logo.png" height="32">
 #       <span>Dawaii</span>
  #  """,
#}

app_include_css = [
    "/assets/my_medicinal/css/dawaii_theme.css"
]

app_include_js = [
    "/assets/my_medicinal/js/dawaii_custom.js"
]

# Include CSS/JS ?? Web Pages
#web_include_css = [
 #   "/assets/my_medicinal/css/dawaii_theme.css"
#]

#web_include_js = [
#    "/assets/my_medicinal/js/dawaii_custom.js"
#]


website_context = {
    "brand_html": """
        <div class="dawaii-brand" style="display: flex; align-items: center; gap: 8px;">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="32" height="32" rx="8" fill="#2D6A4F"/>
                <path d="M16 8L16 24M8 16L24 16" stroke="white" stroke-width="3" stroke-linecap="round"/>
                <circle cx="16" cy="16" r="3" fill="white"/>
            </svg>
            <span style="font-weight: 700; font-size: 1.1rem; color: #2D6A4F;">?????</span>
        </div>
    """,
    "favicon": "/assets/my_medicinal/images/favicon.ico",
    "splash_image": "/assets/my_medicinal/images/dawaii_logo.jpg"
}


#Includes in <head>
# ------------------
#include js, css files in header of desk.html
#app_include_css = "/assets/my_medicinal/css/dawaii_theme.css"
#app_include_js = "/assets/my_medicinal/js/dawaii_custom.js"

# include js, css files in header of web template
#web_include_css = "/assets/my_medicinal/css/theme.css"
#web_include_js = "/assets/my_medicinal/js/custom.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "my_medicinal/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "my_medicinal.utils.jinja_methods",
#	"filters": "my_medicinal.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "my_medicinal.install.before_install"
# after_install = "my_medicinal.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "my_medicinal.uninstall.before_uninstall"
# after_uninstall = "my_medicinal.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "my_medicinal.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------
# Scheduled Tasks
# ---------------


#scheduler_events = {
    # Every 5 minutes - Medication Reminders
 #   "cron": {
  #      "*/5 * * * *": [
   #         "my_medicinal.my_medicinal.tasks.send_medication_reminders"
    #    ]
  #  },
   # 
    # Hourly
 #   "hourly": [
  #      "my_medicinal.my_medicinal.tasks.hourly"
   # ],
    
    # Daily (midnight)
   # "daily": [
    #    "my_medicinal.my_medicinal.tasks.all"
   # ],
    
    # Weekly (Sunday)
  #  "weekly": [
    #    "my_medicinal.my_medicinal.tasks.cleanup_old_notifications"
   # ]
#}



scheduler_events = {
    # Every 5 minutes - Medication Reminders
    "cron": {
        "*/5 * * * *": [
            "my_medicinal.my_medicinal.tasks.send_medication_reminders"
        ]
    },

    # Hourly - Check medications and send reminders
    "hourly": [
        "my_medicinal.my_medicinal.tasks.hourly"
    ],

    # Daily - Run all daily tasks (stock check, adherence reports)
    "daily": [
        "my_medicinal.my_medicinal.tasks.all"
    ],

    # Weekly - Cleanup old notifications
    "weekly": [
        "my_medicinal.my_medicinal.tasks.cleanup_old_notifications"
    ]
}


doc_events = {
    # Medication Schedule - جميع الدوال موجودة ✓
    "Medication Schedule": {
        "validate": "my_medicinal.my_medicinal.api.medication.validate",
        "after_insert": "my_medicinal.my_medicinal.api.medication.after_insert",
        "on_update": "my_medicinal.my_medicinal.api.medication.on_update",
        "before_save": "my_medicinal.my_medicinal.api.medication.calculate_depletion"
    },

    # Medication Log - الدالة موجودة ✓
    "Medication Log": {
        "after_insert": "my_medicinal.my_medicinal.api.medication.update_adherence"
    }

    # Medical Prescription - معلق (الدوال غير موجودة)
    # "Medical Prescription": {
    #     "on_submit": "my_medicinal.my_medicinal.api.prescription.notify_patient",
    #     "validate": "my_medicinal.my_medicinal.api.prescription.validate_prescription"
    # },

    # Patient Order - معلق (الدوال غير موجودة)
    # "Patient Order": {
    #     "validate": "my_medicinal.my_medicinal.api.order.validate_order",
    #     "on_update": "my_medicinal.my_medicinal.api.order.update_inventory",
    #     "on_submit": "my_medicinal.my_medicinal.api.order.process_payment"
    # },

    # Medical Consultation - معلق (الدوال غير موجودة)
    # "Medical Consultation": {
    #     "after_insert": "my_medicinal.my_medicinal.api.consultation.notify_doctor",
    #     "on_update": "my_medicinal.my_medicinal.api.consultation.notify_patient"
    # }
}




override_whitelisted_methods = {
    # Patient APIs - تم تصحيح أسماء الدوال
    "my_medicinal.my_medicinal.api.patient.register": "my_medicinal.my_medicinal.api.patient.register",
    "my_medicinal.my_medicinal.api.patient.get_profile": "my_medicinal.my_medicinal.api.patient.get_profile",
    "my_medicinal.my_medicinal.api.patient.update_profile": "my_medicinal.my_medicinal.api.patient.update_profile",

    # Medication APIs
    "my_medicinal.my_medicinal.api.medication.add": "my_medicinal.my_medicinal.api.medication.add_medication",
    "my_medicinal.my_medicinal.api.medication.get_list": "my_medicinal.my_medicinal.api.medication.get_patient_medications",
    "my_medicinal.my_medicinal.api.medication.log_taken": "my_medicinal.my_medicinal.api.medication.log_medication_taken",

    # Consultation APIs - تم تصحيح اسم الدالة
    "my_medicinal.my_medicinal.api.consultation.create": "my_medicinal.my_medicinal.api.consultation.create_consultation",
    "my_medicinal.my_medicinal.api.consultation.get_list": "my_medicinal.my_medicinal.api.consultation.get_my_consultations",

    # Order APIs - تم تصحيح اسم الدالة
    "my_medicinal.my_medicinal.api.order.create": "my_medicinal.my_medicinal.api.order.create_order",
    "my_medicinal.my_medicinal.api.order.get_list": "my_medicinal.my_medicinal.api.order.get_my_orders",

    # Shop APIs - تم تصحيح أسماء الدوال
    "my_medicinal.my_medicinal.api.product.get_products": "my_medicinal.my_medicinal.api.product.get_products",
    "my_medicinal.my_medicinal.api.product.search": "my_medicinal.my_medicinal.api.product.search_products",

    # Provider APIs
    "my_medicinal.my_medicinal.api.provider.get_my_consultations": "my_medicinal.my_medicinal.api.provider.get_my_consultations",
    "my_medicinal.my_medicinal.api.provider.get_consultation_details": "my_medicinal.my_medicinal.api.provider.get_consultation_details",
    "my_medicinal.my_medicinal.api.provider.update_consultation": "my_medicinal.my_medicinal.api.provider.update_consultation",
    "my_medicinal.my_medicinal.api.provider.create_prescription": "my_medicinal.my_medicinal.api.provider.create_prescription",
    "my_medicinal.my_medicinal.api.provider.get_my_prescriptions": "my_medicinal.my_medicinal.api.provider.get_my_prescriptions",
    "my_medicinal.my_medicinal.api.provider.get_my_patients": "my_medicinal.my_medicinal.api.provider.get_my_patients",
    "my_medicinal.my_medicinal.api.provider.get_patient_history": "my_medicinal.my_medicinal.api.provider.get_patient_history",
    "my_medicinal.my_medicinal.api.provider.get_doctor_statistics": "my_medicinal.my_medicinal.api.provider.get_doctor_statistics",
    "my_medicinal.my_medicinal.api.provider.update_my_profile": "my_medicinal.my_medicinal.api.provider.update_my_profile",

    # Real-time Chat APIs
    "my_medicinal.my_medicinal.api.realtime_chat.send_chat_message": "my_medicinal.my_medicinal.api.realtime_chat.send_chat_message",
    "my_medicinal.my_medicinal.api.realtime_chat.get_chat_messages": "my_medicinal.my_medicinal.api.realtime_chat.get_chat_messages",
    "my_medicinal.my_medicinal.api.realtime_chat.mark_messages_as_read": "my_medicinal.my_medicinal.api.realtime_chat.mark_messages_as_read",
    "my_medicinal.my_medicinal.api.realtime_chat.set_typing_status": "my_medicinal.my_medicinal.api.realtime_chat.set_typing_status",
    "my_medicinal.my_medicinal.api.realtime_chat.get_chat_status": "my_medicinal.my_medicinal.api.realtime_chat.get_chat_status",
    "my_medicinal.my_medicinal.api.realtime_chat.get_unread_counts": "my_medicinal.my_medicinal.api.realtime_chat.get_unread_counts",
    "my_medicinal.my_medicinal.api.realtime_chat.delete_message": "my_medicinal.my_medicinal.api.realtime_chat.delete_message",
    "my_medicinal.my_medicinal.api.realtime_chat.get_active_chats": "my_medicinal.my_medicinal.api.realtime_chat.get_active_chats",

}

# ============================================================================
# NOTIFICATION CONFIG - ? ??????? ?????????
# ============================================================================

notification_config = "my_medicinal.my_medicinal.notifications.get_notification_config"

# ============================================================================
# EMAIL CONFIGURATION - ? ??????? ??????
# ============================================================================

email_brand_logo = os.getenv("EMAIL_BRAND_LOGO", "/assets/my_medicinal/images/email-logo.png")
email_brand_color = os.getenv("EMAIL_BRAND_COLOR", "#2D6A4F")

# CORS Configuration - Use environment variable for production
# Format: comma-separated list (e.g., "https://app.com,https://www.app.com")
_cors_origins = os.getenv("ALLOWED_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:8000")
allow_cors = [origin.strip() for origin in _cors_origins.split(",") if origin.strip()]

# ============================================================================
# RATE LIMITING - Use environment variables
# ============================================================================

rate_limit = {
    "limit": int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100")),
    "window": int(os.getenv("RATE_LIMIT_WINDOW", "60"))
}

# ============================================================================
# FILE UPLOAD LIMITS - ? ???? ??? ???????
# ============================================================================

max_file_size = 5 * 1024 * 1024  # 5MB

# ============================================================================
# AUTHENTICATION HOOKS - ? ?????? ?????
# ============================================================================

# auth_hooks = [
#     "my_medicinal.auth.validate_patient_login"
# ]

# ============================================================================
# CUSTOM DOCTYPES TO IGNORE - ? DocTypes ???????
# ============================================================================

ignore_links_on_delete = [
    "Communication",
    "Comment",
    "Notification Log"
]

# ============================================================================
# AUTO CANCEL EXEMPTIONS - ? ????????? ??????? ????????
# ============================================================================

auto_cancel_exempted_doctypes = [
    "Medication Log",
    "Notification Log"
]


user_data_fields = [
    {
        "doctype": "Patient",
        "filter_by": "user",
        "redact_fields": ["mobile", "email", "national_id"],
        "partial": 1,
    },
    {
        "doctype": "Medical Prescription",
        "filter_by": "patient",
        "redact_fields": ["prescription_details"],
        "partial": 1,
    }
]


# FCM Configuration (Push Notifications) - Use environment variables
fcm_enabled = bool(int(os.getenv("FCM_ENABLED", "0")))
fcm_server_key = os.getenv("FCM_SERVER_KEY")
fcm_credentials_path = os.getenv("FCM_CREDENTIALS_PATH", "./firebase_credentials.json")

# SMS Configuration - Use environment variables
sms_enabled = bool(int(os.getenv("SMS_ENABLED", "0")))
sms_provider = os.getenv("SMS_PROVIDER", "twilio")  # "twilio" or "unifonic"

# Twilio settings (if using Twilio)
sms_settings = {
    "account_sid": os.getenv("TWILIO_ACCOUNT_SID"),
    "auth_token": os.getenv("TWILIO_AUTH_TOKEN"),
    "from_number": os.getenv("TWILIO_FROM_NUMBER")
}

# Payment Gateway - Use environment variables
payment_gateway_enabled = bool(int(os.getenv("PAYMENT_GATEWAY_ENABLED", "0")))
payment_gateway_provider = os.getenv("PAYMENT_GATEWAY_PROVIDER", "stripe")  # "stripe", "payfort", or "paytabs"

# ============================================================================
# SECURITY & MONITORING HOOKS
# ============================================================================

# Add security headers to all responses
after_request = [
    "my_medicinal.my_medicinal.security_headers.add_security_headers"
]

# Validate requests before processing
before_request = [
    "my_medicinal.my_medicinal.security_headers.validate_content_type",
    "my_medicinal.my_medicinal.security_headers.sanitize_input"
]

# Enable API request logging (set to 0 to disable)
api_logging_enabled = bool(int(os.getenv("API_LOGGING_ENABLED", "1")))

# ============================================================================
# CONSOLE LOG
# ============================================================================
# Log app startup
import frappe

def on_session_creation(login_manager):
    """Called when user logs in"""
    frappe.logger().info(f"Dawaii {login_manager.user}")



