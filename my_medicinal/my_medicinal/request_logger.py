# -*- coding: utf-8 -*-
# Copyright (c) 2024, My Medicinal and contributors
# For license information, please see license.txt

import frappe
import json
import time
from frappe import _
from datetime import datetime


class RequestLogger:
    """
    Middleware for logging API requests and responses
    Helps with debugging, monitoring, and audit trails
    """

    @staticmethod
    def log_request(request_data=None):
        """
        Log incoming API request

        Args:
            request_data: Optional custom request data

        Returns:
            Log ID for correlation with response
        """
        try:
            # Get request details
            request = frappe.local.request

            # Extract relevant data
            log_data = {
                "doctype": "API Request Log",
                "timestamp": frappe.utils.now_datetime(),
                "method": request.method,
                "endpoint": request.path,
                "user": frappe.session.user if frappe.session else "Guest",
                "ip_address": frappe.local.request_ip or "Unknown",
                "user_agent": request.headers.get("User-Agent", "Unknown"),
                "request_id": frappe.generate_hash(length=16)
            }

            # Add request body for POST/PUT/PATCH
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    # Get form data or JSON
                    if request.form:
                        body = dict(request.form)
                        # Redact sensitive fields
                        body = RequestLogger._redact_sensitive_data(body)
                    elif request.json:
                        body = request.json
                        body = RequestLogger._redact_sensitive_data(body)
                    else:
                        body = {}

                    log_data["request_body"] = json.dumps(body, default=str)
                except Exception:
                    log_data["request_body"] = "Unable to parse"

            # Add query parameters
            if request.args:
                log_data["query_params"] = json.dumps(dict(request.args), default=str)

            # Create log document
            log_doc = frappe.get_doc(log_data)
            log_doc.insert(ignore_permissions=True)
            frappe.db.commit()

            return log_doc.name

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Request Logging Error")
            return None

    @staticmethod
    def log_response(request_log_id, response_data, status_code=200, execution_time=0):
        """
        Log API response

        Args:
            request_log_id: ID from log_request
            response_data: Response data
            status_code: HTTP status code
            execution_time: Request execution time in seconds
        """
        try:
            if not request_log_id:
                return

            # Update request log with response data
            frappe.db.set_value("API Request Log", request_log_id, {
                "status_code": status_code,
                "execution_time": execution_time,
                "response_body": json.dumps(response_data, default=str)[:5000],  # Limit size
                "completed_at": frappe.utils.now_datetime()
            })
            frappe.db.commit()

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Response Logging Error")

    @staticmethod
    def log_error(request_log_id, error_message, error_type="Exception"):
        """
        Log API error

        Args:
            request_log_id: ID from log_request
            error_message: Error message
            error_type: Type of error
        """
        try:
            if not request_log_id:
                return

            # Update request log with error data
            frappe.db.set_value("API Request Log", request_log_id, {
                "status_code": 500,
                "error_message": str(error_message)[:1000],
                "error_type": error_type,
                "completed_at": frappe.utils.now_datetime()
            })
            frappe.db.commit()

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Error Logging Error")

    @staticmethod
    def _redact_sensitive_data(data):
        """
        Redact sensitive fields from request/response data

        Args:
            data: Dictionary to redact

        Returns:
            Redacted dictionary
        """
        sensitive_fields = [
            "password", "api_key", "api_secret", "token",
            "secret", "auth", "authorization", "access_token",
            "refresh_token", "credit_card", "cvv", "pin"
        ]

        if isinstance(data, dict):
            redacted = {}
            for key, value in data.items():
                # Check if key is sensitive
                if any(sensitive in key.lower() for sensitive in sensitive_fields):
                    redacted[key] = "***REDACTED***"
                elif isinstance(value, dict):
                    redacted[key] = RequestLogger._redact_sensitive_data(value)
                elif isinstance(value, list):
                    redacted[key] = [
                        RequestLogger._redact_sensitive_data(item) if isinstance(item, dict) else item
                        for item in value
                    ]
                else:
                    redacted[key] = value
            return redacted
        else:
            return data

    @staticmethod
    def get_request_stats(hours=24):
        """
        Get API request statistics

        Args:
            hours: Number of hours to analyze

        Returns:
            Statistics dictionary
        """
        try:
            from frappe.utils import add_to_date, now_datetime

            start_time = add_to_date(now_datetime(), hours=-hours)

            # Total requests
            total_requests = frappe.db.count(
                "API Request Log",
                {"timestamp": [">=", start_time]}
            )

            # Requests by status code
            status_breakdown = frappe.db.sql("""
                SELECT status_code, COUNT(*) as count
                FROM `tabAPI Request Log`
                WHERE timestamp >= %s
                GROUP BY status_code
                ORDER BY count DESC
            """, (start_time,), as_dict=True)

            # Top endpoints
            top_endpoints = frappe.db.sql("""
                SELECT endpoint, COUNT(*) as count, AVG(execution_time) as avg_time
                FROM `tabAPI Request Log`
                WHERE timestamp >= %s
                GROUP BY endpoint
                ORDER BY count DESC
                LIMIT 10
            """, (start_time,), as_dict=True)

            # Error rate
            error_count = frappe.db.count(
                "API Request Log",
                {
                    "timestamp": [">=", start_time],
                    "status_code": [">=", 400]
                }
            )
            error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0

            # Average response time
            avg_response = frappe.db.sql("""
                SELECT AVG(execution_time) as avg_time
                FROM `tabAPI Request Log`
                WHERE timestamp >= %s AND execution_time > 0
            """, (start_time,), as_dict=True)

            return {
                "total_requests": total_requests,
                "error_count": error_count,
                "error_rate": round(error_rate, 2),
                "avg_response_time": round(avg_response[0].avg_time, 3) if avg_response and avg_response[0].avg_time else 0,
                "status_breakdown": status_breakdown,
                "top_endpoints": top_endpoints,
                "period_hours": hours
            }

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Request Stats Error")
            return {}


