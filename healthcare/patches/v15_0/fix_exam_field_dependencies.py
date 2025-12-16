import frappe

def execute():
	"""Fix depends_on for all clinical examination fields"""
	print("\n" + "="*60)
	print("Fixing Clinical Examination Field Dependencies")
	print("="*60)
	
	# Get all exam_ fields
	all_exam_fields = frappe.db.get_all('Custom Field', 
		filters={'dt': 'Patient Encounter', 'fieldname': ['like', 'exam_%']},
		fields=['name', 'fieldname', 'depends_on', 'fieldtype']
	)
	
	base_condition = 'eval:doc.practitioner && doc.show_clinical_examination'
	
	for f in all_exam_fields:
		current = f.depends_on or ''
		fieldname = f.fieldname
		new_cond = None
		
		# Skip column breaks - they inherit from section
		if f.fieldtype == 'Column Break':
			continue
		
		# Fields that should show only when Abnormal is selected
		if fieldname == 'exam_abnormal_body_parts_section':
			new_cond = base_condition + " && doc.exam_complaints_status=='Complaints - Abnormal'"
		
		# Body part checkboxes - show when abnormal
		elif fieldname in ['exam_complaint_face', 'exam_complaint_neck', 'exam_complaint_oral_cavity', 'exam_complaint_teeth', 'exam_complaint_others']:
			new_cond = base_condition + " && doc.exam_complaints_status=='Complaints - Abnormal'"
		
		# Face section fields
		elif 'exam_face_' in fieldname:
			new_cond = base_condition + ' && doc.exam_complaint_face'
		
		# Neck section fields  
		elif 'exam_neck_' in fieldname:
			new_cond = base_condition + ' && doc.exam_complaint_neck'
		
		# Oral section fields (except exam_oral_hygiene which is in physical exam)
		elif 'exam_oral_' in fieldname and fieldname not in ['exam_oral_hygiene']:
			new_cond = base_condition + ' && doc.exam_complaint_oral_cavity'
		
		# Teeth section fields (except exam_teeth_issues which is in physical exam)
		elif 'exam_teeth_' in fieldname and fieldname not in ['exam_teeth_issues']:
			new_cond = base_condition + ' && doc.exam_complaint_teeth'
		
		# Others section fields
		elif 'exam_others_' in fieldname:
			new_cond = base_condition + ' && doc.exam_complaint_others'
		
		# Step1 section and filled_by
		elif fieldname in ['exam_step1_section', 'exam_filled_by', 'exam_complaints_status']:
			new_cond = base_condition
		
		# All other exam fields without proper condition
		elif 'show_clinical_examination' not in current:
			new_cond = base_condition
		
		if new_cond:
			frappe.db.set_value('Custom Field', f.name, 'depends_on', new_cond)
			print(f"  ✓ Fixed: {fieldname}")
	
	frappe.db.commit()
	print("\n✓ All field dependencies fixed!")
	print("="*60 + "\n")

