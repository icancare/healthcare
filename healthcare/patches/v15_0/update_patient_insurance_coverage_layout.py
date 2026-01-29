# Copyright (c) 2026, Healthcare Team
# For license information, please see license.txt

"""
Patch to update Patient Insurance layout:
1. Merge Coverage Details section - move Top Up Amount and Co-Pay Amount into Coverage Details
2. Remove section_break_7 between coverage fields
3. All 4 fields (Coverage Amount, Co-pay Percentage, Top Up Amount, Co-Pay Amount) in one section
"""

import frappe
from frappe.model.sync import sync_for


def execute():
	"""Execute the patch to update Patient Insurance layout"""
	
	try:
		# Clear cache and sync Patient Insurance doctype
		frappe.clear_cache(doctype='Patient Insurance')
		sync_for('Patient Insurance', force=True, reset_permissions=False)
		print("✓ Synced Patient Insurance - Coverage Details layout updated")
		
		frappe.db.commit()
		print("✓ Patient Insurance layout updated successfully")
	except Exception as e:
		print(f"✗ Error syncing Patient Insurance: {str(e)}")
		frappe.log_error("Error syncing Patient Insurance", str(e))
		raise
