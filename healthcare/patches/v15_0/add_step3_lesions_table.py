import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add exam_lesions child table for Step 3 diagram lesion marking"""
	print("\n" + "="*60)
	print("Adding Lesions Table for Step 3 Diagram")
	print("="*60)
	
	doctype = "Patient Encounter"
	
	# FIX: Convert string status values to integers before schema sync
	# This prevents "Data truncated" errors on production
	status_fields = [
		'exam_face_status', 'exam_neck_status', 'exam_mouth_status',
		'exam_dental_status', 'exam_throat_status'
	]
	
	for field in status_fields:
		try:
			# Check if column exists
			if frappe.db.has_column(doctype, field):
				# Convert Normal/empty to 0, Abnormal to 1
				frappe.db.sql(f"""
					UPDATE `tab{doctype}` 
					SET `{field}` = CASE 
						WHEN `{field}` IN ('Abnormal', '1', 1) THEN 1 
						ELSE 0 
					END
				""")
				print(f"  ✓ Fixed data for {field}")
		except Exception as e:
			print(f"  ⚠ Could not fix {field}: {str(e)}")
	
	frappe.db.commit()
	
	# Add child table field for lesions
	fields = {
		doctype: [
			{
				"fieldname": "exam_lesions_section",
				"label": "Marked Lesions",
				"fieldtype": "Section Break",
				"insert_after": "exam_step3_diagram_html",
				"depends_on": "eval:doc.show_clinical_examination",
				"collapsible": 0
			},
			{
				"fieldname": "exam_lesions",
				"label": "Diagram Lesions",
				"fieldtype": "Table",
				"options": "Clinical Exam Lesion",
				"insert_after": "exam_lesions_section",
				"depends_on": "eval:doc.show_clinical_examination"
			}
		]
	}
	
	create_custom_fields(fields, update=True)
	print("  ✓ Added exam_lesions child table field")
	
	# Also add exam_diagram_lesions as alias (used in code)
	fields2 = {
		doctype: [
			{
				"fieldname": "exam_diagram_lesions",
				"label": "Diagram Lesions (Alias)",
				"fieldtype": "Table",
				"options": "Clinical Exam Lesion",
				"insert_after": "exam_lesions",
				"depends_on": "eval:doc.show_clinical_examination",
				"hidden": 1  # Hidden as it's just for code compatibility
			}
		]
	}
	
	create_custom_fields(fields2, update=True)
	print("  ✓ Added exam_diagram_lesions alias field")
	
	frappe.db.commit()
	frappe.clear_cache(doctype=doctype)
	
	print("  ✓ Cache cleared for Patient Encounter")
	print("="*60 + "\n")
