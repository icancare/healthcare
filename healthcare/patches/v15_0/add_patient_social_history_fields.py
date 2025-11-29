import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add Social History tables to Patient"""
	
	custom_fields = {
		"Patient": [
			{
				"fieldname": "social_history_section",
				"fieldtype": "Section Break",
				"label": "Social History",
				"insert_after": "surgical_history",
				"collapsible": 0
			},
			{
				"fieldname": "smokeless_tobacco_history_heading",
				"fieldtype": "Heading",
				"label": "Smokeless Tobacco History",
				"insert_after": "social_history_section"
			},
			{
				"fieldname": "patient_smokeless_tobacco_history",
				"fieldtype": "Table",
				"label": "Smokeless Tobacco History",
				"options": "Patient Smokeless Tobacco History",
				"insert_after": "smokeless_tobacco_history_heading",
				"description": "Patient smokeless tobacco usage history"
			},
			{
				"fieldname": "smoking_tobacco_history_heading",
				"fieldtype": "Heading",
				"label": "Smoking Tobacco History",
				"insert_after": "patient_smokeless_tobacco_history"
			},
			{
				"fieldname": "patient_smoking_tobacco_history",
				"fieldtype": "Table",
				"label": "Smoking Tobacco History",
				"options": "Patient Smoking Tobacco History",
				"insert_after": "smoking_tobacco_history_heading",
				"description": "Patient smoking tobacco usage history"
			},
			{
				"fieldname": "substance_abuse_history_heading",
				"fieldtype": "Heading",
				"label": "Substance Abuse History",
				"insert_after": "patient_smoking_tobacco_history"
			},
			{
				"fieldname": "patient_substance_abuse_history",
				"fieldtype": "Table",
				"label": "Substance Abuse History",
				"options": "Patient Substance Abuse History",
				"insert_after": "substance_abuse_history_heading",
				"description": "Patient substance abuse history"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	frappe.db.commit()
	
	print("✓ Patient Social History fields added")

