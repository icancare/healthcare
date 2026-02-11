
import frappe

def execute():
	print("\nCleaning up old Tobacco First Visit fields...")
	
	# Fields to delete (ALL tobacco_ fields to be safe and rebuild)
	# We will keep the Section Break if we can, but simpler to wipe and recreate structure.
	
	fields = frappe.get_all(
		"Custom Field",
		filters=[
			["dt", "=", "Patient Encounter"],
			["fieldname", "like", "tobacco_%"]
		],
		pluck="name"
	)
	
	for f in fields:
		frappe.delete_doc("Custom Field", f, force=True)
		
	# Also delete the Child Doctype "Quit Buddy" since we don't need it per new requirements
	if frappe.db.exists("DocType", "Quit Buddy"):
		frappe.delete_doc("DocType", "Quit Buddy", force=True)
		
	print(f"✓ Deleted {len(fields)} custom fields and Quit Buddy doctype.")
	
	frappe.db.commit()
	frappe.clear_cache()
