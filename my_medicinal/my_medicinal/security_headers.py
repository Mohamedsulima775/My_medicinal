# -*- coding: utf-8 -*-
# Copyright (c) 2024, My Medicinal and contributors
# For license information, please see license.txt

import frappe
import os


def add_security_headers():
    """
    Add security headers to all HTTP responses
    Should be called in hooks.py as after_request hook
    """
    response = frappe.local.response

    if not response:
        return

    # Get headers dict
    headers = response.get("headers", {})

    # X-Content-Type-Options: Prevent MIME type sniffing
    headers["X-Content-Type-Options"] = "nosniff"

    # X-Frame-Options: Prevent clickjacking
    headers["X-Frame-Options"] = "SAMEORIGIN"

    # X-XSS-Protection: Enable browser XSS protection
    headers["X-XSS-Protection"] = "1; mode=block"

    # Strict-Transport-Security: Enforce HTTPS (only in production)
    if os.getenv("APP_ENV") == "production":
        headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # Content-Security-Policy: Prevent XSS and injection attacks
    csp_directives = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Frappe needs unsafe-inline/eval
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: https:",
        "font-src 'self' data:",
        "connect-src 'self'",
        "frame-ancestors 'self'",
        "base-uri 'self'",
        "form-action 'self'"
    ]
    headers["Content-Security-Policy"] = "; ".join(csp_directives)

    # Referrer-Policy: Control referrer information
    headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Permissions-Policy: Control browser features
    permissions = [
        "geolocation=()",
        "microphone=()",
        "camera=()",
        "payment=()",
        "usb=()",
        "magnetometer=()",
        "gyroscope=()",
        "accelerometer=()"
    ]
    headers["Permissions-Policy"] = ", ".join(permissions)

    # Update response headers
    response["headers"] = headers


def validate_content_type():
    """
    Validate Content-Type for POST/PUT/PATCH requests
    Prevents content type confusion attacks
    """
    request = frappe.local.request

    if not request:
        return

    # Only check for data-modifying methods
    if request.method not in ["POST", "PUT", "PATCH"]:
        return

    content_type = request.headers.get("Content-Type", "")

    # Allow these content types
    allowed_types = [
        "application/json",
        "application/x-www-form-urlencoded",
        "multipart/form-data"
    ]

    # Check if content type is allowed
    is_allowed = any(allowed in content_type for allowed in allowed_types)

    if not is_allowed and request.data:
        frappe.throw(
            "Invalid Content-Type. Allowed types: " + ", ".join(allowed_types),
            frappe.InvalidRequestError
        )


def sanitize_input():
    """
    Basic input sanitization for common attack vectors
    Note: Frappe already has built-in SQL injection protection
    """
    request = frappe.local.request

    if not request:
        return

    # Check for common attack patterns in URL
    dangerous_patterns = [
        "../",  # Path traversal
        "..\\",  # Path traversal (Windows)
        "<script",  # XSS
        "javascript:",  # XSS
        "onerror=",  # XSS
        "onload=",  # XSS
    ]

    request_path = request.path.lower()

    for pattern in dangerous_patterns:
        if pattern in request_path:
            frappe.throw(
                "Suspicious request pattern detected",
                frappe.SecurityException
            )


def check_https():
    """
    Enforce HTTPS in production
    """
    if os.getenv("APP_ENV") != "production":
        return

    request = frappe.local.request

    if not request:
        return

    # Check if request is HTTPS
    is_https = (
        request.is_secure or
        request.headers.get("X-Forwarded-Proto") == "https" or
        request.headers.get("X-Forwarded-SSL") == "on"
    )

    if not is_https:
        # Redirect to HTTPS
        https_url = request.url.replace("http://", "https://", 1)
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = https_url


class SecurityException(frappe.ValidationError):
    """Custom security exception"""
    pass


# Register custom exception
frappe.SecurityException = SecurityException
frappe.InvalidRequestError = type("InvalidRequestError", (frappe.ValidationError,), {})
