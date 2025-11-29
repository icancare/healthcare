# Copyright (c) 2024, healthcare and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Add Health Insurance tab and fields to Patient DocType
	"""
	frappe.logger().info("Adding Patient Insurance fields...")
	
	custom_fields = {
		"Patient": [
			# Health Insurance Tab
			{
				"fieldname": "health_insurance_tab",
				"fieldtype": "Tab Break",
				"label": "Health Insurance",
				"insert_after": "contact_html",  # After Address & Contacts tab
			},
			# Insurance Section
			{
				"fieldname": "insurance_section",
				"fieldtype": "Section Break",
				"label": "Insurance Information",
				"insert_after": "health_insurance_tab",
			},
			# Patient Insurance Table
			{
				"fieldname": "patient_insurance",
				"fieldtype": "Table",
				"label": "Insurance Details",
				"options": "Patient Insurance",
				"insert_after": "insurance_section",
				"description": "Add multiple insurance policies for this patient. You can track both current and past insurance records.",
			},
			# Insurance Summary Section
			{
				"fieldname": "insurance_summary_section",
				"fieldtype": "Section Break",
				"label": "Insurance Summary",
				"insert_after": "patient_insurance",
				"collapsible": 1,
			},
			# Primary Insurance HTML field for quick view
			{
				"fieldname": "primary_insurance_html",
				"fieldtype": "HTML",
				"label": "Primary Insurance",
				"insert_after": "insurance_summary_section",
				"options": "<p class='text-muted'>Primary insurance details will be displayed here</p>",
			},
		]
	}
	
	try:
		create_custom_fields(custom_fields, update=True)
		frappe.logger().info("✅ Patient Insurance fields added successfully!")
	except Exception as e:
		frappe.logger().error(f"❌ Error adding Patient Insurance fields: {str(e)}")
		raise

