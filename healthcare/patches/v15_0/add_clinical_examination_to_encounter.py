import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field, create_custom_fields


def execute():
	"""Add Clinical Examination Section to Patient Encounter and Healthcare Practitioner"""
	
	# First add fields to Healthcare Practitioner for template assignment
	add_practitioner_fields()
	
	# Then add fields to Patient Encounter
	add_encounter_fields()


def add_practitioner_fields():
	"""Add Clinical Examination Template selector to Healthcare Practitioner"""
	print("\n" + "="*60)
	print("Adding Clinical Examination Settings to Healthcare Practitioner")
	print("="*60)
	
	custom_fields = {
		'Healthcare Practitioner': [
			{
				'fieldname': 'clinical_exam_section',
				'label': 'Clinical Examination Settings',
				'fieldtype': 'Section Break',
				'insert_after': 'department',
				'collapsible': 0
			},
			{
				'fieldname': 'default_examination_template',
				'label': 'Default Examination Template',
				'fieldtype': 'Link',
				'options': 'Clinical Examination Template',
				'insert_after': 'clinical_exam_section',
				'description': 'This examination form will be shown in Patient Encounter for this practitioner'
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	print("  ✓ Added Clinical Examination Settings to Healthcare Practitioner")


def add_encounter_fields():
	"""Add Clinical Examination Section to Patient Encounter"""
	print("\n" + "="*60)
	print("Adding Clinical Examination Section to Patient Encounter")
	print("="*60)
	
	doctype = "Patient Encounter"
	
	# Clinical Examination Section - After diagnosis_notes, before codification
	fields = [
		# Hidden field to control visibility based on practitioner template
		{
			"fieldname": "show_clinical_examination",
			"label": "Show Clinical Examination",
			"fieldtype": "Check",
			"insert_after": "invoiced",
			"hidden": 1,
			"default": "0"
		},
		
		# Main Section Break - Only show when practitioner has template
		{
			"fieldname": "clinical_examination_section",
			"label": "Clinical Examination",
			"fieldtype": "Section Break",
			"insert_after": "diagnosis_notes",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		
		# Case Type Row
		{
			"fieldname": "exam_case_type",
			"label": "Case Type",
			"fieldtype": "Select",
			"insert_after": "clinical_examination_section",
			"options": "\nNew Case\nFollow Up Case"
		},
		{
			"fieldname": "exam_follow_up_status",
			"label": "Follow Up Status",
			"fieldtype": "Select",
			"insert_after": "exam_case_type",
			"options": "\nNo New Complaints\nNo New Lesion\nNew Complaints\nNew Lesion",
			"depends_on": "eval:doc.exam_case_type=='Follow Up Case'"
		},
		{
			"fieldname": "exam_column_break_1",
			"fieldtype": "Column Break",
			"insert_after": "exam_follow_up_status"
		},
		{
			"fieldname": "exam_examination_type",
			"label": "Examination Type",
			"fieldtype": "Select",
			"insert_after": "exam_column_break_1",
			"options": "\nOral Screening\nDermatology\nGeneral Physical\nENT\nOphthalmology\nCardiology\nOther"
		},
		
		# STEP 1 - Patient Complaints Section
		{
			"fieldname": "exam_step1_section",
			"label": "STEP 1 - Patient Complaints",
			"fieldtype": "Section Break",
			"insert_after": "exam_examination_type",
			"collapsible": 0,
			"description": "Can be filled by: Patient Himself, Doctor Assistant, Counsellor, Doctor"
		},
		{
			"fieldname": "exam_filled_by",
			"label": "Filled By",
			"fieldtype": "Select",
			"insert_after": "exam_step1_section",
			"options": "\nPatient Himself\nDoctor Assistant\nCounsellor\nDoctor"
		},
		{
			"fieldname": "exam_complaints_status",
			"label": "Complaints Status",
			"fieldtype": "Select",
			"insert_after": "exam_filled_by",
			"options": "\nNo Complaints - Normal\nComplaints - Abnormal",
			"bold": 1
		},
		
		# Body Parts Selection - Only show if Abnormal
		{
			"fieldname": "exam_abnormal_body_parts_section",
			"label": "Abnormal Complaints Related To",
			"fieldtype": "Section Break",
			"insert_after": "exam_complaints_status",
			"depends_on": "eval:doc.exam_complaints_status=='Complaints - Abnormal'"
		},
		{
			"fieldname": "exam_complaint_face",
			"label": "Face",
			"fieldtype": "Check",
			"insert_after": "exam_abnormal_body_parts_section",
			"default": "0"
		},
		{
			"fieldname": "exam_complaint_neck",
			"label": "Neck",
			"fieldtype": "Check",
			"insert_after": "exam_complaint_face",
			"default": "0"
		},
		{
			"fieldname": "exam_complaint_oral_cavity",
			"label": "Oral Cavity (Mouth and Tongue)",
			"fieldtype": "Check",
			"insert_after": "exam_complaint_neck",
			"default": "0"
		},
		{
			"fieldname": "exam_complaint_teeth",
			"label": "Teeth (Dental)",
			"fieldtype": "Check",
			"insert_after": "exam_complaint_oral_cavity",
			"default": "0"
		},
		{
			"fieldname": "exam_complaint_others",
			"label": "Others",
			"fieldtype": "Check",
			"insert_after": "exam_complaint_teeth",
			"default": "0"
		},
		
		# Face Complaints - Only show if Face is checked
		{
			"fieldname": "exam_face_complaints_section",
			"label": "Face Complaints",
			"fieldtype": "Section Break",
			"insert_after": "exam_complaint_others",
			"depends_on": "eval:doc.exam_complaint_face",
			"collapsible": 0
		},
		{
			"fieldname": "exam_face_lump_swelling",
			"label": "Lump/Swelling on face",
			"fieldtype": "Check",
			"insert_after": "exam_face_complaints_section",
			"default": "0"
		},
		{
			"fieldname": "exam_face_pigmentation",
			"label": "Pigmentation",
			"fieldtype": "Check",
			"insert_after": "exam_face_lump_swelling",
			"default": "0"
		},
		{
			"fieldname": "exam_face_ulcer",
			"label": "Ulcer",
			"fieldtype": "Check",
			"insert_after": "exam_face_pigmentation",
			"default": "0"
		},
		{
			"fieldname": "exam_face_col_break",
			"fieldtype": "Column Break",
			"insert_after": "exam_face_ulcer"
		},
		{
			"fieldname": "exam_face_duration_days",
			"label": "Duration (Days)",
			"fieldtype": "Int",
			"insert_after": "exam_face_col_break"
		},
		{
			"fieldname": "exam_face_duration_category",
			"label": "Duration Category",
			"fieldtype": "Select",
			"insert_after": "exam_face_duration_days",
			"options": "\n1-5 days\n5-14 days\n>14 days - 1 month\n>1 month - 1 year\nLong time\nOccurs off and on"
		},
		{
			"fieldname": "exam_face_pattern",
			"label": "Pattern",
			"fieldtype": "Select",
			"insert_after": "exam_face_duration_category",
			"options": "\nIncreasing\nDecreasing\nPersistent\nIntermittent"
		},
		
		# Neck Complaints - Only show if Neck is checked
		{
			"fieldname": "exam_neck_complaints_section",
			"label": "Neck Complaints",
			"fieldtype": "Section Break",
			"insert_after": "exam_face_pattern",
			"depends_on": "eval:doc.exam_complaint_neck",
			"collapsible": 0
		},
		{
			"fieldname": "exam_neck_lump_outside",
			"label": "Lump/Swelling in Neck (outside)",
			"fieldtype": "Check",
			"insert_after": "exam_neck_complaints_section",
			"default": "0"
		},
		{
			"fieldname": "exam_neck_lump_throat",
			"label": "Swelling/lump in Throat (inside)",
			"fieldtype": "Check",
			"insert_after": "exam_neck_lump_outside",
			"default": "0"
		},
		{
			"fieldname": "exam_neck_col_break",
			"fieldtype": "Column Break",
			"insert_after": "exam_neck_lump_throat"
		},
		{
			"fieldname": "exam_neck_duration_days",
			"label": "Duration (Days)",
			"fieldtype": "Int",
			"insert_after": "exam_neck_col_break"
		},
		{
			"fieldname": "exam_neck_pattern",
			"label": "Pattern",
			"fieldtype": "Select",
			"insert_after": "exam_neck_duration_days",
			"options": "\nIncreasing\nDecreasing\nPersistent"
		},
		
		# Oral Cavity Complaints - Only show if Oral Cavity is checked
		{
			"fieldname": "exam_oral_complaints_section",
			"label": "Oral Cavity Complaints",
			"fieldtype": "Section Break",
			"insert_after": "exam_neck_pattern",
			"depends_on": "eval:doc.exam_complaint_oral_cavity",
			"collapsible": 0
		},
		{
			"fieldname": "exam_oral_restricted_mouth",
			"label": "Restricted Mouth opening",
			"fieldtype": "Check",
			"insert_after": "exam_oral_complaints_section",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_restricted_tongue",
			"label": "Restricted Tongue Movement",
			"fieldtype": "Check",
			"insert_after": "exam_oral_restricted_mouth",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_trauma",
			"label": "Trauma",
			"fieldtype": "Check",
			"insert_after": "exam_oral_restricted_tongue",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_pain",
			"label": "Pain",
			"fieldtype": "Check",
			"insert_after": "exam_oral_trauma",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_painful_ulcer",
			"label": "Painful Ulcer",
			"fieldtype": "Check",
			"insert_after": "exam_oral_pain",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_painless_ulcer",
			"label": "Painless Ulcer",
			"fieldtype": "Check",
			"insert_after": "exam_oral_painful_ulcer",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_recurrent_ulcer",
			"label": "Recurrent Ulcer",
			"fieldtype": "Check",
			"insert_after": "exam_oral_painless_ulcer",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_red_patch",
			"label": "Red patch in mouth",
			"fieldtype": "Check",
			"insert_after": "exam_oral_recurrent_ulcer",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_white_patch",
			"label": "White patch in mouth",
			"fieldtype": "Check",
			"insert_after": "exam_oral_red_patch",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_nodule_lump",
			"label": "Nodule/Lump",
			"fieldtype": "Check",
			"insert_after": "exam_oral_white_patch",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_swelling",
			"label": "Swelling",
			"fieldtype": "Check",
			"insert_after": "exam_oral_nodule_lump",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_sensitivity",
			"label": "Sensitivity in mouth/teeth",
			"fieldtype": "Check",
			"insert_after": "exam_oral_swelling",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_burning",
			"label": "Burning Sensation",
			"fieldtype": "Check",
			"insert_after": "exam_oral_sensitivity",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_bleeding",
			"label": "Bleeding",
			"fieldtype": "Check",
			"insert_after": "exam_oral_burning",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_decreased_saliva",
			"label": "Decreased Salivation",
			"fieldtype": "Check",
			"insert_after": "exam_oral_bleeding",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_increased_saliva",
			"label": "Increased Salivation",
			"fieldtype": "Check",
			"insert_after": "exam_oral_decreased_saliva",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_foul_smell",
			"label": "Foul Smell (Halitosis)",
			"fieldtype": "Check",
			"insert_after": "exam_oral_increased_saliva",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_swallowing_difficulty",
			"label": "Swallowing Difficulty/pain during",
			"fieldtype": "Check",
			"insert_after": "exam_oral_foul_smell",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_others",
			"label": "Others",
			"fieldtype": "Check",
			"insert_after": "exam_oral_swallowing_difficulty",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_others_specify",
			"label": "Specify Others",
			"fieldtype": "Small Text",
			"insert_after": "exam_oral_others",
			"depends_on": "eval:doc.exam_oral_others"
		},
		{
			"fieldname": "exam_oral_col_break",
			"fieldtype": "Column Break",
			"insert_after": "exam_oral_others_specify"
		},
		{
			"fieldname": "exam_oral_onset_date",
			"label": "Onset - When did the lesion appear?",
			"fieldtype": "Date",
			"insert_after": "exam_oral_col_break"
		},
		{
			"fieldname": "exam_oral_duration_days",
			"label": "Duration (Days)",
			"fieldtype": "Int",
			"insert_after": "exam_oral_onset_date"
		},
		{
			"fieldname": "exam_oral_is_intermittent",
			"label": "Is Intermittent",
			"fieldtype": "Check",
			"insert_after": "exam_oral_duration_days",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_is_recurrent",
			"label": "Is Recurrent",
			"fieldtype": "Check",
			"insert_after": "exam_oral_is_intermittent",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_pattern",
			"label": "Pattern",
			"fieldtype": "Select",
			"insert_after": "exam_oral_is_recurrent",
			"options": "\nIncreasing\nDecreasing\nPersistent"
		},
		{
			"fieldname": "exam_oral_trauma_question",
			"label": "Trauma - Did you experience any trauma in the area?",
			"fieldtype": "Check",
			"insert_after": "exam_oral_pattern",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_medical_treatment",
			"label": "Did you undergo medical treatment?",
			"fieldtype": "Check",
			"insert_after": "exam_oral_trauma_question",
			"default": "0"
		},
		{
			"fieldname": "exam_oral_treatment_details",
			"label": "Treatment Details",
			"fieldtype": "Small Text",
			"insert_after": "exam_oral_medical_treatment",
			"depends_on": "eval:doc.exam_oral_medical_treatment"
		},
		
		# Teeth Complaints - Only show if Teeth is checked
		{
			"fieldname": "exam_teeth_complaints_section",
			"label": "Teeth (Dental) Complaints",
			"fieldtype": "Section Break",
			"insert_after": "exam_oral_treatment_details",
			"depends_on": "eval:doc.exam_complaint_teeth",
			"collapsible": 0
		},
		{
			"fieldname": "exam_teeth_painful",
			"label": "Painful teeth",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_complaints_section",
			"default": "0"
		},
		{
			"fieldname": "exam_teeth_loosening",
			"label": "Loosening of teeth",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_painful",
			"default": "0"
		},
		{
			"fieldname": "exam_teeth_lost",
			"label": "Lost teeth",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_loosening",
			"default": "0"
		},
		{
			"fieldname": "exam_teeth_gum_problem",
			"label": "Teeth or gum problem",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_lost",
			"default": "0"
		},
		{
			"fieldname": "exam_teeth_denture",
			"label": "Denture problem",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_gum_problem",
			"default": "0"
		},
		{
			"fieldname": "exam_teeth_col_break",
			"fieldtype": "Column Break",
			"insert_after": "exam_teeth_denture"
		},
		{
			"fieldname": "exam_teeth_duration_days",
			"label": "Duration (Days)",
			"fieldtype": "Int",
			"insert_after": "exam_teeth_col_break"
		},
		{
			"fieldname": "exam_teeth_pattern",
			"label": "Pattern",
			"fieldtype": "Select",
			"insert_after": "exam_teeth_duration_days",
			"options": "\nIncreasing\nDecreasing\nPersistent"
		},
		{
			"fieldname": "exam_teeth_trauma",
			"label": "Trauma Related",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_pattern",
			"default": "0"
		},
		{
			"fieldname": "exam_teeth_treatment",
			"label": "Medical Treatment Taken",
			"fieldtype": "Check",
			"insert_after": "exam_teeth_trauma",
			"default": "0"
		},
		
		# Others Complaints - Only show if Others is checked
		{
			"fieldname": "exam_others_complaints_section",
			"label": "Other Complaints",
			"fieldtype": "Section Break",
			"insert_after": "exam_teeth_treatment",
			"depends_on": "eval:doc.exam_complaint_others",
			"collapsible": 0
		},
		{
			"fieldname": "exam_others_stickiness",
			"label": "Stickiness in throat",
			"fieldtype": "Check",
			"insert_after": "exam_others_complaints_section",
			"default": "0"
		},
		{
			"fieldname": "exam_others_voice_change",
			"label": "Change in Voice",
			"fieldtype": "Check",
			"insert_after": "exam_others_stickiness",
			"default": "0"
		},
		{
			"fieldname": "exam_others_sore_throat",
			"label": "Sore throat/Hoarseness",
			"fieldtype": "Check",
			"insert_after": "exam_others_voice_change",
			"default": "0"
		},
		{
			"fieldname": "exam_others_swallowing",
			"label": "Swallowing Difficulty/pain",
			"fieldtype": "Check",
			"insert_after": "exam_others_sore_throat",
			"default": "0"
		},
		{
			"fieldname": "exam_others_earache",
			"label": "Earache",
			"fieldtype": "Check",
			"insert_after": "exam_others_swallowing",
			"default": "0"
		},
		{
			"fieldname": "exam_others_specify",
			"label": "Others, please specify",
			"fieldtype": "Small Text",
			"insert_after": "exam_others_earache"
		},
		{
			"fieldname": "exam_others_col_break",
			"fieldtype": "Column Break",
			"insert_after": "exam_others_specify"
		},
		{
			"fieldname": "exam_others_duration_days",
			"label": "Duration (Days)",
			"fieldtype": "Int",
			"insert_after": "exam_others_col_break"
		},
		{
			"fieldname": "exam_others_pattern",
			"label": "Pattern",
			"fieldtype": "Select",
			"insert_after": "exam_others_duration_days",
			"options": "\nIncreasing\nDecreasing\nPersistent"
		},
		{
			"fieldname": "exam_others_trauma",
			"label": "Trauma Related",
			"fieldtype": "Check",
			"insert_after": "exam_others_pattern",
			"default": "0"
		},
		{
			"fieldname": "exam_others_treatment",
			"label": "Medical Treatment Taken",
			"fieldtype": "Check",
			"insert_after": "exam_others_trauma",
			"default": "0"
		},
		
		# Old complaints table - keep for backward compatibility but hidden
		{
			"fieldname": "exam_complaints",
			"label": "Complaints Details",
			"fieldtype": "Table",
			"insert_after": "exam_others_treatment",
			"options": "Clinical Exam Complaint",
			"hidden": 1
		},
		
		# Physical Examination Subsection
		{
			"fieldname": "exam_physical_section",
			"label": "Physical Examination",
			"fieldtype": "Section Break",
			"insert_after": "exam_complaints",
			"collapsible": 1
		},
		{
			"fieldname": "exam_mouth_opening_fingers",
			"label": "Mouth Opening (Fingers)",
			"fieldtype": "Select",
			"insert_after": "exam_physical_section",
			"options": "\nOne\nTwo\nThree\nFour"
		},
		{
			"fieldname": "exam_mouth_opening_mm",
			"label": "Mouth Opening (mm)",
			"fieldtype": "Float",
			"insert_after": "exam_mouth_opening_fingers"
		},
		{
			"fieldname": "exam_tongue_movement",
			"label": "Tongue Movement",
			"fieldtype": "Select",
			"insert_after": "exam_mouth_opening_mm",
			"options": "\nNormal\nPainful\nDeviation to Left\nDeviation to Right\nRestricted Protrusion"
		},
		{
			"fieldname": "exam_tongue_protrusion_mm",
			"label": "Tongue Protrusion (mm)",
			"fieldtype": "Float",
			"insert_after": "exam_tongue_movement"
		},
		{
			"fieldname": "exam_physical_col_break",
			"fieldtype": "Column Break",
			"insert_after": "exam_tongue_protrusion_mm"
		},
		{
			"fieldname": "exam_oral_hygiene",
			"label": "Oral Hygiene",
			"fieldtype": "Select",
			"insert_after": "exam_physical_col_break",
			"options": "\nGood\nModerate\nPoor"
		},
		{
			"fieldname": "exam_prosthesis",
			"label": "Prosthesis",
			"fieldtype": "Select",
			"insert_after": "exam_oral_hygiene",
			"options": "\nYes\nNo"
		},
		{
			"fieldname": "exam_teeth_issues",
			"label": "Teeth Issues",
			"fieldtype": "Small Text",
			"insert_after": "exam_prosthesis",
			"description": "Enter teeth numbers and issues"
		},
		
		# Physical Findings Table
		{
			"fieldname": "exam_findings_section",
			"label": "Physical Findings",
			"fieldtype": "Section Break",
			"insert_after": "exam_teeth_issues",
			"collapsible": 1
		},
		{
			"fieldname": "exam_physical_findings",
			"label": "Physical Findings",
			"fieldtype": "Table",
			"insert_after": "exam_findings_section",
			"options": "Clinical Exam Finding"
		},
		
		# Diagram Marking Section
		{
			"fieldname": "exam_diagram_section",
			"label": "Diagram Marking",
			"fieldtype": "Section Break",
			"insert_after": "exam_physical_findings",
			"collapsible": 1
		},
		{
			"fieldname": "exam_diagram_html",
			"label": "Interactive Diagram",
			"fieldtype": "HTML",
			"insert_after": "exam_diagram_section"
		},
		{
			"fieldname": "exam_lesion_markings_json",
			"label": "Lesion Markings Data",
			"fieldtype": "Code",
			"insert_after": "exam_diagram_html",
			"options": "JSON",
			"hidden": 1
		},
		{
			"fieldname": "exam_lesions",
			"label": "Marked Lesions",
			"fieldtype": "Table",
			"insert_after": "exam_lesion_markings_json",
			"options": "Clinical Exam Lesion"
		},
		
		# Clinical Images Section
		{
			"fieldname": "exam_images_section",
			"label": "Clinical Images",
			"fieldtype": "Section Break",
			"insert_after": "exam_lesions",
			"collapsible": 1
		},
		{
			"fieldname": "exam_images",
			"label": "Clinical Images",
			"fieldtype": "Table",
			"insert_after": "exam_images_section",
			"options": "Clinical Exam Image"
		},
		
		# Special Tests Section
		{
			"fieldname": "exam_special_tests_section",
			"label": "Special Tests",
			"fieldtype": "Section Break",
			"insert_after": "exam_images",
			"collapsible": 1
		},
		{
			"fieldname": "exam_special_tests",
			"label": "Special Tests",
			"fieldtype": "Table",
			"insert_after": "exam_special_tests_section",
			"options": "Clinical Exam Special Test"
		},
		
		# Provisional Diagnosis Section
		{
			"fieldname": "exam_provisional_section",
			"label": "Provisional Diagnosis & Risk Assessment",
			"fieldtype": "Section Break",
			"insert_after": "exam_special_tests",
			"collapsible": 1
		},
		{
			"fieldname": "exam_assessment_status",
			"label": "Assessment Status",
			"fieldtype": "Select",
			"insert_after": "exam_provisional_section",
			"options": "\nNormal\nRisk for PML/Cancer"
		},
		{
			"fieldname": "exam_risk_level",
			"label": "Risk Level",
			"fieldtype": "Select",
			"insert_after": "exam_assessment_status",
			"options": "\nLow Risk\nHigh Risk",
			"depends_on": "eval:doc.exam_assessment_status=='Risk for PML/Cancer'"
		},
		{
			"fieldname": "exam_provisional_col_break",
			"fieldtype": "Column Break",
			"insert_after": "exam_risk_level"
		},
		{
			"fieldname": "exam_provisional_diagnosis",
			"label": "Provisional Diagnosis",
			"fieldtype": "Select",
			"insert_after": "exam_provisional_col_break",
			"options": "\nNormal, routine screening after 1 year\nNormal with risk factors, close screening every six months\nPotentially Malignant lesions, need further management\nHigh risk, need to see nearest center for evaluation\nSuspicious for cancer, need immediate evaluation\nFrank malignancy, requires immediate treatment\nInsufficient data, repeat examination\nInflammation/infection to be ruled out"
		},
		{
			"fieldname": "exam_diagnosis_notes",
			"label": "Clinical Examination Notes",
			"fieldtype": "Small Text",
			"insert_after": "exam_provisional_diagnosis"
		},
		
		# Advice & Prescription Section
		{
			"fieldname": "exam_advice_section",
			"label": "Clinical Examination Advice",
			"fieldtype": "Section Break",
			"insert_after": "exam_diagnosis_notes",
			"collapsible": 1
		},
		{
			"fieldname": "exam_tobacco_cessation",
			"label": "Recommend Tobacco Cessation",
			"fieldtype": "Check",
			"insert_after": "exam_advice_section",
			"default": "0"
		},
		{
			"fieldname": "exam_alcohol_education",
			"label": "Educate About Alcohol Use",
			"fieldtype": "Check",
			"insert_after": "exam_tobacco_cessation",
			"default": "0"
		},
		{
			"fieldname": "exam_dental_care",
			"label": "Recommend Dental Care",
			"fieldtype": "Check",
			"insert_after": "exam_alcohol_education",
			"default": "0"
		},
		{
			"fieldname": "exam_advice_col_break",
			"fieldtype": "Column Break",
			"insert_after": "exam_dental_care"
		},
		{
			"fieldname": "exam_specialist_referral",
			"label": "Referred for Specialist Review",
			"fieldtype": "Check",
			"insert_after": "exam_advice_col_break",
			"default": "0"
		},
		{
			"fieldname": "exam_higher_center_referral",
			"label": "Referred to Higher Center",
			"fieldtype": "Check",
			"insert_after": "exam_specialist_referral",
			"default": "0"
		},
		{
			"fieldname": "exam_prescription_notes",
			"label": "Examination Prescription Notes",
			"fieldtype": "Text Editor",
			"insert_after": "exam_higher_center_referral"
		},
		
		# Follow Up Section
		{
			"fieldname": "exam_followup_section",
			"label": "Examination Follow Up",
			"fieldtype": "Section Break",
			"insert_after": "exam_prescription_notes",
			"collapsible": 1
		},
		{
			"fieldname": "exam_follow_up_required",
			"label": "Follow Up Required",
			"fieldtype": "Check",
			"insert_after": "exam_followup_section",
			"default": "0"
		},
		{
			"fieldname": "exam_follow_up_date",
			"label": "Follow Up Date",
			"fieldtype": "Date",
			"insert_after": "exam_follow_up_required",
			"depends_on": "eval:doc.exam_follow_up_required"
		},
		{
			"fieldname": "exam_follow_up_notes",
			"label": "Follow Up Notes",
			"fieldtype": "Small Text",
			"insert_after": "exam_follow_up_date"
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
	print("\n✓ Clinical Examination Section Added to Patient Encounter!")
	print("="*60 + "\n")

