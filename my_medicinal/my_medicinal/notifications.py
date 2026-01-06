# -*- coding: utf-8 -*-
# Copyright (c) 2024, My Medicinal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json
import os

# ============================================
# NOTIFICATION CONFIGURATION (المطلوب من Frappe)
# ============================================

def get_notification_config():
    """
    Notification configuration for Frappe Desk.
    This function is called by Frappe to get notification settings.
    """
    return {
        "for_doctype": {
            # Medical Consultation notifications
            "Medical Consultation": {
                "status": "Open",
                "priority": ["High", "Urgent"]
            },
            
            # Patient Order notifications
            "Patient Order": {
                "status": ["Pending", "Confirmed"],
            },
            
            # Medication Reminder notifications
            "Medication Reminder": {
                "status": "Pending",
            },
            
            # Notification Log
            "Notification Log": {
                "read": 0,
            }
        },
        
        # Module-wise notifications
        "for_module": {
            "my_medicinal": "green"
        },
        
        # Open count for d
        "open_count_doctype": {
            "Medical Consultation": "status",
            "Patient Order": "status"
        }
    }
# ============================================
# FIREBASE CLOUD MESSAGING (FCM)
# ============================================

class NotificationManager:
    """Manage all types of notifications"""
    
    def __init__(self):
        self.fcm_handler = FCMHandler()
    
    def send_notification(self, user_id, title, body, data=None, channels=None):
        """
        Send notification through multiple channels
        
        Args:
            user_id: User email
            title: Notification title
            body: Notification body
            data: Additional data dict
            channels: List of channels ['push', 'sms', 'email']
        """
        if channels is None:
            channels = ['push']  # Default to push only
        
        results = {}
        
        # 1. Push Notification (FCM)
        if 'push' in channels:
            results['push'] = self.fcm_handler.send_push(user_id, title, body, data)
        
        # 2. SMS (TODO)
        if 'sms' in channels:
            results['sms'] = {"success": False, "message": "SMS not implemented yet"}
        
        # 3. Email (TODO)
        if 'email' in channels:
            results['email'] = {"success": False, "message": "Email not implemented yet"}
        
        # Log notification
        self.log_notification(user_id, title, body, results)
        
        return results
    
    def log_notification(self, user_id, title, body, results):
        """Log notification in database"""
        try:
            notification = frappe.get_doc({
                "doctype": "Notification Log",
                "subject": title,
                "for_user": user_id,
                "type": "Alert",
                "email_content": f"<p>{body}</p>",
                "read": 0
            })
            notification.insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Log Notification Error")


class FCMHandler:
    """Handle Firebase Cloud Messaging"""
    
    def __init__(self):
        self.app = None
        self.credentials_path = self.get_credentials_path()
        self.initialize_firebase()
    
    def get_credentials_path(self):
        """Get Firebase credentials file path"""
        app_path = frappe.get_app_path("my_medicinal")
        return os.path.join(app_path, "..", "firebase_credentials.json")
    
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if credentials file exists
            if not os.path.exists(self.credentials_path):
                frappe.log_error(
                    f"Firebase credentials not found at: {self.credentials_path}",
                    "Firebase Initialization Error"
                )
                print(f"❌ Firebase credentials not found at: {self.credentials_path}")
                return
            
            # Import firebase_admin
            try:
                import firebase_admin
                from firebase_admin import credentials, messaging
                
                # Initialize app if not already done
                if not firebase_admin._apps:
                    cred = credentials.Certificate(self.credentials_path)
                    self.app = firebase_admin.initialize_app(cred)
                    print("✅ Firebase initialized successfully")
                else:
                    self.app = firebase_admin.get_app()
                    print("✅ Firebase already initialized")
                
            except ImportError:
                frappe.log_error(
                    "firebase-admin not installed. Run: pip install firebase-admin --break-system-packages",
                    "Firebase Import Error"
                )
                print("❌ firebase-admin not installed")
                
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Firebase Initialization Error")
            print(f"❌ Firebase initialization error: {str(e)}")
    
    def send_push(self, user_id, title, body, data=None):
        """
        Send push notification via FCM
        
        Args:
            user_id: User email
            title: Notification title
            body: Notification message
            data: Additional data dict
        
        Returns:
            dict with success status and message
        """
        try:
            # Check if Firebase is initialized
            if not self.app:
                return {
                    "success": False,
                    "message": "Firebase not initialized"
                }
            
            # Get FCM token for user
            fcm_token = self.get_user_fcm_token(user_id)
            
            if not fcm_token:
                return {
                    "success": False,
                    "message": "No FCM token found for user"
                }
            
            # Import messaging
            from firebase_admin import messaging
            
            # Prepare notification
            notification = messaging.Notification(
                title=title,
                body=body
            )
            
            # Prepare data
            if data is None:
                data = {}
            
            # Create message
            message = messaging.Message(
                notification=notification,
                data={str(k): str(v) for k, v in data.items()},
                token=fcm_token
            )
            
            # Send message
            response = messaging.send(message)
            
            print(f"✅ Push notification sent: {response}")
            
            return {
                "success": True,
                "message": "Notification sent",
                "response": response
            }
            
        except Exception as e:
            error_msg = str(e)
            frappe.log_error(frappe.get_traceback(), "FCM Send Error")
            print(f"❌ FCM send error: {error_msg}")
            
            return {
                "success": False,
                "message": error_msg
            }
    
    def get_user_fcm_token(self, user_id):
        """Get FCM token for a user from API Key table"""
        try:
            # Get latest active token
            token_data = frappe.db.get_value(
                "API Key",
                {
                    "user": user_id,
                    "enabled": 1
                },
                ["name"],
                order_by="modified desc",
                as_dict=True
            )
            
            if token_data:
                # Get the API Key doc to check for custom fields
                api_key_doc = frappe.get_doc("API Key", token_data.name)
                
                # Try to get fcm_token if field exists
                if hasattr(api_key_doc, 'fcm_token'):
                    return api_key_doc.fcm_token
            
            return None
            
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Get FCM Token Error")
            return None


