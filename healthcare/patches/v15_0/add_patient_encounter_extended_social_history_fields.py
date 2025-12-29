# Copyright (c) 2025, ESS LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Add Oral Habits, Diet, Occupational Exposure, and Environmental Factors
	to Patient Encounter - all grouped under existing Social History section
	"""
	
	custom_fields = {
		"Patient Encounter": [
			# Add to existing Social History section (after substance abuse)
			{
				"fieldname": "custom_oral_habits_heading",
				"fieldtype": "Heading",
				"label": "Oral Habits",
				"insert_after": "custom_substance_abuse_history"
			},
			{
				"fieldname": "custom_oral_habits_history",
				"fieldtype": "Table",
				"label": "Oral Habits History",
				"options": "Patient Encounter Oral Habits History",
				"insert_after": "custom_oral_habits_heading"
			},
			
			{
				"fieldname": "custom_diet_heading",
				"fieldtype": "Heading",
				"label": "Diet",
				"insert_after": "custom_oral_habits_history"
			},
			{
				"fieldname": "custom_diet_history",
				"fieldtype": "Table",
				"label": "Diet History",
				"options": "Patient Encounter Diet History",
				"insert_after": "custom_diet_heading"
			},
			
			{
				"fieldname": "custom_occupational_exposure_heading",
				"fieldtype": "Heading",
				"label": "Occupational Exposure",
				"insert_after": "custom_diet_history"
			},
			{
				"fieldname": "custom_occupational_exposure_history",
				"fieldtype": "Table",
				"label": "Occupational Exposure History",
				"options": "Patient Encounter Occupational Exposure History",
				"insert_after": "custom_occupational_exposure_heading"
			},
			
			{
				"fieldname": "custom_environmental_factors_heading",
				"fieldtype": "Heading",
				"label": "Environmental Factors",
				"insert_after": "custom_occupational_exposure_history"
			},
			{
				"fieldname": "custom_environmental_factors_history",
				"fieldtype": "Table",
				"label": "Environmental Factors History",
				"options": "Patient Encounter Environmental Factors History",
				"insert_after": "custom_environmental_factors_heading"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	frappe.db.commit()
	
	frappe.msgprint("✓ Extended Social History fields added to Patient Encounter (grouped in Social History)")












