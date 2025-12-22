import frappe


def execute():
	"""Fix field positions for Step 1, 2, 3, 4 to match localhost"""
	print("\n" + "="*60)
	print("Fixing Clinical Examination Field Positions")
	print("="*60)
	
	doctype = "Patient Encounter"
	
	# Define correct positions (matching localhost)
	field_positions = [
		# Step 1 fields - after exam_examination_type
		('exam_step1_section', 'exam_examination_type'),
		('exam_step1_table_html', 'exam_step1_section'),
		('exam_filled_by', 'exam_step1_table_html'),
		('exam_complaints_status', 'exam_filled_by'),
		('exam_complaints', 'exam_complaints_status'),
		
		# Step 2 fields - after exam_complaints child table
		('exam_step2_section', 'exam_complaints'),
		('exam_step2_done_by', 'exam_step2_section'),
		('exam_step2_table_html', 'exam_step2_done_by'),
		
		# Step 3 fields
		('exam_step3_section', 'exam_lesion_final_notes'),
		('exam_diagram_interactive', 'exam_step3_section'),
		
		# Step 4 fields
		('exam_step4_section', 'exam_marking_data'),
		('exam_pictures_taken_by', 'exam_step4_section'),
		('exam_pictures_html', 'exam_pictures_taken_by'),
	]
	
	fixed_count = 0
	for fieldname, insert_after in field_positions:
		try:
			cf_name = frappe.db.get_value('Custom Field', {
				'dt': doctype,
				'fieldname': fieldname
			}, 'name')
			
			if cf_name:
				frappe.db.set_value('Custom Field', cf_name, 'insert_after', insert_after)
				print(f"  ✓ {fieldname} -> after {insert_after}")
				fixed_count += 1
			else:
				print(f"  ⚠ {fieldname} not found")
		except Exception as e:
			print(f"  ✗ {fieldname}: {str(e)}")
	
	frappe.db.commit()
	
	# Clear cache
	frappe.clear_cache(doctype=doctype)
	
	print(f"\n  Fixed {fixed_count} field positions")
	print("  ✓ Cache cleared")
	print("="*60 + "\n")
