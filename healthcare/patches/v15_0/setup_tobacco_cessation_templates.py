
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def execute():
	"""
	Setup Tobacco Cessation Templates and related fields on Patient Encounter.
	1. Create 'Quit Buddy' Child Doctype.
	2. Update 'Clinical Examination Template' examination_type options.
	3. Create 'Quit Tobacco First Visit' and 'Quit Tobacco Follow-up Visit' templates.
	4. Create Custom Fields on Patient Encounter for these forms.
	"""
	print("\n" + "="*60)
	print("Setting up Tobacco Cessation Templates")
	print("="*60)

	# 1. Create Quit Buddy Child Doctype
	create_quit_buddy_doctype()

	# 2. Update Examination Type Options
	update_examination_type_options()

	# 3. Create Custom Fields on Patient Encounter
	# create_patient_encounter_fields()

	# 4. Create Templates
	create_templates()

	frappe.db.commit()
	frappe.clear_cache()
	print("\n" + "="*60)
	print("Tobacco Cessation Templates Setup Complete!")
	print("="*60)


def create_quit_buddy_doctype():
	if not frappe.db.exists("DocType", "Quit Buddy"):
		doc = frappe.get_doc({
			"doctype": "DocType",
			"module": "Healthcare",
			"name": "Quit Buddy",
			"istable": 1,
			"editable_grid": 1,
			"fields": [
				{
					"fieldname": "buddy_name",
					"fieldtype": "Data",
					"label": "Name",
					"reqd": 1,
					"in_list_view": 1
				},
				{
					"fieldname": "relation",
					"fieldtype": "Select",
					"label": "Relation",
					"options": "Friend\nSpouse\nBrother\nSister\nCousin\nColleague\nFather\nMother\nSon\nDaughter\nOther",
					"reqd": 1,
					"in_list_view": 1
				},
				{
					"fieldname": "phone",
					"fieldtype": "Data",
					"label": "Phone (WhatsApp)",
					"options": "Phone",
					"in_list_view": 1
				},
				{
					"fieldname": "email",
					"fieldtype": "Data",
					"label": "Email",
					"options": "Email"
				}
			]
		})
		doc.insert(ignore_permissions=True)
		print("✓ Created Child Doctype: Quit Buddy")
	else:
		print("⏭ Child Doctype 'Quit Buddy' already exists")


def update_examination_type_options():
	doctype = "Clinical Examination Template"
	fieldname = "examination_type"
	property_setter_name = f"{doctype}-{fieldname}-options"
	
	# Get existing options
	current_options = frappe.db.get_value("DocField", {"parent": doctype, "fieldname": fieldname}, "options")
	if not current_options:
		current_options = "Oral Screening\nDermatology\nGeneral Physical\nENT\nOphthalmology\nCardiology\nOther"
	
	new_options_list = ["Quit Tobacco First Visit", "Quit Tobacco Follow-up Visit"]
	updated = False
	
	for opt in new_options_list:
		if opt not in current_options:
			current_options += f"\n{opt}"
			updated = True
	
	if updated:
		make_property_setter(doctype, fieldname, "options", current_options, "Small Text")
		print("✓ Updated Examination Type Options")
	else:
		print("⏭ Examination Type Options already updated")


def create_templates():
	templates = [
		{
			"template_name": "Quit Tobacco First Visit",
			"examination_type": "Quit Tobacco First Visit",
			"description": "Tobacco Cessation Protocol V2026.01 - First Visit"
		},
		{
			"template_name": "Quit Tobacco Follow-up Visit",
			"examination_type": "Quit Tobacco Follow-up Visit",
			"description": "Tobacco Cessation Protocol V2026.01 - Follow-up Visit"
		}
	]

	for tmpl in templates:
		if not frappe.db.exists("Clinical Examination Template", tmpl["template_name"]):
			doc = frappe.get_doc({
				"doctype": "Clinical Examination Template",
				"template_name": tmpl["template_name"],
				"examination_type": tmpl["examination_type"],
				"description": tmpl["description"],
				"is_active": 1,
				# Enable specific sections if needed, or disable defaults
				"enable_complaints": 0,
				"enable_physical_exam": 0, 
				"enable_diagram_marking": 0,
				"enable_image_upload": 0,
				"enable_special_tests": 0,
				"enable_provisional_diagnosis": 0,
				"enable_prescription": 0 # We use custom sections
			})
			doc.insert(ignore_permissions=True)
			print(f"✓ Created template: {tmpl['template_name']}")
		else:
			print(f"⏭ Template '{tmpl['template_name']}' already exists")


