# -*- coding: utf-8 -*-
# Copyright (c) 2025, Your Company
# For license information, please see license.txt




#----------------------100%----------




from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, date_diff
from datetime import datetime
import re

class patient(Document):
    def validate(self):
        """Validation on save"""
        self.validate_mobile()
        self.validate_email()
        self.validate_national_id()
        self.validate_date_of_birth()
        self.calculate_age()
    
    def validate_mobile(self):
        """Validate mobile number"""
        if not self.mobile:
            frappe.throw("Mobile number is required")
        
        # Check format (05xxxxxxxx)
        mobile_pattern = r'^05\d{8}$'
        if not re.match(mobile_pattern, self.mobile):
            frappe.throw("Mobile number must be in format: 05xxxxxxxx")
        
        # Check for duplicates
        if self.mobile:
            existing = frappe.db.exists("patient", {
                "mobile": self.mobile,
                "name": ["!=", self.name]
            })
            if existing:
                frappe.throw("Mobile number {0} is already registered".format(self.mobile))
    
    def validate_email(self):
        """Validate email address"""
        if self.email:
            email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if not re.match(email_pattern, self.email):
                frappe.throw("Invalid email address")
    
    def validate_national_id(self):
        """Validate national ID"""
        if self.national_id:
            # Saudi national ID is 10 digits
            if not self.national_id.isdigit() or len(self.national_id) != 10:
                frappe.throw("National ID must be 10 digits")
    
    def validate_date_of_birth(self):
        """Validate date of birth"""
        if self.date_of_birth:
            dob = getdate(self.date_of_birth)
            today_date = getdate(today())
            
            # Check if date is in the future
            if dob > today_date:
                frappe.throw("Date of Birth cannot be in the future")
            
            # Check if date is too old (more than 150 years)
            years_diff = date_diff(today_date, dob) / 365
            if years_diff > 150:
                frappe.throw("Date of Birth seems incorrect. Age cannot be more than 150 years")
            
            # Check minimum age (optional - at least 1 year old)
            if years_diff < 0:
                frappe.throw("Invalid Date of Birth")
    
    def calculate_age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            dob = getdate(self.date_of_birth)
            today_date = getdate(today())
            
            # Calculate age in years
            age_days = date_diff(today_date, dob)
            age_years = int(age_days / 365.25)  # Using 365.25 to account for leap years
            
            self.age = age_years
        else:
            self.age = None
    
    def before_insert(self):
        """Before insert"""
        # Set default status
        if not self.status:
            self.status = "Active"
    
    def after_insert(self):
        """After insert"""
        # Send welcome email
        if self.email:
            self.send_welcome_email()
    
    def on_update(self):
        """On update"""
        pass
    
    def on_trash(self):
        """On delete"""
        # Check for active medications
        active_medications = frappe.db.count("Medication Schedule", {
            "patient": self.name,
            "is_active": 1
        })
        
        if active_medications > 0:
            frappe.throw("Cannot delete patient with {0} active medications".format(active_medications))
    
    def send_welcome_email(self):
        """Send welcome email"""
        try:
            frappe.sendmail(
                recipients=[self.email],
                subject="Welcome to Dawaii System",
                message="""
                    <h3>Welcome {0},</h3>
                    <p>Your account has been successfully created in Dawaii chronic disease management system.</p>
                    <p>Your registered mobile: {1}</p>
                    <p>You can now start adding your medications and receive reminders.</p>
                    <br>
                    <p>We wish you good health!</p>
                """.format(self.patient_name, self.mobile)
            )
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Welcome Email Error")


# Helper Functions

@frappe.whitelist()
def calculate_age_from_dob(date_of_birth):
    """Calculate age from date of birth (for API/JS)"""
    if not date_of_birth:
        return None
    
    dob = getdate(date_of_birth)
    today_date = getdate(today())
    
    # Calculate age in years
    age_days = date_diff(today_date, dob)
    age_years = int(age_days / 365.25)
    
    return age_years