from . import __version__ as app_version

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

"cron": {
        "*/5 * * * *": [
            "my_medicinal.my_medicinal.tasks.send_medication_reminders"  # ? ????
        ]
    },
    
    # Hourly
    "hourly": [
        "my_medicinal.my_medicinal.tasks.hourly",  # ? ????
        "my_medicinal.my_medicinal.tasks.check_low_stock"  # ? ????
    ],
    
    # Daily
    "daily": [
        "my_medicinal.my_medicinal.tasks.daily",  # ? ????
        "my_medicinal.my_medicinal.tasks.calculate_adherence_rates",  # ? ????
        "my_medicinal.my_medicinal.tasks.send_daily_summary"  # ? ????
    ],
    
    # Weekly
    "weekly": [
        "my_medicinal.my_medicinal.tasks.cleanup_old_notifications",  # ? ????
        "my_medicinal.my_medicinal.tasks.generate_weekly_reports"  # ? ????
    ],
    
    # Monthly
    "monthly": [
        "my_medicinal.my_medicinal.tasks.generate_monthly_analytics"  # ? ????
    ]
}


doc_events = {
    #"patient": {
     #   "validate": "my_medicinal.my_medicinal.api.patient.validate_patient",  # ? ????
      #  "after_insert": "my_medicinal.my_medicinal.api.patient#.send_welcome_notification",  # ? ????
 #       "on_update": "my_medicinal.my_medicinal.api.patient.on_update"  # ? ????
  #  },
    
    "Medication Schedule": {
        "validate": "my_medicinal.my_medicinal.api.medication.validate",  # ? ????
        "after_insert": "my_medicinal.my_medicinal.api.medication.after_insert",  # ? ????
        "on_update": "my_medicinal.my_medicinal.api.medication.on_update",  # ? ????
        "before_save": "my_medicinal.my_medicinal.api.medication.calculate_depletion"  # ? ????
    },
    
    "Medication Log": {
        "after_insert": "my_medicinal.my_medicinal.api.medication.update_adherence"  # ? ????
    },
    
    "Medical Prescription": {
        "on_submit": "my_medicinal.my_medicinal.api.prescription.notify_patient",  # ? ????
        "validate": "my_medicinal.my_medicinal.api.prescription.validate_prescription"  # ? ????
    },
    
    "Patient Order": {
        "validate": "my_medicinal.my_medicinal.api.order.validate_order",  # ? ????
        "on_update": "my_medicinal.my_medicinal.api.order.update_inventory",  # ? ????
        "on_submit": "my_medicinal.my_medicinal.api.order.process_payment"  # ? ????
    },
    
    "Medical Consultation": {
        "after_insert": "my_medicinal.my_medicinal.api.consultation.notify_doctor",  # ? ????
        "on_update": "my_medicinal.my_medicinal.api.consultation.notify_patient"  # ? ????
    }
    
}




