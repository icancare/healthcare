import frappe
from frappe import _

def execute():
	"""
	Fix Gender field position in both Patient Children Details and Patient Encounter Children Details
	Gender should come after Child #, not before it
	
	Correct order:
	1. Child #
	2. Gender
	3. Age At Delivery
	4. Delivery Type
	5. Comment
	"""
	try:
		# Fix Patient Children Details
		fix_field_order("Patient Children Details")
		
		# Fix Patient Encounter Children Details
		fix_field_order("Patient Encounter Children Details")
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Successfully fixed Gender field position in Children Details")
		
	except Exception as e:
		print(f"❌ Error: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

def fix_field_order(doctype_name):
	"""Fix field order in the given doctype"""
	
	if not frappe.db.exists("DocType", doctype_name):
		print(f"⚠️  DocType {doctype_name} does not exist")
		return
	
	# Get the DocType document
	doc = frappe.get_doc("DocType", doctype_name)
	
	# Define the correct field order
	correct_order = [
		"child_number",
		"gender",
		"age_at_delivery",
		"column_break_3",
		"delivery_type",
		"comment"
	]
	
	# Create a mapping of fieldname to field object
	field_map = {field.fieldname: field for field in doc.fields}
	
	# Reorder fields according to correct_order
	new_fields = []
	for fieldname in correct_order:
		if fieldname in field_map:
			new_fields.append(field_map[fieldname])
	
	# Add any remaining fields that weren't in correct_order
	for field in doc.fields:
		if field.fieldname not in correct_order:
			new_fields.append(field)
	
	# Update the fields list
	doc.fields = new_fields
	
	# Update field_order
	doc.field_order = [field.fieldname for field in doc.fields]
	
	# Update idx for each field
	for i, field in enumerate(doc.fields):
		field.idx = i + 1
	
	# Save the DocType
	doc.flags.ignore_validate = True
	doc.flags.ignore_permissions = True
	doc.save()
	
	print(f"✅ Fixed field order in {doctype_name}")
	
	# Also update idx in database directly to ensure consistency
	for i, field in enumerate(doc.fields):
		frappe.db.sql("""
			UPDATE `tabDocField`
			SET idx = %s
			WHERE parent = %s AND fieldname = %s
		""", (i + 1, doctype_name, field.fieldname))
	
	# Reload the doctype
	frappe.clear_cache(doctype=doctype_name)

