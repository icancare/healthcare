import frappe


def execute():
	"""
	Move Personal Information and Language Preferences sections BEFORE Customer Details
	Currently they are appearing after Customer Details, need to move them up
	"""
	
	try:
		# Delete the wrongly positioned custom fields
		fields_to_reposition = [
			"personal_information_section",
			"education",
			"occupation_type",
			"column_break_personal_1",
			"religion",
			"ethnic_background",
			"ethnicity",
			"language_preferences_section",
			"preferred_spoken_language",
			"preferred_written_language",
			"column_break_language_1",
			"additional_spoken_languages",
			"additional_written_languages"
		]
		
		for fieldname in fields_to_reposition:
			frappe.db.sql("""
				DELETE FROM `tabCustom Field`
				WHERE dt = 'Patient' AND fieldname = %s
			""", fieldname)
		
		frappe.db.commit()
		print("✓ Removed custom fields from wrong position")
		
		# Now re-add them in correct position (after user_id, before customer_details_section)
		from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
		
		custom_fields = {
			"Patient": [
				# Personal Information Section (BEFORE customer_details_section)
				{
					"fieldname": "personal_information_section",
					"fieldtype": "Section Break",
					"label": "Personal Information",
					"insert_after": "user_id",
					"collapsible": 1
				},
				
				# Education
				{
					"fieldname": "education",
					"fieldtype": "Select",
					"label": "Education",
					"options": "\nPrimary < Class 5\nClass 6-10\nBachelors (Undergraduate)\nMasters (Graduate)\nPost Graduate\nPh.D",
					"insert_after": "personal_information_section",
				},
				
				# Occupation Type
				{
					"fieldname": "occupation_type",
					"fieldtype": "Select",
					"label": "Occupation Type",
					"options": "\nGovernment\nPrivate\nOwn-Business\nHouse hold\nRetired\nUnemployed able to work\nUnemployed – not able to work\nStudent\nRefuse\nOther",
					"insert_after": "education",
				},
				
				{
					"fieldname": "column_break_personal_1",
					"fieldtype": "Column Break",
					"insert_after": "occupation_type",
				},
				
				# Religion
				{
					"fieldname": "religion",
					"fieldtype": "Select",
					"label": "Religion",
					"options": "\nHindu\nMuslim\nChristian\nSikh\nBuddhist\nJain\nParsi\nOther\nRefuse",
					"insert_after": "column_break_personal_1",
				},
				
				# Caste/Ethnic Background
				{
					"fieldname": "ethnic_background",
					"fieldtype": "Data",
					"label": "Ethnic Background / Caste",
					"insert_after": "religion",
					"description": "Optional field"
				},
				
				# Ethnicity
				{
					"fieldname": "ethnicity",
					"fieldtype": "Data",
					"label": "Ethnicity",
					"insert_after": "ethnic_background",
				},
				
				# Language Preferences Section
				{
					"fieldname": "language_preferences_section",
					"fieldtype": "Section Break",
					"label": "Language Preferences",
					"insert_after": "ethnicity",
					"collapsible": 1
				},
				
				# Preferred Spoken Language
				{
					"fieldname": "preferred_spoken_language",
					"fieldtype": "Select",
					"label": "Preferred Spoken Language",
					"options": "\nEnglish\nHindi\nAssamese\nBengali\nBodo\nDogri\nGujarati\nKannada\nKashmiri\nKonkani\nMaithili\nMalayalam\nManipuri\nMarathi\nNepali\nOdia\nPunjabi\nSanskrit\nSantali\nSindhi\nTamil\nTelugu\nUrdu\nForeign\nRefuse",
					"insert_after": "language_preferences_section",
				},
				
				# Preferred Written Language
				{
					"fieldname": "preferred_written_language",
					"fieldtype": "Select",
					"label": "Preferred Written Language",
					"options": "\nEnglish\nHindi\nAssamese\nBengali\nBodo\nDogri\nGujarati\nKannada\nKashmiri\nKonkani\nMaithili\nMalayalam\nManipuri\nMarathi\nNepali\nOdia\nPunjabi\nSanskrit\nSantali\nSindhi\nTamil\nTelugu\nUrdu\nForeign\nRefuse",
					"insert_after": "preferred_spoken_language",
				},
				
				{
					"fieldname": "column_break_language_1",
					"fieldtype": "Column Break",
					"insert_after": "preferred_written_language",
				},
				
				# Additional Spoken Languages
				{
					"fieldname": "additional_spoken_languages",
					"fieldtype": "Table",
					"label": "Additional Spoken Languages",
					"options": "Patient Spoken Language",
					"insert_after": "column_break_language_1",
				},
				
				# Additional Written Languages
				{
					"fieldname": "additional_written_languages",
					"fieldtype": "Table",
					"label": "Additional Written Languages",
					"options": "Patient Written Language",
					"insert_after": "additional_spoken_languages",
				},
			]
		}
		
		create_custom_fields(custom_fields, update=True)
		frappe.db.commit()
		
		print("✓ Successfully moved Personal Information and Language Preferences")
		print("  - Now appearing BEFORE Customer Details section")
		print("  - Order: Basic Info → Personal Information → Language Preferences → Customer Details")
		
	except Exception as e:
		print(f"Error: {str(e)}")
		frappe.db.rollback()

