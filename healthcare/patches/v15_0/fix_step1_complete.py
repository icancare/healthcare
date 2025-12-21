import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Complete fix for Step 1 - Patient Complaints section in Patient Encounter"""
	print("\n" + "="*60)
	print("Complete Step 1 Fix - Patient Encounter")
	print("="*60)
	
	doctype = "Patient Encounter"
	
	# 1. Make show_clinical_examination visible
	if frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": "show_clinical_examination"}):
		frappe.db.set_value(
			"Custom Field", 
			{"dt": doctype, "fieldname": "show_clinical_examination"}, 
			{
				"hidden": 0,
				"depends_on": "eval:doc.practitioner"
			}
		)
		print("  ✓ Made 'show_clinical_examination' checkbox visible")
	
	# 2. Update exam_step1_section with proper depends_on
	if frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": "exam_step1_section"}):
		frappe.db.set_value(
			"Custom Field", 
			{"dt": doctype, "fieldname": "exam_step1_section"}, 
			{
				"hidden": 0,
				"depends_on": "eval:doc.show_clinical_examination"
			}
		)
		print("  ✓ Fixed 'exam_step1_section' depends_on")
	
	# 3. Create/Update exam_step1_table_html with proper position
	fields = {
		doctype: [
			{
				"fieldname": "exam_step1_table_html",
				"label": "",
				"fieldtype": "HTML",
				"insert_after": "exam_step1_section",
				"depends_on": "eval:doc.show_clinical_examination",
				"hidden": 0
			}
		]
	}
	create_custom_fields(fields, update=True)
	print("  ✓ Created/Updated 'exam_step1_table_html' field")
	
	# 4. Hide all the old Step 1 individual fields
	old_fields = [
		"exam_filled_by",
		"exam_complaints_status", 
		"exam_abnormal_body_parts_section",
		"exam_complaint_face",
		"exam_complaint_neck",
		"exam_complaint_oral_cavity",
		"exam_complaint_teeth",
		"exam_complaint_others",
		"exam_face_complaints_section",
		"exam_face_lump_swelling",
		"exam_face_pigmentation",
		"exam_face_ulcer",
		"exam_face_col_break",
		"exam_face_duration_days",
		"exam_face_duration_category",
		"exam_face_pattern",
		"exam_neck_complaints_section",
		"exam_neck_lump_outside",
		"exam_neck_lump_throat",
		"exam_neck_col_break",
		"exam_neck_duration_days",
		"exam_neck_pattern",
		"exam_oral_complaints_section",
		"exam_oral_restricted_mouth",
		"exam_oral_restricted_tongue",
		"exam_oral_trauma",
		"exam_oral_pain",
		"exam_oral_painful_ulcer",
		"exam_oral_painless_ulcer",
		"exam_oral_recurrent_ulcer",
		"exam_oral_red_patch",
		"exam_oral_white_patch",
		"exam_oral_nodule_lump",
		"exam_oral_swelling",
		"exam_oral_sensitivity",
		"exam_oral_burning",
		"exam_oral_bleeding",
		"exam_oral_decreased_saliva",
		"exam_oral_increased_saliva",
		"exam_oral_foul_smell",
		"exam_oral_swallowing_difficulty",
		"exam_oral_others",
		"exam_oral_others_specify",
		"exam_oral_col_break",
		"exam_oral_onset_date",
		"exam_oral_duration_days",
		"exam_oral_is_intermittent",
		"exam_oral_is_recurrent",
		"exam_oral_pattern",
		"exam_oral_trauma_question",
		"exam_oral_medical_treatment",
		"exam_oral_treatment_details",
		"exam_teeth_complaints_section",
		"exam_teeth_painful",
		"exam_teeth_loosening",
		"exam_teeth_lost",
		"exam_teeth_gum_problem",
		"exam_teeth_denture",
		"exam_teeth_col_break",
		"exam_teeth_duration_days",
		"exam_teeth_pattern",
		"exam_teeth_trauma",
		"exam_teeth_treatment",
		"exam_others_complaints_section",
		"exam_others_stickiness",
		"exam_others_voice_change",
		"exam_others_sore_throat",
		"exam_others_swallowing",
		"exam_others_earache",
		"exam_others_specify",
		"exam_others_col_break",
		"exam_others_duration_days",
		"exam_others_pattern",
		"exam_others_trauma",
		"exam_others_treatment"
	]
	
	hidden_count = 0
	for fieldname in old_fields:
		if frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": fieldname}):
			frappe.db.set_value("Custom Field", {"dt": doctype, "fieldname": fieldname}, "hidden", 1)
			hidden_count += 1
	
	print(f"  ✓ Hidden {hidden_count} old individual fields")
	
	frappe.db.commit()
	
	# Clear cache
	frappe.clear_cache(doctype=doctype)
	
	print("  ✓ Cache cleared for Patient Encounter")
	print("="*60 + "\n")
