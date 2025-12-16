import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def execute():
	"""Complete all missing fields for LAB TEST, STEP 7, and FOLLOW UP sections as per sheet"""
	print("\n" + "="*60)
	print("Completing LAB TEST, STEP 7, and FOLLOW UP Fields")
	print("="*60)
	
	doctype = "Patient Encounter"
	depends_on = "eval:doc.practitioner && doc.show_clinical_examination"
	
	# ============================================================
	# Additional LAB TEST fields from sheet
	# ============================================================
	lab_additional = [
		# Calcium/Phosphorus
		{
			"fieldname": "exam_lab_calcium",
			"label": "Calcium",
			"fieldtype": "Check",
			"insert_after": "exam_lab_chloride",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_lab_phosphorus",
			"label": "Phosphorus",
			"fieldtype": "Check",
			"insert_after": "exam_lab_calcium",
			"depends_on": depends_on
		},
		# Electrolytes section
		{
			"fieldname": "exam_lab_electrolytes_section",
			"label": "ELECTROLYTES",
			"fieldtype": "Section Break",
			"insert_after": "exam_lab_phosphorus",
			"collapsible": 0,
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_lab_magnesium",
			"label": "Sr. Magnesium",
			"fieldtype": "Check",
			"insert_after": "exam_lab_electrolytes_section",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_lab_zinc",
			"label": "Sr. Zinc",
			"fieldtype": "Check",
			"insert_after": "exam_lab_magnesium",
			"depends_on": depends_on
		},
		# Anaemia Profile
		{
			"fieldname": "exam_lab_anaemia_section",
			"label": "ANAEMIA PROFILE",
			"fieldtype": "Section Break",
			"insert_after": "exam_lab_ldl_hdl_ratio",
			"collapsible": 0,
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_lab_iron",
			"label": "Iron",
			"fieldtype": "Check",
			"insert_after": "exam_lab_anaemia_section",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_lab_tibc",
			"label": "TIBC (Total Iron Binding Capacity)",
			"fieldtype": "Check",
			"insert_after": "exam_lab_iron",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_lab_folic_acid",
			"label": "Sr. Folic Acid",
			"fieldtype": "Check",
			"insert_after": "exam_lab_vit_c",
			"depends_on": depends_on
		},
		# C-Reactive Protein
		{
			"fieldname": "exam_lab_crp_section",
			"label": "OTHER TESTS",
			"fieldtype": "Section Break",
			"insert_after": "exam_lab_folic_acid",
			"collapsible": 0,
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_lab_crp",
			"label": "C-Reactive Protein",
			"fieldtype": "Check",
			"insert_after": "exam_lab_crp_section",
			"depends_on": depends_on
		},
		# Smokers Lung Test
		{
			"fieldname": "exam_lab_lung_section",
			"label": "SMOKERS LUNG TEST",
			"fieldtype": "Section Break",
			"insert_after": "exam_lab_crp",
			"collapsible": 0,
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_lab_aat",
			"label": "Alpha-1 Antitrypsin (AAT)",
			"fieldtype": "Check",
			"insert_after": "exam_lab_lung_section",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_lab_urine_cotinine",
			"label": "Urine Cotinine",
			"fieldtype": "Check",
			"insert_after": "exam_lab_aat",
			"depends_on": depends_on
		},
		# Urine Routine
		{
			"fieldname": "exam_lab_urine_section",
			"label": "URINE ROUTINE",
			"fieldtype": "Section Break",
			"insert_after": "exam_lab_urine_cotinine",
			"collapsible": 0,
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_lab_urine_routine",
			"label": "Urine Routine",
			"fieldtype": "Check",
			"insert_after": "exam_lab_urine_section",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_lab_urine_glucose",
			"label": "Urine Glucose",
			"fieldtype": "Check",
			"insert_after": "exam_lab_urine_routine",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_lab_urine_protein",
			"label": "Urine Protein",
			"fieldtype": "Check",
			"insert_after": "exam_lab_urine_glucose",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_lab_urine_pus",
			"label": "Urine Pus Cells",
			"fieldtype": "Check",
			"insert_after": "exam_lab_urine_protein",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_lab_urine_rbc",
			"label": "Urine RBC",
			"fieldtype": "Check",
			"insert_after": "exam_lab_urine_pus",
			"depends_on": depends_on
		},
		# Cancer Profile
		{
			"fieldname": "exam_lab_cancer_section",
			"label": "CANCER PROFILE",
			"fieldtype": "Section Break",
			"insert_after": "exam_lab_urine_rbc",
			"collapsible": 0,
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_lab_psa",
			"label": "Sr PSA",
			"fieldtype": "Check",
			"insert_after": "exam_lab_cancer_section",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_lab_cea",
			"label": "Sr CEA",
			"fieldtype": "Check",
			"insert_after": "exam_lab_psa",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_lab_ca125",
			"label": "Sr. CA 125",
			"fieldtype": "Check",
			"insert_after": "exam_lab_cea",
			"depends_on": depends_on
		},
		# Package Selection
		{
			"fieldname": "exam_lab_package_section",
			"label": "Lab Package Selection",
			"fieldtype": "Section Break",
			"insert_after": "exam_lab_ca125",
			"collapsible": 0,
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_lab_package",
			"label": "Package",
			"fieldtype": "Select",
			"options": "\nMAX Full-Body Health Check (Rs. 2500)\nICanCare Smoker Panel 1 (Rs. 6000)\nICanCare Smoker Panel 2 (Rs. 5000)\nCustom Selection",
			"insert_after": "exam_lab_package_section",
			"depends_on": depends_on
		},
	]
	
	# ============================================================
	# STEP 7 additional fields from sheet
	# ============================================================
	step7_additional = [
		# Advice for procedure in-Centre
		{
			"fieldname": "exam_step7_procedure_section",
			"label": "Procedure to be done ORAL",
			"fieldtype": "Section Break",
			"insert_after": "exam_follow_up_date_step7",
			"collapsible": 0,
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_step7_biopsy",
			"label": "BIOPSY",
			"fieldtype": "Check",
			"insert_after": "exam_step7_procedure_section",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_step7_excision",
			"label": "Excision",
			"fieldtype": "Check",
			"insert_after": "exam_step7_biopsy",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_step7_pbm",
			"label": "PBM",
			"fieldtype": "Check",
			"insert_after": "exam_step7_excision",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_step7_pdt",
			"label": "PDT",
			"fieldtype": "Check",
			"insert_after": "exam_step7_pbm",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_step7_col2",
			"fieldtype": "Column Break",
			"insert_after": "exam_step7_pdt"
		},
		{
			"fieldname": "exam_step7_vaporisation",
			"label": "Vapourisation - LASER, Electrocautery",
			"fieldtype": "Check",
			"insert_after": "exam_step7_col2",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_step7_dental_prophylaxis",
			"label": "Dental Prophylaxis",
			"fieldtype": "Check",
			"insert_after": "exam_step7_vaporisation",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_step7_dental_rehab",
			"label": "Dental Rehabilitation",
			"fieldtype": "Check",
			"insert_after": "exam_step7_dental_prophylaxis",
			"depends_on": depends_on
		},
		# Procedure Done
		{
			"fieldname": "exam_step7_done_section",
			"label": "Procedure Done",
			"fieldtype": "Section Break",
			"insert_after": "exam_step7_dental_rehab",
			"collapsible": 0,
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_step7_done_in_centre",
			"label": "In Centre",
			"fieldtype": "Check",
			"insert_after": "exam_step7_done_section",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_step7_done_outside",
			"label": "Outside",
			"fieldtype": "Check",
			"insert_after": "exam_step7_done_in_centre",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_step7_done_cancer_centre",
			"label": "Cancer or Oral Specialized centre Referral centre",
			"fieldtype": "Check",
			"insert_after": "exam_step7_done_outside",
			"depends_on": depends_on
		},
	]
	
	# ============================================================
	# FOLLOW UP additional fields from sheet
	# ============================================================
	followup_additional = [
		# Post Surgical Follow up
		{
			"fieldname": "exam_fu_surgical_section",
			"label": "Follow up treatment post Surgical intervention/LASER",
			"fieldtype": "Section Break",
			"insert_after": "exam_fu_response_malignant",
			"collapsible": 0,
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_fu_excision_status",
			"label": "Excision Status",
			"fieldtype": "Select",
			"options": "\nHealing\nHealed",
			"insert_after": "exam_fu_surgical_section",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_fu_new_lesion",
			"label": "NEW LESION - to be recorded",
			"fieldtype": "Check",
			"insert_after": "exam_fu_excision_status",
			"depends_on": depends_on
		},
		# Advice Section
		{
			"fieldname": "exam_fu_advice_section",
			"label": "Advise",
			"fieldtype": "Section Break",
			"insert_after": "exam_fu_new_lesion",
			"collapsible": 0,
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_fu_tobacco_cessation",
			"label": "Recommend tobacco cessation",
			"fieldtype": "Check",
			"insert_after": "exam_fu_advice_section",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_fu_alcohol_education",
			"label": "Educate about alcohol use",
			"fieldtype": "Check",
			"insert_after": "exam_fu_tobacco_cessation",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_fu_dental_care",
			"label": "Recommend Dental Care",
			"fieldtype": "Check",
			"insert_after": "exam_fu_alcohol_education",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_fu_col_advice",
			"fieldtype": "Column Break",
			"insert_after": "exam_fu_dental_care"
		},
		{
			"fieldname": "exam_fu_specialist_review",
			"label": "Referred for Other Specialist Review",
			"fieldtype": "Check",
			"insert_after": "exam_fu_col_advice",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_fu_higher_centre",
			"label": "Referred for higher Centre for Oral Evaluation",
			"fieldtype": "Check",
			"insert_after": "exam_fu_specialist_review",
			"depends_on": depends_on
		},
		# Prescription Section
		{
			"fieldname": "exam_fu_prescription_section",
			"label": "Prescription",
			"fieldtype": "Section Break",
			"insert_after": "exam_fu_higher_centre",
			"collapsible": 0,
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_fu_supplements",
			"label": "Supplements (Vit B12, D3, E, Vit C)",
			"fieldtype": "Small Text",
			"insert_after": "exam_fu_prescription_section",
			"depends_on": depends_on
		},
		# Procedure Section for Follow Up
		{
			"fieldname": "exam_fu_procedure_section",
			"label": "ORAL Procedures",
			"fieldtype": "Section Break",
			"insert_after": "exam_fu_supplements",
			"collapsible": 0,
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_fu_biopsy",
			"label": "BIOPSY",
			"fieldtype": "Check",
			"insert_after": "exam_fu_procedure_section",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_fu_excision",
			"label": "Excision",
			"fieldtype": "Check",
			"insert_after": "exam_fu_biopsy",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_fu_pbm",
			"label": "PBM",
			"fieldtype": "Check",
			"insert_after": "exam_fu_excision",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_fu_pdt",
			"label": "PDT",
			"fieldtype": "Check",
			"insert_after": "exam_fu_pbm",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_fu_proc_col1",
			"fieldtype": "Column Break",
			"insert_after": "exam_fu_pdt"
		},
		{
			"fieldname": "exam_fu_vaporisation",
			"label": "Vapourisation - LASER, Electrocautery",
			"fieldtype": "Check",
			"insert_after": "exam_fu_proc_col1",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_fu_dental_prophylaxis",
			"label": "Dental Prophylaxis",
			"fieldtype": "Check",
			"insert_after": "exam_fu_vaporisation",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_fu_dental_rehab",
			"label": "Dental Rehabilitation",
			"fieldtype": "Check",
			"insert_after": "exam_fu_dental_prophylaxis",
			"depends_on": depends_on
		},
		# Follow Up Lab Test
		{
			"fieldname": "exam_fu_lab_section",
			"label": "Follow Up LAB TEST",
			"fieldtype": "Section Break",
			"insert_after": "exam_fu_dental_rehab",
			"collapsible": 0,
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_fu_lab_test",
			"label": "Follow Up Lab Test Required",
			"fieldtype": "Check",
			"insert_after": "exam_fu_lab_section",
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_fu_radiology_test",
			"label": "Radiology Tests",
			"fieldtype": "Check",
			"insert_after": "exam_fu_lab_test",
			"depends_on": depends_on
		},
		# Follow Up Date
		{
			"fieldname": "exam_fu_date_section",
			"label": "Follow Up Schedule",
			"fieldtype": "Section Break",
			"insert_after": "exam_fu_radiology_test",
			"collapsible": 0,
			"depends_on": depends_on
		},
		{
			"fieldname": "exam_fu_next_date",
			"label": "Follow up date",
			"fieldtype": "Date",
			"insert_after": "exam_fu_date_section",
			"depends_on": depends_on
		},
	]
	
	# Combine all fields
	all_fields = lab_additional + step7_additional + followup_additional
	
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
	print("\n✓ All missing fields added!")
	print("="*60 + "\n")

