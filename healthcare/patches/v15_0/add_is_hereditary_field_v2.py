import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	"""
	Add 'is_hereditary' checkbox field to medical history tables using Custom Fields
	This is more reliable than modifying DocType directly
	"""
	try:
		custom_fields = {
			"Patient Medical History": [
				{
					"fieldname": "is_hereditary",
					"label": "Is Hereditary",
					"fieldtype": "Check",
					"insert_after": "undergoing_treatment",
					"description": "Check if this condition has hereditary/genetic factors",
					"default": "0"
				}
			],
			"Patient Family Medical History": [
				{
					"fieldname": "is_hereditary",
					"label": "Is Hereditary",
					"fieldtype": "Check",
					"insert_after": "undergoing_treatment",
					"description": "Check if this condition has hereditary/genetic factors",
					"default": "0"
				}
			],
			"Patient Encounter Medical History": [
				{
					"fieldname": "is_hereditary",
					"label": "Is Hereditary",
					"fieldtype": "Check",
					"insert_after": "undergoing_treatment",
					"description": "Check if this condition has hereditary/genetic factors",
					"default": "0"
				}
			],
			"Patient Encounter Family Medical History": [
				{
					"fieldname": "is_hereditary",
					"label": "Is Hereditary",
					"fieldtype": "Check",
					"insert_after": "undergoing_treatment",
					"description": "Check if this condition has hereditary/genetic factors",
					"default": "0"
				}
			]
		}
		
		create_custom_fields(custom_fields, update=True)
		
		frappe.clear_cache()
		print("✅ Added 'is_hereditary' custom field to all medical history tables")
		
	except Exception as e:
		print(f"❌ Error adding is_hereditary custom field: {str(e)}")
		frappe.log_error(f"Error in add_is_hereditary_field_v2 patch: {str(e)}")

