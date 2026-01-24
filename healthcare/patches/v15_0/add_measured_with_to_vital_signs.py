import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	"""
	Add Measured With field to Vital Signs and update Mouth Opening Fingers options
	This will enable sync between Vital Signs and Patient Encounter Step 2 - Mouth examination
	
	Changes:
	1. Add link field between Patient Encounter and Vital Signs
	2. Add "Measured With" field to Vital Signs (Options: TrisCare, Caliper, Other)
	3. Update "Mouth Opening (Fingers)" options to match Patient Encounter: One, Two, Three, Four
	"""
	try:
		# Step 1: Add Vital Signs link field to Patient Encounter
		add_vital_signs_link_field()
		
		# Step 2: Add Measured With field to Vital Signs
		add_measured_with_field()
		
		# Step 3: Update Mouth Opening Fingers options
		update_mouth_opening_fingers_options()
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Successfully updated Vital Signs Oral Examination:")
		print("   - Added link field between Patient Encounter and Vital Signs")
		print("   - Added 'Measured With' field (TrisCare/Caliper/Other)")
		print("   - Updated 'Mouth Opening (Fingers)' options to match Patient Encounter")
		print("   - Now syncs with Patient Encounter Step 2 - Mouth examination")
		
	except Exception as e:
		print(f"❌ Error: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

def add_vital_signs_link_field():
	"""Add Vital Signs link field to Patient Encounter for two-way sync"""
	
	custom_fields = {
		"Patient Encounter": [
			{
				"fieldname": "vital_signs",
				"label": "Vital Signs",
				"fieldtype": "Link",
				"options": "Vital Signs",
				"insert_after": "patient_age"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	print("✅ Added 'Vital Signs' link field to Patient Encounter")

def add_measured_with_field():
	"""Add Measured With field to Vital Signs after mouth_opening_mm"""
	
	custom_fields = {
		"Vital Signs": [
			{
				"fieldname": "measured_with",
				"label": "Measured With",
				"fieldtype": "Select",
				"options": "\nTrisCare\nCaliper\nOther",
				"insert_after": "mouth_opening_mm"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	print("✅ Added 'Measured With' field to Vital Signs")

def update_mouth_opening_fingers_options():
	"""Update Mouth Opening Fingers field options to match Patient Encounter"""
	
	# Get the Vital Signs DocType
	doctype_name = "Vital Signs"
	
	if not frappe.db.exists("DocType", doctype_name):
		print(f"⚠️  DocType {doctype_name} does not exist")
		return
	
	# Check if the field exists
	if not frappe.db.exists("DocField", {"parent": doctype_name, "fieldname": "mouth_opening_fingers"}):
		print(f"⚠️  Field mouth_opening_fingers does not exist in {doctype_name}")
		return
	
	# Update the field options
	frappe.db.sql("""
		UPDATE `tabDocField`
		SET options = %s
		WHERE parent = %s AND fieldname = %s
	""", ("\nOne\nTwo\nThree\nFour", doctype_name, "mouth_opening_fingers"))
	
	print(f"✅ Updated mouth_opening_fingers options in {doctype_name}")
	
	# Clear cache for the doctype
	frappe.clear_cache(doctype=doctype_name)


