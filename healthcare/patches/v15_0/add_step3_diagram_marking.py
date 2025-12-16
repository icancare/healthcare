import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def execute():
	"""Add STEP 3 - Interactive Diagram Marking to Patient Encounter"""
	print("\n" + "="*60)
	print("Adding STEP 3 - Diagram Marking to Patient Encounter")
	print("="*60)
	
	doctype = "Patient Encounter"
	base_condition = 'eval:doc.practitioner && doc.show_clinical_examination'
	
	fields = [
		# ============================================
		# STEP 3 - Diagram Marking Section
		# ============================================
		{
			"fieldname": "exam_step3_section",
			"label": "STEP 3 - Representation MARKING on Diagram",
			"fieldtype": "Section Break",
			"insert_after": "exam_lesion_final_notes",
			"collapsible": 0,
			"depends_on": base_condition,
			"description": "Click on diagram regions to mark lesions. Markings will automatically appear in the table below."
		},
		
		# Interactive Diagram HTML
		{
			"fieldname": "exam_diagram_interactive",
			"label": "Interactive Diagrams",
			"fieldtype": "HTML",
			"insert_after": "exam_step3_section",
			"depends_on": base_condition
		},
		
		# JSON to store marking data
		{
			"fieldname": "exam_marking_data",
			"label": "Marking Data",
			"fieldtype": "Code",
			"insert_after": "exam_diagram_interactive",
			"options": "JSON",
			"hidden": 1
		},
		
		# Marked Lesions Table Section
		{
			"fieldname": "exam_marked_lesions_section",
			"label": "Marked Lesions",
			"fieldtype": "Section Break",
			"insert_after": "exam_marking_data",
			"collapsible": 0,
			"depends_on": base_condition
		},
		
		# Table to show marked lesions
		{
			"fieldname": "exam_diagram_lesions",
			"label": "Diagram Lesions",
			"fieldtype": "Table",
			"insert_after": "exam_marked_lesions_section",
			"options": "Clinical Exam Lesion",
			"depends_on": base_condition
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
	print("\n✓ STEP 3 - Diagram Marking Added!")
	print("="*60 + "\n")

