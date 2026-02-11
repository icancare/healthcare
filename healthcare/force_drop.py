
import frappe

def execute():
	print("Force Dropping Tobacco Columns from SQL...")
	table = "tabPatient Encounter"
	columns = frappe.db.sql(f"SHOW COLUMNS FROM `{table}`", as_dict=1)
	
	tobacco_cols = [c['Field'] for c in columns if c['Field'].startswith('tobacco_')]
	print(f"Found {len(tobacco_cols)} columns to drop.")
	
	if not tobacco_cols:
		return

	# Drop in batches or one by one?
	# One valid ALTER table statement is better.
	drop_list = ", ".join([f"DROP COLUMN `{col}`" for col in tobacco_cols])
	path = f"ALTER TABLE `{table}` {drop_list}"
	
	try:
		frappe.db.sql(path)
		print("✓ Successfully dropped columns.")
		frappe.db.commit()
	except Exception as e:
		print(f"Error dropping columns: {e}")

