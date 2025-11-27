// Copyright (c) 2025, Earthians and contributors
// For license information, please see license.txt

frappe.ui.form.on("Patient Allergy", {
	allergen: function(frm, cdt, cdn) {
		// Allow manual entry - if not in list, it will be created
		let row = locals[cdt][cdn];
		if (row.allergen) {
			// Check if allergen exists, if not user can still type
			frappe.db.get_value("Allergen", row.allergen, "name", (r) => {
				if (!r || !r.name) {
					frappe.show_alert({
						message: __("New allergen will be created: {0}", [row.allergen]),
						indicator: "blue"
					});
				}
			});
		}
	},
	
	reaction: function(frm, cdt, cdn) {
		// Allow manual entry - if not in list, it will be created
		let row = locals[cdt][cdn];
		if (row.reaction) {
			// Check if reaction exists, if not user can still type
			frappe.db.get_value("Allergen Reaction", row.reaction, "name", (r) => {
				if (!r || !r.name) {
					frappe.show_alert({
						message: __("New reaction will be created: {0}", [row.reaction]),
						indicator: "blue"
					});
				}
			});
		}
	}
});

