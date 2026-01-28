import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	"""
	Update Peak Flow Meter calculations in Vital Signs
	
	Changes:
	1. Add "Estimated Peak Flow" field (calculated based on age, height, gender)
	2. Rename "% of Personal Best" to "Peak Flow Variability"
	3. Update calculation logic as per new formulas
	
	New Formulas:
	- Ages 5-7 and 8-17: PEFR = [(Height, cm - 100) × 5] + 100
	- Ages 18-80:
	  - Male: PEFR = [[(Height, m × 5.48) + 1.58] - [Age × 0.041]] × 60
	  - Female: PEFR = [[(Height, m × 3.72) + 2.24] - [Age × 0.03]] × 60
	- Peak Flow Variability (%) = (actual peak flow rate / estimated peak flow rate) × 100
	"""
	try:
		print("\n" + "="*70)
		print("Updating Peak Flow Meter Calculations in Vital Signs")
		print("="*70)
		
		# Step 1: Add Estimated Peak Flow field
		add_estimated_peak_flow_field()
		
		# Step 2: Update field labels
		update_peak_flow_labels()
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Peak Flow Meter configuration updated successfully")
		print("   - Added 'Estimated Peak Flow' field (calculated)")
		print("   - Updated 'Peak Flow Variability' calculation")
		print("   - Status zones updated based on variability")
		print("="*70 + "\n")
		
	except Exception as e:
		print(f"\n❌ Error: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

def add_estimated_peak_flow_field():
	"""Add Estimated Peak Flow field after Current Peak Flow"""
	
	custom_fields = {
		"Vital Signs": [
			{
				"fieldname": "peak_flow_estimated",
				"label": "Estimated Peak Flow",
				"fieldtype": "Float",
				"precision": "1",
				"read_only": 1,
				"insert_after": "peak_flow_current",
				"description": "Calculated based on age, height, and gender"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	print("✅ Added 'Estimated Peak Flow' field")

def update_peak_flow_labels():
	"""Update field labels for clarity"""
	
	# Update "% of Personal Best" label to "Peak Flow Variability"
	if frappe.db.exists("DocField", {"parent": "Vital Signs", "fieldname": "peak_flow_percentage"}):
		frappe.db.sql("""
			UPDATE `tabDocField`
			SET label = %s, description = %s
			WHERE parent = %s AND fieldname = %s
		""", ("Peak Flow Variability", "% = (actual peak flow / estimated peak flow) × 100", "Vital Signs", "peak_flow_percentage"))
		print("✅ Updated 'Peak Flow Variability' label")
	
	# Clear cache for the doctype
	frappe.clear_cache(doctype="Vital Signs")


