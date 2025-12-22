import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add Step 2 Table Format HTML field and hide old fields"""
	print("\n" + "="*60)
	print("Adding Step 2 Table Format to Patient Encounter")
	print("="*60)
	
	doctype = "Patient Encounter"
	
	# Add HTML field for Step 2 table rendering
	fields = {
		doctype: [
			{
				"fieldname": "exam_step2_table_html",
				"label": "",
				"fieldtype": "HTML",
				"insert_after": "exam_step2_section",
				"depends_on": "eval:doc.show_clinical_examination",
				"hidden": 0
			}
		]
	}
	
	create_custom_fields(fields, update=True)
	print("  ✓ Added Step 2 Table HTML field")
	
	# Hide the old individual Step 2 fields (but keep them for data storage)
	old_fields = [
		# Step 2 done by field (shown in custom UI)
		"exam_step2_done_by",
		
		# Examination Status fields (will be in custom UI)
		"exam_status_subsection",
		"exam_face_status",
		"exam_neck_status", 
		"exam_mouth_status",
		"exam_dental_status",
		"exam_throat_status",

		
		# Face examination fields
		"exam_face_exam_section",
		"exam_face_loc_forehead_left",
		"exam_face_loc_forehead_right",
		"exam_face_loc_eye_left",
		"exam_face_loc_eye_right",
		"exam_face_loc_nose_left",
		"exam_face_loc_nose_right",
		"exam_face_loc_chin",
		"exam_face_loc_cheek_left",
		"exam_face_loc_cheek_right",
		"exam_face_loc_parotid_left",
		"exam_face_loc_parotid_right",
		"exam_face_loc_ear_left",
		"exam_face_loc_ear_right",
		"exam_face_col_break1",
		"exam_face_abn_asymmetry",
		"exam_face_abn_swelling",
		"exam_face_abn_lymph",
		"exam_face_abn_ulcer",
		"exam_face_abn_decreased_movement",
		"exam_face_notes",
		
		# Neck examination fields
		"exam_neck_exam_section",
		"exam_neck_loc_left",
		"exam_neck_loc_right",
		"exam_neck_loc_central",
		"exam_neck_loc_submandibular_left",
		"exam_neck_loc_submandibular_right",
		"exam_neck_loc_thyroid_left",
		"exam_neck_loc_thyroid_right",
		"exam_neck_loc_thyroid_central",
		"exam_neck_loc_parathyroid",
		"exam_neck_loc_back_left",
		"exam_neck_loc_back_right",
		"exam_neck_loc_other",
		"exam_neck_loc_other_specify",
		"exam_neck_col_break1",
		"exam_neck_abn_pain",
		"exam_neck_abn_asymmetry",
		"exam_neck_abn_swelling",
		"exam_neck_abn_lymph",
		"exam_neck_abn_ulcer",
		"exam_neck_notes",
		
		# Mouth examination fields
		"exam_mouth_exam_section",
		"exam_mouth_opening_label",
		"exam_mouth_opening_fingers",
		"exam_mouth_opening_mm",
		"exam_mouth_measured_with",
		"exam_mouth_col_break1",
		"exam_tongue_label",
		"exam_tongue_normal",
		"exam_tongue_painful",
		"exam_tongue_deviation_left",
		"exam_tongue_deviation_right",
		"exam_tongue_restricted",
		"exam_tongue_protrusion_mm",
		"exam_oral_hygiene_section",
		"exam_oral_hygiene_good",
		"exam_oral_hygiene_moderate",
		"exam_oral_hygiene_poor",
		"exam_hygiene_col_break",
		"exam_prosthesis",
		"exam_prosthesis_details",
		
		# Dental examination fields
		"exam_dental_exam_section",
		"exam_teeth_numbers",
		"exam_teeth_issue_loose",
		"exam_teeth_issue_painful",
		"exam_teeth_issue_lost",
		"exam_teeth_issue_caries",
		"exam_teeth_issue_stained",
		"exam_teeth_issue_calculus",
		"exam_teeth_issue_missing",
		"exam_dental_col_break1",
		"exam_teeth_issue_broken",
		"exam_teeth_issue_abrasion",
		"exam_teeth_issue_irregular",
		"exam_teeth_issue_sharp",
		"exam_teeth_issue_attrition",
		"exam_teeth_issue_root_stump",
		"exam_teeth_issue_tender",
		"exam_dental_notes",
		
		# Lesion examination fields - all will be hidden
		"exam_lesion_exam_section",
		"exam_lesion_present",
		"exam_lesion_definition_section",
		"exam_lesion_single",
		"exam_lesion_multiple",
		"exam_lesion_col_def",
		"exam_lesion_localized",
		"exam_lesion_generalized"
	]
	
	# Hide old fields from the list
	hidden_count = 0
	for fieldname in old_fields:
		if frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": fieldname}):
			frappe.db.set_value("Custom Field", {"dt": doctype, "fieldname": fieldname}, "hidden", 1)
			hidden_count += 1
	
	# Also hide ALL lesion-related fields (there are many)
	lesion_fields = frappe.get_all(
		"Custom Field", 
		filters={"dt": doctype, "fieldname": ["like", "%lesion%"]},
		pluck="fieldname"
	)
	for fieldname in lesion_fields:
		frappe.db.set_value("Custom Field", {"dt": doctype, "fieldname": fieldname}, "hidden", 1)
		hidden_count += 1
	
	frappe.db.commit()
	frappe.clear_cache(doctype=doctype)
	
	print(f"  ✓ Hidden {hidden_count} old individual Step 2 fields")
	print("  ✓ Cache cleared for Patient Encounter")
	print("="*60 + "\n")

