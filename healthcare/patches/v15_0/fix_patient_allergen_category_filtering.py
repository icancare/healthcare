import frappe
from frappe import _

def execute():
	"""
	Fix allergen category and allergen field interaction in Patient form
	
	This patch ensures that:
	1. When allergen_category is selected first, allergen dropdown filters correctly
	2. When allergen is selected first, allergen_category auto-fills
	3. When allergen_category auto-fills, it doesn't clear the allergen field
	4. When allergen_category is manually changed, allergen field refreshes to show filtered options
	
	The fix is in the patient.js file's allergen_category event handler.
	This patch clears cache to ensure the updated JS is loaded.
	"""
	try:
		frappe.clear_cache()
		print("✅ Cleared cache - Patient allergen category filtering fix applied (v2)")
		print("📝 The allergen category and allergen fields now work correctly:")
		print("   - Select category first → allergen filters by category")
		print("   - Select allergen first → category auto-fills without clearing allergen")
		print("   - Change category manually → allergen field refreshes with new filter")
		
	except Exception as e:
		print(f"❌ Error in fix_patient_allergen_category_filtering patch: {str(e)}")
		frappe.log_error(f"Error in fix_patient_allergen_category_filtering patch: {str(e)}")

