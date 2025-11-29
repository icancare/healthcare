# Copyright (c) 2024, healthcare and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Fix Health Insurance tab position - move Emergency Contacts and Patient Relation
	back to Address & Contact tab where they belong
	"""
	frappe.logger().info("Fixing Health Insurance tab structure...")
	
	# Step 1: Delete and re-add Health Insurance tab AFTER patient_relation
	# This ensures it comes AFTER all Address & Contact content
	
	try:
		# Delete existing Health Insurance tab fields
		for fieldname in ["health_insurance_tab", "insurance_section", "patient_insurance", "insurance_summary_section", "primary_insurance_html"]:
			if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": fieldname}):
				frappe.delete_doc("Custom Field", {"dt": "Patient", "fieldname": fieldname}, force=1)
				frappe.logger().info(f"✓ Deleted: {fieldname}")
		
		frappe.db.commit()
		
		# Step 2: Re-add Health Insurance tab AFTER patient_relation (which is in Address & Contact tab)
		custom_fields = {
			"Patient": [
				# Health Insurance Tab - insert after sb_relation (Patient Relation section)
				{
					"fieldname": "health_insurance_tab",
					"fieldtype": "Tab Break",
					"label": "Health Insurance",
					"insert_after": "patient_relation",  # This is the last field in Address & Contact tab
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
		
		create_custom_fields(custom_fields, update=True)
		frappe.logger().info("✅ Health Insurance tab re-added in correct position!")
		
	except Exception as e:
		frappe.logger().error(f"❌ Error fixing Health Insurance tab: {str(e)}")
		raise

