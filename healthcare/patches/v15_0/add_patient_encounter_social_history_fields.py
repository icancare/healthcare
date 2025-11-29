import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add Social History tables to Patient Encounter"""
	
	custom_fields = {
		"Patient Encounter": [
			{
				"fieldname": "social_history_section",
				"fieldtype": "Section Break",
				"label": "Social History",
				"insert_after": "custom_surgical_history",
				"collapsible": 1,
				"collapsible_depends_on": "eval:(doc.custom_smokeless_tobacco_history && doc.custom_smokeless_tobacco_history.length > 0) || (doc.custom_smoking_tobacco_history && doc.custom_smoking_tobacco_history.length > 0) || (doc.custom_substance_abuse_history && doc.custom_substance_abuse_history.length > 0)"
			},
			{
				"fieldname": "smokeless_tobacco_history_label",
				"fieldtype": "HTML",
				"label": "Smokeless Tobacco History",
				"options": "<h6 style='margin-bottom: 10px;'>Smokeless Tobacco History</h6>",
				"insert_after": "social_history_section"
			},
			{
				"fieldname": "custom_smokeless_tobacco_history",
				"fieldtype": "Table",
				"label": "Smokeless Tobacco History",
				"options": "Patient Encounter Smokeless Tobacco History",
				"insert_after": "smokeless_tobacco_history_label"
			},
			{
				"fieldname": "smoking_tobacco_history_label",
				"fieldtype": "HTML",
				"label": "Smoking Tobacco History",
				"options": "<h6 style='margin-top: 20px; margin-bottom: 10px;'>Smoking Tobacco History</h6>",
				"insert_after": "custom_smokeless_tobacco_history"
			},
			{
				"fieldname": "custom_smoking_tobacco_history",
				"fieldtype": "Table",
				"label": "Smoking Tobacco History",
				"options": "Patient Encounter Smoking Tobacco History",
				"insert_after": "smoking_tobacco_history_label"
			},
			{
				"fieldname": "substance_abuse_history_label",
				"fieldtype": "HTML",
				"label": "Substance Abuse History",
				"options": "<h6 style='margin-top: 20px; margin-bottom: 10px;'>Substance Abuse History</h6>",
				"insert_after": "custom_smoking_tobacco_history"
			},
			{
				"fieldname": "custom_substance_abuse_history",
				"fieldtype": "Table",
				"label": "Substance Abuse History",
				"options": "Patient Encounter Substance Abuse History",
				"insert_after": "substance_abuse_history_label"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	frappe.db.commit()
	
	print("✓ Patient Encounter Social History fields added")

