import frappe

def execute():
	print("\n" + "="*70)
	print("CLEANUP Step 5: Keep only 4 tests as per production")
	print("="*70)
	
	# Remove Autofluorescence, Spectroscopy, Lung XRAY, AI Lung XRAY (wrong additions)
	remove_extra_step5_tests()
	
	frappe.db.commit()
	frappe.clear_cache()
	print("\n✅ Step 5 cleaned up - only 4 tests remain!")


def remove_extra_step5_tests():
	"""Remove the tests that were incorrectly added - keep only 4 original tests"""
	
	# These fields should be removed (NOT in production)
	fields_to_remove = [
		# Autofluorescence
		'exam_autofluor_row_break',
		'exam_autofluor_section',
		'exam_autofluor_result',
		'exam_autofluor_col',
		'exam_autofluor_notes',
		# Spectroscopy
		'exam_spectroscopy_section',
		'exam_spectroscopy_result',
		'exam_spectroscopy_col',
		'exam_spectroscopy_notes',
		# Lung XRAY
		'exam_lung_row_break',
		'exam_lung_xray_section',
		'exam_lung_xray_result',
		'exam_lung_xray_col',
		'exam_lung_xray_notes',
		# AI Lung XRAY
		'exam_ai_lung_section',
		'exam_ai_lung_result',
		'exam_ai_lung_col',
		'exam_ai_lung_notes'
	]
	
	for fieldname in fields_to_remove:
		try:
			if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": fieldname}):
				frappe.db.delete("Custom Field", {"dt": "Patient Encounter", "fieldname": fieldname})
				print(f"✅ Deleted: {fieldname}")
		except Exception as e:
			print(f"⚠️  Could not delete {fieldname}: {str(e)}")
	
	print(f"\n✅ Removed {len(fields_to_remove)} extra fields - keeping only 4 tests")
