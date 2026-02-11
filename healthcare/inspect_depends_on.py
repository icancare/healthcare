
import frappe

def execute():
	print("\nInspecting 'depends_on' values for Clinical Exam fields...")
	
	fields = frappe.get_all(
		"Custom Field",
		filters=[
			["dt", "=", "Patient Encounter"],
			["fieldname", "like", "exam_%"]
		],
		fields=["fieldname", "depends_on"]
	)
	
	print(f"Found {len(fields)} exam_ fields.")
	for f in fields:
		if f.depends_on and "Quit Tobacco" in f.depends_on:
			print(f"\nField: {f.fieldname}")
			print(f"Depends On: {f.depends_on}")

	print("\nInspecting 'depends_on' values for Tobacco fields...")
	tobacco_fields = frappe.get_all(
		"Custom Field",
		filters=[
			["dt", "=", "Patient Encounter"],
			["fieldname", "like", "tobacco_%"]
		],
		fields=["fieldname", "depends_on"]
	)
	for f in tobacco_fields:
		print(f"\nField: {f.fieldname}")
		print(f"Depends On: {f.depends_on}")
