import frappe


def execute():
	"""Setup Clinical Examination System - Body Parts and Oral Screening Template"""
	print("\n" + "="*60)
	print("Setting up Clinical Examination System")
	print("="*60)
	
	# Step 1: Create Body Parts
	create_body_parts()
	
	# Step 2: Create Oral Screening Template
	create_oral_screening_template()
	
	frappe.db.commit()
	print("✓ Clinical Examination System Setup Complete!")
	print("="*60 + "\n")


def create_body_parts():
	"""Create body parts for oral examination"""
	print("\n  Creating Body Parts...")
	
	body_parts = [
		{"body_part_name": "Face - Forehead Left", "body_part_group": "Face", "svg_region_id": "forehead-left"},
		{"body_part_name": "Face - Forehead Right", "body_part_group": "Face", "svg_region_id": "forehead-right"},
		{"body_part_name": "Face - Cheek Left", "body_part_group": "Face", "svg_region_id": "cheek-left"},
		{"body_part_name": "Face - Cheek Right", "body_part_group": "Face", "svg_region_id": "cheek-right"},
		{"body_part_name": "Face - Chin", "body_part_group": "Face", "svg_region_id": "chin"},
		{"body_part_name": "Face - Eye Left", "body_part_group": "Face", "svg_region_id": "eye-left"},
		{"body_part_name": "Face - Eye Right", "body_part_group": "Face", "svg_region_id": "eye-right"},
		{"body_part_name": "Face - Nose", "body_part_group": "Face", "svg_region_id": "nose"},
		{"body_part_name": "Face - Ear Left", "body_part_group": "Face", "svg_region_id": "ear-left"},
		{"body_part_name": "Face - Ear Right", "body_part_group": "Face", "svg_region_id": "ear-right"},
		{"body_part_name": "Face - Parotid Left", "body_part_group": "Face", "svg_region_id": "parotid-left"},
		{"body_part_name": "Face - Parotid Right", "body_part_group": "Face", "svg_region_id": "parotid-right"},
		{"body_part_name": "Neck - Left", "body_part_group": "Neck", "svg_region_id": "neck-left"},
		{"body_part_name": "Neck - Right", "body_part_group": "Neck", "svg_region_id": "neck-right"},
		{"body_part_name": "Neck - Central", "body_part_group": "Neck", "svg_region_id": "neck-central"},
		{"body_part_name": "Neck - Submandibular Left", "body_part_group": "Neck", "svg_region_id": "submandibular-left"},
		{"body_part_name": "Neck - Submandibular Right", "body_part_group": "Neck", "svg_region_id": "submandibular-right"},
		{"body_part_name": "Neck - Thyroid Left", "body_part_group": "Neck", "svg_region_id": "thyroid-left"},
		{"body_part_name": "Neck - Thyroid Right", "body_part_group": "Neck", "svg_region_id": "thyroid-right"},
		{"body_part_name": "Neck - Thyroid Central", "body_part_group": "Neck", "svg_region_id": "thyroid-central"},
		{"body_part_name": "Oral Cavity - Lower Lip Left", "body_part_group": "Oral Cavity", "svg_region_id": "lower-lip-left"},
		{"body_part_name": "Oral Cavity - Lower Lip Right", "body_part_group": "Oral Cavity", "svg_region_id": "lower-lip-right"},
		{"body_part_name": "Oral Cavity - Upper Lip Left", "body_part_group": "Oral Cavity", "svg_region_id": "upper-lip-left"},
		{"body_part_name": "Oral Cavity - Upper Lip Right", "body_part_group": "Oral Cavity", "svg_region_id": "upper-lip-right"},
		{"body_part_name": "Oral Cavity - Anterior Arch Left", "body_part_group": "Oral Cavity", "svg_region_id": "anterior-arch-left"},
		{"body_part_name": "Oral Cavity - Anterior Arch Right", "body_part_group": "Oral Cavity", "svg_region_id": "anterior-arch-right"},
		{"body_part_name": "Oral Cavity - Angle of Mouth Left", "body_part_group": "Oral Cavity", "svg_region_id": "angle-mouth-left"},
		{"body_part_name": "Oral Cavity - Angle of Mouth Right", "body_part_group": "Oral Cavity", "svg_region_id": "angle-mouth-right"},
		{"body_part_name": "Oral Cavity - Buccal Mucosa Left", "body_part_group": "Oral Cavity", "svg_region_id": "buccal-left"},
		{"body_part_name": "Oral Cavity - Buccal Mucosa Right", "body_part_group": "Oral Cavity", "svg_region_id": "buccal-right"},
		{"body_part_name": "Oral Cavity - Upper Alveolus Left", "body_part_group": "Oral Cavity", "svg_region_id": "upper-alveolus-left"},
		{"body_part_name": "Oral Cavity - Upper Alveolus Right", "body_part_group": "Oral Cavity", "svg_region_id": "upper-alveolus-right"},
		{"body_part_name": "Oral Cavity - Lower Alveolus Left", "body_part_group": "Oral Cavity", "svg_region_id": "lower-alveolus-left"},
		{"body_part_name": "Oral Cavity - Lower Alveolus Right", "body_part_group": "Oral Cavity", "svg_region_id": "lower-alveolus-right"},
		{"body_part_name": "Oral Cavity - Hard Palate Left", "body_part_group": "Oral Cavity", "svg_region_id": "hard-palate-left"},
		{"body_part_name": "Oral Cavity - Hard Palate Right", "body_part_group": "Oral Cavity", "svg_region_id": "hard-palate-right"},
		{"body_part_name": "Oral Cavity - Hard Palate Midline", "body_part_group": "Oral Cavity", "svg_region_id": "hard-palate-midline"},
		{"body_part_name": "Oral Cavity - Soft Palate Left", "body_part_group": "Oral Cavity", "svg_region_id": "soft-palate-left"},
		{"body_part_name": "Oral Cavity - Soft Palate Right", "body_part_group": "Oral Cavity", "svg_region_id": "soft-palate-right"},
		{"body_part_name": "Oral Cavity - Soft Palate Midline", "body_part_group": "Oral Cavity", "svg_region_id": "soft-palate-midline"},
		{"body_part_name": "Oral Cavity - Floor of Mouth", "body_part_group": "Oral Cavity", "svg_region_id": "floor-mouth"},
		{"body_part_name": "Oral Cavity - RMT Left", "body_part_group": "Oral Cavity", "svg_region_id": "rmt-left"},
		{"body_part_name": "Oral Cavity - RMT Right", "body_part_group": "Oral Cavity", "svg_region_id": "rmt-right"},
		{"body_part_name": "Tongue - Dorsum", "body_part_group": "Tongue", "svg_region_id": "tongue-dorsum"},
		{"body_part_name": "Tongue - Ventral Left", "body_part_group": "Tongue", "svg_region_id": "tongue-ventral-left"},
		{"body_part_name": "Tongue - Ventral Right", "body_part_group": "Tongue", "svg_region_id": "tongue-ventral-right"},
		{"body_part_name": "Tongue - Ventral Midline", "body_part_group": "Tongue", "svg_region_id": "tongue-ventral-midline"},
		{"body_part_name": "Tongue - Lateral Left", "body_part_group": "Tongue", "svg_region_id": "tongue-lateral-left"},
		{"body_part_name": "Tongue - Lateral Right", "body_part_group": "Tongue", "svg_region_id": "tongue-lateral-right"},
		{"body_part_name": "Tongue - Base Left", "body_part_group": "Tongue", "svg_region_id": "tongue-base-left"},
		{"body_part_name": "Tongue - Base Right", "body_part_group": "Tongue", "svg_region_id": "tongue-base-right"},
		{"body_part_name": "Tongue - Base Midline", "body_part_group": "Tongue", "svg_region_id": "tongue-base-midline"},
		{"body_part_name": "Throat - Tonsil Left", "body_part_group": "Throat", "svg_region_id": "tonsil-left"},
		{"body_part_name": "Throat - Tonsil Right", "body_part_group": "Throat", "svg_region_id": "tonsil-right"},
		{"body_part_name": "Throat - Oropharynx Left", "body_part_group": "Throat", "svg_region_id": "oropharynx-left"},
		{"body_part_name": "Throat - Oropharynx Right", "body_part_group": "Throat", "svg_region_id": "oropharynx-right"},
		{"body_part_name": "Throat - Oropharynx Midline", "body_part_group": "Throat", "svg_region_id": "oropharynx-midline"},
		{"body_part_name": "Teeth - Upper Right", "body_part_group": "Teeth", "svg_region_id": "teeth-upper-right"},
		{"body_part_name": "Teeth - Upper Left", "body_part_group": "Teeth", "svg_region_id": "teeth-upper-left"},
		{"body_part_name": "Teeth - Lower Right", "body_part_group": "Teeth", "svg_region_id": "teeth-lower-right"},
		{"body_part_name": "Teeth - Lower Left", "body_part_group": "Teeth", "svg_region_id": "teeth-lower-left"},
	]
	
	created_count = 0
	for bp in body_parts:
		if not frappe.db.exists("Clinical Exam Body Part", bp["body_part_name"]):
			doc = frappe.new_doc("Clinical Exam Body Part")
			doc.body_part_name = bp["body_part_name"]
			doc.body_part_group = bp["body_part_group"]
			doc.svg_region_id = bp["svg_region_id"]
			doc.flags.ignore_permissions = True
			doc.insert()
			created_count += 1
	
	print(f"    ✓ Created {created_count} body parts")


