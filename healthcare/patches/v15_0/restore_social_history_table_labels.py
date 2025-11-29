# Copyright (c) 2025, ESS LLP and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Restore proper labels for social history tables
	We deleted headings (correct) but also removed table labels (wrong)
	Now restoring table labels properly
	"""
	
	# Restore table labels with proper names
	table_labels = {
		"patient_smokeless_tobacco_history": "Smokeless Tobacco History",
		"patient_smoking_tobacco_history": "Smoking Tobacco History",
		"patient_substance_abuse_history": "Substance Abuse History",
		"patient_oral_habits_history": "Oral Habits History",
		"patient_diet_history": "Diet History",
		"patient_occupational_exposure_history": "Occupational Exposure History",
		"patient_environmental_factors_history": "Environmental Factors History"
	}
	
	for fieldname, label in table_labels.items():
		if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": fieldname}):
			frappe.db.set_value("Custom Field", 
				{"dt": "Patient", "fieldname": fieldname}, 
				"label", 
				label
			)
			print(f"✓ Restored label: {fieldname} = '{label}'")
	
	frappe.db.commit()
	frappe.clear_cache(doctype="Patient")
	
	frappe.msgprint("✓ Social history table labels restored properly")

