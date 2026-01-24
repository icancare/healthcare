import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	"""
	Complete fix for social history:
	1. Fix layout for Smokeless, Substance Abuse (age fields before Additional Info)
	2. Fix layout for Alcohol (years fields before Additional Info)
	3. Add Pack Years and Bidi Pack Years to Smoking Tobacco History
	"""
	try:
		# Step 1: Fix Smokeless Tobacco layout
		fix_smokeless_layout()
		
		# Step 2: Fix Substance Abuse layout
		fix_substance_abuse_layout()
		
		# Step 3: Fix Alcohol layout
		fix_alcohol_layout()
		
		# Step 4: Add Pack Years fields to Smoking Tobacco
		add_pack_years_fields()
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Successfully completed all social history fixes:")
		print("   - Fixed Smokeless Tobacco layout")
		print("   - Fixed Substance Abuse layout")
		print("   - Fixed Alcohol layout")
		print("   - Added Pack Years and Bidi Pack Years to Smoking")
		
	except Exception as e:
		print(f"❌ Error: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

def fix_smokeless_layout():
	"""Fix Smokeless Tobacco - age fields should be after quantity_unit"""
	tables = [
		"Patient Smokeless Tobacco History",
		"Patient Encounter Smokeless Tobacco History"
	]
	
	for table in tables:
		doc = frappe.get_doc("DocType", table)
		doc.field_order = [
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
		doc.save()
		print(f"✅ Fixed layout: {table}")

def fix_substance_abuse_layout():
	"""Fix Substance Abuse - age fields should be after quantity_unit"""
	tables = [
		"Patient Substance Abuse History",
		"Patient Encounter Substance Abuse History"
	]
	
	for table in tables:
		doc = frappe.get_doc("DocType", table)
		doc.field_order = [
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
		doc.save()
		print(f"✅ Fixed layout: {table}")

def fix_alcohol_layout():
	"""Fix Alcohol - years fields should be after quantity_unit"""
	tables = [
		"Patient Alcohol History",
		"Patient Encounter Alcohol History"
	]
	
	for table in tables:
		doc = frappe.get_doc("DocType", table)
		doc.field_order = [
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
		doc.save()
		print(f"✅ Fixed layout: {table}")

def add_pack_years_fields():
	"""Add Pack Years and Bidi Pack Years to Smoking Tobacco History"""
	
	# Fields for Patient Smoking Tobacco History
	patient_fields = {
		"Patient Smoking Tobacco History": [
			{
				"fieldname": "pack_years",
				"label": "Pack Years",
				"fieldtype": "Float",
				"precision": 2,
				"read_only": 1,
				"insert_after": "used_for_years",
				"description": "Computed as: (Cigarettes per day / 20) × Years Smoked (for Cigarette type only)"
			},
			{
				"fieldname": "bidi_pack_years",
				"label": "Bidi Pack Years",
				"fieldtype": "Float",
				"precision": 2,
				"read_only": 1,
				"insert_after": "pack_years",
				"description": "Computed as: (Bidis per day / 4) / 20 × Years Smoked (for Bidi type only)"
			}
		],
		"Patient Encounter Smoking Tobacco History": [
			{
				"fieldname": "pack_years",
				"label": "Pack Years",
				"fieldtype": "Float",
				"precision": 2,
				"read_only": 1,
				"insert_after": "used_for_years",
				"description": "Computed as: (Cigarettes per day / 20) × Years Smoked (for Cigarette type only)"
			},
			{
				"fieldname": "bidi_pack_years",
				"label": "Bidi Pack Years",
				"fieldtype": "Float",
				"precision": 2,
				"read_only": 1,
				"insert_after": "pack_years",
				"description": "Computed as: (Bidis per day / 4) / 20 × Years Smoked (for Bidi type only)"
			}
		]
	}
	
	create_custom_fields(patient_fields, update=True)
	
	# Update field order to include pack years
	for table in ["Patient Smoking Tobacco History", "Patient Encounter Smoking Tobacco History"]:
		doc = frappe.get_doc("DocType", table)
		doc.field_order = [
			"type",
			"column_break_3",
			"frequency",
			"quantity",
			"quantity_unit",
			"column_break_age",
			"started_at_age",
			"discontinued_at_age",
			"used_for_years",
			"pack_years",
			"bidi_pack_years",
			"section_break_10",
			"comment"
		]
		doc.save()
		print(f"✅ Added Pack Years fields to: {table}")

