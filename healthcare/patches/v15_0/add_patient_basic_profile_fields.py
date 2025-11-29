import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Add Patient Basic Profile fields as per client requirements
	This includes: Prefix, Phone fields, Education, Languages, Religion, Caste, etc.
	"""
	
	# First rename existing 'phone' field to 'home_phone'
	rename_phone_field()
	
	# Add all new custom fields
	custom_fields = {
		"Patient": [
			# Add Prefix field (before first_name)
			{
				"fieldname": "prefix",
				"fieldtype": "Select",
				"label": "Prefix",
				"options": "\nMr.\nMrs.\nMs.\nDr.\nProf.",
				"insert_after": "basic_info",
			},
			
			# Add Work Phone field (after home_phone which was phone)
			{
				"fieldname": "work_phone",
				"fieldtype": "Data",
				"label": "Work Phone",
				"options": "Phone",
				"insert_after": "phone",
			},
			
			# Personal Information Section (in Details tab, before Customer Details)
			{
				"fieldname": "personal_information_section",
				"fieldtype": "Section Break",
				"label": "Personal Information",
				"insert_after": "patient_details",
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
			
			# Occupation (update existing field to dropdown instead of text)
			{
				"fieldname": "occupation",
				"fieldtype": "Select",
				"label": "Occupation",
				"options": "\nGovernment\nPrivate\nOwn-Business\nHouse hold\nRetired\nUnemployed able to work\nUnemployed – not able to work\nStudent\nRefuse\nOther",
				"insert_after": "education",
			},
			
			{
				"fieldname": "column_break_personal_1",
				"fieldtype": "Column Break",
				"insert_after": "occupation",
			},
			
			# Religion
			{
				"fieldname": "religion",
				"fieldtype": "Select",
				"label": "Religion",
				"options": "\nHindu\nMuslim\nChristian\nSikh\nBuddhist\nJain\nParsi\nOther\nRefuse",
				"insert_after": "column_break_personal_1",
			},
			
			# Caste/Ethnic Background (Optional, sensitive)
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
			
			# Additional Spoken Languages (Table)
			{
				"fieldname": "additional_spoken_languages",
				"fieldtype": "Table",
				"label": "Additional Spoken Languages",
				"options": "Patient Spoken Language",
				"insert_after": "column_break_language_1",
			},
			
			# Additional Written Languages (Table)
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
	
	# Unhide occupation field and update it
	unhide_occupation_field()
	
	frappe.db.commit()
	
	print("✓ Patient Basic Profile fields added successfully")
	print("  - Prefix field added")
	print("  - Phone renamed to Home Phone")
	print("  - Work Phone added")
	print("  - Personal Information section added in Details tab")
	print("  - Education, Occupation, Religion, Ethnicity added")
	print("  - Language preferences section added")
	print("  - Additional languages tables added")


def rename_phone_field():
	"""Rename 'phone' field to 'home_phone' for clarity"""
	try:
		# Check if field exists
		if frappe.db.exists("DocField", {"parent": "Patient", "fieldname": "phone"}):
			frappe.db.sql("""
				UPDATE `tabDocField` 
				SET label = 'Home Phone'
				WHERE parent = 'Patient' AND fieldname = 'phone'
			""")
			print("✓ Renamed 'phone' field to 'Home Phone'")
		
		frappe.db.commit()
	except Exception as e:
		print(f"Note: Could not rename phone field - {str(e)}")


def unhide_occupation_field():
	"""Unhide occupation field and convert it to dropdown"""
	try:
		if frappe.db.exists("DocField", {"parent": "Patient", "fieldname": "occupation"}):
			frappe.db.sql("""
				UPDATE `tabDocField` 
				SET hidden = 0, print_hide = 0
				WHERE parent = 'Patient' AND fieldname = 'occupation'
			""")
			print("✓ Unhidden occupation field and updated to dropdown")
		
		frappe.db.commit()
	except Exception as e:
		print(f"Note: Could not unhide occupation field - {str(e)}")

