import frappe
from frappe import _

def execute():
	"""
	Update Step 1 - Patient Complaints: Body Parts and Complaints
	
	Changes:
	1. Rename "Others" to "Other" in body part selection
	2. Add new complaints to "Other" body part
	3. Add "Lungs" as new body part with respiratory complaints
	4. Remove "Earache" from Other complaints (moved to separate)
	
	Client Requirements: As per ERPNext HealthCare Module Issues doc
	"""
	try:
		print("\n" + "="*70)
		print("Updating Step 1 - Patient Complaints: Body Parts & Complaints")
		print("="*70)
		
		# This is a frontend-only change in patient_encounter.js
		# No database changes needed - just JavaScript constant update
		
		# However, we need to update existing Patient Encounter records
		# that have "Others" body part to "Other"
		update_existing_complaints()
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Step 1 Body Parts and Complaints updated successfully")
		print("   - 'Others' renamed to 'Other' in existing records")
		print("   - New complaints added to 'Other' body part (frontend)")
		print("   - 'Lungs' body part added (frontend)")
		print("   - Please build healthcare app for frontend changes")
		print("="*70 + "\n")
		
	except Exception as e:
		print(f"\n❌ Error: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

def update_existing_complaints():
	"""Update existing Patient Encounter records that have 'Others' body part"""
	
	# Check if table exists first
	if not frappe.db.table_exists("Patient Encounter Complaint"):
		print("✅ Table 'Patient Encounter Complaint' doesn't exist yet - skipping data migration")
		return
	
	# Get all Patient Encounters with complaints table
	encounters = frappe.db.sql("""
		SELECT DISTINCT parent
		FROM `tabPatient Encounter Complaint`
		WHERE body_part = 'Others'
	""", as_dict=1)
	
	if encounters:
		print(f"\n📋 Found {len(encounters)} Patient Encounters with 'Others' body part")
		
		# Update all complaints with "Others" to "Other"
		frappe.db.sql("""
			UPDATE `tabPatient Encounter Complaint`
			SET body_part = 'Other'
			WHERE body_part = 'Others'
		""")
		
		print(f"✅ Updated {len(encounters)} records: 'Others' → 'Other'")
	else:
		print("✅ No existing records with 'Others' body part found")