override_whitelisted_methods = {
   # Patient APIs
    "my_medicinal.my_medicinal.api.patient.register": "my_medicinal.my_medicinal.api.patient.register",  # ? ????
    "my_medicinal.my_medicinal.api.patient.get_profile": "my_medicinal.my_medicinal.api.patient.get_patient_profile",  # ? ????
    "my_medicinal.my_medicinal.api.patient.update_profile": "my_medicinal.my_medicinal.api.patient.update_patient_profile",  # ? ????
    
    # Medication APIs
    "my_medicinal.my_medicinal.api.medication.add": "my_medicinal.my_medicinal.api.medication.add_medication",  # ? ????
    "my_medicinal.my_medicinal.api.medication.get_list": "my_medicinal.my_medicinal.api.medication.get_patient_medications",  # ? ????
    "my_medicinal.my_medicinal.api.medication.log_taken": "my_medicinal.my_medicinal.api.medication.log_medication_taken",  # ? ????
    
    # Consultation APIs
    "my_medicinal.my_medicinal.api.consultation.create": "my_medicinal.my_medicinal.api.consultation.create_consultation",  # ? ????
    "my_medicinal.my_medicinal.api.consultation.get_list": "my_medicinal.my_medicinal.api.consultation.get_consultations",  # ? ????
    
    # Order APIs
    "my_medicinal.my_medicinal.api.order.create": "my_medicinal.my_medicinal.api.order.create_order",  # ? ????
    "my_medicinal.my_medicinal.api.order.get_list": "my_medicinal.my_medicinal.api.order.get_orders",  # ? ????
    
    # Shop APIs
    "my_medicinal.my_medicinal.api.product.get_products": "my_medicinal.my_medicinal.api.product.get_medication_products",  # ? ????
    "my_medicinal.my_medicinal.api.product.search": "my_medicinal.my_medicinal.api.product.search_products",  # ? ????
    
     # Provider APIs
    "my_medicinal.my_medicinal.api.provider.get_my_consultations": "my_medicinal.my_medicinal.api.provider.get_my_consultations",  # ? ????
    "my_medicinal.my_medicinal.api.provider.get_consultation_details": "my_medicinal.my_medicinal.api.provider.get_consultation_details",  # ? ????
    "my_medicinal.my_medicinal.api.provider.update_consultation": "my_medicinal.my_medicinal.api.provider.update_consultation",  # ? ????
    "my_medicinal.my_medicinal.api.provider.create_prescription": "my_medicinal.my_medicinal.api.provider.create_prescription",  # ? ????
    "my_medicinal.my_medicinal.api.provider.get_my_prescriptions": "my_medicinal.my_medicinal.api.provider.get_my_prescriptions",  # ? ????
    "my_medicinal.my_medicinal.api.provider.get_my_patients": "my_medicinal.my_medicinal.api.provider.get_my_patients",  # ? ????
    "my_medicinal.my_medicinal.api.provider.get_patient_history": "my_medicinal.my_medicinal.api.provider.get_patient_history",  # ? ????
    "my_medicinal.my_medicinal.api.provider.get_doctor_statistics": "my_medicinal.my_medicinal.api.provider.get_doctor_statistics",
    "my_medicinal.my_medicinal.api.provider.update_my_profile": "my_medicinal.my_medicinal.api.provider.update_my_profile",  

}

# ============================================================================
# NOTIFICATION CONFIG - ? ??????? ?????????
# ============================================================================

notification_config = "my_medicinal.my_medicinal.notifications.get_notification_config"

# ============================================================================
# EMAIL CONFIGURATION - ? ??????? ??????
# ============================================================================

email_brand_logo = "/assets/my_medicinal/images/email-logo.png"
email_brand_color = "#2D6A4F"

allow_cors = [
    "https://yourdomain.com",
    "http://localhost:3000",  # ???????
    "http://127.0.0.1:8000"   # ???????
]

# ============================================================================
# RATE LIMITING - ? ????? ???? ???????
# ============================================================================

rate_limit = {
    "limit": 100,  
    "window": 60 
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


# FCM Configuration (Push Notifications)
fcm_enabled = True
# fcm_server_key = "your_fcm_server_key_here"  # ??? ??????? ?? Firebase

# SMS Configuration
sms_enabled = True
sms_provider = "twilio"  # ?? "unifonic"
# sms_settings = {
#     "account_sid": "your_account_sid",
#     "auth_token": "your_auth_token",
#     "from_number": "+1234567890"
# }

# Payment Gateway
payment_gateway_enabled = True
# payment_gateway_provider = "stripe"  # ?? "payfort" ?? "paytabs"

# ============================================================================
# CONSOLE LOG - ? ??? Console
# ============================================================================
# Log app startup
import frappe

def on_session_creation(login_manager):
    """Called when user logs in"""
    frappe.logger().info(f"Dawaii {login_manager.user}")



