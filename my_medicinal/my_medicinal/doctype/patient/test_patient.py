# Copyright (c) 2025, mohammedsuliman and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime, add_days
from my_medicinal.my_medicinal.api.patient import (
    register,
    login,
    get_profile,
    update_profile,
    refresh_token,
    validate_api_key
)


class TestPatient(FrappeTestCase):
    """Test Patient API endpoints and authentication"""

    def setUp(self):
        """Set up test data before each test"""
        # Clean up any existing test data
        self.cleanup_test_data()

        # Test user data
        self.test_mobile = "0512345678"
        self.test_password = "TestPassword123!"
        self.test_name = "Test Patient"
        self.test_email = "testpatient@test.com"

    def tearDown(self):
        """Clean up after each test"""
        self.cleanup_test_data()

    def cleanup_test_data(self):
        """Remove test data from database"""
        try:
            # Delete test patient
            frappe.db.sql("DELETE FROM `tabpatient` WHERE mobile = %s", (self.test_mobile,))

            # Delete test user
            frappe.db.sql("DELETE FROM `tabUser` WHERE email = %s OR mobile_no = %s",
                         (self.test_email, self.test_mobile))

            # Delete test API keys
            frappe.db.sql("DELETE FROM `tabAPI Key` WHERE user LIKE %s", (f"%{self.test_mobile}%",))

            frappe.db.commit()
        except Exception:
            pass

    # ============================================
    # REGISTRATION TESTS
    # ============================================

    def test_register_success(self):
        """Test successful patient registration"""
        # Register new patient
        result = register(
            patient_name=self.test_name,
            mobile=self.test_mobile,
            password=self.test_password,
            email=self.test_email,
            date_of_birth="1990-01-01",
            gender="Male"
        )

        # Assertions
        self.assertTrue(result.get("success"))
        self.assertIn("token", result)
        self.assertIn("patient", result)
        self.assertEqual(result["patient"]["mobile"], self.test_mobile)

        # Verify token is 32 characters (secure length)
        self.assertGreaterEqual(len(result["token"]), 32)

        # Verify patient created in database
        patient_exists = frappe.db.exists("patient", {"mobile": self.test_mobile})
        self.assertTrue(patient_exists)

    def test_register_duplicate_mobile(self):
        """Test registration with duplicate mobile number"""
        # Register first time
        register(
            patient_name=self.test_name,
            mobile=self.test_mobile,
            password=self.test_password
        )

        # Try to register again with same mobile
        with self.assertRaises(Exception) as context:
            register(
                patient_name="Another Patient",
                mobile=self.test_mobile,
                password="AnotherPassword123!"
            )

        self.assertIn("already registered", str(context.exception).lower())

    def test_register_invalid_mobile(self):
        """Test registration with invalid mobile number"""
        with self.assertRaises(Exception) as context:
            register(
                patient_name=self.test_name,
                mobile="1234567890",  # Invalid format (doesn't start with 05)
                password=self.test_password
            )

        self.assertIn("invalid", str(context.exception).lower())

    # ============================================
    # LOGIN TESTS
    # ============================================

    def test_login_success(self):
        """Test successful login"""
        # Register first
        register(
            patient_name=self.test_name,
            mobile=self.test_mobile,
            password=self.test_password
        )

        # Login
        result = login(
            mobile=self.test_mobile,
            password=self.test_password
        )

        # Assertions
        self.assertTrue(result.get("success"))
        self.assertIn("token", result)
        self.assertIn("patient", result)
        self.assertEqual(result["patient"]["mobile"], self.test_mobile)

    def test_login_wrong_password(self):
        """Test login with wrong password"""
        # Register first
        register(
            patient_name=self.test_name,
            mobile=self.test_mobile,
            password=self.test_password
        )

        # Try login with wrong password
        with self.assertRaises(Exception) as context:
            login(
                mobile=self.test_mobile,
                password="WrongPassword123!"
            )

        self.assertIn("invalid", str(context.exception).lower())

    def test_login_nonexistent_user(self):
        """Test login with non-existent mobile number"""
        with self.assertRaises(Exception) as context:
            login(
                mobile="0599999999",
                password=self.test_password
            )

        self.assertIn("not registered", str(context.exception).lower())

    # ============================================
    # TOKEN VALIDATION TESTS
    # ============================================

    def test_token_validation_success(self):
        """Test valid token validation"""
        # Register and get token
        result = register(
            patient_name=self.test_name,
            mobile=self.test_mobile,
            password=self.test_password
        )
        token = result["token"]

        # Validate token
        user = validate_api_key(token)

        # Assertions
        self.assertIsNotNone(user)
        self.assertIn("@", user)  # Should return user email

    def test_token_validation_invalid(self):
        """Test invalid token validation"""
        # Try to validate non-existent token
        user = validate_api_key("invalid_token_12345")

        # Should return None for invalid token
        self.assertIsNone(user)

    def test_token_expiration(self):
        """Test token expiration after 90 days"""
        # Register and get token
        result = register(
            patient_name=self.test_name,
            mobile=self.test_mobile,
            password=self.test_password
        )
        token = result["token"]

        # Get API Key document
        api_key_doc = frappe.db.get_value(
            "API Key",
            {"api_key": token},
            ["name", "expires_at"],
            as_dict=True
        )

        # Verify expiration is set to ~90 days from now
        self.assertIsNotNone(api_key_doc["expires_at"])

        # Manually set expiration to past date
        frappe.db.set_value("API Key", api_key_doc["name"], "expires_at", add_days(now_datetime(), -1))
        frappe.db.commit()

        # Try to validate expired token
        user = validate_api_key(token)

        # Should return None for expired token
        self.assertIsNone(user)

        # Verify token is deactivated
        is_active = frappe.db.get_value("API Key", api_key_doc["name"], "is_active")
        self.assertEqual(is_active, 0)

    # ============================================
    # REFRESH TOKEN TESTS
    # ============================================

    def test_refresh_token_success(self):
        """Test token refresh"""
        # Register and get token
        result = register(
            patient_name=self.test_name,
            mobile=self.test_mobile,
            password=self.test_password
        )
        old_token = result["token"]

        # Refresh token
        refresh_result = refresh_token(old_token)

        # Assertions
        self.assertTrue(refresh_result.get("success"))
        self.assertIn("token", refresh_result)

        # New token should be different from old one
        new_token = refresh_result["token"]
        self.assertNotEqual(old_token, new_token)

        # Old token should be deactivated
        old_token_active = frappe.db.get_value(
            "API Key",
            {"api_key": old_token},
            "is_active"
        )
        self.assertEqual(old_token_active, 0)

    def test_refresh_token_invalid(self):
        """Test refresh with invalid token"""
        with self.assertRaises(Exception) as context:
            refresh_token("invalid_token_12345")

        self.assertIn("invalid", str(context.exception).lower())

    # ============================================
    # PROFILE TESTS
    # ============================================

    def test_get_profile(self):
        """Test getting patient profile"""
        # Register patient
        result = register(
            patient_name=self.test_name,
            mobile=self.test_mobile,
            password=self.test_password,
            email=self.test_email
        )
        patient_id = result["patient"]["patient_id"]

        # Set user session
        frappe.set_user(result["user"])

        # Get profile
        profile = get_profile(patient_id)

        # Assertions
        self.assertTrue(profile.get("success"))
        self.assertEqual(profile["patient"]["patient_name"], self.test_name)
        self.assertEqual(profile["patient"]["mobile"], self.test_mobile)

    def test_update_profile(self):
        """Test updating patient profile"""
        # Register patient
        result = register(
            patient_name=self.test_name,
            mobile=self.test_mobile,
            password=self.test_password
        )
        patient_id = result["patient"]["patient_id"]

        # Set user session
        frappe.set_user(result["user"])

        # Update profile
        updated_data = {
            "blood_group": "A+",
            "allergies": "Peanuts"
        }

        update_result = update_profile(patient_id, updated_data)

        # Assertions
        self.assertTrue(update_result.get("success"))
        self.assertEqual(update_result["patient"]["blood_group"], "A+")

    # ============================================
    # SECURITY TESTS
    # ============================================

    def test_password_not_stored_in_patient(self):
        """Test that password is NOT stored in Patient doctype"""
        # Register patient
        result = register(
            patient_name=self.test_name,
            mobile=self.test_mobile,
            password=self.test_password
        )

        # Get patient document
        patient = frappe.get_doc("patient", result["patient"]["patient_id"])

        # Verify password field doesn't exist or is empty
        self.assertFalse(hasattr(patient, "password") and patient.password)

    def test_api_key_length(self):
        """Test that API key is at least 32 characters"""
        # Register patient
        result = register(
            patient_name=self.test_name,
            mobile=self.test_mobile,
            password=self.test_password
        )

        # Check token length
        token = result["token"]
        self.assertGreaterEqual(len(token), 32)


# Run tests
if __name__ == "__main__":
    import unittest
    unittest.main()
