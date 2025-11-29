import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Final fix for all Patient Basic Profile fields
	This ensures all fields are in correct position regardless of previous state
	"""
	
	print("Starting final fix for Patient fields...")
	
	# Step 1: Clear all our custom fields completely
	clear_custom_fields()
	
	# Step 2: Clear cache to ensure fresh start
	frappe.clear_cache(doctype="Patient")
	
	# Step 3: Add all fields in ONE go with correct positions
	add_all_fields_correctly()
	
	# Step 4: Fix occupation field in Medical History
	fix_occupation_field()
	
	# Step 5: Fix phone field label
	fix_phone_field()
	
	frappe.db.commit()
	
	print("✓ All Patient fields fixed and positioned correctly")


def clear_custom_fields():
	"""Remove all custom fields we created"""
	try:
		fields_to_remove = [
			# Emergency Contact
			"emergency_contact_section",
			"patient_emergency_contact",
			# Personal Information
			"personal_information_section",
			"education",
			"occupation_type",
			"occupation_level",
			"column_break_personal_1",
			"religion",
			"ethnic_background",
			"ethnicity",
			# Language Preferences
			"language_preferences_section",
			"preferred_spoken_language",
			"preferred_written_language",
			"column_break_language_1",
			"additional_spoken_languages",
			"additional_written_languages",
			# Phone fields
			"work_phone",
			"prefix"
		]
		
		for fieldname in fields_to_remove:
			# Delete from Custom Field table
			frappe.db.sql("""
				DELETE FROM `tabCustom Field`
				WHERE dt = 'Patient' AND fieldname = %s
			""", fieldname)
		
		frappe.db.commit()
		print("✓ Cleared all custom fields")
		
	except Exception as e:
		print(f"Note during clearing: {str(e)}")


def add_all_fields_correctly():
	"""Add all fields in correct order"""
	
	custom_fields = {
		"Patient": [
			# ========== BASIC INFO SECTION ==========
			# Prefix (at the very beginning)
			{
				"fieldname": "prefix",
				"fieldtype": "Select",
				"label": "Prefix",
				"options": "\nMr.\nMrs.\nMs.\nDr.\nProf.",
				"insert_after": "basic_info",
			},
			
			# Work Phone (after phone field)
			{
				"fieldname": "work_phone",
				"fieldtype": "Data",
				"label": "Work Phone",
				"options": "Phone",
				"insert_after": "phone",
			},
			
			# ========== PERSONAL INFORMATION (Before Customer Details) ==========
			{
				"fieldname": "personal_information_section",
				"fieldtype": "Section Break",
				"label": "Personal Information",
				"insert_after": "user_id",
				"collapsible": 1
			},
			
			{
				"fieldname": "education",
				"fieldtype": "Select",
				"label": "Education",
				"options": "\nPrimary < Class 5\nClass 6-10\nBachelors (Undergraduate)\nMasters (Graduate)\nPost Graduate\nPh.D",
				"insert_after": "personal_information_section",
			},
			
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
			
			{
				"fieldname": "religion",
				"fieldtype": "Select",
				"label": "Religion",
				"options": "\nHindu\nMuslim\nChristian\nSikh\nBuddhist\nJain\nParsi\nOther\nRefuse",
				"insert_after": "column_break_personal_1",
			},
			
			{
				"fieldname": "ethnic_background",
				"fieldtype": "Data",
				"label": "Ethnic Background / Caste",
				"insert_after": "religion",
				"description": "Optional field"
			},
			
			{
				"fieldname": "ethnicity",
				"fieldtype": "Data",
				"label": "Ethnicity",
				"insert_after": "ethnic_background",
			},
			
			# ========== LANGUAGE PREFERENCES ==========
			{
				"fieldname": "language_preferences_section",
				"fieldtype": "Section Break",
				"label": "Language Preferences",
				"insert_after": "ethnicity",
				"collapsible": 1
			},
			
			{
				"fieldname": "preferred_spoken_language",
				"fieldtype": "Select",
				"label": "Preferred Spoken Language",
				"options": "\nEnglish\nHindi\nAssamese\nBengali\nBodo\nDogri\nGujarati\nKannada\nKashmiri\nKonkani\nMaithili\nMalayalam\nManipuri\nMarathi\nNepali\nOdia\nPunjabi\nSanskrit\nSantali\nSindhi\nTamil\nTelugu\nUrdu\nForeign\nRefuse",
				"insert_after": "language_preferences_section",
			},
			
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
			
			{
				"fieldname": "additional_spoken_languages",
				"fieldtype": "Table",
				"label": "Additional Spoken Languages",
				"options": "Patient Spoken Language",
				"insert_after": "column_break_language_1",
			},
			
			{
				"fieldname": "additional_written_languages",
				"fieldtype": "Table",
				"label": "Additional Written Languages",
				"options": "Patient Written Language",
				"insert_after": "additional_spoken_languages",
			},
			
			# ========== EMERGENCY CONTACTS (Address & Contact Tab) ==========
			{
				"fieldname": "emergency_contact_section",
				"fieldtype": "Section Break",
				"label": "Emergency Contacts",
				"insert_after": "contact_html",
				"collapsible": 0
			},
			{
				"fieldname": "patient_emergency_contact",
				"fieldtype": "Table",
				"label": "Emergency Contacts",
				"options": "Patient Emergency Contact",
				"insert_after": "emergency_contact_section",
				"description": "Emergency contact persons who can be reached in case of emergency"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	print("✓ Added all fields:")
	print("  - Prefix and Work Phone in Basic Info")
	print("  - Personal Information section in Details tab")
	print("  - Language Preferences section in Details tab")
	print("  - Emergency Contacts in Address & Contact tab")


def fix_occupation_field():
	"""Convert occupation field to dropdown in Medical History tab"""
	try:
		frappe.db.sql("""
			UPDATE `tabDocField` 
			SET 
				fieldtype = 'Select',
				options = '\nGovernment\nPrivate\nOwn-Business\nHouse hold\nRetired\nUnemployed able to work\nUnemployed – not able to work\nStudent\nRefuse\nOther'
			WHERE parent = 'Patient' 
			AND fieldname = 'occupation'
		""")
		print("✓ Occupation field converted to dropdown")
	except Exception as e:
		print(f"Note: {str(e)}")


def fix_phone_field():
	"""Rename phone to Home Phone"""
	try:
		frappe.db.sql("""
			UPDATE `tabDocField` 
			SET label = 'Home Phone'
			WHERE parent = 'Patient' AND fieldname = 'phone'
		""")
		print("✓ Phone renamed to Home Phone")
	except Exception as e:
		print(f"Note: {str(e)}")

