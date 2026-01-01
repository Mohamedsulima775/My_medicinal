# Copyright (c) 2025, mohammedsuliman and contributors
# For license information, please see license.txt

# -*- coding: utf-8 -*-
# Copyright (c) 2024, Dawaii and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _


class HealthcareProvider(Document):
    """Healthcare Provider DocType Controller"""
    
    def validate(self):
        """Validate before saving"""
        self.validate_user()
        self.validate_license()
        self.sync_user_email()
    
    def validate_user(self):
        """Validate user field"""
        if not self.user:
            frappe.throw(_("User is required"))
        
        # Check if user exists
        if not frappe.db.exists("User", self.user):
            frappe.throw(_("User {0} does not exist").format(self.user))
        
        # Check if user is already linked to another provider
        existing = frappe.db.get_value(
            "Healthcare Provider",
            {"user": self.user, "name": ["!=", self.name]},
            "name"
        )
        
        if existing:
            frappe.throw(
                _("User {0} is already linked to Healthcare Provider {1}").format(
                    self.user, existing
                )
            )
    
    def validate_license(self):
        """Validate license number if provided"""
        if self.license_number:
            # Check for duplicate license
            existing = frappe.db.get_value(
                "Healthcare Provider",
                {
                    "license_number": self.license_number,
                    "name": ["!=", self.name]
                },
                "name"
            )
            
            if existing:
                frappe.throw(
                    _("License Number {0} is already registered to {1}").format(
                        self.license_number, existing
                    )
                )
    
    def sync_user_email(self):
        """Sync email from User if not provided"""
        if not self.email and self.user:
            user_email = frappe.db.get_value("User", self.user, "email")
            if user_email:
                self.email = user_email
    
    def on_update(self):
        """After save operations"""
        self.update_user_role()
        self.create_provider_schedule()
    
    def update_user_role(self):
        """Ensure user has Healthcare Provider role"""
        if self.user:
            user = frappe.get_doc("User", self.user)
            
            # Check if role exists
            has_role = False
            for role in user.roles:
                if role.role == "Healthcare Provider":
                    has_role = True
                    break
            
            # Add role if not present
            if not has_role:
                user.append("roles", {
                    "role": "Healthcare Provider"
                })
                user.save(ignore_permissions=True)
                frappe.msgprint(
                    _("Healthcare Provider role added to user {0}").format(self.user),
                    alert=True
                )
    
    def create_provider_schedule(self):
        """Create default schedule if not exists"""
        if not frappe.db.exists("Provider Schedule", {"provider": self.name}):
            # Create default schedule for Monday to Friday, 9 AM to 5 PM
            try:
                schedule = frappe.get_doc({
                    "doctype": "Provider Schedule",
                    "provider": self.name,
                    "provider_name": self.provider_name,
                    "day_of_week": "Monday",
                    "start_time": "09:00:00",
                    "end_time": "17:00:00",
                    "is_available": 1
                })
                schedule.insert(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), "Create Provider Schedule Error")
    
    def on_trash(self):
        """Before delete operations"""
        # Check if provider has active consultations
        active_consultations = frappe.db.count(
            "Medical Consultation",
            {"provider": self.name, "status": ["in", ["Pending", "Active"]]}
        )
        
        if active_consultations > 0:
            frappe.throw(
                _("Cannot delete Healthcare Provider with {0} active consultations").format(
                    active_consultations
                )
            )
    
    def get_availability_status(self):
        """Get current availability status"""
        if not self.is_available:
            return {
                "available": False,
                "message": _("Provider is not available")
            }
        
        # Check schedule
        from datetime import datetime
        
        current_day = datetime.now().strftime("%A")
        current_time = datetime.now().time()
        
        schedule = frappe.db.get_value(
            "Provider Schedule",
            {
                "provider": self.name,
                "day_of_week": current_day,
                "is_available": 1
            },
            ["start_time", "end_time"],
            as_dict=True
        )
        
        if schedule:
            if schedule.start_time <= current_time <= schedule.end_time:
                return {
                    "available": True,
                    "message": _("Provider is available now")
                }
            else:
                return {
                    "available": False,
                    "message": _("Provider is not available at this time")
                }
        
        return {
            "available": False,
            "message": _("No schedule defined for today")
        }
    
    def get_statistics(self):
        """Get provider statistics"""
        return {
            "total_consultations": frappe.db.count(
                "Medical Consultation",
                {"provider": self.name}
            ),
            "active_consultations": frappe.db.count(
                "Medical Consultation",
                {"provider": self.name, "status": "Active"}
            ),
            "pending_consultations": frappe.db.count(
                "Medical Consultation",
                {"provider": self.name, "status": "Pending"}
            ),
            "completed_consultations": frappe.db.count(
                "Medical Consultation",
                {"provider": self.name, "status": "Completed"}
            ),
            "total_prescriptions": frappe.db.count(
                "Medical Prescription",
                {"provider": self.name}
            ),
            "total_patients": frappe.db.sql("""
                SELECT COUNT(DISTINCT patient)
                FROM `tabMedical Consultation`
                WHERE provider = %s
            """, self.name)[0][0] if frappe.db.exists("Medical Consultation", {"provider": self.name}) else 0,
            "average_rating": self.get_average_rating()
        }
    
    def get_average_rating(self):
        """Calculate average rating"""
        # If you have a rating field in Medical Consultation
        try:
            avg = frappe.db.sql("""
                SELECT AVG(rating)
                FROM `tabMedical Consultation`
                WHERE provider = %s
                AND rating IS NOT NULL
            """, self.name)
            
            return round(avg[0][0], 2) if avg and avg[0][0] else 0.0
        except:
            return 0.0


