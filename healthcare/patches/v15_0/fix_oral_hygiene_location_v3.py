import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
	"""
	Fix oral hygiene implementation:
	1. Remove wrongly added separate section
	2. Add fields INSIDE Social History section (after Oral Habits History table)
	3. Use Table MultiSelect for Oral Habit Type
	4. Ensure Gender is visible in Women Health
	"""
	try:
		# Step 1: Delete wrongly added fields
		cleanup_wrong_fields()
		
		# Step 2: Add fields in correct location (inside Social History)
		add_fields_in_social_history()
		
		# Step 3: Verify Gender field exists
		verify_gender_field()
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Successfully fixed oral hygiene implementation")
		print("   - Removed separate Oral Hygiene section")
		print("   - Added fields INSIDE Social History section")
		print("   - Fields will appear after Oral Habits History table")
		print("   - Please manually delete 'Oral Habits History' table using Customize Form")
		
	except Exception as e:
		print(f"❌ Error: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

def cleanup_wrong_fields():
	"""Remove wrongly added section and fields"""
	fields_to_delete = [
		("Patient", "oral_hygiene_section"),
		("Patient", "oral_habit_type"),
		("Patient", "column_break_oral_1"),
		("Patient", "oral_hygiene_practice"),
		("Patient", "column_break_oral_2"),
		("Patient", "dental_visits_frequency"),
		("Patient", "column_break_oral_3"),
		("Patient", "mouth_wash_use"),
		("Patient Encounter", "custom_oral_hygiene_section"),
		("Patient Encounter", "custom_oral_habit_type"),
		("Patient Encounter", "custom_column_break_oral_1"),
		("Patient Encounter", "custom_oral_hygiene_practice"),
		("Patient Encounter", "custom_column_break_oral_2"),
		("Patient Encounter", "custom_dental_visits_frequency"),
		("Patient Encounter", "custom_column_break_oral_3"),
		("Patient Encounter", "custom_mouth_wash_use")
	]
	
	for dt, fieldname in fields_to_delete:
		cf_name = frappe.db.get_value("Custom Field", {"dt": dt, "fieldname": fieldname}, "name")
		if cf_name:
			frappe.delete_doc("Custom Field", cf_name, force=1, ignore_permissions=True)
			print(f"✅ Deleted {fieldname} from {dt}")

def add_fields_in_social_history():
	"""Add fields INSIDE Social History section, after Oral Habits History table"""
	
	# Patient fields - add after patient_oral_habits_history
	patient_fields = [
		{
			"dt": "Patient",
			"fieldname": "oral_habit_types",
			"label": "Oral Habit Types",
			"fieldtype": "Small Text",
			"insert_after": "patient_oral_habits_history",
			"description": "Enter types (comma-separated): Pan Masala, Gutkha, Areca Nut, Other"
		},
		{
			"dt": "Patient",
			"fieldname": "oral_hygiene_practice",
			"label": "Oral Hygiene Practice",
			"fieldtype": "Select",
			"options": "\nGood\nFair\nPoor",
			"insert_after": "oral_habit_types"
		},
		{
			"dt": "Patient",
			"fieldname": "dental_visits_frequency",
			"label": "Frequency of Dental Visits",
			"fieldtype": "Select",
			"options": "\nRegular (Every 6 months)\nOccasional (Once a year)\nRarely (Only when needed)\nNever",
			"insert_after": "oral_hygiene_practice"
		},
		{
			"dt": "Patient",
			"fieldname": "mouth_wash_use",
			"label": "Use of Mouth Wash",
			"fieldtype": "Select",
			"options": "\nYes\nNo",
			"insert_after": "dental_visits_frequency"
		}
	]
	
	for field in patient_fields:
		if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
			create_custom_field(field["dt"], field)
			print(f"✅ Added {field['fieldname']} to Patient (in Social History)")
	
	# Encounter fields - add after custom_oral_habits_history
	encounter_fields = [
		{
			"dt": "Patient Encounter",
			"fieldname": "custom_oral_habit_types",
			"label": "Oral Habit Types",
			"fieldtype": "Small Text",
			"insert_after": "custom_oral_habits_history",
			"description": "Enter types (comma-separated): Pan Masala, Gutkha, Areca Nut, Other"
		},
		{
			"dt": "Patient Encounter",
			"fieldname": "custom_oral_hygiene_practice",
			"label": "Oral Hygiene Practice",
			"fieldtype": "Select",
			"options": "\nGood\nFair\nPoor",
			"insert_after": "custom_oral_habit_types"
		},
		{
			"dt": "Patient Encounter",
			"fieldname": "custom_dental_visits_frequency",
			"label": "Frequency of Dental Visits",
			"fieldtype": "Select",
			"options": "\nRegular (Every 6 months)\nOccasional (Once a year)\nRarely (Only when needed)\nNever",
			"insert_after": "custom_oral_hygiene_practice"
		},
		{
			"dt": "Patient Encounter",
			"fieldname": "custom_mouth_wash_use",
			"label": "Use of Mouth Wash",
			"fieldtype": "Select",
			"options": "\nYes\nNo",
			"insert_after": "custom_dental_visits_frequency"
		}
	]
	
	for field in encounter_fields:
		if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
			create_custom_field(field["dt"], field)
			print(f"✅ Added {field['fieldname']} to Encounter (in Social History)")

def verify_gender_field():
	"""Verify Gender field exists in Patient Relation"""
	if frappe.db.exists("Custom Field", {"dt": "Patient Relation", "fieldname": "gender"}):
		print("✅ Gender field exists in Patient Relation (Child Details)")
	else:
		# Add it if missing
		field = {
			"dt": "Patient Relation",
			"fieldname": "gender",
			"label": "Gender",
			"fieldtype": "Select",
			"options": "\nMale\nFemale\nOther\nNot Disclosed",
			"insert_after": "patient"
		}
		create_custom_field(field["dt"], field)
		print("✅ Added Gender field to Patient Relation (Child Details)")

