import frappe
from frappe import _

def execute():
	"""
	Add 'is_hereditary' checkbox field to medical history tables
	
	This field indicates if a condition has hereditary/genetic factors
	Applies to both:
	1. Patient Medical History (self history)
	2. Patient Family Medical History
	"""
	try:
		# Add to Patient Medical History
		add_is_hereditary_field("Patient Medical History")
		
		# Add to Patient Family Medical History  
		add_is_hereditary_field("Patient Family Medical History")
		
		# Add to Patient Encounter Medical History
		add_is_hereditary_field("Patient Encounter Medical History")
		
		# Add to Patient Encounter Family Medical History
		add_is_hereditary_field("Patient Encounter Family Medical History")
		
		frappe.clear_cache()
		print("✅ Added 'is_hereditary' field to medical history tables")
		
	except Exception as e:
		print(f"❌ Error adding is_hereditary field: {str(e)}")
		frappe.log_error(f"Error in add_is_hereditary_to_medical_history patch: {str(e)}")


def add_is_hereditary_field(doctype):
	"""Add is_hereditary checkbox field to a doctype"""
	try:
		# Check if field already exists
		existing_field = frappe.db.get_value(
			"DocField",
			{"parent": doctype, "fieldname": "is_hereditary"},
			"name"
		)
		
		if existing_field:
			print(f"  ✓ is_hereditary field already exists in {doctype}")
			return
		
		# Get the DocType
		doc = frappe.get_doc("DocType", doctype)
		
		# Find position after 'undergoing_treatment' field
		insert_after = "undergoing_treatment"
		insert_idx = None
		
		for idx, field in enumerate(doc.fields):
			if field.fieldname == insert_after:
				insert_idx = idx + 1
				break
		
		if insert_idx is None:
			# If undergoing_treatment not found, add at end
			insert_idx = len(doc.fields)
		
		# Create new field
		new_field = frappe.new_doc("DocField")
		new_field.parent = doctype
		new_field.parenttype = "DocType"
		new_field.parentfield = "fields"
		new_field.fieldname = "is_hereditary"
		new_field.fieldtype = "Check"
		new_field.label = "Is Hereditary"
		new_field.description = "Check if this condition has hereditary/genetic factors"
		new_field.default = "0"
		
		# Insert field at the right position
		doc.fields.insert(insert_idx, new_field)
		
		# Update field_order if it exists (for non-child tables)
		if hasattr(doc, 'field_order') and doc.field_order:
			if "is_hereditary" not in doc.field_order:
				field_order_list = list(doc.field_order)
				# Add after undergoing_treatment
				if insert_after in field_order_list:
					pos = field_order_list.index(insert_after)
					field_order_list.insert(pos + 1, "is_hereditary")
				else:
					field_order_list.append("is_hereditary")
				doc.field_order = field_order_list
		
		# Save the DocType
		doc.save()
		print(f"  ✅ Added is_hereditary field to {doctype}")
		
	except Exception as e:
		print(f"  ✗ Error adding field to {doctype}: {str(e)}")
		raise

