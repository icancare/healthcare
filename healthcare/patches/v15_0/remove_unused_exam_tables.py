import frappe


def execute():
	"""Remove unused Clinical Examination TABLE fields from Patient Encounter
	
	Only removes the 3 unnecessary TABLE sections:
	1. Physical Findings (table)
	2. Marked Lesions / Diagram Lesions (table)
	3. Clinical Images (table)
	
	These are replaced by direct form fields instead of child tables.
	"""
	print("\n" + "="*60)
	print("Removing Unused Table Fields (3 tables only)")
	print("="*60)
	
	doctype = "Patient Encounter"
	
	# ONLY remove these 3 table sections - nothing else!
	fields_to_remove = [
		# 1. Physical Findings table
		"exam_findings_section",
		"exam_findings",
		
		# 2. Marked Lesions / Diagram Lesions table
		"exam_marked_lesions_section",
		"exam_diagram_lesions",
		
		# 3. Clinical Images table
		"exam_images_section", 
		"exam_images",
	]
	
	for fieldname in fields_to_remove:
		try:
			cf = frappe.db.get_value('Custom Field', 
				{'dt': doctype, 'fieldname': fieldname}, 
				'name'
			)
			if cf:
				frappe.delete_doc('Custom Field', cf, force=True)
				print(f"  ✓ Deleted: {fieldname}")
			else:
				print(f"  ⏭ Not found: {fieldname}")
		except Exception as e:
			print(f"  ✗ Error deleting {fieldname}: {e}")
	
	frappe.db.commit()
	print("\n✓ 3 unused table sections removed!")
	print("="*60 + "\n")