def log_api_request():
    """
    Decorator to log API requests and responses

    Usage:
        @frappe.whitelist()
        @log_api_request()
        def my_api_function():
            ...
    """
    def decorator(fn):
        def wrapper(*args, **kwargs):
            # Start timer
            start_time = time.time()

            # Log request
            log_id = RequestLogger.log_request()

            try:
                # Execute function
                result = fn(*args, **kwargs)

                # Calculate execution time
                execution_time = time.time() - start_time

                # Log response
                RequestLogger.log_response(
                    log_id,
                    result,
                    status_code=200,
                    execution_time=execution_time
                )

                return result

            except Exception as e:
                # Calculate execution time
                execution_time = time.time() - start_time

                # Log error
                RequestLogger.log_error(
                    log_id,
                    str(e),
                    error_type=type(e).__name__
                )

                # Re-raise exception
                raise

        return wrapper
    return decorator


@frappe.whitelist()
def get_api_stats(hours=24):
    """
    Get API statistics (admin only)

    Args:
        hours: Number of hours to analyze

    Returns:
        Statistics dictionary
    """
    # Check if user is System Manager
    if "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not authorized"))

    return RequestLogger.get_request_stats(int(hours))


@frappe.whitelist()
def cleanup_old_logs(days=30):
    """
    Clean up old API request logs (admin only)

    Args:
        days: Delete logs older than this many days

    Returns:
        Number of deleted logs
    """
    # Check if user is System Manager
    if "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not authorized"))

    from frappe.utils import add_to_date, now_datetime

    cutoff_date = add_to_date(now_datetime(), days=-int(days))

    # Delete old logs
    deleted = frappe.db.sql("""
        DELETE FROM `tabAPI Request Log`
        WHERE timestamp < %s
    """, (cutoff_date,))

    frappe.db.commit()

    return {"deleted_count": deleted}
