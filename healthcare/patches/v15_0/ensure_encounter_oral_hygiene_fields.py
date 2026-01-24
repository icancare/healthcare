import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
	"""
	Ensure oral hygiene fields are added to Patient Encounter
	This patch handles cases where custom_oral_habits_history might not exist
	"""
	try:
		# Add fields to Patient Encounter with safe insert_after
		add_encounter_fields_safe()
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Successfully added/verified oral hygiene fields in Patient Encounter")
		
	except Exception as e:
		print(f"❌ Error: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

def add_encounter_fields_safe():
	"""Add fields to Patient Encounter with fallback insert_after logic"""
	
	# Find safe insert_after location
	# Try: custom_oral_habits_history, custom_substance_abuse_history, or last field in social history
	insert_after_field = get_safe_insert_after()
	
	print(f"Using insert_after: {insert_after_field}")
	
	encounter_fields = [
		{
			"dt": "Patient Encounter",
			"fieldname": "custom_oral_habit_types",
			"label": "Oral Habit Types",
			"fieldtype": "Small Text",
			"insert_after": insert_after_field,
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
			print(f"✅ Added {field['fieldname']} to Patient Encounter")
		else:
			print(f"ℹ️  {field['fieldname']} already exists in Patient Encounter")

def get_safe_insert_after():
	"""Find a safe field to insert after in Patient Encounter"""
	# Try multiple options in order of preference
	possible_fields = [
		"custom_oral_habits_history",
		"custom_substance_abuse_history", 
		"custom_alcohol_history",
		"custom_smokeless_tobacco_history",
		"custom_smoking_tobacco_history"
	]
	
	for field in possible_fields:
		# Check if custom field exists
		if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": field}):
			return field
		# Check if standard field exists
		if frappe.db.exists("DocField", {"parent": "Patient Encounter", "fieldname": field}):
			return field
	
	# Fallback: use a field that definitely exists
	return "patient"  # This field always exists in Patient Encounter

