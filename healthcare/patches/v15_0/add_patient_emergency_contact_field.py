import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Add Patient Emergency Contact section and table to Patient DocType
	This adds emergency contact information in the Address & Contact tab
	"""
	
	custom_fields = {
		"Patient": [
			# Emergency Contact Section
			{
				"fieldname": "emergency_contact_section",
				"fieldtype": "Section Break",
				"label": "Emergency Contacts",
				"insert_after": "contact_html",
				"collapsible": 0
			},
			{
				"fieldname": "patient_emergency_contact",
				"fieldtype": "Table",
				"label": "Emergency Contacts",
				"options": "Patient Emergency Contact",
				"insert_after": "emergency_contact_section",
				"description": "Emergency contact persons who can be reached in case of emergency"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	frappe.db.commit()
	
	print("✓ Patient Emergency Contact field added to Address & Contact tab")

