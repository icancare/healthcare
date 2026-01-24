import frappe
from frappe import _

def execute():
	"""
	Improve Alcohol History layout:
	- Move Years of Use and Alcohol Years fields up (after quantity fields)
	- Remove "Additional Information" section break
	- Rename section to "Alcohol Years Calculation" -> remove it
	- Make layout cleaner
	"""
	try:
		# Update Patient Alcohol History layout
		update_alcohol_history_layout("Patient Alcohol History")
		
		# Update Patient Encounter Alcohol History layout
		update_alcohol_history_layout("Patient Encounter Alcohol History")
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Successfully improved Alcohol History layout")
		print("   - Moved Years of Use and Alcohol Years fields up")
		print("   - Cleaned up section breaks")
		
	except Exception as e:
		print(f"❌ Error improving layout: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

def update_alcohol_history_layout(doctype_name):
	"""Update field order for cleaner layout"""
	
	# Remove the computation section break
	meta = frappe.get_meta(doctype_name)
	section_field = meta.get_field("section_break_computation")
	if section_field:
		frappe.delete_doc("DocField", section_field.name, force=1, ignore_permissions=True)
		print(f"✅ Removed section_break_computation from {doctype_name}")
	
	# Remove column break
	col_field = meta.get_field("column_break_comp")
	if col_field:
		frappe.delete_doc("DocField", col_field.name, force=1, ignore_permissions=True)
		print(f"✅ Removed column_break_comp from {doctype_name}")
	
	# Update field order - Years of Use and Alcohol Years right after quantity fields
	new_field_order = [
		"type",
		"column_break_3",
		"frequency",
		"quantity",
		"quantity_unit",
		"column_break_years",
		"years_of_use",
		"alcohol_years",
		"section_break_10",
		"comment"
	]
	
	doc = frappe.get_doc("DocType", doctype_name)
	
	# Add new column break if it doesn't exist
	if not meta.get_field("column_break_years"):
		doc.append("fields", {
			"fieldname": "column_break_years",
			"fieldtype": "Column Break"
		})
		print(f"✅ Added column_break_years to {doctype_name}")
	
	doc.field_order = new_field_order
	doc.save()
	
	print(f"✅ Updated field order for {doctype_name}")

