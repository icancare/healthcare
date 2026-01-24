import frappe
from frappe import _

def execute():
	"""
	Fix layout of age fields in social history - move them BEFORE Additional Information section
	Age fields should be right after quantity fields, not inside Additional Information
	"""
	try:
		# Tables to fix
		tables = [
			"Patient Smoking Tobacco History",
			"Patient Encounter Smoking Tobacco History",
			"Patient Smokeless Tobacco History",
			"Patient Encounter Smokeless Tobacco History",
			"Patient Substance Abuse History",
			"Patient Encounter Substance Abuse History"
		]
		
		for table in tables:
			fix_field_order(table)
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Successfully fixed age fields layout")
		print("   - Age fields now appear right after quantity fields")
		print("   - Before Additional Information section")
		
	except Exception as e:
		print(f"❌ Error fixing layout: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

def fix_field_order(doctype_name):
	"""Fix field order - age fields should be BEFORE section_break_10"""
	
	# Correct order: Type, Frequency, Quantity, AGE FIELDS, then Additional Info
	correct_field_order = [
		"type",
		"column_break_3",
		"frequency",
		"quantity",
		"quantity_unit",
		"column_break_age",
		"started_at_age",
		"discontinued_at_age",
		"used_for_years",
		"section_break_10",  # Additional Information section AFTER age fields
		"comment"
	]
	
	doc = frappe.get_doc("DocType", doctype_name)
	doc.field_order = correct_field_order
	doc.save()
	
	print(f"✅ Fixed field order for {doctype_name}")

