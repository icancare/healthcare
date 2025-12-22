import frappe
import json

def execute():
	"""Import Patient Encounter custom fields from JSON - fixes field positions"""
	print("\n" + "="*60)
	print("Syncing Patient Encounter Custom Fields from Localhost")
	print("="*60)
	
	doctype = "Patient Encounter"
	
	# Clinical exam field names to sync (only position-related fields)
	target_fields = [
		'exam_step1_section', 'exam_step1_table_html', 'exam_filled_by', 'exam_complaints_status',
		'exam_complaints', 'exam_step2_section', 'exam_step2_done_by', 'exam_step2_table_html',
		'exam_step3_section', 'exam_diagram_interactive', 'exam_lesions',
		'exam_step4_section', 'exam_pictures_taken_by', 'exam_pictures_html'
	]
	
	# Correct positions from localhost
	correct_positions = {
		'exam_step1_section': ('exam_examination_type', 71),
		'exam_step1_table_html': ('exam_step1_section', 72),
		'exam_filled_by': ('exam_step1_table_html', 73),
		'exam_complaints_status': ('exam_filled_by', 74),
		'exam_complaints': ('exam_complaints_status', 75),
		'exam_step2_section': ('exam_complaints', 149),
		'exam_step2_done_by': ('exam_step2_section', 150),
		'exam_step2_table_html': ('exam_step2_done_by', 151),
		'exam_step3_section': ('exam_lesion_final_notes', 346),
		'exam_diagram_interactive': ('exam_step3_section', 347),
		'exam_step4_section': ('exam_marking_data', 351),
		'exam_pictures_taken_by': ('exam_step4_section', 352),
		'exam_pictures_html': ('exam_pictures_taken_by', 353),
	}
	
	updated = 0
	for fieldname, (insert_after, idx) in correct_positions.items():
		cf_name = frappe.db.get_value('Custom Field', {
			'dt': doctype,
			'fieldname': fieldname
		}, 'name')
		
		if cf_name:
			current = frappe.db.get_value('Custom Field', cf_name, ['insert_after', 'idx'])
			if current[0] != insert_after or current[1] != idx:
				frappe.db.set_value('Custom Field', cf_name, {
					'insert_after': insert_after,
					'idx': idx,
					'hidden': 0
				})
				print(f"  ✓ {fieldname}: {current[0]} -> {insert_after}")
				updated += 1
			else:
				print(f"  = {fieldname}: OK")
		else:
			print(f"  ⚠ {fieldname}: NOT FOUND")
	
	frappe.db.commit()
	frappe.clear_cache(doctype=doctype)
	
	print(f"\n  Updated {updated} fields")
	print("  ✓ Cache cleared")
	print("="*60 + "\n")