def create_oral_screening_template():
	"""Create ICanCaRe Oral Screening Form Template"""
	print("\n  Creating Oral Screening Template...")
	
	template_name = "ICanCaRe Oral Screening Form"
	
	if frappe.db.exists("Clinical Examination Template", template_name):
		# Ensure practitioner is assigned
		assign_practitioners_to_template(template_name)
		print(f"    ⏭ Template '{template_name}' already exists, checked practitioners...")
		return
	
	template = frappe.new_doc("Clinical Examination Template")
	template.template_name = template_name
	template.examination_type = "Oral Screening"
	template.description = """Comprehensive oral screening form for tobacco users. 
Includes:
- Patient Complaints (Face, Neck, Oral Cavity, Teeth, Throat)
- Physical Examination with detailed findings
- Interactive Diagram Marking for lesion documentation
- Clinical Image Upload
- Special Tests (Toluidine Blue, Autofluorescence, etc.)
- Provisional Diagnosis and Risk Assessment
- Treatment Prescription and Follow-up Planning"""
	template.disabled = 0
	
	# Enable all sections
	template.enable_complaints = 1
	template.enable_physical_exam = 1
	template.enable_diagram_marking = 1
	template.diagram_type = "Oral Cavity"
	template.enable_image_upload = 1
	template.image_categories = """Face and Neck
Open Mouth with Finger/Scale/TRISCaRe
Central Arch with Both Lips
Right Cheek with Alveolus
Left Cheek with Alveolus
Tongue Protruded
Tongue Pulled Up with Floor of Mouth
Hard and Soft Palate
Abnormal Area Focused
Special Tests Documentation"""
	
	template.enable_special_tests = 1
	template.special_tests = """Toluidine Blue Test
Blue Light Test
Autofluorescence Test
Spectroscopy Test"""
	
	template.enable_provisional_diagnosis = 1
	template.diagnosis_options = """Normal, routine screening after 1 year, continue self-oral examination
Normal with risk factors, close screening every six months
Potentially Malignant lesions, precancerous lesions, need further management
High risk, need to see the nearest center for further evaluation
Suspicious for cancer, need to see the nearest center for further evaluation
Frank malignancy, requires immediate treatment visit specialized cancer center
Insufficient data for any comments, repeat examination
Inflammation or infection or nutritional factors to be ruled out or treated and then repeat examination"""
	
	template.enable_prescription = 1
	template.default_prescriptions = """Mouth opening exercise - TRISCaRe Regular use
Tab Folic Acid (5 mg) 1 tab thrice/once daily for 30 days
Tab Vit C + Zinc tab Cbinan once daily for 30 days
Multivitamins, Multiminerals - Tab Vitabliz 1 tab once daily
Oral Probiotics – Sporalac DG chewable tablets 1 tab twice daily for 3 months
Oral Gargles – regular use - Turmwash/BiQOL
Antioxidants - Tab Clik/Lycoedge 1 cap once a day
Antifungal oral application - Clotrace lozenges 1 tab thrice daily
Antifungal tablets - Tab Forcan 100/150 mg 1 tab once a day for 14 days
Tab Curcunan/Turmnova tab 1 tab twice daily for 3 months
Local Anti Inflammatory Analgesic - Turminace Gel/ Metrogyl DG LA Gel
Artificial Saliva - Spray/Gargles - Oraxero Spray
Toothpaste - Treatment management of oral lesions
BIOPSY
Excision
PBM (Photobiomodulation)
PDT (Photodynamic Therapy)
Vapourisation - LASER, Electrocautery
Oral Prophylaxis
Dental Rehabilitation"""
	
	template.flags.ignore_permissions = True
	template.insert()
	
	# Assign practitioners
	assign_practitioners_to_template(template_name)
	
	print(f"    ✓ Created '{template_name}'")


def assign_practitioners_to_template(template_name):
	"""Assign Photo Medicine practitioners to the Oral Screening template"""
	# Get all Photo Medicine practitioners
	practitioners = frappe.db.get_all(
		"Healthcare Practitioner",
		filters={"department": "Photo Medicine"},
		fields=["name"]
	)
	
	if not practitioners:
		print("    ⚠ No Photo Medicine practitioners found")
		return
	
	template = frappe.get_doc("Clinical Examination Template", template_name)
	existing_pracs = [p.practitioner for p in template.practitioners] if template.practitioners else []
	
	added = 0
	for i, prac in enumerate(practitioners):
		if prac.name not in existing_pracs:
			template.append("practitioners", {
				"practitioner": prac.name,
				"is_default": 1 if i == 0 else 0  # First one is default
			})
			added += 1
	
	if added > 0:
		template.save(ignore_permissions=True)
		frappe.db.commit()
		print(f"    ✓ Assigned {added} practitioners to template")

