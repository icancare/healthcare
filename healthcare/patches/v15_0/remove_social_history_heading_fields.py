# Copyright (c) 2025, ESS LLP and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Remove heading fields that were created by original social history patch
	These are showing as duplicate text labels
	"""
	
	# Delete heading fields from Patient
	patient_heading_fields = [
		"smokeless_tobacco_history_heading",
		"smoking_tobacco_history_heading",
		"substance_abuse_history_heading",
		"oral_habits_history_heading",
		"diet_history_heading",
		"occupational_exposure_history_heading",
		"environmental_factors_history_heading"
	]
	
	for fieldname in patient_heading_fields:
		try:
			if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": fieldname}):
				cf_name = frappe.get_value("Custom Field", {"dt": "Patient", "fieldname": fieldname}, "name")
				frappe.delete_doc("Custom Field", cf_name, force=True)
				print(f"✓ Deleted Patient heading: {fieldname}")
		except Exception as e:
			print(f"Error deleting {fieldname}: {str(e)}")
	
	# Also check for any heading fields without _heading suffix
	alternative_names = [
		"smokeless_tobacco_heading",
		"smoking_tobacco_heading",
		"substance_abuse_heading"
	]
	
	for fieldname in alternative_names:
		try:
			if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": fieldname}):
				cf_name = frappe.get_value("Custom Field", {"dt": "Patient", "fieldname": fieldname}, "name")
				frappe.delete_doc("Custom Field", cf_name, force=True)
				print(f"✓ Deleted Patient heading (alt): {fieldname}")
		except Exception as e:
			print(f"Error deleting {fieldname}: {str(e)}")
	
	frappe.db.commit()
	frappe.clear_cache(doctype="Patient")
	
	frappe.msgprint("✓ All social history heading fields removed - tables will show without duplicate labels")






