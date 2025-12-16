import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def execute():
	"""Fix STEP 2 - Physical Examination flow - Main Status then body part checkboxes"""
	print("\n" + "="*60)
	print("Fixing STEP 2 - Physical Examination Flow")
	print("="*60)
	
	base_condition = 'eval:doc.practitioner && doc.show_clinical_examination'
	abnormal_condition = base_condition + " && doc.exam_main_status=='Abnormal'"
	
	# 1. Add main status field if not exists
	if not frappe.db.exists('Custom Field', {'dt': 'Patient Encounter', 'fieldname': 'exam_main_status'}):
		create_custom_field('Patient Encounter', {
			'fieldname': 'exam_main_status',
			'label': 'Status',
			'fieldtype': 'Select',
			'insert_after': 'exam_status_subsection',
			'options': '\nNormal\nAbnormal',
			'depends_on': base_condition,
			'bold': 1
		})
		print("  ✓ Added exam_main_status field")
	
	# 2. Convert body part fields to checkboxes
	body_part_fields = ['exam_face_status', 'exam_neck_status', 'exam_mouth_status', 'exam_dental_status', 'exam_throat_status']
	for fieldname in body_part_fields:
		cf = frappe.db.get_value('Custom Field', {'dt': 'Patient Encounter', 'fieldname': fieldname}, 'name')
		if cf:
			frappe.db.set_value('Custom Field', cf, {
				'fieldtype': 'Check',
				'options': '',
				'default': '0',
				'depends_on': abnormal_condition
			})
			print(f"  ✓ Converted {fieldname} to Check")
	
	# 3. Update Face examination fields
	face_fields = frappe.db.get_all('Custom Field', 
		filters={'dt': 'Patient Encounter', 'fieldname': ['like', 'exam_face_%']},
		fields=['name', 'fieldname']
	)
	for f in face_fields:
		if f.fieldname not in ['exam_face_status']:
			frappe.db.set_value('Custom Field', f.name, 'depends_on', base_condition + ' && doc.exam_face_status')
	print("  ✓ Updated Face fields")
	
	# 4. Update Neck examination fields
	neck_fields = frappe.db.get_all('Custom Field', 
		filters={'dt': 'Patient Encounter', 'fieldname': ['like', 'exam_neck_%']},
		fields=['name', 'fieldname']
	)
	for f in neck_fields:
		if f.fieldname not in ['exam_neck_status']:
			frappe.db.set_value('Custom Field', f.name, 'depends_on', base_condition + ' && doc.exam_neck_status')
	print("  ✓ Updated Neck fields")
	
	# 5. Update Mouth examination fields
	mouth_fields = frappe.db.get_all('Custom Field', 
		filters={'dt': 'Patient Encounter', 'fieldname': ['like', 'exam_mouth_%']},
		fields=['name', 'fieldname']
	)
	for f in mouth_fields:
		if f.fieldname not in ['exam_mouth_status']:
			frappe.db.set_value('Custom Field', f.name, 'depends_on', base_condition + ' && doc.exam_mouth_status')
	
	# Tongue fields (part of mouth)
	tongue_fields = frappe.db.get_all('Custom Field', 
		filters={'dt': 'Patient Encounter', 'fieldname': ['like', 'exam_tongue_%']},
		fields=['name', 'fieldname']
	)
	for f in tongue_fields:
		frappe.db.set_value('Custom Field', f.name, 'depends_on', base_condition + ' && doc.exam_mouth_status')
	
	# Oral Hygiene fields (part of mouth)
	hygiene_fields = frappe.db.get_all('Custom Field', 
		filters={'dt': 'Patient Encounter', 'fieldname': ['like', 'exam_oral_hygiene%']},
		fields=['name', 'fieldname']
	)
	for f in hygiene_fields:
		frappe.db.set_value('Custom Field', f.name, 'depends_on', base_condition + ' && doc.exam_mouth_status')
	
	# Prosthesis fields
	frappe.db.sql('''UPDATE `tabCustom Field` SET depends_on = %s 
		WHERE dt = 'Patient Encounter' AND fieldname IN ('exam_prosthesis', 'exam_prosthesis_details', 'exam_hygiene_col_break')''',
		(base_condition + ' && doc.exam_mouth_status',))
	print("  ✓ Updated Mouth/Tongue/Hygiene fields")
	
	# 6. Update Dental/Teeth examination fields
	dental_fields = frappe.db.get_all('Custom Field', 
		filters={'dt': 'Patient Encounter', 'fieldname': ['like', 'exam_dental_%']},
		fields=['name', 'fieldname']
	)
	for f in dental_fields:
		if f.fieldname not in ['exam_dental_status']:
			frappe.db.set_value('Custom Field', f.name, 'depends_on', base_condition + ' && doc.exam_dental_status')
	
	teeth_fields = frappe.db.get_all('Custom Field', 
		filters={'dt': 'Patient Encounter', 'fieldname': ['like', 'exam_teeth_%']},
		fields=['name', 'fieldname']
	)
	for f in teeth_fields:
		frappe.db.set_value('Custom Field', f.name, 'depends_on', base_condition + ' && doc.exam_dental_status')
	print("  ✓ Updated Dental/Teeth fields")
	
	frappe.db.commit()
	print("\n✓ STEP 2 Flow Fixed!")
	print("="*60 + "\n")

