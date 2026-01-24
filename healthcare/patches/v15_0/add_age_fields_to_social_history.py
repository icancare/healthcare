import frappe
from frappe import _

def execute():
	"""
	Add age-based fields to Smoking, Smokeless, and Substance Abuse History
	
	Changes:
	1. Remove old discontinued_since fields
	2. Add started_at_age, discontinued_at_age, used_for_years
	3. Update field order for clean layout
	"""
	try:
		# Tables to update
		tables = [
			"Patient Smoking Tobacco History",
			"Patient Encounter Smoking Tobacco History",
			"Patient Smokeless Tobacco History",
			"Patient Encounter Smokeless Tobacco History",
			"Patient Substance Abuse History",
			"Patient Encounter Substance Abuse History"
		]
		
		for table in tables:
			# Remove old discontinuation fields
			remove_old_fields(table)
			
			# Add new age fields
			add_age_fields(table)
			
			# Update field order
			update_field_order_for_table(table)
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Successfully added age fields to social history")
		print("   - Removed old discontinued_since fields")
		print("   - Added started_at_age, discontinued_at_age, used_for_years")
		print("   - Updated layout for all 6 tables")
		
	except Exception as e:
		print(f"❌ Error adding age fields: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

def remove_old_fields(doctype_name):
	"""Remove old discontinuation fields"""
	meta = frappe.get_meta(doctype_name)
	
	fields_to_remove = ["section_break_7", "discontinued_since", "discontinued_since_unit"]
	
	for fieldname in fields_to_remove:
		field = meta.get_field(fieldname)
		if field:
			frappe.delete_doc("DocField", field.name, force=1, ignore_permissions=True)
			print(f"✅ Removed {doctype_name}.{fieldname}")

def add_age_fields(doctype_name):
	"""Add age-based fields"""
	meta = frappe.get_meta(doctype_name)
	doc = frappe.get_doc("DocType", doctype_name)
	
	# Add column break
	if not meta.get_field("column_break_age"):
		doc.append("fields", {
			"fieldname": "column_break_age",
			"fieldtype": "Column Break"
		})
		print(f"✅ Added column_break_age to {doctype_name}")
	
	# Add started_at_age
	if not meta.get_field("started_at_age"):
		doc.append("fields", {
			"fieldname": "started_at_age",
			"fieldtype": "Int",
			"label": "Started at Age (Year)",
			"description": "Age when started using"
		})
		print(f"✅ Added started_at_age to {doctype_name}")
	
	# Add discontinued_at_age
	if not meta.get_field("discontinued_at_age"):
		doc.append("fields", {
			"fieldname": "discontinued_at_age",
			"fieldtype": "Int",
			"label": "Discontinued at Age (Year)",
			"description": "Age when discontinued (leave blank if ongoing)"
		})
		print(f"✅ Added discontinued_at_age to {doctype_name}")
	
	# Add used_for_years (computed)
	if not meta.get_field("used_for_years"):
		doc.append("fields", {
			"fieldname": "used_for_years",
			"fieldtype": "Int",
			"label": "Used for # Years",
			"read_only": 1,
			"description": "Computed: Discontinued Age - Started Age + 1 (or Current Age - Started Age + 1 if ongoing)"
		})
		print(f"✅ Added used_for_years to {doctype_name}")
	
	doc.save()

def update_field_order_for_table(doctype_name):
	"""Update field order for clean layout"""
	
	new_field_order = [
		"type",
		"column_break_3",
		"frequency",
		"quantity",
		"quantity_unit",
		"column_break_age",
		"started_at_age",
		"discontinued_at_age",
		"used_for_years",
		"section_break_10",
		"comment"
	]
	
	doc = frappe.get_doc("DocType", doctype_name)
	doc.field_order = new_field_order
	doc.save()
	
	print(f"✅ Updated field order for {doctype_name}")

