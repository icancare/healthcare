import frappe


def execute():
	"""Setup ICanCaRe Oral Screening Form Template v2 with correct Step 1 configuration"""
	print("\n" + "="*60)
	print("Setting up Oral Screening Template v2")
	print("="*60)
	
	create_oral_screening_template()
	
	frappe.db.commit()
	print("✓ Oral Screening Template v2 Setup Complete!")
	print("="*60 + "\n")


def create_oral_screening_template():
	"""Create ICanCaRe Oral Screening Form Template with complete Step 1 configuration"""
	print("\n  Creating Oral Screening Template v2...")
	
	template_name = "ICanCaRe Oral Screening Form"
	
	if frappe.db.exists("Clinical Examination Template", template_name):
		# Update existing template
		template = frappe.get_doc("Clinical Examination Template", template_name)
		print(f"    ⏭ Template '{template_name}' exists, updating...")
	else:
		template = frappe.new_doc("Clinical Examination Template")
		template.template_name = template_name
	
	template.examination_type = "Oral Screening"
	template.description = """ICanCaRe TOBACCO USERS ORAL Screening Form
	
Complete oral screening form for tobacco users with structured Step-by-Step examination:
- Step 1: Patient Complaints (Body part wise symptoms with checkboxes)
- Step 2: Physical Examination 
- Step 3: Diagram Marking for lesion documentation
- Step 4: Clinical Images
- Step 5: Special Tests (Photo Diagnosis)
- Step 6: Interpretation/Assessment
- Step 7: Management, Prescription & Follow-up"""
	
	template.disabled = 0
	
	# Step 1: Patient Complaints Configuration
	template.enable_complaints = 1
	template.complaint_body_parts = """Face
Neck  
Oral Cavity (mouth and tongue)
Teeth (dental)
Others"""
	
	# Step 2: Physical Examination
	template.enable_physical_exam = 1
	template.exam_body_parts = """Face
Neck
Lips
Buccal Mucosa
Alveolus
Hard Palate
Soft Palate
Floor of Mouth
Retromolar Trigone
Tongue
Oropharynx
Teeth"""
	
	# Step 3: Diagram Marking
	template.enable_diagram_marking = 1
	template.diagram_type = "Oral Cavity"
	
	# Step 4: Image Upload
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
	
	# Step 5: Special Tests (Photo Diagnosis)
	template.enable_special_tests = 1
	template.special_tests = """Toluidine Blue Test
Blue Light Test
Autofluorescence Test
Spectroscopy Test"""
	
	# Step 6: Provisional Diagnosis
	template.enable_provisional_diagnosis = 1
	template.diagnosis_options = """Normal, routine screening after 1 year, continue self-oral examination
Normal with risk factors, close screening every six months
Potentially Malignant lesions, precancerous lesions, need further management
High risk, need to see the nearest center for further evaluation
Suspicious for cancer, need to see the nearest center for further evaluation
Frank malignancy, requires immediate treatment visit specialized cancer center
Insufficient data for any comments, repeat examination
Inflammation or infection or nutritional factors to be ruled out or treated and then repeat examination"""
	
	# Step 7: Prescription
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
	
	if template.name:
		template.save(ignore_permissions=True)
	else:
		template.insert()
	
	# Assign practitioners
	assign_practitioners_to_template(template_name)
	
	print(f"    ✓ Created/Updated '{template_name}'")


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
