import frappe


def execute():
	"""Delete old ICanCaRe Oral Screening Form template to recreate with correct configuration"""
	print("\n" + "="*60)
	print("Deleting Old Oral Screening Template")
	print("="*60)
	
	template_name = "ICanCaRe Oral Screening Form"
	
	# Check if template exists
	if not frappe.db.exists("Clinical Examination Template", template_name):
		print(f"  ⏭ Template '{template_name}' does not exist, skipping...")
		return
	
	try:
		# First, delete any Clinical Examination documents using this template
		exams = frappe.db.get_all(
			"Clinical Examination",
			filters={"examination_template": template_name},
			pluck="name"
		)
		
		if exams:
			print(f"  ⚠ Found {len(exams)} Clinical Examinations using this template")
			# Don't delete exams, just unlink them
			for exam in exams:
				frappe.db.set_value("Clinical Examination", exam, "examination_template", None)
			print(f"  ✓ Unlinked {len(exams)} examinations from template")
		
		# Delete the template
		frappe.delete_doc("Clinical Examination Template", template_name, force=True, ignore_permissions=True)
		frappe.db.commit()
		
		print(f"  ✓ Deleted template '{template_name}'")
		
	except Exception as e:
		print(f"  ✗ Error deleting template: {str(e)}")
		frappe.log_error(f"Error deleting Oral Screening Template: {str(e)}")
	
	print("="*60 + "\n")
