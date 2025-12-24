from . import __version__ as app_version

app_name = "my_medicinal"
app_title = "my_medicinal"
app_publisher = "mohammedsuliman"
app_description = "enhancing pharmaceutical care services"
app_email = "mohamedsuliman923@gmail.com"
app_license = "MIT"



fixtures = ["Custom Field"]





doctype_js = {
    "medicineprofile": "public/js/medicine_profile.js",
    "prescription": "public/js/prescription.js",
    "patientmedication": "public/js/patient_medication.js",
}





# Includes in <head>
# ------------------
# include js, css files in header of desk.html
#app_include_css = "/assets/my_medicinal/css/theme.css"
# app_include_js = "/assets/my_medicinal/js/my_medicinal.js"

# include js, css files in header of web template
# web_include_css = "/assets/my_medicinal/css/my_medicinal.css"
# web_include_js = "/assets/my_medicinal/js/my_medicinal.js"

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
#scheduler_events = {
#	"hourly": [
#		"my_medicinal.my_medicinal.doctype.medication_log.medication_log.auto_log_missed_doses"
#	],
#}
scheduler_events = {
    "all": [
        "my_medicinal.tasks.all"
    ],
    "hourly": [
        "my_medicinal.tasks.hourly"
    ]
}
# scheduler_events = {
#	"all": [
#		"my_medicinal.tasks.all"
#	],
#	"daily": [
#		"my_medicinal.tasks.daily"
#	],
#	"hourly": [
#		"my_medicinal.tasks.hourly"
#	],
#	"weekly": [
#		"my_medicinal.tasks.weekly"
#	],
#	"monthly": [
#		"my_medicinal.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "my_medicinal.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "my_medicinal.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "my_medicinal.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["my_medicinal.utils.before_request"]
# after_request = ["my_medicinal.utils.after_request"]

# Job Events
# ----------
# before_job = ["my_medicinal.utils.before_job"]
# after_job = ["my_medicinal.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"my_medicinal.auth.validate"
# ]
