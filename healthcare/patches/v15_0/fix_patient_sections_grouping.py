# Copyright (c) 2025, ESS LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Fix Patient Medical History tab grouping:
	1. Allergy section (separate)
	2. Immunization section (separate)
	3. Medical History section (separate)
	4. Surgical History section (separate)
	5. Social History section (all tobacco, substance, oral, diet, occupational, environmental together)
	"""
	
	# First, cleanup and recreate all sections with proper section breaks
	cleanup_and_recreate_sections()
	frappe.db.commit()
	frappe.msgprint("✓ Patient sections fixed with proper grouping")


def cleanup_and_recreate_sections():
	"""Delete and recreate all custom fields with proper section breaks"""
	
	# Delete old fields
	old_fields = [
		"allergy_section",
		"immunization_section", 
		"medical_history_section",
		"surgical_history_section",
		"social_history_section",
		"oral_habits_heading",
		"diet_heading",
		"occupational_exposure_heading",
		"environmental_factors_heading"
	]
	
	for fieldname in old_fields:
		if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": fieldname}):
			try:
				cf_name = frappe.get_value("Custom Field", {"dt": "Patient", "fieldname": fieldname}, "name")
				frappe.delete_doc("Custom Field", cf_name, force=True)
				print(f"Deleted: {fieldname}")
			except Exception as e:
				print(f"Error deleting {fieldname}: {str(e)}")
	
	frappe.db.commit()
	
	# Now recreate with proper structure
	# Note: We're adding section breaks BEFORE each major section
	
	custom_fields = {
		"Patient": [
			# 1. Allergy Section (after existing patient_allergy field)
			{
				"fieldname": "allergy_section_break",
				"fieldtype": "Section Break",
				"label": "Allergy",
				"insert_after": "patient_relation",  # Or find appropriate field
				"collapsible": 1
			},
			
			# 2. Immunization Section (after patient_allergy)
			{
				"fieldname": "immunization_section_break",
				"fieldtype": "Section Break",
				"label": "Immunization",
				"insert_after": "patient_allergy",
				"collapsible": 1
			},
			
			# 3. Medical History Section (after patient_immunization)
			{
				"fieldname": "medical_history_section_break",
				"fieldtype": "Section Break",
				"label": "Medical History",
				"insert_after": "patient_immunization",
				"collapsible": 1
			},
			
			# 4. Surgical History Section (after medical_history/patient_medical_history)
			{
				"fieldname": "surgical_history_section_break",
				"fieldtype": "Section Break",
				"label": "Surgical History",
				"insert_after": "patient_medical_history",
				"collapsible": 1
			},
			
			# 5. Social History Section (after surgical_history/patient_surgical_history)
			# This will contain all social history tables with headings
			{
				"fieldname": "social_history_section_break",
				"fieldtype": "Section Break",
				"label": "Social History",
				"insert_after": "patient_surgical_history",
				"collapsible": 1
			},
			
			# Social History sub-headings (inside Social History section)
			{
				"fieldname": "smokeless_tobacco_heading",
				"fieldtype": "Heading",
				"label": "Smokeless Tobacco",
				"insert_after": "social_history_section_break"
			},
			# patient_smokeless_tobacco_history already exists after this
			
			{
				"fieldname": "smoking_tobacco_heading",
				"fieldtype": "Heading",
				"label": "Smoking Tobacco",
				"insert_after": "patient_smokeless_tobacco_history"
			},
			# patient_smoking_tobacco_history already exists after this
			
			{
				"fieldname": "substance_abuse_heading",
				"fieldtype": "Heading",
				"label": "Substance Abuse",
				"insert_after": "patient_smoking_tobacco_history"
			},
			# patient_substance_abuse_history already exists after this
			
			{
				"fieldname": "oral_habits_heading",
				"fieldtype": "Heading",
				"label": "Oral Habits",
				"insert_after": "patient_substance_abuse_history"
			},
			# patient_oral_habits_history already exists after this
			
			{
				"fieldname": "diet_heading",
				"fieldtype": "Heading",
				"label": "Diet",
				"insert_after": "patient_oral_habits_history"
			},
			# patient_diet_history already exists after this
			
			{
				"fieldname": "occupational_exposure_heading",
				"fieldtype": "Heading",
				"label": "Occupational Exposure",
				"insert_after": "patient_diet_history"
			},
			# patient_occupational_exposure_history already exists after this
			
			{
				"fieldname": "environmental_factors_heading",
				"fieldtype": "Heading",
				"label": "Environmental Factors",
				"insert_after": "patient_occupational_exposure_history"
			}
			# patient_environmental_factors_history already exists after this
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	frappe.db.commit()


















