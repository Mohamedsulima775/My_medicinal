// Copyright (c) 2025, mohammedsuliman and contributors
// For license information, please see license.txt

//frappe.ui.form.on('Medication Schedule', {
	// refresh: function(frm) {

	// }
//});

// Copyright (c) 2025, mohammedsuliman and contributors
// For license information, please see license.txt

frappe.ui.form.on('Medication Schedule', {
	refresh: function(frm) {
		// Custom buttons
		add_custom_buttons(frm);
		
		// Update status indicator
		update_status_indicator(frm);
		
		// Set queries
		set_queries(frm);
	},
	
	patient: function(frm) {
		// Auto-fetch patient name
		if (frm.doc.patient) {
			frappe.db.get_value('patient', frm.doc.patient, 'patient_name', (r) => {
				if (r && r.patient_name) {
					frm.set_value('patient_name', r.patient_name);
				}
			});
		}
	},
	
	current_stock: function(frm) {
		// Recalculate when stock changes
		calculate_days_until_depletion(frm);
	},
	
	dosage: function(frm) {
		calculate_daily_consumption(frm);
	},
	
	frequency: function(frm) {
		calculate_daily_consumption(frm);
	},
	
	times: function(frm) {
		// Recalculate when times change
		calculate_daily_consumption(frm);
	},
	
	is_active: function(frm) {
		// Update button states
		frm.trigger('refresh');
	}
});

// ============================================
// Child Table: Medication Time
// ============================================

frappe.ui.form.on('Medication Time', {
	times_add: function(frm, cdt, cdn) {
		// Set default time when adding new row
		let row = locals[cdt][cdn];
		if (!row.time) {
			let now = new Date();
			row.time = now.getHours() + ':' + String(now.getMinutes()).padStart(2, '0') + ':00';
			frm.refresh_field('times');
		}
	},
	
	time: function(frm, cdt, cdn) {
		// Recalculate daily consumption when time changes
		calculate_daily_consumption(frm);
	}
});

// ============================================
// Custom Functions
// ============================================

function add_custom_buttons(frm) {
	if (!frm.doc.__islocal) {
		// Refill Stock Button
		if (frm.doc.is_active && frm.doc.days_until_depletion <= 10) {
			frm.add_custom_button(__('Refill Stock'), function() {
				refill_stock_dialog(frm);
			}, __('Actions'));
		}
		
		// Deactivate/Activate Button
		if (frm.doc.is_active) {
			frm.add_custom_button(__('Deactivate'), function() {
				deactivate_medication(frm);
			}, __('Actions'));
		} else {
			frm.add_custom_button(__('Activate'), function() {
				activate_medication(frm);
			}, __('Actions'));
		}
		
		// View History
		frm.add_custom_button(__('View Logs'), function() {
			frappe.set_route('List', 'Medication Log', {
				'medication_schedule': frm.doc.name
			});
		}, __('View'));
		
		// Quick Consume (for testing)
		if (frm.doc.is_active && frm.doc.current_stock > 0) {
			frm.add_custom_button(__('Record Dose Taken'), function() {
				record_dose_taken(frm);
			}, __('Actions'));
		}
	}
}

function update_status_indicator(frm) {
	if (!frm.doc.is_active) {
		frm.dashboard.set_headline_alert(__('This medication is inactive'), 'orange');
		return;
	}
	
	let days = frm.doc.days_until_depletion || 0;
	
	if (days <= 0) {
		frm.dashboard.set_headline_alert(
			__('OUT OF STOCK! Please refill immediately.'),
			'red'
		);
	} else if (days <= 2) {
		frm.dashboard.set_headline_alert(
			__('CRITICAL: Only {0} days of medication left!', [days]),
			'red'
		);
	} else if (days <= 5) {
		frm.dashboard.set_headline_alert(
			__('Low Stock: {0} days remaining', [days]),
			'orange'
		);
	} else if (days <= 10) {
		frm.dashboard.set_headline_alert(
			__('Stock OK: {0} days remaining', [days]),
			'blue'
		);
	} else {
		frm.dashboard.set_headline_alert(
			__('Stock Good: {0} days remaining', [days]),
			'green'
		);
	}
}

function set_queries(frm) {
	// Filter patient to active only
	frm.set_query('patient', function() {
		return {
			filters: {
				'status': 'Active'
			}
		};
	});
}

