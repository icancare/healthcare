// Copyright (c) 2025, Earthians and contributors
// For license information, please see license.txt

frappe.ui.form.on("Patient Immunization", {
	vaccine_name: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		if (row.vaccine_name) {
			// Fetch medication details and auto-fill manufacturer
			frappe.db.get_value("Medication", row.vaccine_name, ["manufacturer"], (r) => {
				if (r && r.manufacturer) {
					frappe.model.set_value(cdt, cdn, "manufacturer", r.manufacturer);
					frappe.show_alert({
						message: __("Manufacturer auto-filled from Medication"),
						indicator: "green"
					});
				}
			});
		}
	}
});

