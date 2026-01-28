import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	"""
	Update Peak Flow Meter fields in Vital Signs - Version 2
	
	Changes:
	1. Rename "Current Peak Flow" label to "Peak Flow"
	2. Add "Expected Peak Flow" field (calculated based on age, height, gender)
	3. Rename "% of Best" to "Peak Flow Variability"
	4. Update "Zone" field label to "Status" with proper description
	5. Hide "Personal Best" field (keep data)
	
	Formulas:
	- Ages 5-17: PEFR = [(Height, cm - 100) × 5] + 100
	- Ages 18-80:
	  - Male: PEFR = [[(Height, m × 5.48) + 1.58] - [Age × 0.041]] × 60
	  - Female: PEFR = [[(Height, m × 3.72) + 2.24] - [Age × 0.03]] × 60
	- Peak Flow Variability (%) = (actual peak flow / expected peak flow) × 100
	- Status: Green (80-100%), Yellow (50-80%), Red (<50%)
	"""
	try:
		print("\n" + "="*70)
		print("Updating Peak Flow Meter Fields in Vital Signs - V2")
		print("="*70)
		
		# Step 1: Update field labels
		update_peak_flow_labels()
		
		# Step 2: Add Expected Peak Flow field
		add_expected_peak_flow_field()
		
		# Step 3: Hide Personal Best field
		hide_personal_best_field()
		
		# Step 4: Update status field
		update_status_field()
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Peak Flow Meter fields updated successfully")
		print("   - Renamed 'Current Peak Flow' to 'Peak Flow'")
		print("   - Added 'Expected Peak Flow' field (calculated)")
		print("   - Updated 'Peak Flow Variability' label")
		print("   - Updated 'Status' field description")
		print("   - Hidden 'Personal Best' field")
		print("="*70 + "\n")
		
	except Exception as e:
		print(f"\n❌ Error: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

def update_peak_flow_labels():
	"""Update field labels for clarity"""
	
	# Update "Current Peak Flow" label to "Peak Flow"
	frappe.db.sql("""
		UPDATE `tabDocField`
		SET label = %s, description = %s
		WHERE parent = %s AND fieldname = %s
	""", ("Peak Flow", "L/min - Current reading", "Vital Signs", "peak_flow_current"))
	print("✅ Updated 'Peak Flow' label")
	
	# Update "% of Best" label to "Peak Flow Variability"
	frappe.db.sql("""
		UPDATE `tabDocField`
		SET label = %s, description = %s
		WHERE parent = %s AND fieldname = %s
	""", ("Peak Flow Variability", "% = (actual peak flow / expected peak flow) × 100", "Vital Signs", "peak_flow_percentage"))
	print("✅ Updated 'Peak Flow Variability' label")

def add_expected_peak_flow_field():
	"""Add Expected Peak Flow field after Peak Flow"""
	
	# Check if field already exists
	if frappe.db.exists("Custom Field", {"dt": "Vital Signs", "fieldname": "peak_flow_expected"}):
		print("ℹ️  'Expected Peak Flow' field already exists, updating...")
		frappe.db.sql("""
			UPDATE `tabCustom Field`
			SET label = %s, description = %s, fieldtype = %s, 
			    `precision` = %s, read_only = %s, insert_after = %s
			WHERE dt = %s AND fieldname = %s
		""", ("Expected Peak Flow", "Calculated based on age, height, and gender", 
		      "Float", "1", 1, "peak_flow_current", "Vital Signs", "peak_flow_expected"))
	else:
		custom_fields = {
			"Vital Signs": [
				{
					"fieldname": "peak_flow_expected",
					"label": "Expected Peak Flow",
					"fieldtype": "Float",
					"precision": "1",
					"read_only": 1,
					"insert_after": "peak_flow_current",
					"description": "Calculated based on age, height, and gender"
				}
			]
		}
		create_custom_fields(custom_fields, update=True)
	
	print("✅ Added/Updated 'Expected Peak Flow' field")

def hide_personal_best_field():
	"""Hide Personal Best field but keep data"""
	
	frappe.db.sql("""
		UPDATE `tabDocField`
		SET hidden = 1
		WHERE parent = %s AND fieldname = %s
	""", ("Vital Signs", "peak_flow_personal_best"))
	print("✅ Hidden 'Personal Best' field")

def update_status_field():
	"""Update status field description"""
	
	frappe.db.sql("""
		UPDATE `tabDocField`
		SET label = %s, description = %s
		WHERE parent = %s AND fieldname = %s
	""", ("Status", "Green: 80-100% (Good control), Yellow: 50-80% (Caution), Red: <50% (Emergency)", 
	      "Vital Signs", "peak_flow_status"))
	print("✅ Updated 'Status' field")
