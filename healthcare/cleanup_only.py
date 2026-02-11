
import frappe

def execute():
	print("Starting Cleanup Only...")
	fields = frappe.get_all("Custom Field", filters=[["dt", "=", "Patient Encounter"], ["fieldname", "like", "tobacco_%"]], pluck="name")
	print(f"Found {len(fields)} existing tobacco fields.")
	
	count = 0
	for f in fields:
		try:
			frappe.delete_doc("Custom Field", f, force=True)
			count += 1
		except Exception as e:
			print(f"Failed to delete {f}: {e}")
			
	frappe.db.commit()
	print(f"Successfully deleted {count} fields.")