# ============================================
# API ENDPOINTS
# ============================================

@frappe.whitelist()
def register_device(fcm_token, device_type="Android", device_id=None):
    """
    Register device FCM token
    
    Args:
        fcm_token: Firebase Cloud Messaging token
        device_type: Android/iOS
        device_id: Unique device identifier
    """
    try:
        user_id = frappe.session.user
        
        # Check if API Key exists for this user
        existing = frappe.db.get_value(
            "API Key",
            {"user": user_id},
            "name"
        )
        
        if existing:
            # Update existing
            doc = frappe.get_doc("API Key", existing)
            
            # Set fcm_token if field exists
            if hasattr(doc, 'fcm_token'):
                doc.fcm_token = fcm_token
            if hasattr(doc, 'device_type'):
                doc.device_type = device_type
            if hasattr(doc, 'device_id') and device_id:
                doc.device_id = device_id
                
            doc.save(ignore_permissions=True)
        else:
            # Create new
            doc = frappe.get_doc({
                "doctype": "API Key",
                "user": user_id,
                "enabled": 1
            })
            
            doc.insert(ignore_permissions=True)
            
            # Update with FCM fields after insert
            if hasattr(doc, 'fcm_token'):
                doc.fcm_token = fcm_token
            if hasattr(doc, 'device_type'):
                doc.device_type = device_type
            if hasattr(doc, 'device_id') and device_id:
                doc.device_id = device_id
                
            doc.save(ignore_permissions=True)
        
        frappe.db.commit()
        
        return {
            "success": True,
            "message": "Device registered successfully"
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Register Device Error")
        frappe.throw(_("Failed to register device: {0}").format(str(e)))


@frappe.whitelist()
def send_test_notification(user_id=None, title="Test Notification", body="This is a test notification"):
    """Send test notification (for testing)"""
    try:
        if not user_id:
            user_id = frappe.session.user
        
        manager = NotificationManager()
        result = manager.send_notification(
            user_id,
            title,
            body,
            data={"type": "test"},
            channels=['push']
        )
        
        return result
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Test Notification Error")
        frappe.throw(_("Failed to send test: {0}").format(str(e)))


@frappe.whitelist()
def get_my_notifications(limit=20):
    """Get user notifications"""
    try:
        user_id = frappe.session.user
        
        notifications = frappe.get_all(
            "Notification Log",
            filters={"for_user": user_id},
            fields=[
                "name", "subject", "email_content", "type",
                "read", "creation"
            ],
            limit=limit,
            order_by="creation desc"
        )
        
        return notifications
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Notifications Error")
        frappe.throw(_("Failed to get notifications: {0}").format(str(e)))


@frappe.whitelist()
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        frappe.db.set_value(
            "Notification Log",
            notification_id,
            "read",
            1
        )
        
        frappe.db.commit()
        
        return {"success": True}
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Mark Read Error")
        frappe.throw(_("Failed to mark as read: {0}").format(str(e)))


# ============================================
# HELPER FUNCTION (for tasks.py)
# ============================================

def send_medication_notification_fcm(patient_id, medication_name, dosage, time):
    """Helper function to send medication reminder via FCM"""
    try:
        patient = frappe.get_doc("patient", patient_id)
        
        manager = NotificationManager()
        result = manager.send_notification(
            user_id=patient.user,
            title="⏰ موعد الدواء",
            body=f"{medication_name} - {dosage}\nالموعد: {time}",
            data={
                "type": "medication_reminder",
                "patient_id": patient_id,
                "medication_name": medication_name,
                "time": str(time)
            },
            channels=['push']
        )
        
        return result
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Send Medication FCM Error")
        return {"success": False, "message": str(e)}


# ============================================
# INITIALIZATION
# ============================================

# Create global instance
notification_manager = NotificationManager()
