import frappe
from frappe import _

def execute():
	"""
	Simple direct approach:
	1. Add Oral Hygiene fields as direct fields on Patient and Encounter
	2. Add Gender to Child Details
	3. User will manually delete Oral Habits History table from admin
	"""
	try:
		# Step 1: Add fields to Patient
		add_patient_fields()
		
		# Step 2: Add fields to Patient Encounter
		add_encounter_fields()
		
		# Step 3: Add Gender to Patient Relation
		add_gender_field()
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Successfully added oral hygiene direct fields")
		print("✅ Successfully added gender field to Child Details")
		print("⚠️  Please manually delete 'Oral Habits History' table from Patient and Encounter using Customize Form")
		
	except Exception as e:
		print(f"❌ Error: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

def add_patient_fields():
	"""Add fields directly to Patient"""
	from frappe.custom.doctype.custom_field.custom_field import create_custom_field
	
	fields = [
		{
			"dt": "Patient",
			"fieldname": "oral_hygiene_section",
			"label": "Oral Hygiene",
			"fieldtype": "Section Break",
			"insert_after": "patient_oral_habits_history",
			"collapsible": 1
		},
		{
			"dt": "Patient",
			"fieldname": "oral_habit_type",
			"label": "Oral Habit Type",
			"fieldtype": "Small Text",
			"insert_after": "oral_hygiene_section",
			"description": "Enter oral habit types (comma-separated): Pan Masala, Gutkha, Areca Nut, Other"
		},
		{
			"dt": "Patient",
			"fieldname": "column_break_oral_1",
			"fieldtype": "Column Break",
			"insert_after": "oral_habit_type"
		},
		{
			"dt": "Patient",
			"fieldname": "oral_hygiene_practice",
			"label": "Oral Hygiene Practice",
			"fieldtype": "Select",
			"options": "\nGood\nFair\nPoor",
			"insert_after": "column_break_oral_1"
		},
		{
			"dt": "Patient",
			"fieldname": "column_break_oral_2",
			"fieldtype": "Column Break",
			"insert_after": "oral_hygiene_practice"
		},
		{
			"dt": "Patient",
			"fieldname": "dental_visits_frequency",
			"label": "Frequency of Dental Visits",
			"fieldtype": "Select",
			"options": "\nRegular (Every 6 months)\nOccasional (Once a year)\nRarely (Only when needed)\nNever",
			"insert_after": "column_break_oral_2"
		},
		{
			"dt": "Patient",
			"fieldname": "column_break_oral_3",
			"fieldtype": "Column Break",
			"insert_after": "dental_visits_frequency"
		},
		{
			"dt": "Patient",
			"fieldname": "mouth_wash_use",
			"label": "Use of Mouth Wash",
			"fieldtype": "Select",
			"options": "\nYes\nNo",
			"insert_after": "column_break_oral_3"
		}
	]
	
	for field in fields:
		if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
			create_custom_field(field["dt"], field)
			print(f"✅ Added {field['fieldname']} to Patient")

def add_encounter_fields():
	"""Add fields directly to Patient Encounter"""
	from frappe.custom.doctype.custom_field.custom_field import create_custom_field
	
	fields = [
		{
			"dt": "Patient Encounter",
			"fieldname": "custom_oral_hygiene_section",
			"label": "Oral Hygiene",
			"fieldtype": "Section Break",
			"insert_after": "custom_oral_habits_history",
			"collapsible": 1
		},
		{
			"dt": "Patient Encounter",
			"fieldname": "custom_oral_habit_type",
			"label": "Oral Habit Type",
			"fieldtype": "Small Text",
			"insert_after": "custom_oral_hygiene_section",
			"description": "Enter oral habit types (comma-separated): Pan Masala, Gutkha, Areca Nut, Other"
		},
		{
			"dt": "Patient Encounter",
			"fieldname": "custom_column_break_oral_1",
			"fieldtype": "Column Break",
			"insert_after": "custom_oral_habit_type"
		},
		{
			"dt": "Patient Encounter",
			"fieldname": "custom_oral_hygiene_practice",
			"label": "Oral Hygiene Practice",
			"fieldtype": "Select",
			"options": "\nGood\nFair\nPoor",
			"insert_after": "custom_column_break_oral_1"
		},
		{
			"dt": "Patient Encounter",
			"fieldname": "custom_column_break_oral_2",
			"fieldtype": "Column Break",
			"insert_after": "custom_oral_hygiene_practice"
		},
		{
			"dt": "Patient Encounter",
			"fieldname": "custom_dental_visits_frequency",
			"label": "Frequency of Dental Visits",
			"fieldtype": "Select",
			"options": "\nRegular (Every 6 months)\nOccasional (Once a year)\nRarely (Only when needed)\nNever",
			"insert_after": "custom_column_break_oral_2"
		},
		{
			"dt": "Patient Encounter",
			"fieldname": "custom_column_break_oral_3",
			"fieldtype": "Column Break",
			"insert_after": "custom_dental_visits_frequency"
		},
		{
			"dt": "Patient Encounter",
			"fieldname": "custom_mouth_wash_use",
			"label": "Use of Mouth Wash",
			"fieldtype": "Select",
			"options": "\nYes\nNo",
			"insert_after": "custom_column_break_oral_3"
		}
	]
	
	for field in fields:
		if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
			create_custom_field(field["dt"], field)
			print(f"✅ Added {field['fieldname']} to Patient Encounter")

def add_gender_field():
	"""Add Gender to Patient Relation (Child Details)"""
	from frappe.custom.doctype.custom_field.custom_field import create_custom_field
	
	field = {
		"dt": "Patient Relation",
		"fieldname": "gender",
		"label": "Gender",
		"fieldtype": "Select",
		"options": "\nMale\nFemale\nOther\nNot Disclosed",
		"insert_after": "patient"
	}
	
	if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
		create_custom_field(field["dt"], field)
		print(f"✅ Added gender field to Patient Relation")

