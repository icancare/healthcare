import frappe


def execute():
	"""Create sample Treatment Plan Templates for demonstration"""
	print("\n" + "="*60)
	print("Creating Sample Treatment Plan Templates")
	print("="*60)
	
	templates = [
		{
			"template_name": "Diabetes Type 2 Management Plan",
			"description": "Comprehensive treatment plan for Type 2 Diabetes Mellitus patients including lifestyle modifications, medications, and regular monitoring.",
			"goal": "Maintain HbA1c below 7%, prevent complications, improve quality of life",
			"disabled": 0,
			"patient_age_from": 18,
			"patient_age_to": 100,
			"diagnosis_list": ["Type 2 diabetes mellitus"],
			"complaints_list": [],
			"drugs": [
				{
					"drug_name": "Metformin 500mg",
					"dosage": "1-0-1",
					"period": "1 Month",
					"comment": "Take after meals. Start with low dose and increase gradually.",
					"patient_instruction": "Take with food to reduce stomach upset. Drink 1 litre water daily. Avoid alcohol."
				}
			]
		},
		{
			"template_name": "Hypertension Management Plan",
			"description": "Standard treatment protocol for Essential Hypertension including lifestyle changes, medication, and regular BP monitoring.",
			"goal": "Maintain BP below 130/80 mmHg, prevent cardiovascular complications",
			"disabled": 0,
			"patient_age_from": 30,
			"patient_age_to": 100,
			"diagnosis_list": ["Essential hypertension"],
			"complaints_list": ["Headache", "Chest pain"],
			"drugs": [
				{
					"drug_name": "Amlodipine 5mg",
					"dosage": "0-0-1",
					"period": "1 Month",
					"comment": "Calcium channel blocker. Take at night.",
					"patient_instruction": "Take at the same time daily. Reduce salt intake. Exercise 30 mins daily. Avoid stress."
				}
			]
		},
		{
			"template_name": "General Fever Management Plan",
			"description": "Standard protocol for managing fever with symptomatic treatment and investigations to identify cause.",
			"goal": "Reduce fever, identify underlying cause, prevent complications",
			"disabled": 0,
			"patient_age_from": 5,
			"patient_age_to": 100,
			"diagnosis_list": [],
			"complaints_list": ["Other"],
			"drugs": [
				{
					"drug_name": "Paracetamol 500mg",
					"dosage": "1-1-1",
					"period": "3 Day",
					"comment": "Antipyretic. Take when temperature above 100°F.",
					"patient_instruction": "Take every 6-8 hours if fever persists. Drink plenty of fluids (2-3 litres water daily). Rest adequately. Sponge with lukewarm water if high fever."
				}
			]
		}
	]
	
	for template_data in templates:
		# Check if template already exists
		if frappe.db.exists("Treatment Plan Template", template_data["template_name"]):
			print(f"  ⏭ Template '{template_data['template_name']}' already exists, skipping...")
			continue
		
		try:
			doc = frappe.new_doc("Treatment Plan Template")
			doc.template_name = template_data["template_name"]
			doc.description = template_data["description"]
			doc.goal = template_data["goal"]
			doc.disabled = template_data["disabled"]
			doc.patient_age_from = template_data["patient_age_from"]
			doc.patient_age_to = template_data["patient_age_to"]
			
			# Add diagnosis
			for diagnosis_name in template_data.get("diagnosis_list", []):
				if frappe.db.exists("Diagnosis", diagnosis_name):
					doc.append("diagnosis", {
						"diagnosis": diagnosis_name
					})
			
			# Add complaints
			for complaint_name in template_data.get("complaints_list", []):
				if frappe.db.exists("Complaint", complaint_name):
					doc.append("complaints", {
						"complaint": complaint_name
					})
			
			# Add drugs
			for drug in template_data.get("drugs", []):
				doc.append("drugs", {
					"drug_name": drug["drug_name"],
					"dosage": drug.get("dosage"),
					"period": drug.get("period"),
					"comment": drug.get("comment"),
					"patient_instruction": drug.get("patient_instruction")
				})
			
			doc.flags.ignore_permissions = True
			doc.flags.ignore_mandatory = True
			doc.insert()
			print(f"  ✓ Created '{template_data['template_name']}'")
		except Exception as e:
			print(f"  ✗ Error creating '{template_data['template_name']}': {str(e)}")
	
	frappe.db.commit()
	print("✓ Sample Treatment Plan Templates Created!")
	print("="*60 + "\n")

