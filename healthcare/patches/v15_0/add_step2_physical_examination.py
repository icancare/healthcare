import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def execute():
	"""Add STEP 2 - Physical Examination fields to Patient Encounter"""
	print("\n" + "="*60)
	print("Adding STEP 2 - Physical Examination to Patient Encounter")
	print("="*60)
	
	doctype = "Patient Encounter"
	base_condition = 'eval:doc.practitioner && doc.show_clinical_examination'
	
	fields = [
		# ============================================
		# STEP 2 - Physical Examination Main Section
		# ============================================
		{
			"fieldname": "exam_step2_section",
			"label": "STEP 2 - Physical Examination",
			"fieldtype": "Section Break",
			"insert_after": "exam_complaints",
			"collapsible": 0,
			"depends_on": base_condition,
			"description": "Done by: Doctor, Doctor Assistant"
		},
		{
			"fieldname": "exam_step2_done_by",
			"label": "Examination Done By",
			"fieldtype": "Select",
			"insert_after": "exam_step2_section",
			"options": "\nDoctor\nDoctor Assistant",
			"depends_on": base_condition
		},
		
		# ============================================
		# Examination Status - Normal/Abnormal per area
		# ============================================
		{
			"fieldname": "exam_status_subsection",
			"label": "Examination Status",
			"fieldtype": "Section Break",
			"insert_after": "exam_step2_done_by",
			"collapsible": 0,
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_face_status",
			"label": "Face",
			"fieldtype": "Select",
			"insert_after": "exam_status_subsection",
			"options": "\nNormal\nAbnormal",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_neck_status",
			"label": "Neck",
			"fieldtype": "Select",
			"insert_after": "exam_face_status",
			"options": "\nNormal\nAbnormal",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_mouth_status",
			"label": "Mouth",
			"fieldtype": "Select",
			"insert_after": "exam_neck_status",
			"options": "\nNormal\nAbnormal",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_dental_status",
			"label": "Dental",
			"fieldtype": "Select",
			"insert_after": "exam_mouth_status",
			"options": "\nNormal\nAbnormal",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_throat_status",
			"label": "Throat",
			"fieldtype": "Select",
			"insert_after": "exam_dental_status",
			"options": "\nNormal\nAbnormal",
			"depends_on": base_condition
		},
		
		# ============================================
		# FACE EXAMINATION - Shows when Face = Abnormal
		# ============================================
		{
			"fieldname": "exam_face_exam_section",
			"label": "Face Examination",
			"fieldtype": "Section Break",
			"insert_after": "exam_throat_status",
			"collapsible": 0,
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		# Face Locations
		{
			"fieldname": "exam_face_loc_forehead_left",
			"label": "Forehead - Left",
			"fieldtype": "Check",
			"insert_after": "exam_face_exam_section",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		{
			"fieldname": "exam_face_loc_forehead_right",
			"label": "Forehead - Right",
			"fieldtype": "Check",
			"insert_after": "exam_face_loc_forehead_left",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		{
			"fieldname": "exam_face_loc_eye_left",
			"label": "Eye - Left",
			"fieldtype": "Check",
			"insert_after": "exam_face_loc_forehead_right",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		{
			"fieldname": "exam_face_loc_eye_right",
			"label": "Eye - Right",
			"fieldtype": "Check",
			"insert_after": "exam_face_loc_eye_left",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		{
			"fieldname": "exam_face_loc_nose_left",
			"label": "Nose - Left",
			"fieldtype": "Check",
			"insert_after": "exam_face_loc_eye_right",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		{
			"fieldname": "exam_face_loc_nose_right",
			"label": "Nose - Right",
			"fieldtype": "Check",
			"insert_after": "exam_face_loc_nose_left",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		{
			"fieldname": "exam_face_loc_chin",
			"label": "Chin",
			"fieldtype": "Check",
			"insert_after": "exam_face_loc_nose_right",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		{
			"fieldname": "exam_face_loc_cheek_left",
			"label": "Cheek - Left",
			"fieldtype": "Check",
			"insert_after": "exam_face_loc_chin",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		{
			"fieldname": "exam_face_loc_cheek_right",
			"label": "Cheek - Right",
			"fieldtype": "Check",
			"insert_after": "exam_face_loc_cheek_left",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		{
			"fieldname": "exam_face_loc_parotid_left",
			"label": "Parotid - Left",
			"fieldtype": "Check",
			"insert_after": "exam_face_loc_cheek_right",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		{
			"fieldname": "exam_face_loc_parotid_right",
			"label": "Parotid - Right",
			"fieldtype": "Check",
			"insert_after": "exam_face_loc_parotid_left",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		{
			"fieldname": "exam_face_loc_ear_left",
			"label": "Ear - Left",
			"fieldtype": "Check",
			"insert_after": "exam_face_loc_parotid_right",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		{
			"fieldname": "exam_face_loc_ear_right",
			"label": "Ear - Right",
			"fieldtype": "Check",
			"insert_after": "exam_face_loc_ear_left",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		{
			"fieldname": "exam_face_col_break1",
			"fieldtype": "Column Break",
			"insert_after": "exam_face_loc_ear_right"
		},
		# Face Abnormalities
		{
			"fieldname": "exam_face_abn_asymmetry",
			"label": "Asymmetry",
			"fieldtype": "Check",
			"insert_after": "exam_face_col_break1",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		{
			"fieldname": "exam_face_abn_swelling",
			"label": "Swelling/Nodule",
			"fieldtype": "Check",
			"insert_after": "exam_face_abn_asymmetry",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		{
			"fieldname": "exam_face_abn_lymph",
			"label": "Lymph Nodes",
			"fieldtype": "Check",
			"insert_after": "exam_face_abn_swelling",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		{
			"fieldname": "exam_face_abn_ulcer",
			"label": "Ulcer",
			"fieldtype": "Check",
			"insert_after": "exam_face_abn_lymph",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		{
			"fieldname": "exam_face_abn_decreased_movement",
			"label": "Decreased Movement",
			"fieldtype": "Check",
			"insert_after": "exam_face_abn_ulcer",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		{
			"fieldname": "exam_face_notes",
			"label": "Face Examination Notes",
			"fieldtype": "Small Text",
			"insert_after": "exam_face_abn_decreased_movement",
			"depends_on": base_condition + " && doc.exam_face_status=='Abnormal'"
		},
		
		# ============================================
		# NECK EXAMINATION - Shows when Neck = Abnormal
		# ============================================
		{
			"fieldname": "exam_neck_exam_section",
			"label": "Neck Examination",
			"fieldtype": "Section Break",
			"insert_after": "exam_face_notes",
			"collapsible": 0,
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		# Neck Locations
		{
			"fieldname": "exam_neck_loc_left",
			"label": "Neck - Left",
			"fieldtype": "Check",
			"insert_after": "exam_neck_exam_section",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		{
			"fieldname": "exam_neck_loc_right",
			"label": "Neck - Right",
			"fieldtype": "Check",
			"insert_after": "exam_neck_loc_left",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		{
			"fieldname": "exam_neck_loc_central",
			"label": "Neck - Central",
			"fieldtype": "Check",
			"insert_after": "exam_neck_loc_right",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		{
			"fieldname": "exam_neck_loc_submandibular_left",
			"label": "SUBMANDIBULAR - Left",
			"fieldtype": "Check",
			"insert_after": "exam_neck_loc_central",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		{
			"fieldname": "exam_neck_loc_submandibular_right",
			"label": "SUBMANDIBULAR - Right",
			"fieldtype": "Check",
			"insert_after": "exam_neck_loc_submandibular_left",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		{
			"fieldname": "exam_neck_loc_thyroid_left",
			"label": "THYROID - Left Lobe",
			"fieldtype": "Check",
			"insert_after": "exam_neck_loc_submandibular_right",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		{
			"fieldname": "exam_neck_loc_thyroid_right",
			"label": "THYROID - Right Lobe",
			"fieldtype": "Check",
			"insert_after": "exam_neck_loc_thyroid_left",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		{
			"fieldname": "exam_neck_loc_thyroid_central",
			"label": "THYROID - Central",
			"fieldtype": "Check",
			"insert_after": "exam_neck_loc_thyroid_right",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		{
			"fieldname": "exam_neck_loc_parathyroid",
			"label": "Parathyroid",
			"fieldtype": "Check",
			"insert_after": "exam_neck_loc_thyroid_central",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		{
			"fieldname": "exam_neck_loc_back_left",
			"label": "Back of Neck - Left",
			"fieldtype": "Check",
			"insert_after": "exam_neck_loc_parathyroid",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		{
			"fieldname": "exam_neck_loc_back_right",
			"label": "Back of Neck - Right",
			"fieldtype": "Check",
			"insert_after": "exam_neck_loc_back_left",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		{
			"fieldname": "exam_neck_loc_other",
			"label": "Any Other",
			"fieldtype": "Check",
			"insert_after": "exam_neck_loc_back_right",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		{
			"fieldname": "exam_neck_loc_other_specify",
			"label": "Specify Other Location",
			"fieldtype": "Data",
			"insert_after": "exam_neck_loc_other",
			"depends_on": base_condition + " && doc.exam_neck_loc_other"
		},
		{
			"fieldname": "exam_neck_col_break1",
			"fieldtype": "Column Break",
			"insert_after": "exam_neck_loc_other_specify"
		},
		# Neck Abnormalities
		{
			"fieldname": "exam_neck_abn_pain",
			"label": "Pain",
			"fieldtype": "Check",
			"insert_after": "exam_neck_col_break1",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		{
			"fieldname": "exam_neck_abn_asymmetry",
			"label": "Asymmetry",
			"fieldtype": "Check",
			"insert_after": "exam_neck_abn_pain",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		{
			"fieldname": "exam_neck_abn_swelling",
			"label": "Swelling/Nodule",
			"fieldtype": "Check",
			"insert_after": "exam_neck_abn_asymmetry",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		{
			"fieldname": "exam_neck_abn_lymph",
			"label": "Lymph Nodes",
			"fieldtype": "Check",
			"insert_after": "exam_neck_abn_swelling",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		{
			"fieldname": "exam_neck_abn_ulcer",
			"label": "Ulcer",
			"fieldtype": "Check",
			"insert_after": "exam_neck_abn_lymph",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		{
			"fieldname": "exam_neck_notes",
			"label": "Neck Examination Notes",
			"fieldtype": "Small Text",
			"insert_after": "exam_neck_abn_ulcer",
			"depends_on": base_condition + " && doc.exam_neck_status=='Abnormal'"
		},
		
		# ============================================
		# MOUTH EXAMINATION - Shows when Mouth = Abnormal
		# ============================================
		{
			"fieldname": "exam_mouth_exam_section",
			"label": "Mouth Examination",
			"fieldtype": "Section Break",
			"insert_after": "exam_neck_notes",
			"collapsible": 0,
			"depends_on": base_condition + " && doc.exam_mouth_status=='Abnormal'"
		},
		# Mouth Opening
		{
			"fieldname": "exam_mouth_opening_label",
			"label": "Mouth Opening",
			"fieldtype": "Heading",
			"insert_after": "exam_mouth_exam_section",
			"depends_on": base_condition + " && doc.exam_mouth_status=='Abnormal'"
		},
		{
			"fieldname": "exam_mouth_opening_fingers",
			"label": "Fingers",
			"fieldtype": "Select",
			"insert_after": "exam_mouth_opening_label",
			"options": "\nOne\nTwo\nThree\nFour",
			"depends_on": base_condition + " && doc.exam_mouth_status=='Abnormal'"
		},
		{
			"fieldname": "exam_mouth_opening_mm",
			"label": "Measured (mm)",
			"fieldtype": "Float",
			"insert_after": "exam_mouth_opening_fingers",
			"depends_on": base_condition + " && doc.exam_mouth_status=='Abnormal'"
		},
		{
			"fieldname": "exam_mouth_measured_with",
			"label": "Measured With",
			"fieldtype": "Select",
			"insert_after": "exam_mouth_opening_mm",
			"options": "\nTrisCare\nCaliper\nOther",
			"depends_on": base_condition + " && doc.exam_mouth_status=='Abnormal'"
		},
		{
			"fieldname": "exam_mouth_col_break1",
			"fieldtype": "Column Break",
			"insert_after": "exam_mouth_measured_with"
		},
		# Tongue Movement
		{
			"fieldname": "exam_tongue_label",
			"label": "Tongue Movement",
			"fieldtype": "Heading",
			"insert_after": "exam_mouth_col_break1",
			"depends_on": base_condition + " && doc.exam_mouth_status=='Abnormal'"
		},
		{
			"fieldname": "exam_tongue_normal",
			"label": "Normal Tongue",
			"fieldtype": "Check",
			"insert_after": "exam_tongue_label",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_mouth_status=='Abnormal'"
		},
		{
			"fieldname": "exam_tongue_painful",
			"label": "Painful Tongue",
			"fieldtype": "Check",
			"insert_after": "exam_tongue_normal",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_mouth_status=='Abnormal'"
		},
		{
			"fieldname": "exam_tongue_deviation_left",
			"label": "Tongue Deviation to Left",
			"fieldtype": "Check",
			"insert_after": "exam_tongue_painful",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_mouth_status=='Abnormal'"
		},
		{
			"fieldname": "exam_tongue_deviation_right",
			"label": "Tongue Deviation to Right",
			"fieldtype": "Check",
			"insert_after": "exam_tongue_deviation_left",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_mouth_status=='Abnormal'"
		},
		{
			"fieldname": "exam_tongue_restricted",
			"label": "Restricted Protrusion of Tongue",
			"fieldtype": "Check",
			"insert_after": "exam_tongue_deviation_right",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_mouth_status=='Abnormal'"
		},
		{
			"fieldname": "exam_tongue_protrusion_mm",
			"label": "Tongue Protrusion measured by scale (mm)",
			"fieldtype": "Float",
			"insert_after": "exam_tongue_restricted",
			"depends_on": base_condition + " && doc.exam_mouth_status=='Abnormal'"
		},
		# Oral Hygiene Section
		{
			"fieldname": "exam_oral_hygiene_section",
			"label": "Oral Hygiene & Prosthesis",
			"fieldtype": "Section Break",
			"insert_after": "exam_tongue_protrusion_mm",
			"collapsible": 0,
			"depends_on": base_condition + " && doc.exam_mouth_status=='Abnormal'"
		},
		{
			"fieldname": "exam_oral_hygiene_good",
			"label": "Good Oral Hygiene",
			"fieldtype": "Check",
			"insert_after": "exam_oral_hygiene_section",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_mouth_status=='Abnormal'"
		},
		{
			"fieldname": "exam_oral_hygiene_moderate",
			"label": "Moderate Oral Hygiene",
			"fieldtype": "Check",
			"insert_after": "exam_oral_hygiene_good",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_mouth_status=='Abnormal'"
		},
		{
			"fieldname": "exam_oral_hygiene_poor",
			"label": "Poor Oral Hygiene",
			"fieldtype": "Check",
			"insert_after": "exam_oral_hygiene_moderate",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_mouth_status=='Abnormal'"
		},
		{
			"fieldname": "exam_hygiene_col_break",
			"fieldtype": "Column Break",
			"insert_after": "exam_oral_hygiene_poor"
		},
		{
			"fieldname": "exam_prosthesis",
			"label": "Prosthesis",
			"fieldtype": "Select",
			"insert_after": "exam_hygiene_col_break",
			"options": "\nYes\nNo",
			"depends_on": base_condition + " && doc.exam_mouth_status=='Abnormal'"
		},
		{
			"fieldname": "exam_prosthesis_details",
			"label": "Prosthesis Details",
			"fieldtype": "Small Text",
			"insert_after": "exam_prosthesis",
			"depends_on": base_condition + " && doc.exam_prosthesis=='Yes'"
		},
		
		# ============================================
		# DENTAL EXAMINATION - Shows when Dental = Abnormal
		# ============================================
		{
			"fieldname": "exam_dental_exam_section",
			"label": "Dental/Teeth Examination",
			"fieldtype": "Section Break",
			"insert_after": "exam_prosthesis_details",
			"collapsible": 0,
			"depends_on": base_condition + " && doc.exam_dental_status=='Abnormal'"
		},
		{
			"fieldname": "exam_teeth_numbers",
			"label": "Teeth Numbers (comma separated)",
			"fieldtype": "Data",
			"insert_after": "exam_dental_exam_section",
			"description": "Enter affected teeth numbers",
			"depends_on": base_condition + " && doc.exam_dental_status=='Abnormal'"
		},
		# Teeth Issues
		{
			"fieldname": "exam_teeth_issue_loose",
			"label": "Loose Teeth",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_numbers",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_dental_status=='Abnormal'"
		},
		{
			"fieldname": "exam_teeth_issue_painful",
			"label": "Painful Teeth",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_issue_loose",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_dental_status=='Abnormal'"
		},
		{
			"fieldname": "exam_teeth_issue_lost",
			"label": "Lost Teeth",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_issue_painful",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_dental_status=='Abnormal'"
		},
		{
			"fieldname": "exam_teeth_issue_caries",
			"label": "Caries Teeth",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_issue_lost",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_dental_status=='Abnormal'"
		},
		{
			"fieldname": "exam_teeth_issue_stained",
			"label": "Stained Teeth",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_issue_caries",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_dental_status=='Abnormal'"
		},
		{
			"fieldname": "exam_teeth_issue_calculus",
			"label": "Calculus Around Teeth",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_issue_stained",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_dental_status=='Abnormal'"
		},
		{
			"fieldname": "exam_teeth_issue_missing",
			"label": "Missing Teeth",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_issue_calculus",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_dental_status=='Abnormal'"
		},
		{
			"fieldname": "exam_dental_col_break1",
			"fieldtype": "Column Break",
			"insert_after": "exam_teeth_issue_missing"
		},
		{
			"fieldname": "exam_teeth_issue_broken",
			"label": "Broken Teeth",
			"fieldtype": "Check",
			"insert_after": "exam_dental_col_break1",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_dental_status=='Abnormal'"
		},
		{
			"fieldname": "exam_teeth_issue_abrasion",
			"label": "Abrasion Teeth",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_issue_broken",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_dental_status=='Abnormal'"
		},
		{
			"fieldname": "exam_teeth_issue_irregular",
			"label": "Irregular Alignment of Teeth",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_issue_abrasion",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_dental_status=='Abnormal'"
		},
		{
			"fieldname": "exam_teeth_issue_sharp",
			"label": "Sharp Teeth",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_issue_irregular",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_dental_status=='Abnormal'"
		},
		{
			"fieldname": "exam_teeth_issue_attrition",
			"label": "Attrition in Teeth",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_issue_sharp",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_dental_status=='Abnormal'"
		},
		{
			"fieldname": "exam_teeth_issue_root_stump",
			"label": "Root Stump Teeth",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_issue_attrition",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_dental_status=='Abnormal'"
		},
		{
			"fieldname": "exam_teeth_issue_tender",
			"label": "Tender Teeth",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_issue_root_stump",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_dental_status=='Abnormal'"
		},
		{
			"fieldname": "exam_dental_notes",
			"label": "Dental Examination Notes",
			"fieldtype": "Small Text",
			"insert_after": "exam_teeth_issue_tender",
			"depends_on": base_condition + " && doc.exam_dental_status=='Abnormal'"
		},
		
		# ============================================
		# LESION EXAMINATION SECTION
		# ============================================
		{
			"fieldname": "exam_lesion_exam_section",
			"label": "Lesion Examination",
			"fieldtype": "Section Break",
			"insert_after": "exam_dental_notes",
			"collapsible": 0,
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_lesion_present",
			"label": "Lesion Present",
			"fieldtype": "Select",
			"insert_after": "exam_lesion_exam_section",
			"options": "\nNo\nYes",
			"depends_on": base_condition
		},
		
		# Lesion Definition
		{
			"fieldname": "exam_lesion_definition_section",
			"label": "Lesion Definition",
			"fieldtype": "Section Break",
			"insert_after": "exam_lesion_present",
			"collapsible": 0,
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_single",
			"label": "Single",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_definition_section",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_multiple",
			"label": "Multiple",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_single",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_col_def",
			"fieldtype": "Column Break",
			"insert_after": "exam_lesion_multiple"
		},
		{
			"fieldname": "exam_lesion_localized",
			"label": "Localized (focal, found in one area only)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_col_def",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_generalized",
			"label": "Generalized (diffuse, found in most of the tissues in one area)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_localized",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		
		# Lesion Location
		{
			"fieldname": "exam_lesion_location_section",
			"label": "Lesion Location",
			"fieldtype": "Section Break",
			"insert_after": "exam_lesion_generalized",
			"collapsible": 0,
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_lower_lip",
			"label": "Lower lip (L, R)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_location_section",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_upper_lip",
			"label": "Upper lip (L, R)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_loc_lower_lip",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_anterior_arch",
			"label": "Anterior Arch (L, R)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_loc_upper_lip",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_upper_gb_sulcus",
			"label": "Upper anterior GB sulcus (L, R)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_loc_anterior_arch",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_lower_gb_sulcus",
			"label": "Lower anterior GB sulcus (L, R)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_loc_upper_gb_sulcus",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_angle_mouth",
			"label": "Angle of Mouth (L, R)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_loc_lower_gb_sulcus",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_upper_alveolus",
			"label": "Upper Alveolus and Gingivo-Buccal Sulcus Maxillary Gingiva (L, R)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_loc_angle_mouth",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_lower_alveolus",
			"label": "Lower Alveolus and Gingivo-Buccal Sulcus Mandibular Gingiva (L, R)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_loc_upper_alveolus",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_col1",
			"fieldtype": "Column Break",
			"insert_after": "exam_lesion_loc_lower_alveolus"
		},
		{
			"fieldname": "exam_lesion_loc_ventral_tongue",
			"label": "Ventral Tongue (L, R, Midline)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_loc_col1",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_rmt",
			"label": "RMT (L, R)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_loc_ventral_tongue",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_dorsum_tongue",
			"label": "Dorsum Tongue and Anterior floor of mouth",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_loc_rmt",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_lateral_tongue",
			"label": "Lateral Tongue and FOM (L, R)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_loc_dorsum_tongue",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_buccal_mucosa",
			"label": "Buccal mucosa (L, R)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_loc_lateral_tongue",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_hard_palate",
			"label": "Hard palate (L, R, Midline)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_loc_buccal_mucosa",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_soft_palate",
			"label": "Soft palate (L, R, Midline)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_loc_hard_palate",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_oropharynx",
			"label": "Oropharynx (L, R, Midline)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_loc_soft_palate",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_base_tongue",
			"label": "Base of Tongue (L, R, Midline)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_loc_oropharynx",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_tonsil",
			"label": "Tonsil (L, R)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_loc_base_tongue",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_loc_other",
			"label": "Other Location",
			"fieldtype": "Data",
			"insert_after": "exam_lesion_loc_tonsil",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		
		# Lesion Distribution (Margin/Border)
		{
			"fieldname": "exam_lesion_distribution_section",
			"label": "Lesion Distribution (Margin/Border)",
			"fieldtype": "Section Break",
			"insert_after": "exam_lesion_loc_other",
			"collapsible": 0,
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_well_defined",
			"label": "Well-defined (circumscribed)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_distribution_section",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_poorly_defined",
			"label": "Poorly-defined (vague)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_well_defined",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_regular",
			"label": "Regular",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_poorly_defined",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_irregular_borders",
			"label": "Irregular Borders",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_regular",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		
		# Lesion Size
		{
			"fieldname": "exam_lesion_size_section",
			"label": "Lesion Size",
			"fieldtype": "Section Break",
			"insert_after": "exam_lesion_irregular_borders",
			"collapsible": 0,
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_length_mm",
			"label": "Length (mm)",
			"fieldtype": "Float",
			"insert_after": "exam_lesion_size_section",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_width_mm",
			"label": "Width (mm)",
			"fieldtype": "Float",
			"insert_after": "exam_lesion_length_mm",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_height_mm",
			"label": "Height (mm)",
			"fieldtype": "Float",
			"insert_after": "exam_lesion_width_mm",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_size_note",
			"label": "Size Note",
			"fieldtype": "Small Text",
			"insert_after": "exam_lesion_height_mm",
			"description": "Measure with probe; note greatest dimensions",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		
		# Lesion Color
		{
			"fieldname": "exam_lesion_color_section",
			"label": "Color of Lesion",
			"fieldtype": "Section Break",
			"insert_after": "exam_lesion_size_note",
			"collapsible": 0,
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_color_uniform",
			"label": "Uniform lesion in mouth oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_color_section",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_color_variegated",
			"label": "Variegated color lesion in mouth oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_color_uniform",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_color_white",
			"label": "White lesion in mouth oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_color_variegated",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_color_red",
			"label": "Red lesion in mouth oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_color_white",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_color_black",
			"label": "Black lesion in mouth oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_color_red",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_color_brown",
			"label": "Brown lesion in mouth oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_color_black",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_color_mixed",
			"label": "Mixed type lesion in mouth cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_color_brown",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		
		# Lesion Shape
		{
			"fieldname": "exam_lesion_shape_section",
			"label": "Shape of Lesion",
			"fieldtype": "Section Break",
			"insert_after": "exam_lesion_color_mixed",
			"collapsible": 0,
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_shape_round",
			"label": "Round",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_shape_section",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_shape_oval",
			"label": "Oval",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_shape_round",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_shape_irregular",
			"label": "Irregular",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_shape_oval",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_shape_rectangular",
			"label": "Rectangular",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_shape_irregular",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		
		# Lesion Description (Visual Inspection)
		{
			"fieldname": "exam_lesion_desc_section",
			"label": "Lesion Description - Open Mouth Examination Visual Inspection",
			"fieldtype": "Section Break",
			"insert_after": "exam_lesion_shape_rectangular",
			"collapsible": 0,
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_foul_smell",
			"label": "Foul Smell Halitosis",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_section",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_cracked_lip",
			"label": "Cracked lip/angle of Mouth",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_foul_smell",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_macule",
			"label": "Macule—flat lesion in mouth",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_cracked_lip",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_vesicle",
			"label": "Vesicle—elevated lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_macule",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_pustule",
			"label": "Pustule—purulent lesion (filled with pus) lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_vesicle",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_papule",
			"label": "Papule—lesion less than 5 mm in diameter, raised with no fluid lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_pustule",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_nodule",
			"label": "Nodule—lesion less than 2 cm in diameter, raised with no fluid lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_papule",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_plaque",
			"label": "Plaque—broad, slightly raised lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_nodule",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_sessile",
			"label": "Sessile-based—broad attachment lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_plaque",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_pedunculated",
			"label": "Pedunculated—stalk-like attachment lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_sessile",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_col1",
			"fieldtype": "Column Break",
			"insert_after": "exam_lesion_desc_pedunculated"
		},
		{
			"fieldname": "exam_lesion_desc_white_patch",
			"label": "White Patch (leukoplakia) lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_col1",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_smooth_white",
			"label": "SMOOTH white (Homogenous) lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_white_patch",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_verrucous_white",
			"label": "Verrucous greyish white lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_smooth_white",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_irregular_white",
			"label": "Irregular white lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_verrucous_white",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_lacy_white",
			"label": "Lacy like lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_irregular_white",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_verrucous",
			"label": "Verrucous",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_lacy_white",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_red_patch",
			"label": "Red Patch (Erythroplakia) lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_verrucous",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_smooth_red",
			"label": "Smooth Red lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_red_patch",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_erosive_red",
			"label": "Erosive red lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_smooth_red",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_superficial_ulcer",
			"label": "Superficial ulcer lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_erosive_red",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_deep_ulcer",
			"label": "Deep Ulcer lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_superficial_ulcer",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_deep_ulcer_smooth",
			"label": "Deep ulcer with Smooth margins lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_deep_ulcer",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_deep_ulcer_irregular",
			"label": "Deep ulcer with Irregular margins lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_deep_ulcer_smooth",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_fungal",
			"label": "Fungal lesion (white lesion scrapable) lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_deep_ulcer_irregular",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_bleeding",
			"label": "Bleeding lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_fungal",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_marbelled",
			"label": "Marbelled lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_bleeding",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_fibrous_bands",
			"label": "Fibrous bands lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_marbelled",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_desc_hypertrophic",
			"label": "Hypertrophic Mucosa lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_desc_fibrous_bands",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		
		# Lesion Consistency (Palpation)
		{
			"fieldname": "exam_lesion_consistency_section",
			"label": "Consistency - Palpation (Gloved Fingers)",
			"fieldtype": "Section Break",
			"insert_after": "exam_lesion_desc_hypertrophic",
			"collapsible": 0,
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_cons_tender",
			"label": "Tender painful on touch lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_consistency_section",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_cons_soft",
			"label": "Soft lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_cons_tender",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_cons_firm",
			"label": "Firm to feel lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_cons_soft",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_cons_hard",
			"label": "Hard to feel lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_cons_firm",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_cons_fluctuant",
			"label": "Fluctuant lesion in mouth/oral cavity (fluid-filled lesion that moves fluid from one area to another when the lesion is pressed)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_cons_hard",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_cons_bleeds",
			"label": "Bleeds on Touch lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_cons_fluctuant",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_cons_col1",
			"fieldtype": "Column Break",
			"insert_after": "exam_lesion_cons_bleeds"
		},
		{
			"fieldname": "exam_lesion_cons_blanching",
			"label": "Blanching of mucosa (Marble) SMF lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_cons_col1",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_cons_scrapable_white",
			"label": "Scrapable lesion white or red lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_cons_blanching",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_cons_non_scrapable",
			"label": "Non-Scrapable lesion lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_cons_scrapable_white",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_cons_smooth_border",
			"label": "Smooth border lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_cons_non_scrapable",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_cons_irregular_border",
			"label": "Irregular border lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_cons_smooth_border",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_cons_induration_present",
			"label": "Induration present lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_cons_irregular_border",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_cons_induration_absent",
			"label": "Induration absent lesion in mouth/oral cavity",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_cons_induration_present",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		
		# Lesion Texture
		{
			"fieldname": "exam_lesion_texture_section",
			"label": "Texture (Use tactile and visual assessment)",
			"fieldtype": "Section Break",
			"insert_after": "exam_lesion_cons_induration_absent",
			"collapsible": 0,
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_texture_smooth",
			"label": "Smooth",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_texture_section",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_texture_rough",
			"label": "Rough—papillary (finger-like projections)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_texture_smooth",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_texture_corrugated",
			"label": "Corrugated (rippled)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_texture_rough",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_texture_fissured",
			"label": "Fissured (deep crevices)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_texture_corrugated",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_texture_crusted",
			"label": "Crusted (covered with scab)",
			"fieldtype": "Check",
			"insert_after": "exam_lesion_texture_fissured",
			"default": "0",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
		},
		{
			"fieldname": "exam_lesion_final_notes",
			"label": "Lesion Examination Notes",
			"fieldtype": "Text Editor",
			"insert_after": "exam_lesion_texture_crusted",
			"depends_on": base_condition + " && doc.exam_lesion_present=='Yes'"
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
	print("\n✓ STEP 2 - Physical Examination Added to Patient Encounter!")
	print("="*60 + "\n")

