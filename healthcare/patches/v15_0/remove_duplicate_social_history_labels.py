# Copyright (c) 2025, ESS LLP and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Remove duplicate labels from social history table fields
	since we already have section headings
	"""
	
	# Social history tables - we'll make their labels blank
	# since the section already has proper headings
	social_history_tables = [
		"patient_smokeless_tobacco_history",
		"patient_smoking_tobacco_history",
		"patient_substance_abuse_history",
		"patient_oral_habits_history",
		"patient_diet_history",
		"patient_occupational_exposure_history",
		"patient_environmental_factors_history"
	]
	
	for fieldname in social_history_tables:
		if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": fieldname}):
			# Set label to empty string (field will still work, just no label shown)
			frappe.db.set_value("Custom Field", 
				{"dt": "Patient", "fieldname": fieldname}, 
				"label", 
				""
			)
			print(f"✓ Removed label from: {fieldname}")
	
	frappe.db.commit()
	frappe.msgprint("✓ Duplicate social history labels removed - fields now show under section headings only")












