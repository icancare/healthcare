import frappe
from frappe import _

def execute():
	"""
	Add Gender field to Patient Children Details DocType
	This ensures both Patient and Patient Encounter have Gender field in Children Details
	"""
	try:
		# Add Gender field to Patient Children Details
		add_gender_to_patient_children_details()
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Successfully added Gender field to Patient Children Details")
		
	except Exception as e:
		print(f"❌ Error: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

def add_gender_to_patient_children_details():
	"""Add Gender field to Patient Children Details DocType"""
	
	doctype_name = "Patient Children Details"
	
	if not frappe.db.exists("DocType", doctype_name):
		print(f"⚠️  DocType {doctype_name} does not exist")
		return
	
	# Check if gender field already exists
	if frappe.db.exists("DocField", {"parent": doctype_name, "fieldname": "gender"}):
		print(f"ℹ️  Gender field already exists in {doctype_name}")
		return
	
	# Get the DocType document
	doc = frappe.get_doc("DocType", doctype_name)
	
	# Find the position to insert (after child_number)
	insert_idx = 0
	for i, field in enumerate(doc.fields):
		if field.fieldname == "child_number":
			insert_idx = i + 1
			break
	
	# Create the gender field
	gender_field = frappe.new_doc("DocField")
	gender_field.fieldname = "gender"
	gender_field.label = "Gender"
	gender_field.fieldtype = "Select"
	gender_field.options = "\nMale\nFemale\nOther\nNot Disclosed"
	gender_field.in_list_view = 1
	gender_field.parent = doctype_name
	gender_field.parenttype = "DocType"
	gender_field.parentfield = "fields"
	
	# Insert the field
	doc.fields.insert(insert_idx, gender_field)
	
	# Update field_order
	doc.field_order = [field.fieldname for field in doc.fields]
	
	# Save the DocType
	doc.flags.ignore_validate = True
	doc.flags.ignore_permissions = True
	doc.save()
	
	print(f"✅ Added Gender field to {doctype_name}")
	
	# Reload the doctype
	frappe.clear_cache(doctype=doctype_name)

