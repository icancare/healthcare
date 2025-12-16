import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def execute():
	"""Add STEP 4 - Pictures and STEP 5 - Special Tests to Patient Encounter"""
	print("\n" + "="*60)
	print("Adding STEP 4 & STEP 5 to Patient Encounter")
	print("="*60)
	
	doctype = "Patient Encounter"
	base_condition = 'eval:doc.practitioner && doc.show_clinical_examination'
	
	fields = [
		# ============================================
		# STEP 4 - PICTURES TO BE TAKEN
		# ============================================
		{
			"fieldname": "exam_step4_section",
			"label": "STEP 4 - PICTURES to be taken",
			"fieldtype": "Section Break",
			"insert_after": "exam_marking_data",
			"collapsible": 0,
			"depends_on": base_condition,
			"description": "Upload clinical photographs. Images will display directly on screen."
		},
		{
			"fieldname": "exam_pictures_taken_by",
			"label": "Pictures Taken By",
			"fieldtype": "Select",
			"insert_after": "exam_step4_section",
			"options": "\nDoctor's Assistant\nDoctor\nPatient",
			"depends_on": base_condition
		},
		# Row 1: Pictures 1-2
		{
			"fieldname": "exam_pic_1_face_neck",
			"label": "1. Face and Neck",
			"fieldtype": "Attach Image",
			"insert_after": "exam_pictures_taken_by",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_pic_col1",
			"fieldtype": "Column Break",
			"insert_after": "exam_pic_1_face_neck"
		},
		{
			"fieldname": "exam_pic_2_open_mouth",
			"label": "2. Open Mouth with Scale",
			"fieldtype": "Attach Image",
			"insert_after": "exam_pic_col1",
			"depends_on": base_condition
		},
		# Row 2: Pictures 3-4
		{
			"fieldname": "exam_pic_row2",
			"fieldtype": "Section Break",
			"insert_after": "exam_pic_2_open_mouth",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_pic_3_central_arch",
			"label": "3. Central Arch with Lips",
			"fieldtype": "Attach Image",
			"insert_after": "exam_pic_row2",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_pic_col2",
			"fieldtype": "Column Break",
			"insert_after": "exam_pic_3_central_arch"
		},
		{
			"fieldname": "exam_pic_4_right_cheek",
			"label": "4. Right Cheek with Alveolus",
			"fieldtype": "Attach Image",
			"insert_after": "exam_pic_col2",
			"depends_on": base_condition
		},
		# Row 3: Pictures 5-6
		{
			"fieldname": "exam_pic_row3",
			"fieldtype": "Section Break",
			"insert_after": "exam_pic_4_right_cheek",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_pic_5_left_cheek",
			"label": "5. Left Cheek with Alveolus",
			"fieldtype": "Attach Image",
			"insert_after": "exam_pic_row3",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_pic_col3",
			"fieldtype": "Column Break",
			"insert_after": "exam_pic_5_left_cheek"
		},
		{
			"fieldname": "exam_pic_6_tongue",
			"label": "6. Tongue Protruded",
			"fieldtype": "Attach Image",
			"insert_after": "exam_pic_col3",
			"depends_on": base_condition
		},
		# Row 4: Pictures 7-8
		{
			"fieldname": "exam_pic_row4",
			"fieldtype": "Section Break",
			"insert_after": "exam_pic_6_tongue",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_pic_7_tongue_floor",
			"label": "7. Tongue with Floor of Mouth",
			"fieldtype": "Attach Image",
			"insert_after": "exam_pic_row4",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_pic_col4",
			"fieldtype": "Column Break",
			"insert_after": "exam_pic_7_tongue_floor"
		},
		{
			"fieldname": "exam_pic_8_palate",
			"label": "8. Hard and Soft Palate",
			"fieldtype": "Attach Image",
			"insert_after": "exam_pic_col4",
			"depends_on": base_condition
		},
		# Row 5: Pictures 9-10
		{
			"fieldname": "exam_pic_row5",
			"fieldtype": "Section Break",
			"insert_after": "exam_pic_8_palate",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_pic_9_abnormal",
			"label": "9. Abnormal Area Focused",
			"fieldtype": "Attach Image",
			"insert_after": "exam_pic_row5",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_pic_col5",
			"fieldtype": "Column Break",
			"insert_after": "exam_pic_9_abnormal"
		},
		{
			"fieldname": "exam_pic_10_special",
			"label": "10. Special Tests",
			"fieldtype": "Attach Image",
			"insert_after": "exam_pic_col5",
			"depends_on": base_condition
		},
		
		# ============================================
		# STEP 5 - SPECIAL TESTS
		# ============================================
		{
			"fieldname": "exam_step5_section",
			"label": "STEP 5 - SPECIAL TESTS",
			"fieldtype": "Section Break",
			"insert_after": "exam_pic_10_special",
			"collapsible": 0,
			"depends_on": base_condition,
			"description": "Record findings from special diagnostic tests"
		},
		{
			"fieldname": "exam_skip_special_tests",
			"label": "Skip Special Tests",
			"fieldtype": "Check",
			"insert_after": "exam_step5_section",
			"default": "0",
			"depends_on": base_condition
		},
		
		# Toluidine Blue Test
		{
			"fieldname": "exam_toluidine_section",
			"label": "Toluidine Blue Test",
			"fieldtype": "Section Break",
			"insert_after": "exam_skip_special_tests",
			"collapsible": 0,
			"depends_on": f"{base_condition} && !doc.exam_skip_special_tests"
		},
		{
			"fieldname": "exam_toluidine_result",
			"label": "Result",
			"fieldtype": "Select",
			"insert_after": "exam_toluidine_section",
			"options": "\nNormal\nLow Suspicious\nHigh Suspicious",
			"depends_on": f"{base_condition} && !doc.exam_skip_special_tests"
		},
		{
			"fieldname": "exam_toluidine_col",
			"fieldtype": "Column Break",
			"insert_after": "exam_toluidine_result"
		},
		{
			"fieldname": "exam_toluidine_notes",
			"label": "Notes",
			"fieldtype": "Small Text",
			"insert_after": "exam_toluidine_col",
			"depends_on": f"{base_condition} && !doc.exam_skip_special_tests"
		},
		
		# Blue Light Test
		{
			"fieldname": "exam_bluelight_section",
			"label": "Blue Light Test",
			"fieldtype": "Section Break",
			"insert_after": "exam_toluidine_notes",
			"collapsible": 0,
			"depends_on": f"{base_condition} && !doc.exam_skip_special_tests"
		},
		{
			"fieldname": "exam_bluelight_result",
			"label": "Result",
			"fieldtype": "Select",
			"insert_after": "exam_bluelight_section",
			"options": "\nNormal\nLow Suspicious\nHigh Suspicious",
			"depends_on": f"{base_condition} && !doc.exam_skip_special_tests"
		},
		{
			"fieldname": "exam_bluelight_col",
			"fieldtype": "Column Break",
			"insert_after": "exam_bluelight_result"
		},
		{
			"fieldname": "exam_bluelight_notes",
			"label": "Notes",
			"fieldtype": "Small Text",
			"insert_after": "exam_bluelight_col",
			"depends_on": f"{base_condition} && !doc.exam_skip_special_tests"
		},
		
		# Autofluorescence Test
		{
			"fieldname": "exam_autofluor_section",
			"label": "Autofluorescence Test",
			"fieldtype": "Section Break",
			"insert_after": "exam_bluelight_notes",
			"collapsible": 0,
			"depends_on": f"{base_condition} && !doc.exam_skip_special_tests"
		},
		{
			"fieldname": "exam_autofluor_result",
			"label": "Result",
			"fieldtype": "Select",
			"insert_after": "exam_autofluor_section",
			"options": "\nNormal\nLow Suspicious\nHigh Suspicious",
			"depends_on": f"{base_condition} && !doc.exam_skip_special_tests"
		},
		{
			"fieldname": "exam_autofluor_col",
			"fieldtype": "Column Break",
			"insert_after": "exam_autofluor_result"
		},
		{
			"fieldname": "exam_autofluor_notes",
			"label": "Notes",
			"fieldtype": "Small Text",
			"insert_after": "exam_autofluor_col",
			"depends_on": f"{base_condition} && !doc.exam_skip_special_tests"
		},
		
		# Spectroscopy Test
		{
			"fieldname": "exam_spectroscopy_section",
			"label": "Spectroscopy Test",
			"fieldtype": "Section Break",
			"insert_after": "exam_autofluor_notes",
			"collapsible": 0,
			"depends_on": f"{base_condition} && !doc.exam_skip_special_tests"
		},
		{
			"fieldname": "exam_spectroscopy_result",
			"label": "Result",
			"fieldtype": "Select",
			"insert_after": "exam_spectroscopy_section",
			"options": "\nNormal\nLow Suspicious\nHigh Suspicious",
			"depends_on": f"{base_condition} && !doc.exam_skip_special_tests"
		},
		{
			"fieldname": "exam_spectroscopy_col",
			"fieldtype": "Column Break",
			"insert_after": "exam_spectroscopy_result"
		},
		{
			"fieldname": "exam_spectroscopy_notes",
			"label": "Notes",
			"fieldtype": "Small Text",
			"insert_after": "exam_spectroscopy_col",
			"depends_on": f"{base_condition} && !doc.exam_skip_special_tests"
		},
		
		# Special Tests Summary
		{
			"fieldname": "exam_special_tests_summary",
			"label": "Special Tests Summary/Notes",
			"fieldtype": "Text",
			"insert_after": "exam_spectroscopy_notes",
			"depends_on": f"{base_condition} && !doc.exam_skip_special_tests"
		},
	]
	
	# Create all custom fields
	for field in fields:
		try:
			create_custom_field(doctype, field)
			print(f"  ✓ Added field: {field['fieldname']}")
		except Exception as e:
			if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
				print(f"  ⏭ Field already exists: {field['fieldname']}")
			else:
				print(f"  ✗ Error adding {field['fieldname']}: {e}")
	
	frappe.db.commit()
	print("\n✓ STEP 4 & STEP 5 Added!")
	print("="*60 + "\n")

