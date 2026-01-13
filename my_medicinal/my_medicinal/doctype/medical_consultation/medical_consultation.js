// Copyright (c) 2025, mohammedsuliman and contributors
// For license information, please see license.txt

// Medical Consultation Client Script
// File: medical_consultation.js

frappe.ui.form.on('Medical Consultation', {
    refresh: function(frm) {
        // Add custom buttons based on status
        if (!frm.is_new()) {
            add_custom_buttons(frm);
        }
        
        // Add status indicator
        if (frm.doc.status) {
            add_status_indicator(frm);
        }
        
        // Add priority indicator
        if (frm.doc.priority) {
            add_priority_indicator(frm);
        }
        
        // Show unread messages count
        if (frm.doc.messages) {
            show_unread_count(frm);
        }
        
        // Add help text
        if (frm.doc.__islocal) {
            frm.set_intro(__('Book a new consultation with a healthcare provider'), 'blue');
        }
    },
    
    patient: function(frm) {
        // Auto-fetch patient details
        if (frm.doc.patient) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'patient',
                    name: frm.doc.patient
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('patient_name', r.message.patient_name);
                    }
                }
            });
        }
    },
    
    healthcare_provider: function(frm) {
        // Auto-fetch provider details and fee
        if (frm.doc.healthcare_provider) {
            frappe.call({
                method: 'my_medicinal.my_medicinal.doctype.healthcare_provider.healthcare_provider.get_provider_profile',
                args: {
                    provider_id: frm.doc.healthcare_provider
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('provider_name', r.message.provider_name);
                        frm.set_value('consultation_fee', r.message.consultation_fee);
                    }
                }
            });
        }
    },
    
    consultation_date: function(frm) {
        // Check provider availability
        if (frm.doc.healthcare_provider && frm.doc.consultation_date) {
            check_provider_availability(frm);
        }
    },
    
    status: function(frm) {
        // Update indicators when status changes
        add_status_indicator(frm);
        
        // Show appropriate buttons
        refresh_buttons(frm);
    },
    
    payment_status: function(frm) {
        // Auto-set payment date when paid
        if (frm.doc.payment_status === 'Paid' && !frm.doc.payment_date) {
            frm.set_value('payment_date', frappe.datetime.get_today());
        }
    },
    
    before_save: function(frm) {
        // Validate before saving
        if (frm.doc.consultation_date) {
            validate_consultation_date(frm);
        }
    }
});

// Consultation Message child table
frappe.ui.form.on('Consultation Message', {
    messages_add: function(frm, cdt, cdn) {
        // Auto-set timestamp for new message
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'timestamp', frappe.datetime.now_datetime());
    }
});

// Helper Functions
function add_custom_buttons(frm) {
    // Clear existing custom buttons
    frm.clear_custom_buttons();
    
    // Start Chat button (for active consultations)
    if (['Scheduled', 'In Progress'].includes(frm.doc.status)) {
        frm.add_custom_button(__('Start Chat'), function() {
            open_chat_dialog(frm);
        }, __('Actions')).css({'background-color': '#10B981', 'color': 'white'});
    }
    
    // Update Status buttons
    if (frm.doc.status === 'Pending') {
        frm.add_custom_button(__('Confirm'), function() {
            update_status(frm, 'Scheduled');
        }, __('Status'));frm.add_custom_button(__('Cancel'), function() {
            cancel_consultation_dialog(frm);
        }, __('Status')).css({'background-color': '#EF4444', 'color': 'white'});
    }
    
    if (frm.doc.status === 'Scheduled') {
        frm.add_custom_button(__('Start'), function() {
            update_status(frm, 'In Progress');
        }, __('Status'));
    }
    
    if (frm.doc.status === 'In Progress') {
        frm.add_custom_button(__('Complete'), function() {
            complete_consultation_dialog(frm);
        }, __('Status')).css({'background-color': '#10B981', 'color': 'white'});
    }
    
    // View Provider Profile
    if (frm.doc.healthcare_provider) {
        frm.add_custom_button(__('View Provider Profile'), function() {
            frappe.set_route('Form', 'Healthcare Provider', frm.doc.healthcare_provider);
        }, __('Actions'));
    }
    
    // Mark Messages as Read
    if (frm.doc.messages && frm.doc.messages.length > 0) {
        frm.add_custom_button(__('Mark Messages as Read'), function() {
            mark_all_read(frm);
        }, __('Messages'));
    }
}

