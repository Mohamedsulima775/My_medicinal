#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Flutter-Frappe connection
اختبار الاتصال بين Flutter و Frappe
"""

import requests
import json
import sys

# ========================================
# Configuration - قم بتحديث هذه القيم
# ========================================

# استبدل بـ IP Address الفعلي لخادم Frappe
FRAPPE_URL = "http://192.168.1.100:8000"

# بيانات اختبار
TEST_MOBILE = "0501234567"
TEST_PASSWORD = "test123"
TEST_PATIENT_NAME = "مريض تجريبي"

# ========================================
# Colors for terminal output
# ========================================

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")

# ========================================
# Test Functions
# ========================================

def test_ping():
    """Test basic connectivity"""
    print_info("Testing basic connectivity...")

    try:
        response = requests.get(
            f"{FRAPPE_URL}/api/method/ping",
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("message") == "pong":
                print_success("Server is reachable")
                return True
            else:
                print_error(f"Unexpected response: {data}")
                return False
        else:
            print_error(f"HTTP {response.status_code}: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server. Check:")
        print_error("  1. Server IP address is correct")
        print_error("  2. Server is running (bench start)")
        print_error("  3. Firewall allows port 8000")
        print_error("  4. Both devices are on same network")
        return False

    except requests.exceptions.Timeout:
        print_error("Connection timeout")
        return False

    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_cors():
    """Test CORS configuration"""
    print_info("Testing CORS configuration...")

    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Content-Type': 'application/json'
        }

        response = requests.options(
            f"{FRAPPE_URL}/api/method/ping",
            headers=headers,
            timeout=10
        )

        cors_header = response.headers.get('Access-Control-Allow-Origin')

        if cors_header:
            print_success(f"CORS is configured: {cors_header}")
            return True
        else:
            print_warning("CORS headers not found. You may need to update CORS settings.")
            print_info("Add to .env: ALLOWED_CORS_ORIGINS=*")
            return False

    except Exception as e:
        print_error(f"CORS test failed: {e}")
        return False

def test_register():
    """Test patient registration"""
    print_info("Testing patient registration...")

    try:
        data = {
            "patient_name": TEST_PATIENT_NAME,
            "mobile": TEST_MOBILE,
            "password": TEST_PASSWORD,
            "email": f"{TEST_MOBILE}@test.local"
        }

        response = requests.post(
            f"{FRAPPE_URL}/api/method/my_medicinal.my_medicinal.api.patient.register",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()

            if result.get("message", {}).get("success"):
                print_success("Registration successful")
                token = result["message"].get("token")
                print_info(f"Token: {token[:20]}...")
                return token
            else:
                error_msg = result.get("message", {}).get("message", "Unknown error")

                if "already registered" in error_msg:
                    print_warning("Mobile already registered (this is OK for testing)")
                    return None
                else:
                    print_error(f"Registration failed: {error_msg}")
                    return None
        else:
            print_error(f"HTTP {response.status_code}: {response.text}")
            return None

    except Exception as e:
        print_error(f"Registration test failed: {e}")
        return None

def test_login():
    """Test patient login"""
    print_info("Testing patient login...")

    try:
        data = {
            "mobile": TEST_MOBILE,
            "password": TEST_PASSWORD
        }

        response = requests.post(
            f"{FRAPPE_URL}/api/method/my_medicinal.my_medicinal.api.patient.login",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()

            if result.get("message", {}).get("success"):
                print_success("Login successful")
                token = result["message"].get("token")
                patient = result["message"].get("patient", {})
                print_info(f"Patient: {patient.get('patient_name')}")
                print_info(f"Token: {token[:20]}...")
                return token
            else:
                error_msg = result.get("message", {}).get("message", "Unknown error")
                print_error(f"Login failed: {error_msg}")
                return None
        else:
            print_error(f"HTTP {response.status_code}: {response.text}")
            return None

    except Exception as e:
        print_error(f"Login test failed: {e}")
        return None

def test_authenticated_request(token):
    """Test authenticated API request"""
    print_info("Testing authenticated request (get profile)...")

    if not token:
        print_warning("Skipping - no auth token available")
        return False

    try:
        headers = {
            'Authorization': f'token {token}',
            'Content-Type': 'application/json'
        }

        response = requests.get(
            f"{FRAPPE_URL}/api/method/my_medicinal.my_medicinal.api.patient.get_profile",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()

            if result.get("message", {}).get("success"):
                print_success("Authenticated request successful")
                patient = result["message"].get("patient", {})
                print_info(f"Patient ID: {patient.get('patient_id')}")
                print_info(f"Name: {patient.get('patient_name')}")
                return True
            else:
                print_error("Authenticated request failed")
                return False
        else:
            print_error(f"HTTP {response.status_code}: {response.text}")
            return False

    except Exception as e:
        print_error(f"Authenticated request test failed: {e}")
        return False

# ========================================
# Main Test Runner
# ========================================

def main():
    print("\n" + "="*60)
    print("  Frappe-Flutter Connection Test")
    print("  اختبار اتصال Frappe-Flutter")
    print("="*60 + "\n")

    print_info(f"Target server: {FRAPPE_URL}\n")

    # Test 1: Ping
    print("\n[1/5] Basic Connectivity Test")
    print("-" * 40)
    if not test_ping():
        print_error("\n✗ Basic connectivity failed. Fix this first!")
        sys.exit(1)

    # Test 2: CORS
    print("\n[2/5] CORS Configuration Test")
    print("-" * 40)
    test_cors()

    # Test 3: Registration
    print("\n[3/5] Patient Registration Test")
    print("-" * 40)
    token = test_register()

    # Test 4: Login
    print("\n[4/5] Patient Login Test")
    print("-" * 40)
    login_token = test_login()

    if not token and login_token:
        token = login_token

    # Test 5: Authenticated Request
    print("\n[5/5] Authenticated Request Test")
    print("-" * 40)
    test_authenticated_request(token)

    # Summary
    print("\n" + "="*60)
    print("  Test Summary")
    print("="*60)
    print_info("Basic connectivity: ✓")
    print_info("API endpoints: ✓" if token else "API endpoints: Check logs")
    print_info("Authentication: ✓" if token else "Authentication: Check logs")

    print("\n" + Colors.GREEN + "Connection test completed!" + Colors.RESET)
    print("\nNext steps:")
    print("  1. Update ApiConfig in Flutter with this URL:")
    print(f"     {Colors.YELLOW}{FRAPPE_URL}{Colors.RESET}")
    print("  2. Test login from Flutter app")
    print("  3. Check Frappe logs for any errors:")
    print(f"     {Colors.BLUE}tail -f sites/[site-name]/logs/web.error.log{Colors.RESET}")
    print()

if __name__ == "__main__":
    main()
