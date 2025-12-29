# Copyright (c) 2025, ESS LLP and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Fix Social History section position to appear after Surgical History
	in Medical History tab (not at the top!)
	"""
	
	# Update social_history_section_break position
	if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "social_history_section_break"}):
		frappe.db.set_value("Custom Field", 
			{"dt": "Patient", "fieldname": "social_history_section_break"}, 
			"insert_after", 
			"patient_surgical_history"
		)
		print("✓ Social History section moved after Surgical History")
	
	# Also check for old social_history_section field
	if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "social_history_section"}):
		frappe.db.set_value("Custom Field", 
			{"dt": "Patient", "fieldname": "social_history_section"}, 
			"insert_after", 
			"patient_surgical_history"
		)
		print("✓ Old social_history_section also updated")
	
	frappe.db.commit()
	frappe.clear_cache(doctype="Patient")
	
	frappe.msgprint("✓ Social History section position fixed - now appears after Surgical History")












