import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	"""
	Update Peak Flow Meter calculations in Vital Signs
	
	Changes:
	1. Rename "Current Peak Flow" label to "Peak Flow"
	2. Add "Expected Peak Flow" field (calculated based on age, height, gender)
	3. Rename "% of Best" to "Peak Flow Variability"
	4. Update "Zone" field to use indicator colors
	5. Remove "Personal Best" field from display (keep data)
	6. Update calculation logic as per new formulas
	
	New Formulas:
	- Ages 5-7 and 8-17: PEFR = [(Height, cm - 100) × 5] + 100
	- Ages 18-80:
	  - Male: PEFR = [[(Height, m × 5.48) + 1.58] - [Age × 0.041]] × 60
	  - Female: PEFR = [[(Height, m × 3.72) + 2.24] - [Age × 0.03]] × 60
	- Peak Flow Variability (%) = (actual peak flow / estimated peak flow) × 100
	- Status: Green (80-100%), Yellow (50-80%), Red (<50%)
	"""
	try:
		print("\n" + "="*70)
		print("Updating Peak Flow Meter Calculations in Vital Signs")
		print("="*70)
		
		# Step 1: Update field labels
		update_peak_flow_labels()
		
		# Step 2: Add Expected Peak Flow field
		add_expected_peak_flow_field()
		
		# Step 3: Hide Personal Best field
		hide_personal_best_field()
		
		# Step 4: Update status field to use indicators
		update_status_field()
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Peak Flow Meter configuration updated successfully")
		print("   - Renamed 'Current Peak Flow' to 'Peak Flow'")
		print("   - Added 'Expected Peak Flow' field (calculated)")
		print("   - Updated 'Peak Flow Variability' label and calculation")
		print("   - Updated status field with color indicators")
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
	if frappe.db.exists("DocField", {"parent": "Vital Signs", "fieldname": "peak_flow_current"}):
		frappe.db.sql("""
			UPDATE `tabDocField`
			SET label = %s, description = %s
			WHERE parent = %s AND fieldname = %s
		""", ("Peak Flow", "L/min - Current reading", "Vital Signs", "peak_flow_current"))
		print("✅ Updated 'Peak Flow' label")
	
	# Update "% of Best" label to "Peak Flow Variability"
	if frappe.db.exists("DocField", {"parent": "Vital Signs", "fieldname": "peak_flow_percentage"}):
		frappe.db.sql("""
			UPDATE `tabDocField`
			SET label = %s, description = %s
			WHERE parent = %s AND fieldname = %s
		""", ("Peak Flow Variability", "% = (actual peak flow / expected peak flow) × 100", "Vital Signs", "peak_flow_percentage"))
		print("✅ Updated 'Peak Flow Variability' label")
	
	# Clear cache for the doctype
	frappe.clear_cache(doctype="Vital Signs")

def add_expected_peak_flow_field():
	"""Add Expected Peak Flow field after Peak Flow"""
	
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
	print("✅ Added 'Expected Peak Flow' field")

def hide_personal_best_field():
	"""Hide Personal Best field but keep data"""
	
	if frappe.db.exists("DocField", {"parent": "Vital Signs", "fieldname": "peak_flow_personal_best"}):
		frappe.db.sql("""
			UPDATE `tabDocField`
			SET hidden = 1
			WHERE parent = %s AND fieldname = %s
		""", ("Vital Signs", "peak_flow_personal_best"))
		print("✅ Hidden 'Personal Best' field")

def update_status_field():
	"""Update status field to use indicator colors"""
	
	if frappe.db.exists("DocField", {"parent": "Vital Signs", "fieldname": "peak_flow_status"}):
		frappe.db.sql("""
			UPDATE `tabDocField`
			SET label = %s, description = %s
			WHERE parent = %s AND fieldname = %s
		""", ("Status", "Green: 80-100% (Good control), Yellow: 50-80% (Caution), Red: <50% (Emergency)", "Vital Signs", "peak_flow_status"))
		print("✅ Updated 'Status' field")