function add_status_indicator(frm) {
    let color_map = {
        'Pending': 'gray',
        'Scheduled': 'blue',
        'In Progress': 'orange',
        'Completed': 'green',
        'Cancelled': 'red'
    };
    
    let color = color_map[frm.doc.status] || 'gray';
    frm.page.set_indicator(frm.doc.status, color);
}

function add_priority_indicator(frm) {
    let priority_colors = {
        'Low': 'gray',
        'Normal': 'blue',
        'High': 'orange',
        'Urgent': 'red'
    };
    
    if (frm.doc.priority && frm.doc.priority !== 'Normal') {
        let color = priority_colors[frm.doc.priority];
        frm.dashboard.add_indicator(__('Priority: {0}', [frm.doc.priority]), color);
    }
}

function show_unread_count(frm) {
    let unread = 0;
    frm.doc.messages.forEach(function(msg) {
        if (!msg.is_read && msg.sender_type === 'Provider') {
            unread++;
        }
    });
    
    if (unread > 0) {
        frm.dashboard.add_indicator(__('Unread Messages: {0}', [unread]), 'red');
    }
}

function check_provider_availability(frm) {
    frappe.call({
        method: 'my_medicinal.my_medicinal.doctype.healthcare_provider.healthcare_provider.check_availability',
        args: {
            provider_id: frm.doc.healthcare_provider,
            consultation_date: frm.doc.consultation_date
        },
        callback: function(r) {
            if (r.message && !r.message.available) {
                frappe.msgprint({
                    title: __('Provider Not Available'),
                    message: r.message.message,
                    indicator: 'red'
                });
            }
        }
    });
}

function validate_consultation_date(frm) {
    let consultation_dt = frappe.datetime.str_to_obj(frm.doc.consultation_date);
    let now = new Date();
    
    if (consultation_dt < now && frm.doc.status === 'Pending') {
        frappe.msgprint({
            title: __('Invalid Date'),
            message: __('Cannot book consultation in the past'),
            indicator: 'red'
        });
        frappe.validated = false;
    }
}

function update_status(frm, new_status) {
    frappe.call({
        method: 'my_medicinal.my_medicinal.doctype.medical_consultation.medical_consultation.update_consultation_status',
        args: {
            consultation_id: frm.doc.name,
            new_status: new_status
        },
        callback: function(r) {
            if (r.message) {
                frappe.show_alert({
                    message: __('Status updated to {0}', [new_status]),
                    indicator: 'green'
                }, 3);
                frm.reload_doc();
            }
        }
    });
}

function cancel_consultation_dialog(frm) {let d = new frappe.ui.Dialog({
        title: __('Cancel Consultation'),
        fields: [
            {
                fieldname: 'reason',
                label: __('Cancellation Reason'),
                fieldtype: 'Small Text',
                reqd: 1
            }
        ],
        primary_action_label: __('Cancel Consultation'),
        primary_action(values) {
            frappe.call({
                method: 'my_medicinal.my_medicinal.doctype.medical_consultation.medical_consultation.cancel_consultation',
                args: {
                    consultation_id: frm.doc.name,
                    reason: values.reason
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: __('Consultation cancelled'),
                            indicator: 'orange'
                        }, 3);
                        frm.reload_doc();
                    }
                }
            });
            d.hide();
        }
    });
    
    d.show();
}

