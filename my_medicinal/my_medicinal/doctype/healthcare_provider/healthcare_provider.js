// Copyright (c) 2025, mohammedsuliman and contributors
// For license information, please see license.txt

// Healthcare Provider Client Script
// File: healthcare_provider.js

frappe.ui.form.on('Healthcare Provider', {
    refresh: function(frm) {
        // Add custom buttons
        if (!frm.is_new()) {
            // View Schedule button
            frm.add_custom_button(__('View Full Schedule'), function() {
                show_schedule_dialog(frm);
            }, __('Actions'));
            
            // Check Availability button
            frm.add_custom_button(__('Check Availability'), function() {
                check_availability_dialog(frm);
            }, __('Actions'));
            
            // View Consultations button
            frm.add_custom_button(__('View Consultations'), function() {
                frappe.set_route('List', 'Medical Consultation', {
                    'healthcare_provider': frm.doc.name
                });
            }, __('Actions'));
        }
        
        // Add status indicator
        if (frm.doc.status) {
            add_status_indicator(frm);
        }
        
        // Add help text
        if (frm.doc.__islocal) {
            frm.set_intro(__('Please fill in all required fields to create a new healthcare provider'), 'blue');
        }
    },
    
    status: function(frm) {
        // Update status indicator when status changes
        add_status_indicator(frm);
    },
    
    specialty: function(frm) {
        // Auto-suggestions based on specialty
        if (frm.doc.specialty === 'Cardiology') {
            frm.set_value('consultation_fee', 200);
        } else if (frm.doc.specialty === 'General Practice') {
            frm.set_value('consultation_fee', 100);
        }
    },
    
    email: function(frm) {
        // Validate email format
        if (frm.doc.email) {
            validate_email(frm);
        }
    },
    
    phone: function(frm) {
        // Format phone number
        if (frm.doc.phone) {
            format_phone_number(frm);
        }
    },
    
    before_save: function(frm) {
        // Validation before saving
        if (frm.doc.schedule && frm.doc.schedule.length > 0) {
            validate_schedule(frm);
        }
    }
});

// Provider Schedule child table
frappe.ui.form.on('Provider Schedule', {
    from_time: function(frm, cdt, cdn) {
        validate_time_range(frm, cdt, cdn);
    },
    
    to_time: function(frm, cdt, cdn) {
        validate_time_range(frm, cdt, cdn);
    },
    
    day: function(frm, cdt, cdn) {
        // Check for duplicate days
        let row = locals[cdt][cdn];
        let duplicate = false;
        
        frm.doc.schedule.forEach(function(schedule_row) {
            if (schedule_row.name !== row.name && schedule_row.day === row.day) {
                duplicate = true;
            }
        });
        
        if (duplicate) {
            frappe.msgprint({
                title: __('Duplicate Day'),
                message: __('This day is already in the schedule. Please select a different day.'),
                indicator: 'orange'
            });
            frappe.model.set_value(cdt, cdn, 'day', '');
        }
    }
});

// Helper Functions
function add_status_indicator(frm) {
    let color = {
        'Active': 'green',
        'Inactive': 'red',
        'On Leave': 'orange'
    }[frm.doc.status] || 'gray';
    
    frm.page.set_indicator(frm.doc.status, color);
}

function validate_email(frm) {
    const email_regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email_regex.test(frm.doc.email)) {
        frappe.msgprint({
            title: __('Invalid Email'),
            message: __('Please enter a valid email address'),
            indicator: 'red'
        });
        frm.set_value('email', '');
    }
}

function format_phone_number(frm) {
    // Remove all non-digit characters
    let phone = frm.doc.phone.replace(/\D/g, '');
    
    // Format: +966 50 123 4567
    if (phone.length >= 9) {
        if (!phone.startsWith('966')) {
            phone = '966' + phone;
        }
        frm.set_value('phone', '+' + phone);
    }
}function validate_schedule(frm) {
    let has_error = false;
    
    frm.doc.schedule.forEach(function(row) {
        if (row.from_time && row.to_time) {
            if (row.from_time >= row.to_time) {
                frappe.msgprint({
                    title: __('Invalid Time Range'),
                    message: __('From Time must be before To Time for {0}', [row.day]),
                    indicator: 'red'
                });
                has_error = true;
            }
        }
    });
    
    if (has_error) {
        frappe.validated = false;
    }
}

function validate_time_range(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    
    if (row.from_time && row.to_time) {
        if (row.from_time >= row.to_time) {
            frappe.msgprint({
                title: __('Invalid Time Range'),
                message: __('From Time must be before To Time'),
                indicator: 'red'
            });
            frappe.model.set_value(cdt, cdn, 'to_time', '');
        }
    }
}

function show_schedule_dialog(frm) {
    if (!frm.doc.schedule || frm.doc.schedule.length === 0) {
        frappe.msgprint(__('No schedule available'));
        return;
    }
    
    let html = '<table class="table table-bordered">';
    html += '<thead><tr><th>Day</th><th>From</th><th>To</th><th>Status</th></tr></thead>';
    html += '<tbody>';
    
    frm.doc.schedule.forEach(function(row) {
        let status = row.is_available ? 
            '<span class="indicator green">Available</span>' : 
            '<span class="indicator red">Not Available</span>';
        
        html += <tr>
            <td>${row.day}</td>
            <td>${row.from_time || '-'}</td>
            <td>${row.to_time || '-'}</td>
            <td>${status}</td>
        </tr>;
    });
    
    html += '</tbody></table>';
    
    frappe.msgprint({
        title: __('Weekly Schedule - {0}', [frm.doc.provider_name]),
        message: html,
        wide: true
    });
}

function check_availability_dialog(frm) {
    let d = new frappe.ui.Dialog({
        title: __('Check Availability'),
        fields: [
            {
                fieldname: 'date',
                label: __('Date'),
                fieldtype: 'Date',
                reqd: 1,
                default: frappe.datetime.get_today()
            },
            {
                fieldname: 'time',
                label: __('Time'),
                fieldtype: 'Time',
                reqd: 1
            }
        ],
        primary_action_label: __('Check'),
        primary_action(values) {
            let consultation_date = values.date + ' ' + values.time;
            
            frappe.call({
                method: 'my_medicinal.doctype.healthcare_provider.healthcare_provider.check_availability',
                args: {
                    provider_id: frm.doc.name,
                    consultation_date: consultation_date
                },
                callback: function(r) {
                    if (r.message) {
                        let indicator = r.message.available ? 'green' : 'red';
                        frappe.msgprint({
                            title: __('Availability Check'),
                            message: r.message.message,
                            indicator: indicator
                        });
                    }
                }
            });
            
            d.hide();
        }
    });
    
    d.show();
}