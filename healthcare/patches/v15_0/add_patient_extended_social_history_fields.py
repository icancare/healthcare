# Copyright (c) 2025, ESS LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Add Oral Habits, Diet, Occupational Exposure, and Environmental Factors
	to Patient DocType - all grouped under existing Social History section
	"""
	
	custom_fields = {
		"Patient": [
			# Add to existing Social History section (after substance abuse) with headings
			{
				"fieldname": "oral_habits_heading",
				"fieldtype": "Heading",
				"label": "Oral Habits",
				"insert_after": "patient_substance_abuse_history"
			},
			{
				"fieldname": "patient_oral_habits_history",
				"fieldtype": "Table",
				"label": "Oral Habits History",
				"options": "Patient Oral Habits History",
				"insert_after": "oral_habits_heading"
			},
			
			{
				"fieldname": "diet_heading",
				"fieldtype": "Heading",
				"label": "Diet",
				"insert_after": "patient_oral_habits_history"
			},
			{
				"fieldname": "patient_diet_history",
				"fieldtype": "Table",
				"label": "Diet History",
				"options": "Patient Diet History",
				"insert_after": "diet_heading"
			},
			
			{
				"fieldname": "occupational_exposure_heading",
				"fieldtype": "Heading",
				"label": "Occupational Exposure",
				"insert_after": "patient_diet_history"
			},
			{
				"fieldname": "patient_occupational_exposure_history",
				"fieldtype": "Table",
				"label": "Occupational Exposure History",
				"options": "Patient Occupational Exposure History",
				"insert_after": "occupational_exposure_heading"
			},
			
			{
				"fieldname": "environmental_factors_heading",
				"fieldtype": "Heading",
				"label": "Environmental Factors",
				"insert_after": "patient_occupational_exposure_history"
			},
			{
				"fieldname": "patient_environmental_factors_history",
				"fieldtype": "Table",
				"label": "Environmental Factors History",
				"options": "Patient Environmental Factors History",
				"insert_after": "environmental_factors_heading"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	frappe.db.commit()
	
	frappe.msgprint("✓ Extended Social History fields added to Patient (grouped in Social History section)")

