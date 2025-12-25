# -*- coding: utf-8 -*-
# Copyright (c) 2024, My Medicinal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json

# ============================================
# ORDER APIs
# ============================================

@frappe.whitelist()
def create_order(patient_id, items, delivery_address, payment_method="Cash on Delivery"):
    """Create new order"""
    try:
        if isinstance(items, str):
            items = json.loads(items)
        
        # Create order
        order = frappe.get_doc({
            "doctype": "patient_order",
            "patient": patient_id,
            "delivery_address": delivery_address,
            "payment_method": payment_method,
            "status": "Pending"
        })
        
        total = 0
        for item in items:
            # Get product info
            product = frappe.get_doc("medication_item", item["item_code"])
            
            qty = item["quantity"]
            rate = product.standard_rate
            amount = qty * rate
            total += amount
            
            order.append("items", {
                "item_code": product.name,
                "item_name": product.item_name,
                "quantity": qty,
                "rate": rate,
                "amount": amount
            })
        
        order.total_amount = total
        order.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": True,
            "order_id": order.name,
            "total_amount": total,
            "status": order.status
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Order Error")
        frappe.throw(_("Failed to create order: {0}").format(str(e)))


@frappe.whitelist()
def get_my_orders(patient_id, limit=20):
    """Get patient orders"""
    try:
        orders = frappe.get_all(
            "patient_order",
            filters={"patient": patient_id},
            fields=[
                "name", "creation", "total_amount",
                "status", "delivery_address"
            ],
            limit=limit,
            order_by="creation desc"
        )
        
        return orders
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Orders Error")
        frappe.throw(_("Failed to get orders: {0}").format(str(e)))