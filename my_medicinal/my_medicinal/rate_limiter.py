# -*- coding: utf-8 -*-
# Copyright (c) 2024, My Medicinal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from functools import wraps
import time


def rate_limit(limit=100, window=60, key_func=None):
    """
    Rate limiting decorator for API endpoints

    Args:
        limit: Maximum number of requests allowed
        window: Time window in seconds
        key_func: Function to generate cache key (default: uses IP + endpoint)

    Usage:
        @frappe.whitelist(allow_guest=True)
        @rate_limit(limit=5, window=60)
        def login(mobile, password):
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: IP + endpoint name
                ip_address = frappe.local.request_ip or "unknown"
                endpoint = fn.__name__
                cache_key = f"rate_limit:{ip_address}:{endpoint}"

            # Get current request count from cache
            current_count = frappe.cache().get(cache_key) or 0

            # Check if limit exceeded
            if current_count >= limit:
                frappe.throw(
                    _("Rate limit exceeded. Please try again in {0} seconds.").format(window),
                    frappe.RateLimitExceededError
                )

            # Increment counter
            if current_count == 0:
                # First request - set with expiry
                frappe.cache().setex(cache_key, window, 1)
            else:
                # Increment existing counter
                frappe.cache().incr(cache_key)

            # Execute the original function
            return fn(*args, **kwargs)

        return wrapper
    return decorator


def get_ip_key(*args, **kwargs):
    """
    Generate cache key based on IP address only
    Useful for guest endpoints
    """
    ip_address = frappe.local.request_ip or "unknown"
    return f"rate_limit:{ip_address}:global"


def get_user_key(*args, **kwargs):
    """
    Generate cache key based on user
    Useful for authenticated endpoints
    """
    user = frappe.session.user
    return f"rate_limit:{user}:global"


def get_mobile_key(mobile=None, *args, **kwargs):
    """
    Generate cache key based on mobile number
    Useful for login/registration endpoints
    """
    if not mobile and len(args) > 0:
        mobile = args[0]

    mobile = mobile or "unknown"
    return f"rate_limit:mobile:{mobile}"


# Custom exception for rate limiting
class RateLimitExceededError(frappe.ValidationError):
    """Exception raised when rate limit is exceeded"""
    pass


# Register custom exception
frappe.RateLimitExceededError = RateLimitExceededError


def clear_rate_limit(key):
    """
    Clear rate limit for a specific key
    Useful for admin operations

    Args:
        key: Cache key to clear
    """
    frappe.cache().delete(key)


def get_rate_limit_status(key):
    """
    Get current rate limit status for a key

    Args:
        key: Cache key to check

    Returns:
        dict with current count and TTL
    """
    count = frappe.cache().get(key) or 0
    ttl = frappe.cache().ttl(key) or 0

    return {
        "current_requests": count,
        "time_remaining": ttl,
        "status": "limited" if count > 0 else "available"
    }
