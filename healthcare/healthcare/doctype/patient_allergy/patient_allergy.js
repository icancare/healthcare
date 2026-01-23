// Copyright (c) 2025, Earthians and contributors
// For license information, please see license.txt

frappe.ui.form.on("Patient Allergy", {
	allergen_category: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// Only process if allergen exists and was set BEFORE category
		// This prevents clearing allergen when category is auto-filled
		if (row.allergen && row.allergen_category) {
			frappe.db.get_value('Allergen', row.allergen, 'allergen_category', function(r) {
				// Only clear if allergen's category doesn't match selected category
				if (r && r.allergen_category && r.allergen_category !== row.allergen_category) {
					// Allergen doesn't belong to selected category, clear it
					frappe.model.set_value(cdt, cdn, 'allergen', '');
				}
				// If categories match, do nothing - keep the allergen
			});
		}
	},
	
	allergen: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// Auto-fill category when allergen is selected (only if category is empty)
		if (row.allergen && !row.allergen_category) {
			frappe.db.get_value('Allergen', row.allergen, 'allergen_category', function(r) {
				if (r && r.allergen_category) {
					frappe.model.set_value(cdt, cdn, 'allergen_category', r.allergen_category);
				} else {
					// New allergen - show alert
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

