import frappe


def execute():
	"""Make show_clinical_examination field visible and fix Step 1 section"""
	print("\n" + "="*60)
	print("Fixing Step 1 Clinical Examination visibility")
	print("="*60)
	
	doctype = "Patient Encounter"
	
	# Make show_clinical_examination visible
	if frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": "show_clinical_examination"}):
		frappe.db.set_value(
			"Custom Field", 
			{"dt": doctype, "fieldname": "show_clinical_examination"}, 
			"hidden", 0
		)
		print("  ✓ Made 'show_clinical_examination' checkbox visible")
	
	# Make sure exam_step1_section is visible and positioned correctly
	if frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": "exam_step1_section"}):
		frappe.db.set_value(
			"Custom Field", 
			{"dt": doctype, "fieldname": "exam_step1_section"}, 
			{
				"hidden": 0,
				"depends_on": "eval:doc.show_clinical_examination"
			}
		)
		print("  ✓ Updated 'exam_step1_section' visibility")
	
	# Make sure exam_step1_table_html is visible
	if frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": "exam_step1_table_html"}):
		frappe.db.set_value(
			"Custom Field", 
			{"dt": doctype, "fieldname": "exam_step1_table_html"}, 
			{
				"hidden": 0,
				"depends_on": "eval:doc.show_clinical_examination"
			}
		)
		print("  ✓ Updated 'exam_step1_table_html' visibility")
	
	frappe.db.commit()
	print("="*60 + "\n")
