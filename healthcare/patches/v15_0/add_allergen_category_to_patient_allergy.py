import frappe


def execute():
	"""
	Add allergen_category field to Patient Allergy child table
	This patch ensures the field exists in production
	"""
	
	# Check if field already exists
	if frappe.db.exists("DocField", {
		"parent": "Patient Allergy",
		"fieldname": "allergen_category"
	}):
		print("✓ allergen_category field already exists in Patient Allergy")
		return
	
	try:
		# Get the DocType
		doc = frappe.get_doc("DocType", "Patient Allergy")
		
		# Find the position to insert (before allergen field)
		allergen_idx = None
		for i, field in enumerate(doc.fields):
			if field.fieldname == "allergen":
				allergen_idx = i
				break
		
		if allergen_idx is None:
			print("❌ Could not find allergen field in Patient Allergy")
			return
		
		# Create new field
		new_field = frappe.new_doc("DocField")
		new_field.parent = "Patient Allergy"
		new_field.parenttype = "DocType"
		new_field.parentfield = "fields"
		new_field.fieldname = "allergen_category"
		new_field.fieldtype = "Link"
		new_field.label = "Allergen Category"
		new_field.options = "Allergen Category"
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
		
		print("✅ Added allergen_category field to Patient Allergy")
		
		frappe.db.commit()
		
	except Exception as e:
		print(f"❌ Error adding allergen_category field: {str(e)}")
		frappe.log_error(f"Error in add_allergen_category_to_patient_allergy patch: {str(e)}")

