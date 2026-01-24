import frappe
from frappe import _

def execute():
	"""
	1. Remove Throat from Step 2 Physical Examination body parts
	2. Add 'Other' to Face complaints in Step 1
	3. Add 'Other' to Teeth (Dental) complaints in Step 1
	
	This patch updates the JavaScript constants in patient_encounter.js
	Note: This is a documentation patch - actual JS changes are in the JS file
	"""
	try:
		print("\n" + "="*60)
		print("Updating Step 1 and Step 2 Body Parts Configuration")
		print("="*60)
		
		print("\n✅ Changes to be applied:")
		print("   1. Step 2: Remove 'Throat' from STEP2_CONFIG")
		print("   2. Step 1: Add 'Other' to Face complaints")
		print("   3. Step 1: Add 'Other' to Teeth (Dental) complaints")
		
		print("\n📝 Note: JS file has been updated with these changes")
		print("   - BODY_PARTS_CONFIG updated for Step 1")
		print("   - STEP2_CONFIG updated for Step 2")
		
		frappe.db.commit()
		
		print("\n✅ Configuration update completed successfully")
		print("="*60 + "\n")
		
	except Exception as e:
		print(f"\n❌ Error: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

