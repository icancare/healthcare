// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Diagnosis Category', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Diagnoses'), function() {
				frappe.set_route('List', 'Diagnosis', {
					'diagnosis_category': frm.doc.name
				});
			});
		}
	}
});

