import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add Medical History and Surgical History tables to Patient Encounter"""
	
	custom_fields = {
		"Patient Encounter": [
			{
				"fieldname": "medical_history_section",
				"fieldtype": "Section Break",
				"label": "Medical History",
				"insert_after": "custom_immunization",
				"collapsible": 1,
				"collapsible_depends_on": "eval:doc.custom_medical_history && doc.custom_medical_history.length > 0"
			},
			{
				"fieldname": "custom_medical_history",
				"fieldtype": "Table",
				"label": "Medical History",
				"options": "Patient Encounter Medical History",
				"insert_after": "medical_history_section"
			},
			{
				"fieldname": "surgical_history_section",
				"fieldtype": "Section Break",
				"label": "Surgical History",
				"insert_after": "custom_medical_history",
				"collapsible": 1,
				"collapsible_depends_on": "eval:doc.custom_surgical_history && doc.custom_surgical_history.length > 0"
			},
			{
				"fieldname": "custom_surgical_history",
				"fieldtype": "Table",
				"label": "Surgical History",
				"options": "Patient Encounter Surgical History",
				"insert_after": "surgical_history_section"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	frappe.db.commit()
	
	print("✓ Patient Encounter Medical History and Surgical History fields added")





















