import frappe
from frappe import _

def execute():
	"""
	Change start_date and end_date fields in allergy tables from Date to Data type
	to allow flexible date entry (year only, year-month, or full date)
	
	Changes:
	1. Patient Allergy: start_date, end_date → Data field
	2. Patient Encounter Allergy: start_date, end_date → Data field
	
	This allows users to enter:
	- Year only: "2023"
	- Year and month: "Jan 2023", "2023-01"
	- Full date: "2023-01-15", "15 Jan 2023"
	"""
	try:
		# Change Patient Allergy fields
		change_field_type("Patient Allergy", "start_date")
		change_field_type("Patient Allergy", "end_date")
		
		# Change Patient Encounter Allergy fields
		change_field_type("Patient Encounter Allergy", "start_date")
		change_field_type("Patient Encounter Allergy", "end_date")
		
		frappe.clear_cache()
		print("✅ Changed allergy date fields to flexible format (Data type)")
		print("   Users can now enter: year only, year-month, or full date")
		
	except Exception as e:
		print(f"❌ Error changing allergy date fields: {str(e)}")
		frappe.log_error(f"Error in change_allergy_date_fields_to_flexible_format patch: {str(e)}")


def change_field_type(doctype, fieldname):
	"""Change a field from Date to Data type with flexible format"""
	try:
		# Get the DocType
		doc = frappe.get_doc("DocType", doctype)
		
		# Find the field
		field_found = False
		for field in doc.fields:
			if field.fieldname == fieldname:
				field_found = True
				old_type = field.fieldtype
				
				# Change to Data type
				field.fieldtype = "Data"
				
				# Update description and placeholder to indicate flexible format
				if fieldname == "start_date":
					field.description = "Examples: 2023, Jan 2023, January 2023, 15 Jan 2023, 2023-01-15"
					field.label = "Start Date"
					field.placeholder = "e.g., 2023 or Jan 2023"
				elif fieldname == "end_date":
					field.description = "Examples: 2023, Jan 2023, January 2023, 15 Jan 2023, 2023-01-15 (Leave blank if ongoing)"
					field.label = "End Date"
					field.placeholder = "e.g., 2024 or Feb 2024"
				
				break
		
		if field_found:
			# Save the DocType
			doc.save()
			print(f"  ✓ Changed {doctype}.{fieldname} from {old_type} to Data")
		else:
			print(f"  ⚠ Field {fieldname} not found in {doctype}")
			
	except Exception as e:
		print(f"  ✗ Error changing {doctype}.{fieldname}: {str(e)}")
		raise

