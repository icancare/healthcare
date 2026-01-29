# Copyright (c) 2026, Healthcare Team
# For license information, please see license.txt

"""
Patch to update Social History DocTypes:
1. Update Patient Smoking Tobacco History - add age-related fields, remove discontinuation section
2. Update Patient Smokeless Tobacco History - simplify structure, update quantity units
3. Update Patient Substance Abuse History - simplify structure
4. Update Medical History - add validation for 'when' field
"""

import frappe
from frappe.model.sync import sync_for


def execute():
	"""Execute the patch to update Social History doctypes"""
	
	# Sync doctypes to ensure JSON changes are reflected
	doctypes_to_sync = [
		'Patient Medical History',
		'Patient Family Medical History',
		'Patient Smoking Tobacco History',
		'Patient Smokeless Tobacco History',
		'Patient Substance Abuse History'
	]
	
	for doctype in doctypes_to_sync:
		try:
			frappe.clear_cache(doctype=doctype)
			sync_for(doctype, force=True, reset_permissions=False)
			print(f"✓ Synced {doctype}")
		except Exception as e:
			print(f"✗ Error syncing {doctype}: {str(e)}")
			frappe.log_error(f"Error syncing {doctype}", str(e))
	
	frappe.db.commit()
	print("✓ Social History DocTypes updated successfully")
