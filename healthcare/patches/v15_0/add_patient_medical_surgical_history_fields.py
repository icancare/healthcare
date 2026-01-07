import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add Medical History and Surgical History tables to Patient"""
	
	# Hide old text fields
	hide_old_fields()
	
	# Add new table fields
	custom_fields = {
		"Patient": [
			{
				"fieldname": "patient_medical_history_section",
				"fieldtype": "Section Break",
				"label": "Medical History",
				"insert_after": "surgical_history",
				"collapsible": 0
			},
			{
				"fieldname": "patient_medical_history",
				"fieldtype": "Table",
				"label": "Medical History",
				"options": "Patient Medical History",
				"insert_after": "patient_medical_history_section",
				"description": "Patient medical history details"
			},
			{
				"fieldname": "patient_surgical_history_section",
				"fieldtype": "Section Break",
				"label": "Surgical History",
				"insert_after": "patient_medical_history",
				"collapsible": 0
			},
			{
				"fieldname": "patient_surgical_history",
				"fieldtype": "Table",
				"label": "Surgical History",
				"options": "Patient Surgical History",
				"insert_after": "patient_surgical_history_section",
				"description": "Patient surgical history details"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	frappe.db.commit()
	
	print("✓ Patient Medical History and Surgical History fields added")


def hide_old_fields():
	"""Hide old text-based medical_history and surgical_history fields"""
	try:
		patient_meta = frappe.get_meta("Patient")
		
		if patient_meta.has_field("medical_history"):
			frappe.db.sql("""
				UPDATE `tabDocField` 
				SET hidden = 1 
				WHERE parent = 'Patient' AND fieldname = 'medical_history'
			""")
			print("✓ Hidden old 'medical_history' field")
		
		if patient_meta.has_field("surgical_history"):
			frappe.db.sql("""
				UPDATE `tabDocField` 
				SET hidden = 1 
				WHERE parent = 'Patient' AND fieldname = 'surgical_history'
			""")
			print("✓ Hidden old 'surgical_history' field")
		
		frappe.db.commit()
	except Exception as e:
		print(f"Note: Could not hide old fields - {str(e)}")















