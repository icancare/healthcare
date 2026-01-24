import frappe
from frappe import _

def execute():
	"""
	Update Alcohol and Substance Abuse History:
	1. Remove Discontinuation Details section from both
	2. Add computation fields to Alcohol History for Alcohol Years calculation
	"""
	try:
		# Remove discontinuation fields from Patient Alcohol History
		remove_fields_from_doctype("Patient Alcohol History", [
			"section_break_7",
			"discontinued_since",
			"discontinued_since_unit"
		])
		
		# Remove discontinuation fields from Patient Encounter Alcohol History
		remove_fields_from_doctype("Patient Encounter Alcohol History", [
			"section_break_7",
			"discontinued_since",
			"discontinued_since_unit"
		])
		
		# Remove discontinuation fields from Patient Substance Abuse History
		remove_fields_from_doctype("Patient Substance Abuse History", [
			"section_break_7",
			"discontinued_since",
			"discontinued_since_unit"
		])
		
		# Remove discontinuation fields from Patient Encounter Substance Abuse History
		remove_fields_from_doctype("Patient Encounter Substance Abuse History", [
			"section_break_7",
			"discontinued_since",
			"discontinued_since_unit"
		])
		
		# Add computation fields to Patient Alcohol History
		add_alcohol_computation_fields("Patient Alcohol History")
		
		# Add computation fields to Patient Encounter Alcohol History
		add_alcohol_computation_fields("Patient Encounter Alcohol History")
		
		# Update field order for Patient Alcohol History
		update_field_order("Patient Alcohol History", [
			"type",
			"column_break_3",
			"frequency",
			"quantity",
			"quantity_unit",
			"section_break_computation",
			"years_of_use",
			"column_break_comp",
			"alcohol_years",
			"section_break_10",
			"comment"
		])
		
		# Update field order for Patient Encounter Alcohol History
		update_field_order("Patient Encounter Alcohol History", [
			"type",
			"column_break_3",
			"frequency",
			"quantity",
			"quantity_unit",
			"section_break_computation",
			"years_of_use",
			"column_break_comp",
			"alcohol_years",
			"section_break_10",
			"comment"
		])
		
		# Update field order for Patient Substance Abuse History
		update_field_order("Patient Substance Abuse History", [
			"type",
			"column_break_3",
			"frequency",
			"quantity",
			"quantity_unit",
			"section_break_10",
			"comment"
		])
		
		# Update field order for Patient Encounter Substance Abuse History
		update_field_order("Patient Encounter Substance Abuse History", [
			"type",
			"column_break_3",
			"frequency",
			"quantity",
			"quantity_unit",
			"section_break_10",
			"comment"
		])
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Successfully updated Alcohol and Substance Abuse fields")
		print("   - Removed Discontinuation Details from all 4 tables")
		print("   - Added Years of Use and Alcohol Years computation fields to Alcohol History")
		
	except Exception as e:
		print(f"❌ Error updating fields: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

def remove_fields_from_doctype(doctype_name, fieldnames):
	"""Remove fields from a doctype"""
	meta = frappe.get_meta(doctype_name)
	for fieldname in fieldnames:
		field = meta.get_field(fieldname)
		if field:
			frappe.delete_doc("DocField", field.name, force=1, ignore_permissions=True)
			print(f"✅ Removed {doctype_name}.{fieldname}")

def add_alcohol_computation_fields(doctype_name):
	"""Add computation fields to alcohol history tables"""
	meta = frappe.get_meta(doctype_name)
	
	# Add section break for computation
	if not meta.get_field("section_break_computation"):
		doc = frappe.get_doc("DocType", doctype_name)
		doc.append("fields", {
			"fieldname": "section_break_computation",
			"fieldtype": "Section Break",
			"label": "Alcohol Years Calculation",
			"collapsible": 1
		})
		doc.save()
		print(f"✅ Added section_break_computation to {doctype_name}")
	
	# Add years_of_use field
	if not meta.get_field("years_of_use"):
		doc = frappe.get_doc("DocType", doctype_name)
		doc.append("fields", {
			"fieldname": "years_of_use",
			"fieldtype": "Int",
			"label": "Years of Use",
			"description": "Number of years using this alcohol type"
		})
		doc.save()
		print(f"✅ Added years_of_use to {doctype_name}")
	
	# Add column break
	if not meta.get_field("column_break_comp"):
		doc = frappe.get_doc("DocType", doctype_name)
		doc.append("fields", {
			"fieldname": "column_break_comp",
			"fieldtype": "Column Break"
		})
		doc.save()
		print(f"✅ Added column_break_comp to {doctype_name}")
	
	# Add alcohol_years field (computed)
	if not meta.get_field("alcohol_years"):
		doc = frappe.get_doc("DocType", doctype_name)
		doc.append("fields", {
			"fieldname": "alcohol_years",
			"fieldtype": "Float",
			"label": "Alcohol Years",
			"read_only": 1,
			"precision": 2,
			"description": "Alcohol Years = Quantity (Units/Day) × Years of Use. Example: 3 drinks/day × 20 years = 60 alcohol-years"
		})
		doc.save()
		print(f"✅ Added alcohol_years to {doctype_name}")

def update_field_order(doctype_name, field_order):
	"""Update field order for a doctype"""
	doc = frappe.get_doc("DocType", doctype_name)
	doc.field_order = field_order
	doc.save()
	print(f"✅ Updated field order for {doctype_name}")

