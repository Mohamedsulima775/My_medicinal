// my_medicinal/public/js/dawaii_custom.js
// Custom JavaScript for Dawaii Theme

frappe.ready(function() {
    // ============================================================================
    // THEME INITIALIZATION
    // ============================================================================
    
    console.log("%c?? Dawaii Theme Loaded", "color: #2D6A4F; font-size: 16px; font-weight: bold;");
    
    // Set primary color
    document.documentElement.style.setProperty('--primary-color', '#2D6A4F');
    
    // ============================================================================
    // CUSTOM LOGO
    // ============================================================================
    
    // Replace Frappe logo with Dawaii logo
    if (window.location.pathname.includes('/desk')) {
        const logo = document.querySelector('.navbar-brand img');
        if (logo) {
            logo.src = '/assets/my_medicinal/images/dawaii-logo.png';
            logo.style.height = '32px';
        }
    }
    
    // ============================================================================
    // SIDEBAR ENHANCEMENTS
    // ============================================================================
    
    // Add custom icons to sidebar items
    const sidebarItems = document.querySelectorAll('.standard-sidebar-item');
    const iconMap = {
        'Patient': '??',
        'Medication Schedule': '??',
        'Medical Prescription': '??',
        'Medical Consultation': '??',
        'Patient Order': '??',
        'Healthcare Provider': '?????',
        'Medication Item': '??',
        'Adherence Report': '??',
    };
    
    sidebarItems.forEach(item => {
        const label = item.querySelector('.sidebar-item-label');
        if (label) {
            const text = label.textContent.trim();
            if (iconMap[text]) {
                label.innerHTML = `${iconMap[text]} ${text}`;
            }
        }
    });
    
    // ============================================================================
    // CUSTOM INDICATORS
    // ============================================================================
    
    frappe.ui.form.on('Medication Schedule', {
        refresh: function(frm) {
            // Add stock status indicator
            if (frm.doc.days_until_depletion <= 5) {
                frm.dashboard.add_indicator(
                    __('Stock Low: {0} days', [frm.doc.days_until_depletion]),
                    'red'
                );
            } else if (frm.doc.days_until_depletion <= 10) {
                frm.dashboard.add_indicator(
                    __('Stock Medium: {0} days', [frm.doc.days_until_depletion]),
                    'orange'
                );
            } else {
                frm.dashboard.add_indicator(
                    __('Stock Good: {0} days', [frm.doc.days_until_depletion]),
                    'green'
                );
            }
            
            // Add custom buttons
            if (frm.doc.is_active) {
                frm.add_custom_button(__('Log Medication Taken'), function() {
                    logMedicationTaken(frm.doc.name);
                }, __('Actions'));
                
                frm.add_custom_button(__('Refill Order'), function() {
                    createRefillOrder(frm.doc.name);
                }, __('Actions'));
            }
        }
    });
    
    frappe.ui.form.on('Patient', {
        refresh: function(frm) {
            // Add patient statistics
            if (frm.doc.name) {
                frappe.call({
                    method: 'my_medicinal.api.patient.get_statistics',
                    args: {
                        patient: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            const stats = r.message;
                            
                            frm.dashboard.add_indicator(
                                __('Active Medications: {0}', [stats.active_medications]),
                                'blue'
                            );
                            
                            frm.dashboard.add_indicator(
                                __('Adherence Rate: {0}%', [stats.adherence_rate]),
                                stats.adherence_rate >= 80 ? 'green' : 'orange'
                            );
                        }
                    }
                });
            }
            
            // Add custom buttons
            frm.add_custom_button(__('Add Medication'), function() {
                frappe.new_doc('Medication Schedule', {
                    patient: frm.doc.name,
                    patient_name: frm.doc.patient_name
                });
            }, __('Create'));
            
            frm.add_custom_button(__('New Consultation'), function() {
                frappe.new_doc('Medical Consultation', {
                    patient: frm.doc.name,
                    patient_name: frm.doc.patient_name
                });
            }, __('Create'));
        }
    });
    
    // ============================================================================
    // LIST VIEW CUSTOMIZATION
    // ============================================================================
    
    frappe.listview_settings['Medication Schedule'] = {
        onload: function(listview) {
            // Add custom filters
            listview.page.add_inner_button(__('Low Stock'), function() {
                listview.filter_area.add([[
                    'Medication Schedule',
                    'days_until_depletion',
                    '<=',
                    5
                ]]);
                listview.refresh();
            });
            
            listview.page.add_inner_button(__('Active Only'), function() {
                listview.filter_area.add([[
                    'Medication Schedule',
                    'is_active',
                    '=',
                    1
                ]]);
                listview.refresh();
            });
        },
        
        // Custom indicator colors
        get_indicator: function(doc) {
            if (!doc.is_active) {
                return [__("Inactive"), "gray", "is_active,=,0"];
            } else if (doc.days_until_depletion <= 5) {
                return [__("Low Stock"), "red", "days_until_depletion,<=,5"];
            } else if (doc.days_until_depletion <= 10) {
                return [__("Medium Stock"), "orange", "days_until_depletion,<=,10"];
            } else {
                return [__("Active"), "green", "is_active,=,1"];
            }
        }
    };
    
    frappe.listview_settings['Patient Order'] = {
        get_indicator: function(doc) {
            const status_color = {
                "Draft": "gray",
                "Pending": "orange",
                "Processing": "blue",
                "Shipped": "cyan",
                "Delivered": "green",
                "Cancelled": "red"
            };
            return [__(doc.status), status_color[doc.status], "status,=," + doc.status];
        }
    };
    
    frappe.listview_settings['Medical Consultation'] = {
        get_indicator: function(doc) {
            const status_color = {
                "Pending": "orange",
                "In Progress": "blue",
                "Completed": "green",
                "Cancelled": "red"
            };
            return [__(doc.status), status_color[doc.status], "status,=," + doc.status];
        }
    };
    
    // ============================================================================
    // CUSTOM FUNCTIONS
    // ============================================================================
    
    function logMedicationTaken(medication_schedule) {
        frappe.prompt([
            {
                label: __('Taken Time'),
                fieldname: 'taken_at',
                fieldtype: 'Datetime',
                default: frappe.datetime.now_datetime(),
                reqd: 1
            },
            {
                label: __('Quantity'),
                fieldname: 'quantity_taken',
                fieldtype: 'Int',
                default: 1,
                reqd: 1
            },
            {
                label: __('Notes'),
                fieldname: 'notes',
                fieldtype: 'Small Text'
            }
        ], function(values) {
            frappe.call({
                method: 'my_medicinal.api.medication_schedule.log_medication_taken',
                args: {
                    medication_schedule: medication_schedule,
                    taken_at: values.taken_at,
                    quantity_taken: values.quantity_taken,
                    notes: values.notes
                },
                callback: function(r) {
                    if (!r.exc) {
                        frappe.show_alert({
                            message: __('Medication logged successfully'),
                            indicator: 'green'
                        }, 5);
                        cur_frm.reload_doc();
                    }
                }
            });
        }, __('Log Medication Taken'), __('Submit'));
    }
    
    function createRefillOrder(medication_schedule) {
        frappe.call({
            method: 'my_medicinal.api.medication_schedule.get_refill_details',
            args: {
                medication_schedule: medication_schedule
            },
            callback: function(r) {
                if (r.message) {
                    const details = r.message;
                    
                    frappe.prompt([
                        {
                            label: __('Medication'),
                            fieldname: 'medication_name',
                            fieldtype: 'Data',
                            default: details.medication_name,
                            read_only: 1
                        },
                        {
                            label: __('Quantity Needed'),
                            fieldname: 'quantity',
                            fieldtype: 'Int',
                            default: details.suggested_quantity,
                            reqd: 1
                        },
                        {
                            label: __('Delivery Address'),
                            fieldname: 'delivery_address',
                            fieldtype: 'Small Text',
                            reqd: 1
                        }
                    ], function(values) {
                        frappe.call({
                            method: 'my_medicinal.api.order.create_refill_order',
                            args: {
                                medication_schedule: medication_schedule,
                                quantity: values.quantity,
                                delivery_address: values.delivery_address
                            },
                            callback: function(r) {
                                if (!r.exc && r.message) {
                                    frappe.set_route('Form', 'Patient Order', r.message);
                                }
                            }
                        });
                    }, __('Create Refill Order'), __('Create'));
                }
            }
        });
    }
    
    // ============================================================================
    // NOTIFICATIONS
    // ============================================================================
    
    // Custom notification styling
    frappe.show_alert = function(opts, seconds) {
        if (typeof opts === 'string') {
            opts = {
                message: opts
            };
        }
        
        opts.indicator = opts.indicator || 'blue';
        
        // Create custom alert
        const alert = $(`
            <div class="dawaii-alert alert-${opts.indicator}">
                <div class="alert-icon">
                    ${getAlertIcon(opts.indicator)}
                </div>
                <div class="alert-message">
                    ${opts.message}
                </div>
            </div>
        `);
        
        $('body').append(alert);
        
        setTimeout(function() {
            alert.addClass('show');
        }, 100);
        
        setTimeout(function() {
            alert.removeClass('show');
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, (seconds || 3) * 1000);
    };
    
    function getAlertIcon(indicator) {
        const icons = {
            'green': '?',
            'red': '?',
            'orange': '?',
            'blue': '?'
        };
        return icons[indicator] || '?';
    }
    
    // ============================================================================
    // PAGE ENHANCEMENTS
    // ============================================================================
    
    // Add custom CSS for alerts
    $('head').append(`
        <style>
            .dawaii-alert {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 16px 20px;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
                display: flex;
                align-items: center;
                gap: 12px;
                z-index: 9999;
                transform: translateX(400px);
                transition: transform 0.3s ease;
                max-width: 400px;
            }
            
            .dawaii-alert.show {
                transform: translateX(0);
            }
            
            .dawaii-alert.alert-green {
                background: linear-gradient(135deg, #52B788 0%, #40916C 100%);
                color: white;
            }
            
            .dawaii-alert.alert-red {
                background: linear-gradient(135deg, #E76F51 0%, #E85D75 100%);
                color: white;
            }
            
            .dawaii-alert.alert-orange {
                background: linear-gradient(135deg, #F4A261 0%, #E76F51 100%);
                color: white;
            }
            
            .dawaii-alert.alert-blue {
                background: linear-gradient(135deg, #4ECDC4 0%, #2D6A4F 100%);
                color: white;
            }
            
            .dawaii-alert .alert-icon {
                font-size: 24px;
                font-weight: bold;
            }
            
            .dawaii-alert .alert-message {
                font-size: 14px;
                font-weight: 500;
            }
        </style>
    `);
    
    // ============================================================================
    // QUICK ACTIONS
    // ============================================================================
    
    // Add quick action buttons to desk
    if (window.location.pathname === '/app') {
        setTimeout(function() {
            addQuickActions();
        }, 1000);
    }
    
    function addQuickActions() {
        const container = $('.page-head-content');
        if (container.length && !$('.dawaii-quick-actions').length) {
            const quickActions = $(`
                <div class="dawaii-quick-actions" style="margin-top: 16px;">
                    <button class="btn btn-sm btn-primary" onclick="createNewPatient()">
                        ?? Add Patient
                    </button>
                    <button class="btn btn-sm btn-success" onclick="createNewMedication()">
                        ?? Add Medication
                    </button>
                    <button class="btn btn-sm btn-info" onclick="viewDashboard()">
                        ?? Dashboard
                    </button>
                </div>
            `);
            container.append(quickActions);
        }
    }
    
    window.createNewPatient = function() {
        frappe.new_doc('Patient');
    };
    
    window.createNewMedication = function() {
        frappe.new_doc('Medication Schedule');
    };
    
    window.viewDashboard = function() {
        frappe.set_route('query-report', 'Medication Adherence Dashboard');
    };
    
    // ============================================================================
    // RTL SUPPORT
    // ============================================================================
    
    // Auto-detect Arabic and apply RTL
    function applyRTL() {
        const lang = frappe.boot.lang || 'en';
        if (lang === 'ar') {
            document.documentElement.setAttribute('dir', 'rtl');
            document.body.classList.add('rtl');
        }
    }
    
    applyRTL();
});

// ============================================================================
// EXPORT FUNCTIONS
// ============================================================================

window.dawaii = {
    version: '1.0.0',
    theme: 'medical-green',
    logMedicationTaken: logMedicationTaken,
    createRefillOrder: createRefillOrder
};