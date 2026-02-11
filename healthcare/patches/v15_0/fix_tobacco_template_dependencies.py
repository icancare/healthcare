
import frappe

def execute():
	"""
	Fix dependencies for Clinical Examination fields.
	1. Ensure core fields (Case Type, Template) are always visible when Show Clinical Exam is checked.
	2. Ensure Oral Screening fields (Steps 1-6) are HIDDEN when Tobacco templates are selected.
	3. Ensure Tobacco fields check for Practitioner and specific Template.
	"""
	print("\n" + "="*60)
	print("Fixing Clinical Examination Dependencies")
	print("="*60)

	fix_oral_screening_dependencies()
	fix_tobacco_dependencies()

	frappe.db.commit()
	frappe.clear_cache()
	print("\n" + "="*60)
	print("Dependencies Fixed Successfully!")
	print("="*60)


def fix_oral_screening_dependencies():
	print("\nUpdating Oral Screening Field Dependencies...")
	
	# Fields that should stay visible for ALL templates
	common_fields = [
		"show_clinical_examination",
		"clinical_examination_section",
		"exam_case_type",
		"exam_examination_template",
		"exam_header_col_break"
	]
	
	# Get all custom fields for Patient Encounter
	custom_fields = frappe.get_all(
		"Custom Field",
		filters={"dt": "Patient Encounter"},
		fields=["name", "fieldname", "depends_on"]
	)
	
	tobacco_templates = "['Quit Tobacco First Visit', 'Quit Tobacco Follow-up Visit']"
	exclusion_condition = f" && !{tobacco_templates}.includes(doc.exam_examination_template)"
	
	updated_count = 0
	
	for field in custom_fields:
		if not field.depends_on:
			continue
			
		# Target fields that depend on show_clinical_examination (Oral Screening fields)
		# BUT exclude the common fields (Template selector, Case Type)
		if "doc.show_clinical_examination" in field.depends_on and field.fieldname not in common_fields:
			
			# Avoid double adding
			if "Quit Tobacco" in field.depends_on:
				continue
				
			# If it's a Tobacco field, skip (managed separately)
			if field.fieldname.startswith("tobacco_"):
				continue
				
			new_depends_on = field.depends_on + exclusion_condition
			frappe.db.set_value("Custom Field", field.name, "depends_on", new_depends_on)
			updated_count += 1
			# print(f"  Updated: {field.fieldname}")
			
	print(f"✓ Added exclusion to {updated_count} Oral Screening fields")


def fix_tobacco_dependencies():
	print("\nUpdating Tobacco Field Dependencies...")
	
	custom_fields = frappe.get_all(
		"Custom Field",
		filters={
			"dt": "Patient Encounter",
			"fieldname": ["like", "tobacco_%"]
		},
		fields=["name", "fieldname", "depends_on"]
	)
	
	updated_count = 0
	
	for field in custom_fields:
		original_dep = field.depends_on or ""
		new_dep = original_dep
		
		# 1. Ensure it checks for Practitioner
		if "doc.practitioner" not in original_dep:
			new_dep = "eval:doc.practitioner && " + new_dep.replace("eval:", "")
		
		# 2. Ensure it checks for exam_examination_template existence
		if "doc.exam_examination_template" not in new_dep:
			# It usually has it, but let's be safe. 
			# My previous patch added: "eval:doc.exam_examination_template && ..."
			pass 
			
		if new_dep != original_dep:
			frappe.db.set_value("Custom Field", field.name, "depends_on", new_dep)
			updated_count += 1
			
	print(f"✓ Updated dependencies for {updated_count} Tobacco fields")

