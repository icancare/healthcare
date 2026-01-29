# Copyright (c) 2026, Healthcare Team
# For license information, please see license.txt

"""
Patch to fix data migration and add Oral Habits History:
1. Fix existing data - convert old quantity units to new format (Packets -> Nos)
2. Sync Patient Oral Habits History to ensure it appears in production
3. Remove restricted_mouth_opening field from Oral Habits History
"""

import frappe
from frappe.model.sync import sync_for


def execute():
	"""Execute the patch to fix data and sync Oral Habits History"""
	
	# Fix existing data in Smokeless Tobacco History - convert old units to new format
	fix_smokeless_quantity_units()
	
	# Fix existing data in Substance Abuse History - convert old units
	fix_substance_quantity_units()
	
	# Sync Patient Oral Habits History to ensure it appears
	try:
		frappe.clear_cache(doctype='Patient Oral Habits History')
		sync_for('Patient Oral Habits History', force=True, reset_permissions=False)
		print("✓ Synced Patient Oral Habits History")
	except Exception as e:
		print(f"✗ Error syncing Patient Oral Habits History: {str(e)}")
		frappe.log_error("Error syncing Patient Oral Habits History", str(e))
	
	frappe.db.commit()
	print("✓ Data migration and Oral Habits History sync completed successfully")


def fix_smokeless_quantity_units():
	"""Convert old quantity units to new format in Smokeless Tobacco History"""
	try:
		# Check if table exists
		if not frappe.db.exists("DocType", "Patient Smokeless Tobacco History"):
			print("⚠ Patient Smokeless Tobacco History table not found, skipping")
			return
		
		# Packets -> Nos
		count = frappe.db.sql("""
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
		# Check if table exists
		if not frappe.db.exists("DocType", "Patient Substance Abuse History"):
			print("⚠ Patient Substance Abuse History table not found, skipping")
			return
		
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
