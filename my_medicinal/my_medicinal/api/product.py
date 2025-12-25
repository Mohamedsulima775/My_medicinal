# -*- coding: utf-8 -*-
# Copyright (c) 2024, My Medicinal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint

# ============================================
# PRODUCT APIs (Guest Allowed)
# ============================================

@frappe.whitelist(allow_guest=True)
def get_products(category=None, limit=20, offset=0):
    """Get products list"""
    try:
        filters = {"is_active": 1}
        if category:
            filters["category"] = category
        
        products = frappe.get_all(
            "medication_item",
            filters=filters,
            fields=[
                "name", "item_name", "scientific_name",
                "category", "standard_rate", "stock_quantity",
                "requires_prescription"
            ],
            limit=cint(limit),
            start=cint(offset),
            order_by="item_name"
        )
        
        return products
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Products Error")
        frappe.throw(_("Failed to get products: {0}").format(str(e)))


@frappe.whitelist(allow_guest=True)
def search_products(query, limit=20):
    """Search products"""
    try:
        products = frappe.db.sql("""
            SELECT 
                name, item_name, scientific_name,
                category, standard_rate, stock_quantity
            FROM `tabmedication_item`
            WHERE is_active = 1
            AND (
                item_name LIKE %(query)s
                OR scientific_name LIKE %(query)s
            )
            ORDER BY item_name
            LIMIT %(limit)s
        """, {
            "query": f"%{query}%",
            "limit": cint(limit)
        }, as_dict=True)
        
        return products
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Search Products Error")
        frappe.throw(_("Failed to search: {0}").format(str(e)))


@frappe.whitelist(allow_guest=True)
def get_categories():
    """Get all categories"""
    try:
        categories = frappe.get_all(
            "medication_category",
            fields=["name", "category_name", "description", "icon", "color"],
            order_by="category_name"
        )
        
        return categories
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Categories Error")
        frappe.throw(_("Failed to get categories: {0}").format(str(e)))