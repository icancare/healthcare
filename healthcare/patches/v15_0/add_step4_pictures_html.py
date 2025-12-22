import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add Step 4 Pictures HTML field and hide individual attach fields"""
	print("\n" + "="*60)
	print("Adding Step 4 Pictures HTML Field")
	print("="*60)
	
	doctype = "Patient Encounter"
	
	# Add HTML field for custom Step 4 UI
	fields = {
		doctype: [
			{
				"fieldname": "exam_pictures_html",
				"label": "Pictures Upload",
				"fieldtype": "HTML",
				"insert_after": "exam_pictures_taken_by",
				"depends_on": "eval:doc.show_clinical_examination"
			}
		]
	}
	
	create_custom_fields(fields, update=True)
	print("  ✓ Added exam_pictures_html field")
	
	# Hide individual attach fields (will be shown via custom UI)
	fields_to_hide = [
		"exam_pic_1_face_neck",
		"exam_pic_2_open_mouth", 
		"exam_pic_3_central_arch",
		"exam_pic_4_right_cheek",
		"exam_pic_5_left_cheek",
		"exam_pic_6_tongue",
		"exam_pic_7_tongue_floor",
		"exam_pic_8_palate",
		"exam_pic_9_abnormal",
		"exam_pic_10_special"
	]
	
	hidden_count = 0
	for fieldname in fields_to_hide:
		if frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": fieldname}):
			frappe.db.set_value("Custom Field", {"dt": doctype, "fieldname": fieldname}, "hidden", 1)
			hidden_count += 1
	
	print(f"  ✓ Hidden {hidden_count} individual picture fields")
	
	frappe.db.commit()
	frappe.clear_cache(doctype=doctype)
	
	print("  ✓ Cache cleared")
	print("="*60 + "\n")
