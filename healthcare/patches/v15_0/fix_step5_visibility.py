import frappe

def execute():
	print("\n" + "="*70)
	print("Fix Step 5 Visibility: Add depends_on conditions to new tests")
	print("="*70)
	
	# Add depends_on condition to all new Step 5 fields
	add_depends_on_to_step5_fields()
	
	# Also delete the extra row break sections we added (they're causing issues)
	cleanup_row_breaks()
	
	frappe.db.commit()
	frappe.clear_cache()
	print("\n✅ Step 5 visibility fixed!")


def add_depends_on_to_step5_fields():
	"""Add depends_on condition to Green LED, Amber, Lung XRAY, AI Lung fields"""
	
	# The condition that existing fields use
	depends_on_condition = "eval:doc.practitioner && doc.show_clinical_examination && !doc.exam_skip_special_tests"
	
	# Fields to update
	fields_to_update = [
		'exam_greenled_row_break',
		'exam_greenled_section',
		'exam_greenled_result',
		'exam_greenled_col',
		'exam_greenled_notes',
		'exam_amber_section',
		'exam_amber_result',
		'exam_amber_col',
		'exam_amber_notes',
		'exam_autofluor_row_break',
		'exam_lung_row_break',
		'exam_lung_xray_section',
		'exam_lung_xray_result',
		'exam_lung_xray_col',
		'exam_lung_xray_notes',
		'exam_ai_lung_section',
		'exam_ai_lung_result',
		'exam_ai_lung_col',
		'exam_ai_lung_notes'
	]
	
	for fieldname in fields_to_update:
		try:
			if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": fieldname}):
				field = frappe.get_doc("Custom Field", {"dt": "Patient Encounter", "fieldname": fieldname})
				field.depends_on = depends_on_condition
				field.save()
				print(f"✅ Added depends_on to: {fieldname}")
		except Exception as e:
			print(f"⚠️  Could not update {fieldname}: {str(e)}")


def cleanup_row_breaks():
	"""The row breaks we added are causing layout issues - let's hide them by making them depend on condition"""
	# Actually, keep them but just make sure they have depends_on
	pass
