import frappe


def execute():
	"""
	Add options to Occupation and Marital Status custom fields in Patient doctype
	"""
	
	# Update Occupation field options
	if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "custom_occupation"}):
		frappe.db.set_value(
			"Custom Field",
			{"dt": "Patient", "fieldname": "custom_occupation"},
			"options",
			"\nDoctor\nEngineer\nTeacher\nBusiness Person\nStudent\nHomemaker\nRetired\nUnemployed\nFarmer\nLabourer\nOther"
		)
		print("✅ Occupation field options updated")
	
	# Update Marital Status field options
	if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "custom_marital_status"}):
		frappe.db.set_value(
			"Custom Field",
			{"dt": "Patient", "fieldname": "custom_marital_status"},
			"options",
			"\nSingle\nMarried\nDivorced\nWidowed\nSeparated"
		)
		print("✅ Marital Status field options updated")
	
	frappe.db.commit()
	
	# Clear cache
	frappe.clear_cache(doctype="Patient")
	
	print("✅ Custom field options added successfully")

