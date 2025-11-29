import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Fix Patient Basic Profile fields positioning
	Move fields from Medical History tab to Details tab (before Customer Details section)
	"""
	
	# Remove wrongly positioned fields
	remove_old_custom_fields()
	
	# Re-add fields in correct position
	custom_fields = {
		"Patient": [
			# Personal Information Section (in Details tab, before customer_details_section)
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
			
			# Occupation Type (new field, different from existing occupation text field)
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
	
	# Unhide and move occupation field
	fix_occupation_field()
	
	frappe.db.commit()
	
	print("✓ Fixed Patient Basic Profile field positions")
	print("  - Moved Personal Information section to Details tab")
	print("  - Moved Language Preferences section to Details tab")
	print("  - All sections now appear before Customer Details")
	print("  - Occupation Type field added in correct position")


def remove_old_custom_fields():
	"""Remove custom fields that were added in wrong position"""
	try:
		# List of custom fields to remove (they'll be re-added in correct position)
		fields_to_remove = [
			"personal_information_section",
			"education",
			"occupation_level",
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
		
		for fieldname in fields_to_remove:
			frappe.db.sql("""
				DELETE FROM `tabCustom Field`
				WHERE dt = 'Patient' AND fieldname = %s
			""", fieldname)
		
		print("✓ Removed old custom fields from wrong positions")
		frappe.db.commit()
	except Exception as e:
		print(f"Note: Could not remove old fields - {str(e)}")


def fix_occupation_field():
	"""Unhide occupation field from Medical History tab"""
	try:
		# Unhide the original occupation field
		if frappe.db.exists("DocField", {"parent": "Patient", "fieldname": "occupation"}):
			frappe.db.sql("""
				UPDATE `tabDocField` 
				SET hidden = 0, print_hide = 0
				WHERE parent = 'Patient' AND fieldname = 'occupation'
			""")
			print("✓ Occupation field unhidden and ready to use")
		
		frappe.db.commit()
	except Exception as e:
		print(f"Note: Could not fix occupation field - {str(e)}")

