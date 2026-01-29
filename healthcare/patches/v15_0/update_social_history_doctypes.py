# Copyright (c) 2026, Healthcare Team
# For license information, please see license.txt

"""
Patch to update Social History DocTypes:
1. Update Patient Smoking Tobacco History - add age-related fields, remove discontinuation section
2. Update Patient Smokeless Tobacco History - simplify structure, update quantity units
3. Update Patient Substance Abuse History - simplify structure
4. Update Medical History - add validation for 'when' field
5. Fix existing data - convert old quantity units to new format
6. Update Patient Oral Habits History - remove restricted_mouth_opening field
"""

import frappe
from frappe.model.sync import sync_for


def execute():
	"""Execute the patch to update Social History doctypes"""
	
	# Fix existing data in Smokeless Tobacco History - convert old units to new format
	fix_smokeless_quantity_units()
	
	# Fix existing data in Substance Abuse History - convert old units
	fix_substance_quantity_units()
	
	# Sync doctypes to ensure JSON changes are reflected
	doctypes_to_sync = [
		'Patient Medical History',
		'Patient Family Medical History',
		'Patient Smoking Tobacco History',
		'Patient Smokeless Tobacco History',
		'Patient Substance Abuse History',
		'Patient Oral Habits History'
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


def fix_smokeless_quantity_units():
	"""Convert old quantity units to new format in Smokeless Tobacco History"""
	try:
		# Packets -> Nos
		frappe.db.sql("""
			UPDATE `tabPatient Smokeless Tobacco History`
			SET quantity_unit = 'Nos'
			WHERE quantity_unit = 'Packets'
		""")
		
		# Numbers -> Nos
		frappe.db.sql("""
			UPDATE `tabPatient Smokeless Tobacco History`
			SET quantity_unit = 'Nos'
			WHERE quantity_unit = 'Numbers'
		""")
		
		# Pieces -> Nos
		frappe.db.sql("""
			UPDATE `tabPatient Smokeless Tobacco History`
			SET quantity_unit = 'Nos'
			WHERE quantity_unit = 'Pieces'
		""")
		
		frappe.db.commit()
		print("✓ Fixed Smokeless Tobacco History quantity units")
	except Exception as e:
		print(f"✗ Error fixing smokeless units: {str(e)}")
		frappe.log_error("Error fixing smokeless units", str(e))


def fix_substance_quantity_units():
	"""Convert old quantity units to new format in Substance Abuse History"""
	try:
		# Packets -> Numbers
		frappe.db.sql("""
			UPDATE `tabPatient Substance Abuse History`
			SET quantity_unit = 'Numbers'
			WHERE quantity_unit = 'Packets'
		""")
		
		# Pieces -> Numbers
		frappe.db.sql("""
			UPDATE `tabPatient Substance Abuse History`
			SET quantity_unit = 'Numbers'
			WHERE quantity_unit = 'Pieces'
		""")
		
		frappe.db.commit()
		print("✓ Fixed Substance Abuse History quantity units")
	except Exception as e:
		print(f"✗ Error fixing substance units: {str(e)}")
		frappe.log_error("Error fixing substance units", str(e))