function calculate_daily_consumption(frm) {
	if (!frm.doc.times || frm.doc.times.length === 0) {
		frm.set_value('daily_consumption', 0);
		frm.set_value('days_until_depletion', 0);
		return;
	}
	
	// Simple calculation: number of times per day × dosage
	let times_per_day = frm.doc.times.length;
	
	// Parse dosage (assume 1 if not specified)
	let dosage_amount = 1;
	if (frm.doc.dosage) {
		let numbers = frm.doc.dosage.match(/\d+/);
		if (numbers && numbers.length > 0) {
			dosage_amount = 1; // We count tablets, not mg
		}
	}
	
	let daily_consumption = times_per_day * dosage_amount;
	frm.set_value('daily_consumption', daily_consumption);
	
	// Calculate days until depletion
	calculate_days_until_depletion(frm);
}

function calculate_days_until_depletion(frm) {
	if (!frm.doc.current_stock || !frm.doc.daily_consumption || frm.doc.daily_consumption === 0) {
		frm.set_value('days_until_depletion', 0);
		return;
	}
	
	let days = Math.floor(frm.doc.current_stock / frm.doc.daily_consumption);
	frm.set_value('days_until_depletion', days);
	
	// Update indicator
	update_status_indicator(frm);
}

function refill_stock_dialog(frm) {
	let d = new frappe.ui.Dialog({
		title: __('Refill Stock'),
		fields: [
			{
				label: __('Current Stock'),
				fieldname: 'current_stock',
				fieldtype: 'Int',
				default: frm.doc.current_stock,
				read_only: 1
			},
			{
				label: __('Add Quantity'),
				fieldname: 'add_quantity',
				fieldtype: 'Int',
				reqd: 1,
				default: 30
			},
			{
				fieldtype: 'Column Break'
			},
			{
				label: __('New Stock'),
				fieldname: 'new_stock',
				fieldtype: 'Int',
				read_only: 1,
				default: frm.doc.current_stock
			},
			{
				label: __('Days Until Depletion'),
				fieldname: 'new_days',
				fieldtype: 'Int',
				read_only: 1,
				default: frm.doc.days_until_depletion
			}
		],
		primary_action_label: __('Refill'),
		primary_action: function() {
			let values = d.get_values();
			
			frappe.call({
				method: 'my_medicinal.my_medicinal.doctype.medication_schedule.medication_schedule.update_stock',
				args: {
					schedule_id: frm.doc.name,
					new_stock: frm.doc.current_stock + values.add_quantity
				},
				callback: function(r) {
					if (r.message) {
						frappe.show_alert({
							message: __('Stock refilled successfully'),
							indicator: 'green'
						});
						frm.reload_doc();
					}
				}
			});
			
			d.hide();
		}
	});
	
	// Update new stock calculation
	d.fields_dict.add_quantity.$input.on('change', function() {
		let add_qty = parseInt(d.get_value('add_quantity')) || 0;
		let new_stock = frm.doc.current_stock + add_qty;
		d.set_value('new_stock', new_stock);
		
		if (frm.doc.daily_consumption > 0) {
			let new_days = Math.floor(new_stock / frm.doc.daily_consumption);
			d.set_value('new_days', new_days);
		}
	});
	
	d.show();
}

function deactivate_medication(frm) {
	frappe.confirm(
		__('Are you sure you want to deactivate this medication?'),
		function() {
			frappe.call({
				method: 'my_medicinal.my_medicinal.doctype.medication_schedule.medication_schedule.deactivate_medication',
				args: {
					schedule_id: frm.doc.name
				},
				callback: function(r) {
					if (r.message) {
						frappe.show_alert({
							message: __('Medication deactivated'),
							indicator: 'orange'
						});
						frm.reload_doc();
					}
				}
			});
		}
	);
}

function activate_medication(frm) {
	frappe.call({
		method: 'frappe.client.set_value',
		args: {
			doctype: 'Medication Schedule',
			name: frm.doc.name,
			fieldname: 'is_active',
			value: 1
		},
		callback: function(r) {
			frappe.show_alert({
				message: __('Medication activated'),
				indicator: 'green'
			});
			frm.reload_doc();
		}
	});
}

function record_dose_taken(frm) {
	frappe.confirm(
		__('Record that this dose was taken?<br>This will reduce stock by 1.'),
		function() {
			frappe.call({
				method: 'frappe.client.set_value',
				args: {
					doctype: 'Medication Schedule',
					name: frm.doc.name,
					fieldname: 'current_stock',
					value: frm.doc.current_stock - 1
				},
				callback: function(r) {
					frappe.show_alert({
						message: __('Dose recorded'),
						indicator: 'green'
					});
					frm.reload_doc();
				}
			});
		}
	);
}
