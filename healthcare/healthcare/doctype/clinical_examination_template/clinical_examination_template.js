// Copyright (c) 2024, ICanCare and contributors
// For license information, please see license.txt

frappe.ui.form.on("Clinical Examination Template", {
	refresh(frm) {
		// Add preview button
		if (!frm.is_new()) {
			frm.add_custom_button(__("Preview Form"), function() {
				frappe.set_route("Form", "Clinical Examination", "new-clinical-examination", {
					examination_template: frm.doc.name
				});
			});
		}
	},
	
	examination_type(frm) {
		// Set default diagram type based on examination type
		if (frm.doc.examination_type === "Oral Screening") {
			frm.set_value("diagram_type", "Oral Cavity");
			frm.set_value("image_categories", "Face and Neck\nOpen Mouth with Scale\nCentral Arch with Lips\nRight Cheek with Alveolus\nLeft Cheek with Alveolus\nTongue Protruded\nTongue with Floor of Mouth\nHard and Soft Palate\nAbnormal Area Focused");
		} else if (frm.doc.examination_type === "Dermatology") {
			frm.set_value("diagram_type", "Full Body Front");
		} else if (frm.doc.examination_type === "ENT") {
			frm.set_value("diagram_type", "Face Front");
		}
	}
});

