import frappe
from frappe import _

def execute():
	"""
	Fix Peak Flow Meter fields - Final version
	
	Changes:
	1. Remove duplicate "Estimated Peak Flow" field
	2. Keep only "Expected Peak Flow" field
	3. Update field order properly
	4. Ensure calculations work correctly
	"""
	try:
		print("\n" + "="*70)
		print("Fixing Peak Flow Meter Fields - Final")
		print("="*70)
		
		# Step 1: Delete old "Estimated Peak Flow" custom field
		delete_old_estimated_field()
		
		# Step 2: Ensure Expected Peak Flow field is properly positioned
		fix_expected_field_position()
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Peak Flow Meter fields fixed successfully")
		print("   - Removed duplicate 'Estimated Peak Flow' field")
		print("   - Kept 'Expected Peak Flow' field with proper position")
		print("="*70 + "\n")
		
	except Exception as e:
		print(f"\n❌ Error: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

def delete_old_estimated_field():
	"""Delete the old peak_flow_estimated custom field"""
	
	if frappe.db.exists("Custom Field", {"dt": "Vital Signs", "fieldname": "peak_flow_estimated"}):
		frappe.delete_doc("Custom Field", 
			frappe.db.get_value("Custom Field", {"dt": "Vital Signs", "fieldname": "peak_flow_estimated"}, "name"),
			force=True
		)
		print("✅ Deleted old 'Estimated Peak Flow' field")
	else:
		print("ℹ️  Old 'Estimated Peak Flow' field not found")

def fix_expected_field_position():
	"""Ensure Expected Peak Flow field is in correct position"""
	
	if frappe.db.exists("Custom Field", {"dt": "Vital Signs", "fieldname": "peak_flow_expected"}):
		frappe.db.sql("""
			UPDATE `tabCustom Field`
			SET insert_after = %s, idx = (
				SELECT COALESCE(MAX(idx), 0) + 1 
				FROM (SELECT idx FROM `tabDocField` WHERE parent = %s) as temp
			)
			WHERE dt = %s AND fieldname = %s
		""", ("peak_flow_current", "Vital Signs", "Vital Signs", "peak_flow_expected"))
		print("✅ Fixed 'Expected Peak Flow' field position")