def create_patient_encounter_fields():
	fields = [
		# --- Quit Tobacco First Visit Section ---
		{
			"fieldname": "tobacco_cessation_first_visit_section",
			"label": "Tobacco Cessation - First Visit",
			"fieldtype": "Section Break",
			"insert_after": "exam_examination_template", # Adjust position as needed
			"depends_on": "eval:doc.exam_examination_template && doc.exam_examination_template.includes('Quit Tobacco First Visit')",
			"collapsible": 0
		},
		{
			"fieldname": "tobacco_quit_date",
			"label": "Quit Date",
			"fieldtype": "Date",
			"insert_after": "tobacco_cessation_first_visit_section",
			"reqd": 1
		},
		{
			"fieldname": "tobacco_quit_method",
			"label": "Method of Quitting",
			"fieldtype": "Select",
			"options": "Cold turkey\nGradual reduction",
			"insert_after": "tobacco_quit_date",
			"reqd": 1
		},
		{
			"fieldname": "tobacco_quit_buddies_section",
			"label": "Quit Buddies",
			"fieldtype": "Section Break",
			"insert_after": "tobacco_quit_method",
			"collapsible": 0
		},
		{
			"fieldname": "tobacco_quit_buddies",
			"label": "Quit Buddies",
			"fieldtype": "Table",
			"options": "Quit Buddy",
			"insert_after": "tobacco_quit_buddies_section"
		},
		{
			"fieldname": "tobacco_treatment_planning_section",
			"label": "Treatment Planning",
			"fieldtype": "Section Break",
			"insert_after": "tobacco_quit_buddies",
			"collapsible": 0
		},
		{
			"fieldname": "tobacco_diagnosis_notes",
			"label": "Diagnosis Details",
			"fieldtype": "Small Text",
			"insert_after": "tobacco_treatment_planning_section"
		},
		{
			"fieldname": "tobacco_prescription_notes",
			"label": "Prescription (triggers/withdrawals)",
			"fieldtype": "Text Editor",
			"insert_after": "tobacco_diagnosis_notes"
		},
		{
			"fieldname": "tobacco_lab_investigations",
			"label": "Lab Investigations",
			"fieldtype": "Small Text",
			"insert_after": "tobacco_prescription_notes"
		},
		{
			"fieldname": "tobacco_remedies",
			"label": "Remedies for trigger/withdrawals",
			"fieldtype": "Small Text",
			"insert_after": "tobacco_lab_investigations"
		},
		{
			"fieldname": "tobacco_specialist_referral",
			"label": "Specialist referral",
			"fieldtype": "Check",
			"default": "0",
			"insert_after": "tobacco_remedies"
		},
		{
			"fieldname": "tobacco_advice_notes",
			"label": "Advise for the patients (if any)/Notes",
			"fieldtype": "Text Editor",
			"insert_after": "tobacco_specialist_referral"
		},
		# --- Quit Tobacco Follow-up Visit Section ---
		{
			"fieldname": "tobacco_followup_visit_section",
			"label": "Tobacco Cessation - Follow-up Visit",
			"fieldtype": "Section Break",
			"insert_after": "tobacco_advice_notes",
			"depends_on": "eval:doc.exam_examination_template && doc.exam_examination_template.includes('Quit Tobacco Follow-up Visit')",
			"collapsible": 0
		},
		{
			"fieldname": "tobacco_visit_mode",
			"label": "Mode",
			"fieldtype": "Select",
			"options": "Online\nIn clinic",
			"default": "Online",
			"insert_after": "tobacco_followup_visit_section",
			"reqd": 1
		},
		{
			"fieldname": "tobacco_col_break_1",
			"fieldtype": "Column Break",
			"insert_after": "tobacco_visit_mode"
		},
		{
			"fieldname": "tobacco_start_time",
			"label": "Start Time",
			"fieldtype": "Time",
			"default": "Now",
			"insert_after": "tobacco_col_break_1",
			"reqd": 1
		},
		{
			"fieldname": "tobacco_end_time",
			"label": "End Time",
			"fieldtype": "Time",
			"default": "Now",
			"insert_after": "tobacco_start_time",
			"reqd": 1
		},
		{
			"fieldname": "tobacco_consumption_section",
			"label": "Consumption Details",
			"fieldtype": "Section Break",
			"insert_after": "tobacco_end_time"
		},
		{
			"fieldname": "tobacco_smoking_consumption", # Using bespoke name to avoid conflict/ensure visibility
			"label": "Smoking Consumption",
			"fieldtype": "Table",
			"options": "Patient Smoking Tobacco History", # Reusing existing
			"insert_after": "tobacco_consumption_section"
		},
		{
			"fieldname": "tobacco_smokeless_consumption",
			"label": "Smokeless Consumption",
			"fieldtype": "Table",
			"options": "Patient Smokeless Tobacco History", # Reusing existing
			"insert_after": "tobacco_smoking_consumption"
		},
		{
			"fieldname": "tobacco_status_section",
			"label": "Quit Status",
			"fieldtype": "Section Break",
			"insert_after": "tobacco_smokeless_consumption"
		},
		{
			"fieldname": "tobacco_stuck_to_quit_date",
			"label": "Has the patient stuck to the quit date?",
			"fieldtype": "Select",
			"options": "Yes\nNo",
			"insert_after": "tobacco_status_section",
			"reqd": 1
		},
		{
			"fieldname": "tobacco_reason_delay",
			"label": "Reason for delay in quitting",
			"fieldtype": "Small Text",
			"insert_after": "tobacco_stuck_to_quit_date",
			"depends_on": "eval:doc.tobacco_stuck_to_quit_date=='No'"
		},
		{
			"fieldname": "tobacco_followup_quit_date",
			"label": "Quit Date",
			"fieldtype": "Date",
			"insert_after": "tobacco_reason_delay",
			"depends_on": "eval:doc.tobacco_stuck_to_quit_date=='Yes'"
		},
		{
			"fieldname": "tobacco_obs_positives",
			"label": "Observations/Positives",
			"fieldtype": "Small Text",
			"insert_after": "tobacco_followup_quit_date"
		},
		{
			"fieldname": "tobacco_symptoms_complaints",
			"label": "Symptoms/Complaints",
			"fieldtype": "Small Text",
			"insert_after": "tobacco_obs_positives"
		},
		{
			"fieldname": "tobacco_advices",
			"label": "Advices",
			"fieldtype": "Small Text",
			"insert_after": "tobacco_symptoms_complaints"
		},
		{
			"fieldname": "tobacco_qol_section",
			"label": "Quality of Life Assessment",
			"fieldtype": "Section Break",
			"insert_after": "tobacco_advices"
		},
		{
			"fieldname": "tobacco_qol_score",
			"label": "QOL Score (1-10)",
			"fieldtype": "Int",
			"description": "How has your quality of life been since you quit? (1-10)",
			"insert_after": "tobacco_qol_section"
		},
		{
			"fieldname": "tobacco_emotional_wellbeing_score",
			"label": "Emotional Well Being Score (1-10)",
			"fieldtype": "Int",
			"description": "How has your mental health been since quitting? (1-10)",
			"insert_after": "tobacco_qol_score"
		},
		{
			"fieldname": "tobacco_overall_feeling_score",
			"label": "Overall Feeling Score (1-10)",
			"fieldtype": "Int",
			"description": "Overall how do you feel since you quit tobacco? (1-10)",
			"insert_after": "tobacco_emotional_wellbeing_score"
		},
		{
			"fieldname": "tobacco_home_remedies",
			"label": "Home Remedies",
			"fieldtype": "Text Editor",
			"insert_after": "tobacco_overall_feeling_score"
		}
	]
	
	for field in fields:
		create_custom_field("Patient Encounter", field)
		print(f"✓ Created/Updated Field: {field['fieldname']}")

