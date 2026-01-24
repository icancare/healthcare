import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	"""
	Add Gender field to Patient Encounter Children Details table
	This will sync with Patient Relation (Children Details) which already has Gender field
	"""
	try:
		# Add Gender field to Patient Encounter Children Details
		add_gender_field()
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Successfully added Gender field to Children Details:")
		print("   - Added to Patient Encounter Children Details table")
		print("   - Will sync with Patient Relation (Children Details)")
		
	except Exception as e:
		print(f"❌ Error: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

def add_gender_field():
	"""Add Gender field to Patient Encounter Children Details"""
	
	custom_fields = {
		"Patient Encounter Children Details": [
			{
				"fieldname": "gender",
				"label": "Gender",
				"fieldtype": "Select",
				"options": "\nMale\nFemale\nOther\nNot Disclosed",
				"insert_after": "child_number",
				"in_list_view": 0
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	print("✅ Added Gender field to Patient Encounter Children Details")