function complete_consultation_dialog(frm) {
    let d = new frappe.ui.Dialog({
        title: __('Complete Consultation'),
        fields: [
            {
                fieldname: 'notes',
                label: __('Final Notes'),
                fieldtype: 'Small Text'
            },
            {
                fieldname: 'payment_status',
                label: __('Payment Status'),
                fieldtype: 'Select',
                options: 'Unpaid\nPaid',
                default: 'Paid'
            }
        ],
        primary_action_label: __('Complete'),
        primary_action(values) {
            // Update notes if provided
            if (values.notes) {
                frm.set_value('notes', (frm.doc.notes || '') + '\n\n' + values.notes);
            }
            
            // Update payment status
            frm.set_value('payment_status', values.payment_status);
            
            // Update consultation status
            update_status(frm, 'Completed');
            
            d.hide();
        }
    });
    
    d.show();
}

function open_chat_dialog(frm) {
    let d = new frappe.ui.Dialog({
        title: __('Consultation Chat - {0}', [frm.doc.provider_name]),
        fields: [
            {
                fieldname: 'messages_html',
                fieldtype: 'HTML'
            },
            {
                fieldname: 'message',
                label: __('Your Message'),
                fieldtype: 'Small Text',
                reqd: 1
            }
        ],
        primary_action_label: __('Send'),
        primary_action(values) {
            send_message(frm, values.message);
            values.message = '';
            refresh_chat(frm, d);
        },
        size: 'large'
    });
    
    // Display existing messages
    refresh_chat(frm, d);
    
    d.show();
}

function refresh_chat(frm, dialog) {
    let html = '<div class="chat-messages" style="max-height: 400px; overflow-y: auto; padding: 10px;">';
    
    if (frm.doc.messages && frm.doc.messages.length > 0) {
        frm.doc.messages.forEach(function(msg) {
            let align = msg.sender_type === 'Patient' ? 'right' : 'left';
            let bg_color = msg.sender_type === 'Patient' ? '#DCF8C6' : '#E8E8E8';
            
            html += `
                <div style="text-align: ${align}; margin-bottom: 10px;">
                    <div style="display: inline-block; max-width: 70%; padding: 10px; 
                                background-color: ${bg_color}; border-radius: 10px; text-align: left;">
                        <strong>${msg.sender_type}</strong><br>
                        ${msg.message}<br>
                        <small style="color: #666;">${frappe.datetime.str_to_user(msg.timestamp)}</small></div>
                </div>
            `;
        });
    } else {
        html += '<p style="text-align: center; color: #666;">No messages yet. Start the conversation!</p>';
    }
    
    html += '</div>';
    
    dialog.fields_dict.messages_html.$wrapper.html(html);
    
    // Scroll to bottom
    let chat_div = dialog.fields_dict.messages_html.$wrapper.find('.chat-messages');
    chat_div.scrollTop(chat_div[0].scrollHeight);
}

function send_message(frm, message) {
    frappe.call({
        method: 'my_medicinal.my_medicinal.doctype.medical_consultation.medical_consultation.send_message',
        args: {
            consultation_id: frm.doc.name,
            sender_type: 'Patient',
            message: message
        },
        callback: function(r) {
            if (r.message) {
                frm.reload_doc();
                frappe.show_alert({
                    message: __('Message sent'),
                    indicator: 'green'
                }, 2);
            }
        }
    });
}

function mark_all_read(frm) {
    frappe.call({
        method: 'my_medicinal.my_medicinal.doctype.medical_consultation.medical_consultation.mark_messages_read',
        args: {
            consultation_id: frm.doc.name,
            sender_type: 'Provider'
        },
        callback: function(r) {
            if (r.message) {
                frm.reload_doc();
                frappe.show_alert({
                    message: __('Messages marked as read'),
                    indicator: 'green'
                }, 2);
            }
        }
    });
}

function refresh_buttons(frm) {
    frm.clear_custom_buttons();
    add_custom_buttons(frm);
}