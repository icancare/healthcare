import frappe
import json

def execute():
	"""Export all Patient Encounter custom fields to JSON for production sync"""
	print("\n" + "="*60)
	print("Exporting Patient Encounter Custom Fields")
	print("="*60)
	
	doctype = "Patient Encounter"
	
	# Get all custom fields
	fields = frappe.get_all('Custom Field', 
		filters={'dt': doctype},
		fields=['name', 'fieldname', 'fieldtype', 'label', 'insert_after', 'idx', 
				'hidden', 'depends_on', 'options', 'default', 'reqd', 'collapsible',
				'read_only', 'allow_on_submit', 'length', 'description']
	)
	
	print(f"Found {len(fields)} custom fields")
	
	# Export to JSON
	export_data = {
		'doctype': doctype,
		'fields': fields
	}
	
	# Save to file
	file_path = frappe.get_site_path('private', 'patient_encounter_custom_fields.json')
	with open(file_path, 'w') as f:
		json.dump(export_data, f, indent=2, default=str)
	
	print(f"Exported to: {file_path}")
	print("="*60 + "\n")
	
	return file_path
