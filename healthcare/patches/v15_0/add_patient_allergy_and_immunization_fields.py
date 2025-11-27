import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Add Patient Allergy and Immunization table fields to Patient DocType
	Also hide the old 'Allergies' and 'Medication' text fields
	"""
	
	# Hide old fields
	hide_old_fields()
	
	# Add new table fields
	custom_fields = {
		"Patient": [
			# Allergy Section
			{
				"fieldname": "patient_allergy_section",
				"fieldtype": "Section Break",
				"label": "Allergy",
				"insert_after": "surgical_history",
				"collapsible": 0
			},
			{
				"fieldname": "patient_allergy",
				"fieldtype": "Table",
				"label": "Allergy",
				"options": "Patient Allergy",
				"insert_after": "patient_allergy_section",
				"description": "Patient allergy details"
			},
			# Immunization Section
			{
				"fieldname": "patient_immunization_section",
				"fieldtype": "Section Break",
				"label": "Immunization",
				"insert_after": "patient_allergy",
				"collapsible": 0
			},
			{
				"fieldname": "patient_immunization",
				"fieldtype": "Table",
				"label": "Immunization",
				"options": "Patient Immunization",
				"insert_after": "patient_immunization_section",
				"description": "Patient immunization/vaccination records"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	frappe.db.commit()
	
	print("✓ Patient Allergy and Immunization fields added to Medical History tab")


def hide_old_fields():
	"""Hide old 'allergies' and 'medication' text fields from Patient"""
	try:
		# Check if fields exist in Patient DocType
		patient_meta = frappe.get_meta("Patient")
		
		if patient_meta.has_field("allergies"):
			frappe.db.sql("""
				UPDATE `tabDocField` 
				SET hidden = 1 
				WHERE parent = 'Patient' AND fieldname = 'allergies'
			""")
			print("✓ Hidden old 'allergies' field")
		
		if patient_meta.has_field("medication"):
			frappe.db.sql("""
				UPDATE `tabDocField` 
				SET hidden = 1 
				WHERE parent = 'Patient' AND fieldname = 'medication'
			""")
			print("✓ Hidden old 'medication' field")
		
		frappe.db.commit()
	except Exception as e:
		print(f"Note: Could not hide old fields - {str(e)}")