# API Methods

@frappe.whitelist()
def get_provider_details(provider_id):
    """Get detailed provider information"""
    try:
        if not frappe.db.exists("Healthcare Provider", provider_id):
            frappe.throw(_("Healthcare Provider not found"))
        
        provider = frappe.get_doc("Healthcare Provider", provider_id)
        
        return {
            "name": provider.name,
            "provider_name": provider.provider_name,
            "specialty": provider.specialty,
            "qualifications": provider.qualifications,
            "experience_years": provider.experience_years,
            "consultation_fee": provider.consultation_fee,
            "is_available": provider.is_available,
            "availability_note": provider.availability_note,
            "mobile": provider.mobile,
            "email": provider.email,
            "license_number": provider.license_number,
            "statistics": provider.get_statistics(),
            "availability_status": provider.get_availability_status()
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Provider Details Error")
        frappe.throw(str(e))


@frappe.whitelist()
def get_available_providers(specialty=None):
    """Get list of available providers"""
    try:
        filters = {"is_available": 1}
        
        if specialty:
            filters["specialty"] = specialty
        
        providers = frappe.get_all(
            "Healthcare Provider",
            filters=filters,
            fields=[
                "name", "provider_name", "specialty", "qualifications",
                "experience_years", "consultation_fee", "mobile", "email"
            ]
        )
        
        # Add statistics for each provider
        for provider in providers:
            doc = frappe.get_doc("Healthcare Provider", provider.name)
            provider["statistics"] = doc.get_statistics()
            provider["availability_status"] = doc.get_availability_status()
        
        return providers
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Available Providers Error")
        frappe.throw(str(e))


@frappe.whitelist()
def search_providers(search_term, specialty=None, limit=20):
    """Search providers by name or specialty"""
    try:
        conditions = ["is_available = 1"]
        values = []
        
        if search_term:
            conditions.append(
                "(provider_name LIKE %s OR specialty LIKE %s OR qualifications LIKE %s)"
            )
            search_pattern = f"%{search_term}%"
            values.extend([search_pattern, search_pattern, search_pattern])
        
        if specialty:
            conditions.append("specialty = %s")
            values.append(specialty)
        
        sql = f"""
            SELECT 
                name, provider_name, specialty, qualifications,
                experience_years, consultation_fee, mobile, email
            FROM `tabHealthcare Provider`
            WHERE {' AND '.join(conditions)}
            ORDER BY provider_name
            LIMIT %s
        """
        
        values.append(int(limit))
        
        providers = frappe.db.sql(sql, tuple(values), as_dict=True)
        
        # Add statistics
        for provider in providers:
            doc = frappe.get_doc("Healthcare Provider", provider.name)
            provider["statistics"] = doc.get_statistics()
        
        return providers
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Search Providers Error")
        frappe.throw(str(e))


@frappe.whitelist()
def get_provider_schedule(provider_id):
    """Get provider's schedule"""
    try:
        if not frappe.db.exists("Healthcare Provider", provider_id):
            frappe.throw(_("Healthcare Provider not found"))
        
        schedules = frappe.get_all(
            "Provider Schedule",
            filters={"provider": provider_id},
            fields=[
                "name", "day_of_week", "start_time", "end_time",
                "is_available", "max_appointments"
            ],
            order_by="day_of_week"
        )
        
        return schedules
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Provider Schedule Error")
        frappe.throw(str(e))


@frappe.whitelist()
def update_availability(provider_id, is_available, availability_note=None):
    """Update provider availability status"""
    try:
        # Verify access - only the provider or admin can update
        provider = frappe.get_doc("Healthcare Provider", provider_id)
        
        current_user = frappe.session.user
        
        if current_user != provider.user and not frappe.has_permission(
            "Healthcare Provider", "write"
        ):
            frappe.throw(_("You don't have permission to update this provider"))
        
        provider.is_available = int(is_available)
        if availability_note:
            provider.availability_note = availability_note
        
        provider.save(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "status": "success",
            "message": _("Availability updated successfully")
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Update Availability Error")
        frappe.throw(str(e))


@frappe.whitelist()
def get_my_provider_profile():
    """Get logged-in user's provider profile"""
    try:
        user = frappe.session.user
        
        provider = frappe.db.get_value(
            "Healthcare Provider",
            {"user": user},
            "*",
            as_dict=True
        )
        
        if not provider:
            frappe.throw(_("No Healthcare Provider profile found for this user"))
        
        # Get statistics
        doc = frappe.get_doc("Healthcare Provider", provider.name)
        provider["statistics"] = doc.get_statistics()
        provider["availability_status"] = doc.get_availability_status()
        
        return provider
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get My Provider Profile Error")
        frappe.throw(str(e))


@frappe.whitelist()
def get_specialties():
    """Get list of unique specialties"""
    try:
        specialties = frappe.db.sql("""
            SELECT DISTINCT specialty
            FROM `tabHealthcare Provider`
            WHERE specialty IS NOT NULL
            AND specialty != ''
            AND is_available = 1
            ORDER BY specialty
        """, as_dict=True)
        
        return [s.specialty for s in specialties]
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Specialties Error")
        frappe.throw(str(e))


# Utility Functions

def get_provider_by_user(user):
    """Get provider record by user email"""
    return frappe.db.get_value(
        "Healthcare Provider",
        {"user": user},
        "name"
    )


def is_provider_available(provider_id):
    """Check if provider is currently available"""
    provider = frappe.get_doc("Healthcare Provider", provider_id)
    status = provider.get_availability_status()
    return status["available"]


def get_provider_consultation_fee(provider_id):
    """Get provider's consultation fee"""
    return frappe.db.get_value(
        "Healthcare Provider",
        provider_id,
        "consultation_fee"
    ) or 0.0


def validate_provider_access(provider_id):
    """Validate if current user has access to provider"""
    current_user = frappe.session.user
    
    # Admin has access to all
    if frappe.has_permission("Healthcare Provider", "write"):
        return True
    
    # Provider has access to their own record
    provider_user = frappe.db.get_value(
        "Healthcare Provider",
        provider_id,
        "user"
    )
    
    if current_user == provider_user:
        return True
    
    return False