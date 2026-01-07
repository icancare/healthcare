# Copyright (c) 2025, ESS LLP and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Completely hide/remove labels and descriptions from social history tables
	that are appearing as duplicate text
	"""
	
	# These are the tables showing duplicate labels
	tables_to_fix = [
		"patient_smokeless_tobacco_history",
		"patient_smoking_tobacco_history",
		"patient_substance_abuse_history"
	]
	
	for fieldname in tables_to_fix:
		if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": fieldname}):
			# Get the custom field name
			cf_name = frappe.get_value("Custom Field", {"dt": "Patient", "fieldname": fieldname}, "name")
			
			# Update multiple properties
			frappe.db.set_value("Custom Field", cf_name, {
				"label": "",
				"description": "",
				"print_hide": 0,
				"hidden": 0
			})
			
			print(f"✓ Cleaned up: {fieldname}")
	
	# Also check if there are any heading fields we missed
	heading_fields = [
		"smokeless_tobacco_heading",
		"smoking_tobacco_heading",
		"substance_abuse_heading"
	]
	
	for fieldname in heading_fields:
		if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": fieldname}):
			cf_name = frappe.get_value("Custom Field", {"dt": "Patient", "fieldname": fieldname}, "name")
			frappe.delete_doc("Custom Field", cf_name, force=True)
			print(f"✓ Deleted heading: {fieldname}")
	
	frappe.db.commit()
	frappe.clear_cache(doctype="Patient")
	
	frappe.msgprint("✓ Social history table labels completely cleaned up")















