# -*- coding: utf-8 -*-
# Copyright (c) 2024, My Medicinal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json

# ============================================
# PROVIDER APIs
# ============================================

@frappe.whitelist(allow_guest=True)
def get_available_providers(provider_type=None, specialization=None, limit=20):
    """Get available healthcare providers"""
    try:
        filters = {"status": "Active", "is_available": 1}
        
        if provider_type:
            filters["provider_type"] = provider_type
        
        if specialization:
            filters["specialization"] = specialization
        
        providers = frappe.get_all(
            "healthcare_provider",
            filters=filters,
            fields=[
                "name", "full_name", "provider_type",
                "specialization", "experience_years",
                "consultation_fee", "rating"
            ],
            limit=limit,
            order_by="rating desc"
        )
        
        return providers
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Providers Error")
        frappe.throw(_("Failed to get providers: {0}").format(str(e)))


@frappe.whitelist(allow_guest=True)
def get_specializations(provider_type="Doctor"):
    """Get list of specializations"""
    try:
        specializations = frappe.db.sql("""
            SELECT DISTINCT specialization
            FROM `tabhealthcare_provider`
            WHERE provider_type = %(provider_type)s
            AND status = 'Active'
            ORDER BY specialization
        """, {"provider_type": provider_type}, as_list=True)
        
        return [s[0] for s in specializations if s[0]]
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Specializations Error")
        frappe.throw(_("Failed to get specializations: {0}").format(str(e)))