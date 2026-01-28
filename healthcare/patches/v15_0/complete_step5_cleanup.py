import frappe

def execute():
	print("\n" + "="*70)
	print("COMPLETE CLEANUP: Remove ALL Step 5 custom fields")
	print("="*70)
	
	# Remove ALL Step 5 related custom fields
	complete_step5_cleanup()
	
	frappe.db.commit()
	frappe.clear_cache()
	print("\n✅ Step 5 completely cleaned - ready for fresh build!")


def complete_step5_cleanup():
	"""Remove ALL Step 5 related custom fields to start fresh"""
	
	# Get ALL Step 5 related fields
	step5_fields = frappe.db.sql("""
		SELECT name, fieldname 
		FROM `tabCustom Field` 
		WHERE dt = 'Patient Encounter' 
		AND (
			fieldname LIKE '%toluidine%' OR 
			fieldname LIKE '%bluelight%' OR 
			fieldname LIKE '%greenled%' OR 
			fieldname LIKE '%amber%' OR
			fieldname LIKE '%autofluor%' OR
			fieldname LIKE '%spectro%' OR
			fieldname LIKE '%lung%' OR
			fieldname LIKE '%xray%' OR
			fieldname = 'exam_skip_special_tests'
		)
		AND fieldname != 'exam_step5_section'
	""", as_dict=1)
	
	if step5_fields:
		print(f"\n🗑️  Found {len(step5_fields)} Step 5 fields to delete\n")
		for field in step5_fields:
			try:
				frappe.db.delete("Custom Field", {"name": field.name})
				print(f"✅ Deleted: {field.fieldname}")
			except Exception as e:
				print(f"⚠️  Could not delete {field.fieldname}: {str(e)}")
	else:
		print("✅ No Step 5 fields found to delete")
	
	print(f"\n✅ Step 5 cleanup complete - {len(step5_fields) if step5_fields else 0} fields removed")
