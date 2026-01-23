import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Add allergen_category field to Patient Encounter Allergy child table
	"""
	
	# Check if field already exists
	if frappe.db.exists("DocField", {
		"parent": "Patient Encounter Allergy",
		"fieldname": "allergen_category"
	}):
		print("✓ allergen_category field already exists in Patient Encounter Allergy")
		return
	
	try:
		# Get the DocType
		doc = frappe.get_doc("DocType", "Patient Encounter Allergy")
		
		# Find the position to insert (before allergen field)
		allergen_idx = None
		for i, field in enumerate(doc.fields):
			if field.fieldname == "allergen":
				allergen_idx = i
				break
		
		if allergen_idx is None:
			print("❌ Could not find allergen field")
			return
		
		# Create new field
		new_field = frappe.new_doc("DocField")
		new_field.parent = "Patient Encounter Allergy"
		new_field.parenttype = "DocType"
		new_field.parentfield = "fields"
		new_field.fieldname = "allergen_category"
		new_field.fieldtype = "Link"
		new_field.label = "Allergen Category"
		new_field.options = "Allergen Category"
		new_field.in_list_view = 1
		new_field.description = "Select category to filter allergens"
		new_field.idx = allergen_idx + 1
		
		# Insert at the correct position
		doc.fields.insert(allergen_idx, new_field)
		
		# Update field_order
		if "allergen_category" not in doc.field_order:
			field_order_list = doc.field_order
			allergen_pos = field_order_list.index("allergen")
			field_order_list.insert(allergen_pos, "allergen_category")
			doc.field_order = field_order_list
		
		# Save the DocType
		doc.save()
		
		print("✅ Added allergen_category field to Patient Encounter Allergy")
		
		frappe.db.commit()
		
	except Exception as e:
		print(f"❌ Error adding allergen_category field: {str(e)}")
		frappe.log_error(f"Error in add_allergen_category_to_encounter_allergy patch: {str(e)}")

