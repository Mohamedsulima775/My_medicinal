// Copyright (c) 2025, mohammedsuliman and contributors
// For license information, please see license.txt

frappe.ui.form.on('Medical Prescription', {
    patient_dob: function(frm) {
        if (frm.doc.patient_dob) {
            const birth = new Date(frm.doc.patient_dob);
            const today = new Date();
            let age = today.getFullYear() - birth.getFullYear();
            if (today.getMonth() < birth.getMonth() || 
               (today.getMonth() == birth.getMonth() && today.getDate() < birth.getDate())) {
                age -= 1;
            }
            frm.set_value('patient_age', age);
        }
    }
});
frappe.ui.form.on('PrescriptionItem', {
    frequency: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        const map = { "Once Daily": 1, "BID": 2, "TID": 3, "QID": 4, "PRN": 0 };
        row.frequency_value = map[row.frequency] || 0;
        row.quantity = row.duration * row.frequency_value;
        frm.refresh_field('medications');
    },
    duration: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        row.quantity = row.duration * (row.frequency_value || 0);
        frm.refresh_field('medications');
    }
});