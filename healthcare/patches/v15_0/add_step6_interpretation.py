import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def execute():
	"""Add STEP 6 - Interpretation/Advice (Provisional Diagnosis) to Patient Encounter"""
	print("\n" + "="*60)
	print("Adding STEP 6 - Interpretation/Advice to Patient Encounter")
	print("="*60)
	
	doctype = "Patient Encounter"
	base_condition = 'eval:doc.practitioner && doc.show_clinical_examination'
	
	fields = [
		# ============================================
		# STEP 6 - INTERPRETATION/ADVICE
		# ============================================
		{
			"fieldname": "exam_step6_section",
			"label": "STEP 6 - Interpretation/Advice (Provisional Diagnosis)",
			"fieldtype": "Section Break",
			"insert_after": "exam_special_tests_summary",
			"collapsible": 0,
			"depends_on": base_condition
		},
		
		# Interpretation Options (Checkboxes)
		{
			"fieldname": "exam_interp_normal",
			"label": "Normal, routine screening after 1 year, continue self-oral examination",
			"fieldtype": "Check",
			"insert_after": "exam_step6_section",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_interp_normal_risk",
			"label": "Normal with risk factors, close screening every six months",
			"fieldtype": "Check",
			"insert_after": "exam_interp_normal",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_interp_potentially_malignant",
			"label": "Potentially Malignant lesions, precancerous lesions, need further management",
			"fieldtype": "Check",
			"insert_after": "exam_interp_normal_risk",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_interp_high_risk",
			"label": "High risk, need to see the nearest center for further evaluation",
			"fieldtype": "Check",
			"insert_after": "exam_interp_potentially_malignant",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_interp_suspicious",
			"label": "Suspicious for cancer, need to see the nearest center for further evaluation",
			"fieldtype": "Check",
			"insert_after": "exam_interp_high_risk",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_interp_frank_malignancy",
			"label": "Frank malignancy, requires immediate treatment visit specialized cancer center",
			"fieldtype": "Check",
			"insert_after": "exam_interp_suspicious",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_interp_insufficient",
			"label": "Insufficient data for any comments, repeat examination",
			"fieldtype": "Check",
			"insert_after": "exam_interp_frank_malignancy",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_interp_inflammation",
			"label": "Inflammation or infection or nutritional factors to be ruled out or treated and then repeat examination",
			"fieldtype": "Check",
			"insert_after": "exam_interp_insufficient",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_interp_tobacco_consult",
			"label": "High Risk factors needs consultation for Tobacco de-addiction",
			"fieldtype": "Check",
			"insert_after": "exam_interp_inflammation",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_interp_alcohol_advice",
			"label": "Recommend advice regarding Alcohol Use",
			"fieldtype": "Check",
			"insert_after": "exam_interp_tobacco_consult",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_interp_dental_care",
			"label": "Recommend Dental Care",
			"fieldtype": "Check",
			"insert_after": "exam_interp_alcohol_advice",
			"depends_on": base_condition
		},
		
		# Prescription/Advice Section
		{
			"fieldname": "exam_prescription_section",
			"label": "Prescription/ADVICE at Screening Camps or First Visit",
			"fieldtype": "Section Break",
			"insert_after": "exam_interp_dental_care",
			"collapsible": 0,
			"depends_on": base_condition
		},
		
		# Assessment
		{
			"fieldname": "exam_assessment",
			"label": "Assessment",
			"fieldtype": "Select",
			"insert_after": "exam_prescription_section",
			"options": "\nNormal\nAbnormal",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_risk_pml_cancer",
			"label": "Risk for PML/Cancer",
			"fieldtype": "Select",
			"insert_after": "exam_assessment",
			"options": "\nLow Risk\nHigh Risk",
			"depends_on": base_condition
		},
		
		# Advice Checkboxes
		{
			"fieldname": "exam_advice_section",
			"label": "Advice",
			"fieldtype": "Section Break",
			"insert_after": "exam_risk_pml_cancer",
			"collapsible": 0,
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_advice_tobacco_cessation",
			"label": "Recommend tobacco cessation",
			"fieldtype": "Check",
			"insert_after": "exam_advice_section",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_advice_alcohol",
			"label": "Educate about alcohol use",
			"fieldtype": "Check",
			"insert_after": "exam_advice_tobacco_cessation",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_advice_dental",
			"label": "Recommend Dental Care",
			"fieldtype": "Check",
			"insert_after": "exam_advice_alcohol",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_advice_specialist",
			"label": "Referred for Other Specialist Review",
			"fieldtype": "Check",
			"insert_after": "exam_advice_dental",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_advice_higher_centre",
			"label": "Referred for higher Centre for Oral Evaluation",
			"fieldtype": "Check",
			"insert_after": "exam_advice_specialist",
			"depends_on": base_condition
		},
		
		# Prescription - Oral Medications
		{
			"fieldname": "exam_oral_meds_section",
			"label": "PRESCRIPTION - ADVISE AND TREATMENT - ORAL MEDICATIONS",
			"fieldtype": "Section Break",
			"insert_after": "exam_advice_higher_centre",
			"collapsible": 0,
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_med_mouth_exercise",
			"label": "Mouth opening exercise - TRISCaRe Regular use",
			"fieldtype": "Check",
			"insert_after": "exam_oral_meds_section",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_med_folic_acid",
			"label": "Tab Folic Acid (5 mg) 1 tab thrice/once daily for 30 days",
			"fieldtype": "Check",
			"insert_after": "exam_med_mouth_exercise",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_med_vit_c_zinc",
			"label": "Tab Vit C + Zinc tab Cbinan once daily for 30 days",
			"fieldtype": "Check",
			"insert_after": "exam_med_folic_acid",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_med_multivitamins",
			"label": "Multivitamins, Multiminerals - Tab Vitabliz 1 tab once daily",
			"fieldtype": "Check",
			"insert_after": "exam_med_vit_c_zinc",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_med_probiotics",
			"label": "Oral Probiotics - Sporalac DG chewable tablets 1 tab twice daily for 3 months",
			"fieldtype": "Check",
			"insert_after": "exam_med_multivitamins",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_med_gargles",
			"label": "Oral Gargles - regular use - Turmwash/BiQOL",
			"fieldtype": "Check",
			"insert_after": "exam_med_probiotics",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_med_antioxidants",
			"label": "Antioxidants - Tab Clik/Lycoedge 1 cap once a day",
			"fieldtype": "Check",
			"insert_after": "exam_med_gargles",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_med_antifungal_oral",
			"label": "Antifungal oral application - Clotrace lozenges 1 tab thrice daily",
			"fieldtype": "Check",
			"insert_after": "exam_med_antioxidants",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_med_antifungal_tab",
			"label": "Antifungal tablets - tab Forcan 100/150 mg 1 tab once a day for 14 days",
			"fieldtype": "Check",
			"insert_after": "exam_med_antifungal_oral",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_med_curcunan",
			"label": "Tab Curcunan/Turmnova tab 1 tab twice daily for 3 months",
			"fieldtype": "Check",
			"insert_after": "exam_med_antifungal_tab",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_med_analgesic",
			"label": "Local Anti Inflammatory Analgesic - Turminace Gel/ Metrogyl DG LA Gel",
			"fieldtype": "Check",
			"insert_after": "exam_med_curcunan",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_med_saliva",
			"label": "Artificial Saliva - Spray/Gargles - Oraxero Spray",
			"fieldtype": "Check",
			"insert_after": "exam_med_analgesic",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_med_toothpaste",
			"label": "Toothpaste - Treatment management of oral lesions",
			"fieldtype": "Check",
			"insert_after": "exam_med_saliva",
			"depends_on": base_condition
		},
		
		# Procedure to be done ORAL
		{
			"fieldname": "exam_procedure_section",
			"label": "Procedure to be done ORAL",
			"fieldtype": "Section Break",
			"insert_after": "exam_med_toothpaste",
			"collapsible": 0,
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_proc_biopsy",
			"label": "BIOPSY",
			"fieldtype": "Check",
			"insert_after": "exam_procedure_section",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_proc_excision",
			"label": "Excision",
			"fieldtype": "Check",
			"insert_after": "exam_proc_biopsy",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_proc_pbm",
			"label": "PBM",
			"fieldtype": "Check",
			"insert_after": "exam_proc_excision",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_proc_pdt",
			"label": "PDT",
			"fieldtype": "Check",
			"insert_after": "exam_proc_pbm",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_proc_vapourisation",
			"label": "Vapourisation - LASER, Electrocautery",
			"fieldtype": "Check",
			"insert_after": "exam_proc_pdt",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_proc_oral_prophylaxis",
			"label": "Oral Prophylaxis",
			"fieldtype": "Check",
			"insert_after": "exam_proc_vapourisation",
			"depends_on": base_condition
		},
		{
			"fieldname": "exam_proc_dental_rehab",
			"label": "Dental Rehabilitation",
			"fieldtype": "Check",
			"insert_after": "exam_proc_oral_prophylaxis",
			"depends_on": base_condition
		},
		
		# Additional Notes
		{
			"fieldname": "exam_step6_notes",
			"label": "Additional Notes/Comments",
			"fieldtype": "Text",
			"insert_after": "exam_proc_dental_rehab",
			"depends_on": base_condition
		},
	]
	
	# Create all custom fields
	for field in fields:
		try:
			create_custom_field(doctype, field)
			print(f"  ✓ {field['fieldname']}")
		except Exception as e:
			if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
				print(f"  ⏭ {field['fieldname']} (exists)")
			else:
				print(f"  ✗ {field['fieldname']}: {e}")
	
	frappe.db.commit()
	print("\n✓ STEP 6 - Interpretation/Advice Added!")
	print("="*60 + "\n")

