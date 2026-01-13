# -*- coding: utf-8 -*-
# Copyright (c) 2024, My Medicinal and contributors
# Real-time Chat API for Medical Consultations

import frappe
from frappe import _
from frappe.utils import now_datetime, cint, get_datetime
from frappe.realtime import publish_realtime
import json

# ============================================
# REAL-TIME CHAT APIs
# ============================================

@frappe.whitelist()
def send_chat_message(
    consultation_id,
    message,
    sender_type,
    message_type="text",
    attachment=None,
    attachment_name=None,
    reply_to_idx=None
):
    """
    Send a chat message in a consultation with real-time updates

    Args:
        consultation_id: Medical Consultation ID
        message: Message content
        sender_type: "patient" or "provider"
        message_type: "text", "image", "file", "audio", "video", "system"
        attachment: File attachment URL (optional)
        attachment_name: Original filename (optional)
        reply_to_idx: Index of message being replied to (optional)

    Returns:
        Message details with real-time notification
    """
    try:
        # Validate consultation exists
        if not frappe.db.exists("Medical Consultation", consultation_id):
            frappe.throw(_("Consultation not found"))

        consultation = frappe.get_doc("Medical Consultation", consultation_id)

        # Validate sender has permission
        _validate_sender_permission(consultation, sender_type)

        # Get sender info
        sender_id, sender_name = _get_sender_info(consultation, sender_type)

        # Build reply preview if replying
        reply_preview = None
        if reply_to_idx and cint(reply_to_idx) > 0:
            reply_preview = _get_reply_preview(consultation, cint(reply_to_idx))

        # Get attachment size if provided
        attachment_size = 0
        if attachment:
            attachment_size = _get_file_size(attachment)

        # Create message
        msg_data = {
            "sender_type": sender_type,
            "sender_id": sender_id,
            "sender_name": sender_name,
            "message_type": message_type,
            "message": message,
            "timestamp": now_datetime(),
            "attachment": attachment,
            "attachment_name": attachment_name,
            "attachment_size": attachment_size,
            "is_read": 0,
            "is_delivered": 1,
            "delivered_at": now_datetime(),
            "reply_to_idx": reply_to_idx,
            "reply_preview": reply_preview
        }

        consultation.append("messages", msg_data)

        # Update consultation status
        if consultation.status == "Pending":
            consultation.status = "In Progress"

        # Update chat metadata
        consultation.last_message_at = now_datetime()
        consultation.last_message_preview = (message[:100] + "...") if len(message) > 100 else message

        # Update unread counts
        if sender_type == "patient":
            consultation.unread_count_provider = cint(consultation.unread_count_provider) + 1
        else:
            consultation.unread_count_patient = cint(consultation.unread_count_patient) + 1

        consultation.save(ignore_permissions=True)
        frappe.db.commit()

        # Get message index
        msg_idx = len(consultation.messages)

        # Prepare response data
        response_data = {
            "idx": msg_idx,
            "sender_type": sender_type,
            "sender_id": sender_id,
            "sender_name": sender_name,
            "message_type": message_type,
            "message": message,
            "timestamp": str(now_datetime()),
            "attachment": attachment,
            "attachment_name": attachment_name,
            "is_read": False,
            "is_delivered": True,
            "reply_to_idx": reply_to_idx,
            "reply_preview": reply_preview
        }

        # Send real-time notification
        _publish_chat_event(consultation_id, "new_message", response_data)

        # Send push notification to recipient
        _send_message_notification(consultation, sender_type, message, message_type)

        return {
            "success": True,
            "message": response_data
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Send Chat Message Error")
        frappe.throw(_("Failed to send message: {0}").format(str(e)))


@frappe.whitelist()
def get_chat_messages(consultation_id, limit=50, offset=0, after_idx=None):
    """
    Get chat messages with pagination

    Args:
        consultation_id: Medical Consultation ID
        limit: Number of messages to return (default 50)
        offset: Pagination offset
        after_idx: Get messages after this index (for real-time sync)

    Returns:
        List of messages with metadata
    """
    try:
        if not frappe.db.exists("Medical Consultation", consultation_id):
            frappe.throw(_("Consultation not found"))

        consultation = frappe.get_doc("Medical Consultation", consultation_id)

        messages = []
        for idx, msg in enumerate(consultation.messages, 1):
            # Filter by after_idx if provided
            if after_idx and idx <= cint(after_idx):
                continue

            messages.append({
                "idx": idx,
                "sender_type": msg.sender_type,
                "sender_id": msg.sender_id,
                "sender_name": msg.sender_name,
                "message_type": msg.message_type or "text",
                "message": msg.message,
                "timestamp": str(msg.timestamp),
                "attachment": msg.attachment,
                "attachment_name": msg.attachment_name,
                "attachment_size": msg.attachment_size,
                "is_read": bool(msg.is_read),
                "is_delivered": bool(msg.is_delivered),
                "read_at": str(msg.read_at) if msg.read_at else None,
                "delivered_at": str(msg.delivered_at) if msg.delivered_at else None,
                "reply_to_idx": msg.reply_to_idx,
                "reply_preview": msg.reply_preview
            })

        # Apply pagination
        start = cint(offset)
        end = start + cint(limit)
        paginated_messages = messages[start:end]

        return {
            "success": True,
            "total_messages": len(consultation.messages),
            "returned_count": len(paginated_messages),
            "messages": paginated_messages,
            "has_more": end < len(messages)
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Chat Messages Error")
        frappe.throw(_("Failed to get messages: {0}").format(str(e)))


@frappe.whitelist()
def mark_messages_as_read(consultation_id, reader_type):
    """
    Mark all messages from the other party as read

    Args:
        consultation_id: Medical Consultation ID
        reader_type: "patient" or "provider" (who is reading)

    Returns:
        Number of messages marked as read
    """
    try:
        if not frappe.db.exists("Medical Consultation", consultation_id):
            frappe.throw(_("Consultation not found"))

        consultation = frappe.get_doc("Medical Consultation", consultation_id)

        # Mark messages from the OTHER party as read
        other_party = "provider" if reader_type == "patient" else "patient"

        updated_count = 0
        read_time = now_datetime()

        for msg in consultation.messages:
            if msg.sender_type == other_party and not msg.is_read:
                msg.is_read = 1
                msg.read_at = read_time
                updated_count += 1

        # Reset unread count for the reader
        if reader_type == "patient":
            consultation.unread_count_patient = 0
        else:
            consultation.unread_count_provider = 0

        if updated_count > 0:
            consultation.save(ignore_permissions=True)
            frappe.db.commit()

            # Send real-time event
            _publish_chat_event(consultation_id, "messages_read", {
                "reader_type": reader_type,
                "read_at": str(read_time),
                "count": updated_count
            })

        return {
            "success": True,
            "marked_as_read": updated_count
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Mark Messages Read Error")
        frappe.throw(_("Failed to mark messages as read: {0}").format(str(e)))


@frappe.whitelist()
def set_typing_status(consultation_id, user_type, is_typing):
    """
    Set typing status for real-time indicator

    Args:
        consultation_id: Medical Consultation ID
        user_type: "patient" or "provider"
        is_typing: True or False
    """
    try:
        is_typing = cint(is_typing)

        # Update in database (for persistence)
        if user_type == "patient":
            frappe.db.set_value("Medical Consultation", consultation_id, "patient_typing", is_typing)
        else:
            frappe.db.set_value("Medical Consultation", consultation_id, "provider_typing", is_typing)

        # Send real-time event
        _publish_chat_event(consultation_id, "typing_status", {
            "user_type": user_type,
            "is_typing": bool(is_typing)
        })

        return {"success": True}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Set Typing Status Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_chat_status(consultation_id):
    """
    Get current chat status including typing indicators and unread counts

    Args:
        consultation_id: Medical Consultation ID

    Returns:
        Chat status information
    """
    try:
        if not frappe.db.exists("Medical Consultation", consultation_id):
            frappe.throw(_("Consultation not found"))

        consultation = frappe.get_doc("Medical Consultation", consultation_id)

        return {
            "success": True,
            "consultation_id": consultation_id,
            "status": consultation.status,
            "unread_count_patient": cint(consultation.unread_count_patient),
            "unread_count_provider": cint(consultation.unread_count_provider),
            "last_message_at": str(consultation.last_message_at) if consultation.last_message_at else None,
            "last_message_preview": consultation.last_message_preview,
            "patient_typing": bool(consultation.patient_typing),
            "provider_typing": bool(consultation.provider_typing),
            "total_messages": len(consultation.messages)
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Chat Status Error")
        frappe.throw(_("Failed to get chat status: {0}").format(str(e)))


@frappe.whitelist()
def get_unread_counts(user_type, user_id):
    """
    Get unread message counts for all consultations of a user

    Args:
        user_type: "patient" or "provider"
        user_id: Patient ID or Healthcare Provider ID

    Returns:
        Total unread count and per-consultation counts
    """
    try:
        if user_type == "patient":
            consultations = frappe.get_all(
                "Medical Consultation",
                filters={"patient": user_id, "status": ["!=", "Cancelled"]},
                fields=["name", "unread_count_patient", "provider_name", "last_message_preview"]
            )
            unread_field = "unread_count_patient"
        else:
            consultations = frappe.get_all(
                "Medical Consultation",
                filters={"healthcare_provider": user_id, "status": ["!=", "Cancelled"]},
                fields=["name", "unread_count_provider", "patient_name", "last_message_preview"]
            )
            unread_field = "unread_count_provider"

        total_unread = 0
        unread_by_consultation = []

        for c in consultations:
            count = cint(c.get(unread_field, 0))
            if count > 0:
                total_unread += count
                unread_by_consultation.append({
                    "consultation_id": c.name,
                    "unread_count": count,
                    "other_party_name": c.get("provider_name") or c.get("patient_name"),
                    "last_message_preview": c.get("last_message_preview")
                })

        return {
            "success": True,
            "total_unread": total_unread,
            "consultations": unread_by_consultation
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Unread Counts Error")
        frappe.throw(_("Failed to get unread counts: {0}").format(str(e)))


@frappe.whitelist()
def delete_message(consultation_id, message_idx):
    """
    Soft delete a message (replace content with "Message deleted")

    Args:
        consultation_id: Medical Consultation ID
        message_idx: Index of message to delete (1-based)

    Returns:
        Success status
    """
    try:
        if not frappe.db.exists("Medical Consultation", consultation_id):
            frappe.throw(_("Consultation not found"))

        consultation = frappe.get_doc("Medical Consultation", consultation_id)

        idx = cint(message_idx) - 1
        if idx < 0 or idx >= len(consultation.messages):
            frappe.throw(_("Message not found"))

        msg = consultation.messages[idx]

        # Store original type and update
        original_type = msg.message_type
        msg.message = _("This message was deleted")
        msg.message_type = "system"
        msg.attachment = None
        msg.attachment_name = None
        msg.attachment_size = 0

        consultation.save(ignore_permissions=True)
        frappe.db.commit()

        # Send real-time event
        _publish_chat_event(consultation_id, "message_deleted", {
            "idx": message_idx,
            "deleted_at": str(now_datetime())
        })

        return {"success": True}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delete Message Error")
        frappe.throw(_("Failed to delete message: {0}").format(str(e)))


@frappe.whitelist()
def get_active_chats(user_type, user_id, status_filter=None):
    """
    Get list of active chat consultations for a user

    Args:
        user_type: "patient" or "provider"
        user_id: User identifier
        status_filter: Optional status filter

    Returns:
        List of active chats with latest message info
    """
    try:
        filters = {"status": ["not in", ["Cancelled", "Completed"]]}

        if status_filter:
            filters["status"] = status_filter

        if user_type == "patient":
            filters["patient"] = user_id
            fields = [
                "name", "provider_name as other_party_name", "healthcare_provider as other_party_id",
                "status", "consultation_type", "last_message_at", "last_message_preview",
                "unread_count_patient as unread_count", "provider_typing as other_typing"
            ]
        else:
            filters["healthcare_provider"] = user_id
            fields = [
                "name", "patient_name as other_party_name", "patient as other_party_id",
                "status", "consultation_type", "last_message_at", "last_message_preview",
                "unread_count_provider as unread_count", "patient_typing as other_typing"
            ]

        chats = frappe.get_all(
            "Medical Consultation",
            filters=filters,
            fields=fields,
            order_by="last_message_at desc"
        )

        # Format response
        for chat in chats:
            chat["unread_count"] = cint(chat.get("unread_count", 0))
            chat["other_typing"] = bool(chat.get("other_typing"))
            chat["last_message_at"] = str(chat["last_message_at"]) if chat["last_message_at"] else None

        return {
            "success": True,
            "chats": chats
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Active Chats Error")
        frappe.throw(_("Failed to get active chats: {0}").format(str(e)))


# ============================================
# HELPER FUNCTIONS
# ============================================

def _validate_sender_permission(consultation, sender_type):
    """Validate that sender has permission to send message"""
    # In production, add proper permission checks here
    if sender_type not in ["patient", "provider"]:
        frappe.throw(_("Invalid sender type"))


def _get_sender_info(consultation, sender_type):
    """Get sender ID and name"""
    if sender_type == "patient":
        return consultation.patient, consultation.patient_name
    else:
        return consultation.healthcare_provider, consultation.provider_name


def _get_reply_preview(consultation, reply_idx):
    """Get preview of the message being replied to"""
    if reply_idx <= 0 or reply_idx > len(consultation.messages):
        return None

    original_msg = consultation.messages[reply_idx - 1]
    preview = original_msg.message or ""

    if original_msg.message_type in ["image", "file", "audio", "video"]:
        preview = f"[{original_msg.message_type.title()}] {original_msg.attachment_name or ''}"

    return (preview[:50] + "...") if len(preview) > 50 else preview


def _get_file_size(file_url):
    """Get file size from URL"""
    try:
        if not file_url:
            return 0
        file_doc = frappe.get_doc("File", {"file_url": file_url})
        return file_doc.file_size or 0
    except:
        return 0


def _publish_chat_event(consultation_id, event_type, data):
    """Publish real-time event for chat updates"""
    try:
        event_data = {
            "consultation_id": consultation_id,
            "event_type": event_type,
            "data": data,
            "timestamp": str(now_datetime())
        }

        # Publish to consultation-specific room
        room = f"consultation_{consultation_id}"
        publish_realtime(
            event="chat_update",
            message=event_data,
            room=room
        )

    except Exception as e:
        frappe.log_error(f"Failed to publish chat event: {str(e)}", "Chat Realtime Error")


def _send_message_notification(consultation, sender_type, message, message_type):
    """Send push/SMS notification for new message"""
    try:
        # Determine recipient
        if sender_type == "patient":
            # Notify provider
            recipient_type = "provider"
            recipient_id = consultation.healthcare_provider
            recipient_name = consultation.provider_name
            sender_name = consultation.patient_name
        else:
            # Notify patient
            recipient_type = "patient"
            recipient_id = consultation.patient
            recipient_name = consultation.patient_name
            sender_name = consultation.provider_name

        # Build notification message
        if message_type == "text":
            notif_message = message[:100] if len(message) <= 100 else message[:97] + "..."
        else:
            notif_message = f"Sent a {message_type}"

        # Create notification log
        notification = frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"New message from {sender_name}",
            "email_content": notif_message,
            "for_user": frappe.session.user,
            "type": "Alert",
            "document_type": "Medical Consultation",
            "document_name": consultation.name
        })
        notification.insert(ignore_permissions=True)

        # Send push notification if FCM is enabled
        # This will integrate with existing FCM setup in hooks.py

    except Exception as e:
        frappe.log_error(f"Failed to send message notification: {str(e)}", "Chat Notification Error")
