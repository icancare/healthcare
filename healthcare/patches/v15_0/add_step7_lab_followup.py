import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def execute():
	"""Add Lab Test, STEP 7 Management Intervention, and Follow Up sections to Patient Encounter
	
	These sections come after STEP 6 and before Medical Coding as per the client sheet.
	"""
	print("\n" + "="*60)
	print("Adding Lab Test, STEP 7 Management, and Follow Up Sections")
	print("="*60)
	
	doctype = "Patient Encounter"
	
	# ============================================================
	# LAB TEST at Screening Camps or First Visit
	# ============================================================
	lab_test_fields = [
		{
			"fieldname": "exam_lab_test_section",
			"label": "LAB TEST at Screening Camps or First Visit",
			"fieldtype": "Section Break",
			"insert_after": "exam_risk_pml_cancer",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_test_date",
			"label": "Date",
			"fieldtype": "Date",
			"insert_after": "exam_lab_test_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_col1",
			"fieldtype": "Column Break",
			"insert_after": "exam_lab_test_date"
		},
		{
			"fieldname": "exam_lab_name",
			"label": "Lab Name",
			"fieldtype": "Data",
			"insert_after": "exam_lab_col1",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		# CBC Panel
		{
			"fieldname": "exam_lab_cbc_section",
			"label": "CBC",
			"fieldtype": "Section Break",
			"insert_after": "exam_lab_name",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_cbc",
			"label": "CBC",
			"fieldtype": "Check",
			"insert_after": "exam_lab_cbc_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_haemoglobin",
			"label": "Haemoglobin",
			"fieldtype": "Check",
			"insert_after": "exam_lab_cbc",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		# Diabetes Panel
		{
			"fieldname": "exam_lab_diabetes_section",
			"label": "DIABETES PANEL",
			"fieldtype": "Section Break",
			"insert_after": "exam_lab_haemoglobin",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_rbs",
			"label": "RBS",
			"fieldtype": "Check",
			"insert_after": "exam_lab_diabetes_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_glycosylated_hb",
			"label": "Glycosylated Haemoglobin",
			"fieldtype": "Check",
			"insert_after": "exam_lab_rbs",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		# Liver Function Test
		{
			"fieldname": "exam_lab_lft_section",
			"label": "LIVER FUNCTION TEST",
			"fieldtype": "Section Break",
			"insert_after": "exam_lab_glycosylated_hb",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_bilirubin_total",
			"label": "Bilirubin Total",
			"fieldtype": "Check",
			"insert_after": "exam_lab_lft_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_bilirubin_direct",
			"label": "Bilirubin Direct",
			"fieldtype": "Check",
			"insert_after": "exam_lab_bilirubin_total",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_bilirubin_indirect",
			"label": "Bilirubin Indirect",
			"fieldtype": "Check",
			"insert_after": "exam_lab_bilirubin_direct",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_sgot",
			"label": "SGOT",
			"fieldtype": "Check",
			"insert_after": "exam_lab_bilirubin_indirect",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_sgpt",
			"label": "SGPT",
			"fieldtype": "Check",
			"insert_after": "exam_lab_sgot",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_lft_col1",
			"fieldtype": "Column Break",
			"insert_after": "exam_lab_sgpt"
		},
		{
			"fieldname": "exam_lab_alkaline_phosphatase",
			"label": "Alkaline Phosphatase",
			"fieldtype": "Check",
			"insert_after": "exam_lab_lft_col1",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_albumin",
			"label": "Albumin",
			"fieldtype": "Check",
			"insert_after": "exam_lab_alkaline_phosphatase",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_globulin",
			"label": "Globulin",
			"fieldtype": "Check",
			"insert_after": "exam_lab_albumin",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_ag_ratio",
			"label": "A:G ratio",
			"fieldtype": "Check",
			"insert_after": "exam_lab_globulin",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_ggt",
			"label": "Gamma Glutamyl Transferase",
			"fieldtype": "Check",
			"insert_after": "exam_lab_ag_ratio",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		# Renal Function Test
		{
			"fieldname": "exam_lab_rft_section",
			"label": "RENAL FUNCTION TEST",
			"fieldtype": "Section Break",
			"insert_after": "exam_lab_ggt",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_urea",
			"label": "Urea",
			"fieldtype": "Check",
			"insert_after": "exam_lab_rft_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_creatinine",
			"label": "Creatinine",
			"fieldtype": "Check",
			"insert_after": "exam_lab_urea",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_uric_acid",
			"label": "Uric Acid",
			"fieldtype": "Check",
			"insert_after": "exam_lab_creatinine",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_rft_col1",
			"fieldtype": "Column Break",
			"insert_after": "exam_lab_uric_acid"
		},
		{
			"fieldname": "exam_lab_sodium",
			"label": "Sodium",
			"fieldtype": "Check",
			"insert_after": "exam_lab_rft_col1",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_potassium",
			"label": "Potassium",
			"fieldtype": "Check",
			"insert_after": "exam_lab_sodium",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_chloride",
			"label": "Chloride",
			"fieldtype": "Check",
			"insert_after": "exam_lab_potassium",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		# Lipid Profile
		{
			"fieldname": "exam_lab_lipid_section",
			"label": "LIPID PROFILE",
			"fieldtype": "Section Break",
			"insert_after": "exam_lab_chloride",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_total_cholesterol",
			"label": "Total Cholesterol",
			"fieldtype": "Check",
			"insert_after": "exam_lab_lipid_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_hdl",
			"label": "HDL",
			"fieldtype": "Check",
			"insert_after": "exam_lab_total_cholesterol",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_ldl",
			"label": "LDL",
			"fieldtype": "Check",
			"insert_after": "exam_lab_hdl",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_vldl",
			"label": "VLDL",
			"fieldtype": "Check",
			"insert_after": "exam_lab_ldl",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_lipid_col1",
			"fieldtype": "Column Break",
			"insert_after": "exam_lab_vldl"
		},
		{
			"fieldname": "exam_lab_triglycerides",
			"label": "Triglycerides",
			"fieldtype": "Check",
			"insert_after": "exam_lab_lipid_col1",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_total_hdl_ratio",
			"label": "Total/HDL Ratio",
			"fieldtype": "Check",
			"insert_after": "exam_lab_triglycerides",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_ldl_hdl_ratio",
			"label": "LDL/HDL Ratio",
			"fieldtype": "Check",
			"insert_after": "exam_lab_total_hdl_ratio",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		# Thyroid Panel
		{
			"fieldname": "exam_lab_thyroid_section",
			"label": "THYROID PANEL",
			"fieldtype": "Section Break",
			"insert_after": "exam_lab_ldl_hdl_ratio",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_t3",
			"label": "T3",
			"fieldtype": "Check",
			"insert_after": "exam_lab_thyroid_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_t4",
			"label": "T4",
			"fieldtype": "Check",
			"insert_after": "exam_lab_t3",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_tsh",
			"label": "TSH",
			"fieldtype": "Check",
			"insert_after": "exam_lab_t4",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		# Vitamins
		{
			"fieldname": "exam_lab_vitamins_section",
			"label": "VITAMINS",
			"fieldtype": "Section Break",
			"insert_after": "exam_lab_tsh",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_vit_b12",
			"label": "Vit B12",
			"fieldtype": "Check",
			"insert_after": "exam_lab_vitamins_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_vit_d3",
			"label": "D3",
			"fieldtype": "Check",
			"insert_after": "exam_lab_vit_b12",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_vit_e",
			"label": "E",
			"fieldtype": "Check",
			"insert_after": "exam_lab_vit_d3",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_vit_c",
			"label": "Vit C",
			"fieldtype": "Check",
			"insert_after": "exam_lab_vit_e",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
	]
	
	# ============================================================
	# STEP 7 - MANAGEMENT Intervention
	# ============================================================
	step7_fields = [
		{
			"fieldname": "exam_step7_section",
			"label": "STEP 7 - MANAGEMENT Intervention",
			"fieldtype": "Section Break",
			"insert_after": "exam_lab_package",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_opd_procedure",
			"label": "OPD procedure - Scarp cytology, Saliva biomarkers/special Tests",
			"fieldtype": "Small Text",
			"insert_after": "exam_step7_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_lab_tests_biochem",
			"label": "Lab Tests - Biochemistry and Hematology",
			"fieldtype": "Small Text",
			"insert_after": "exam_opd_procedure",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_radiology_tests",
			"label": "Radiology Tests",
			"fieldtype": "Small Text",
			"insert_after": "exam_lab_tests_biochem",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_step7_col1",
			"fieldtype": "Column Break",
			"insert_after": "exam_radiology_tests"
		},
		{
			"fieldname": "exam_prescription_1st",
			"label": "Prescription (1st Prescription as above)",
			"fieldtype": "Small Text",
			"insert_after": "exam_step7_col1",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_followup_reports_1st",
			"label": "Follow up with reports 1st",
			"fieldtype": "Small Text",
			"insert_after": "exam_prescription_1st",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		# Management Plan
		{
			"fieldname": "exam_mgmt_plan_section",
			"label": "Management Plan",
			"fieldtype": "Section Break",
			"insert_after": "exam_followup_reports_1st",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_mgmt_conservative",
			"label": "Conservative Medicines only",
			"fieldtype": "Check",
			"insert_after": "exam_mgmt_plan_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_mgmt_tobacco_cessation",
			"label": "Tobacco Cessation",
			"fieldtype": "Check",
			"insert_after": "exam_mgmt_conservative",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_mgmt_dental_care",
			"label": "Dental Care",
			"fieldtype": "Check",
			"insert_after": "exam_mgmt_tobacco_cessation",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_mgmt_local_oral",
			"label": "Local Oral Management",
			"fieldtype": "Check",
			"insert_after": "exam_mgmt_dental_care",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_mgmt_col1",
			"fieldtype": "Column Break",
			"insert_after": "exam_mgmt_local_oral"
		},
		{
			"fieldname": "exam_mgmt_biopsy",
			"label": "Biopsy",
			"fieldtype": "Check",
			"insert_after": "exam_mgmt_col1",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_mgmt_excision",
			"label": "Excision",
			"fieldtype": "Check",
			"insert_after": "exam_mgmt_biopsy",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_mgmt_referral_higher",
			"label": "Referral to Higher Centre",
			"fieldtype": "Check",
			"insert_after": "exam_mgmt_excision",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_mgmt_referral_specialist",
			"label": "Referral to Specialist",
			"fieldtype": "Check",
			"insert_after": "exam_mgmt_referral_higher",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_follow_up_date_step7",
			"label": "Follow up date",
			"fieldtype": "Date",
			"insert_after": "exam_mgmt_referral_specialist",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
	]
	
	# ============================================================
	# FOLLOW UP - 1M, 2M, 3 monthly
	# ============================================================
	followup_fields = [
		{
			"fieldname": "exam_followup_monthly_section",
			"label": "FOLLOW UP - 1M, 2M, 3 Monthly",
			"fieldtype": "Section Break",
			"insert_after": "exam_step7_done_cancer_centre",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_patient_interval",
			"label": "Follow up of patient at regular interval",
			"fieldtype": "Data",
			"insert_after": "exam_followup_monthly_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_mouth_opening",
			"label": "MOUTH OPENING - Record",
			"fieldtype": "Data",
			"insert_after": "exam_fu_patient_interval",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		# Tobacco History
		{
			"fieldname": "exam_fu_tobacco_section",
			"label": "TOBACCO HISTORY SMOKING or CHEWING",
			"fieldtype": "Section Break",
			"insert_after": "exam_fu_mouth_opening",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_tobacco_continues",
			"label": "Continues",
			"fieldtype": "Check",
			"insert_after": "exam_fu_tobacco_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_tobacco_stopped",
			"label": "STOPPED",
			"fieldtype": "Check",
			"insert_after": "exam_fu_tobacco_continues",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		# Alcohol History
		{
			"fieldname": "exam_fu_alcohol_section",
			"label": "ALCOHOL HISTORY",
			"fieldtype": "Section Break",
			"insert_after": "exam_fu_tobacco_stopped",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_alcohol_continues",
			"label": "Continues",
			"fieldtype": "Check",
			"insert_after": "exam_fu_alcohol_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_alcohol_stopped",
			"label": "STOPPED",
			"fieldtype": "Check",
			"insert_after": "exam_fu_alcohol_continues",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		# General Parameters
		{
			"fieldname": "exam_fu_general_section",
			"label": "General Parameters (BP, RBS, CO, PEEK, Weight)",
			"fieldtype": "Section Break",
			"insert_after": "exam_fu_alcohol_stopped",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_stable",
			"label": "Stable",
			"fieldtype": "Check",
			"insert_after": "exam_fu_general_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_better",
			"label": "Better",
			"fieldtype": "Check",
			"insert_after": "exam_fu_stable",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_needs_specialist",
			"label": "Needs Specialist Care",
			"fieldtype": "Check",
			"insert_after": "exam_fu_better",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		# Review of Reports
		{
			"fieldname": "exam_fu_reports_section",
			"label": "Review of Reports - LAB Reports - Note on the APP",
			"fieldtype": "Section Break",
			"insert_after": "exam_fu_needs_specialist",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_reports_stable",
			"label": "Stable",
			"fieldtype": "Check",
			"insert_after": "exam_fu_reports_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_reports_better",
			"label": "Better",
			"fieldtype": "Check",
			"insert_after": "exam_fu_reports_stable",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		# Parameters not in normal limit
		{
			"fieldname": "exam_fu_abnormal_section",
			"label": "Parameters not in normal limit highlighted for management",
			"fieldtype": "Section Break",
			"insert_after": "exam_fu_reports_better",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_abnormal_specialist",
			"label": "Needs Specialist Care",
			"fieldtype": "Check",
			"insert_after": "exam_fu_abnormal_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		# Response to treatment
		{
			"fieldname": "exam_fu_response_section",
			"label": "Response to treatment conservative/PBM/PDT",
			"fieldtype": "Section Break",
			"insert_after": "exam_fu_abnormal_specialist",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_response_stable",
			"label": "STABLE",
			"fieldtype": "Check",
			"insert_after": "exam_fu_response_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_response_progressive",
			"label": "PROGRESSIVE",
			"fieldtype": "Check",
			"insert_after": "exam_fu_response_stable",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_response_regression",
			"label": "REGRESSION",
			"fieldtype": "Check",
			"insert_after": "exam_fu_response_progressive",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_response_col1",
			"fieldtype": "Column Break",
			"insert_after": "exam_fu_response_regression"
		},
		{
			"fieldname": "exam_fu_response_partial",
			"label": "Partial response",
			"fieldtype": "Check",
			"insert_after": "exam_fu_response_col1",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_response_complete",
			"label": "Complete response",
			"fieldtype": "Check",
			"insert_after": "exam_fu_response_partial",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_response_malignant",
			"label": "Malignant transformation",
			"fieldtype": "Check",
			"insert_after": "exam_fu_response_complete",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		# Pictures for record
		{
			"fieldname": "exam_fu_pictures_section",
			"label": "PICTURES TO BE TAKEN FOR RECORD AND COMPARISON",
			"fieldtype": "Section Break",
			"insert_after": "exam_fu_response_malignant",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_pic_face",
			"label": "Face and Neck",
			"fieldtype": "Attach Image",
			"insert_after": "exam_fu_pictures_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_pic_col1",
			"fieldtype": "Column Break",
			"insert_after": "exam_fu_pic_face"
		},
		{
			"fieldname": "exam_fu_pic_oral",
			"label": "Oral Cavity",
			"fieldtype": "Attach Image",
			"insert_after": "exam_fu_pic_col1",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_pic_col2",
			"fieldtype": "Column Break",
			"insert_after": "exam_fu_pic_oral"
		},
		{
			"fieldname": "exam_fu_pic_lesion",
			"label": "Lesion",
			"fieldtype": "Attach Image",
			"insert_after": "exam_fu_pic_col2",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		# Final Notes
		{
			"fieldname": "exam_fu_notes_section",
			"label": "Follow Up Notes",
			"fieldtype": "Section Break",
			"insert_after": "exam_fu_pic_lesion",
			"collapsible": 0,
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
		{
			"fieldname": "exam_fu_notes",
			"label": "Notes",
			"fieldtype": "Text Editor",
			"insert_after": "exam_fu_notes_section",
			"depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
		},
	]
	
	# Combine all fields
	all_fields = lab_test_fields + step7_fields + followup_fields
	
	for field in all_fields:
		try:
			create_custom_field(doctype, field)
			print(f"  ✓ Added: {field['fieldname']}")
		except Exception as e:
			if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
				print(f"  ⏭ Already exists: {field['fieldname']}")
			else:
				print(f"  ✗ Error: {field['fieldname']} - {e}")
	
	frappe.db.commit()
	print("\n✓ Lab Test, STEP 7 Management, and Follow Up sections added!")
	print("="*60 + "\n")

