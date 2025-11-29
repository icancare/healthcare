import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Force add Patient fields in production
	This will run regardless of previous patch state
	"""
	
	print("=" * 80)
	print("FORCE ADDING PATIENT FIELDS - PRODUCTION FIX")
	print("=" * 80)
	
	# Step 1: Check current state
	check_current_state()
	
	# Step 2: Force clear and re-add
	force_clear_all_fields()
	force_add_all_fields()
	
	# Step 3: Fix other fields
	force_fix_occupation()
	force_fix_phone()
	
	# Step 4: Verify
	verify_fields()
	
	frappe.db.commit()
	
	print("=" * 80)
	print("✓ PRODUCTION FIX COMPLETE")
	print("=" * 80)


def check_current_state():
	"""Check what fields currently exist"""
	print("\n--- CHECKING CURRENT STATE ---")
	
	try:
		# Check custom fields
		custom_fields = frappe.db.sql("""
			SELECT fieldname, label, insert_after 
			FROM `tabCustom Field` 
			WHERE dt = 'Patient' 
			ORDER BY idx
		""", as_dict=True)
		
		print(f"Found {len(custom_fields)} custom fields")
		
		our_fields = [
			'prefix', 'work_phone', 'personal_information_section',
			'education', 'occupation_type', 'religion', 'ethnic_background',
			'ethnicity', 'language_preferences_section', 'preferred_spoken_language',
			'preferred_written_language', 'additional_spoken_languages',
			'additional_written_languages', 'emergency_contact_section',
			'patient_emergency_contact'
		]
		
		found_fields = [f['fieldname'] for f in custom_fields if f['fieldname'] in our_fields]
		missing_fields = [f for f in our_fields if f not in found_fields]
		
		print(f"✓ Found our fields: {len(found_fields)}")
		print(f"✗ Missing fields: {len(missing_fields)}")
		if missing_fields:
			print(f"  Missing: {', '.join(missing_fields)}")
		
	except Exception as e:
		print(f"Error checking state: {str(e)}")


def force_clear_all_fields():
	"""Force delete all our custom fields"""
	print("\n--- FORCE CLEARING FIELDS ---")
	
	fields_to_remove = [
		'emergency_contact_section', 'patient_emergency_contact',
		'personal_information_section', 'education', 'occupation_type',
		'occupation_level', 'column_break_personal_1', 'religion',
		'ethnic_background', 'ethnicity', 'language_preferences_section',
		'preferred_spoken_language', 'preferred_written_language',
		'column_break_language_1', 'additional_spoken_languages',
		'additional_written_languages', 'work_phone', 'prefix'
	]
	
	deleted_count = 0
	for fieldname in fields_to_remove:
		try:
			result = frappe.db.sql("""
				DELETE FROM `tabCustom Field`
				WHERE dt = 'Patient' AND fieldname = %s
			""", fieldname)
			deleted_count += 1
		except Exception as e:
			print(f"  Note: {fieldname} - {str(e)}")
	
	frappe.db.commit()
	print(f"✓ Cleared {deleted_count} fields")


def force_add_all_fields():
	"""Force add all fields - no conditions"""
	print("\n--- FORCE ADDING ALL FIELDS ---")
	
	# Delete any existing first to avoid duplicates
	frappe.clear_cache(doctype="Patient")
	
	custom_fields = {
		"Patient": [
			# Prefix
			{
				"fieldname": "prefix",
				"fieldtype": "Select",
				"label": "Prefix",
				"options": "\nMr.\nMrs.\nMs.\nDr.\nProf.",
				"insert_after": "basic_info",
			},
			
			# Work Phone
			{
				"fieldname": "work_phone",
				"fieldtype": "Data",
				"label": "Work Phone",
				"options": "Phone",
				"insert_after": "phone",
			},
			
			# Personal Information Section
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
			
			# Language Preferences
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
			
			# Emergency Contacts
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
	
	try:
		create_custom_fields(custom_fields, update=True)
		print("✓ All fields added successfully")
	except Exception as e:
		print(f"Error adding fields: {str(e)}")
		# Try one by one
		for field_def in custom_fields["Patient"]:
			try:
				create_custom_fields({"Patient": [field_def]}, update=True)
				print(f"  ✓ Added: {field_def['fieldname']}")
			except Exception as e2:
				print(f"  ✗ Failed: {field_def['fieldname']} - {str(e2)}")


def force_fix_occupation():
	"""Force fix occupation field"""
	print("\n--- FIXING OCCUPATION FIELD ---")
	
	try:
		frappe.db.sql("""
			UPDATE `tabDocField` 
			SET 
				fieldtype = 'Select',
				options = '\nGovernment\nPrivate\nOwn-Business\nHouse hold\nRetired\nUnemployed able to work\nUnemployed – not able to work\nStudent\nRefuse\nOther'
			WHERE parent = 'Patient' 
			AND fieldname = 'occupation'
		""")
		print("✓ Occupation converted to dropdown")
	except Exception as e:
		print(f"✗ Occupation fix failed: {str(e)}")


def force_fix_phone():
	"""Force fix phone label"""
	print("\n--- FIXING PHONE LABEL ---")
	
	try:
		frappe.db.sql("""
			UPDATE `tabDocField` 
			SET label = 'Home Phone'
			WHERE parent = 'Patient' AND fieldname = 'phone'
		""")
		print("✓ Phone renamed to Home Phone")
	except Exception as e:
		print(f"✗ Phone fix failed: {str(e)}")


def verify_fields():
	"""Verify all fields are added"""
	print("\n--- VERIFYING FIELDS ---")
	
	try:
		custom_fields = frappe.db.sql("""
			SELECT fieldname 
			FROM `tabCustom Field` 
			WHERE dt = 'Patient'
		""", as_dict=True)
		
		our_fields = [
			'prefix', 'work_phone', 'personal_information_section',
			'education', 'occupation_type', 'religion', 'ethnic_background',
			'ethnicity', 'language_preferences_section', 'preferred_spoken_language',
			'preferred_written_language', 'additional_spoken_languages',
			'additional_written_languages', 'emergency_contact_section',
			'patient_emergency_contact'
		]
		
		found_fields = [f['fieldname'] for f in custom_fields if f['fieldname'] in our_fields]
		
		print(f"✓ Verified: {len(found_fields)}/{len(our_fields)} fields present")
		
		if len(found_fields) == len(our_fields):
			print("✓ ALL FIELDS SUCCESSFULLY ADDED!")
		else:
			missing = [f for f in our_fields if f not in found_fields]
			print(f"✗ Still missing: {', '.join(missing)}")
		
	except Exception as e:
		print(f"Error verifying: {str(e)}")

