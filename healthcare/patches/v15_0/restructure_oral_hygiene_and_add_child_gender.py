import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	"""
	1. Remove Oral Habits History child table completely
	2. Add Oral Hygiene fields as direct fields on Patient and Encounter (including Type as Multiselect)
	3. Add Gender field to Child Details table
	"""
	try:
		# Step 1: Add Oral Hygiene direct fields (including Type) to Patient and Encounter
		add_oral_hygiene_direct_fields()
		
		# Step 2: Remove Oral Habits History child tables
		remove_oral_habits_child_tables()
		
		# Step 3: Add Gender to Child Details
		add_gender_to_child_details()
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Successfully completed oral hygiene restructure:")
		print("   - Added Oral Hygiene direct fields (including Type) to Patient and Encounter")
		print("   - Removed Oral Habits History child tables")
		print("   - Added Gender field to Child Details")
		
	except Exception as e:
		print(f"❌ Error: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

def add_oral_hygiene_direct_fields():
	"""Add Oral Hygiene fields as direct fields (not child table)"""
	
	# Options for the fields
	type_options = "\nPan Masala\nGutkha\nAreca Nut\nOther"  # Removed Betel Chewing
	hygiene_options = "\nGood\nFair\nPoor"
	dental_visits_options = "\nRegular (Every 6 months)\nOccasional (Once a year)\nRarely (Only when needed)\nNever"
	mouth_wash_options = "\nYes\nNo"
	
	custom_fields = {
		"Patient": [
			{
				"fieldname": "oral_hygiene_section",
				"label": "Oral Hygiene",
				"fieldtype": "Section Break",
				"insert_after": "patient_oral_habits_history",
				"collapsible": 1
			},
			{
				"fieldname": "oral_habit_type",
				"label": "Oral Habit Type",
				"fieldtype": "Small Text",
				"insert_after": "oral_hygiene_section",
				"description": "Enter oral habit types (comma-separated): Pan Masala, Gutkha, Areca Nut, Other"
			},
			{
				"fieldname": "column_break_oral_1",
				"fieldtype": "Column Break",
				"insert_after": "oral_habit_type"
			},
			{
				"fieldname": "oral_hygiene_practice",
				"label": "Oral Hygiene Practice",
				"fieldtype": "Select",
				"options": hygiene_options,
				"insert_after": "column_break_oral_1"
			},
			{
				"fieldname": "column_break_oral_2",
				"fieldtype": "Column Break",
				"insert_after": "oral_hygiene_practice"
			},
			{
				"fieldname": "dental_visits_frequency",
				"label": "Frequency of Dental Visits",
				"fieldtype": "Select",
				"options": dental_visits_options,
				"insert_after": "column_break_oral_2"
			},
			{
				"fieldname": "column_break_oral_3",
				"fieldtype": "Column Break",
				"insert_after": "dental_visits_frequency"
			},
			{
				"fieldname": "mouth_wash_use",
				"label": "Use of Mouth Wash",
				"fieldtype": "Select",
				"options": mouth_wash_options,
				"insert_after": "column_break_oral_3"
			}
		],
		"Patient Encounter": [
			{
				"fieldname": "custom_oral_hygiene_section",
				"label": "Oral Hygiene",
				"fieldtype": "Section Break",
				"insert_after": "custom_oral_habits_history",
				"collapsible": 1
			},
			{
				"fieldname": "custom_oral_habit_type",
				"label": "Oral Habit Type",
				"fieldtype": "Small Text",
				"insert_after": "custom_oral_hygiene_section",
				"description": "Enter oral habit types (comma-separated): Pan Masala, Gutkha, Areca Nut, Other"
			},
			{
				"fieldname": "custom_column_break_oral_1",
				"fieldtype": "Column Break",
				"insert_after": "custom_oral_habit_type"
			},
			{
				"fieldname": "custom_oral_hygiene_practice",
				"label": "Oral Hygiene Practice",
				"fieldtype": "Select",
				"options": hygiene_options,
				"insert_after": "custom_column_break_oral_1"
			},
			{
				"fieldname": "custom_column_break_oral_2",
				"fieldtype": "Column Break",
				"insert_after": "custom_oral_hygiene_practice"
			},
			{
				"fieldname": "custom_dental_visits_frequency",
				"label": "Frequency of Dental Visits",
				"fieldtype": "Select",
				"options": dental_visits_options,
				"insert_after": "custom_column_break_oral_2"
			},
			{
				"fieldname": "custom_column_break_oral_3",
				"fieldtype": "Column Break",
				"insert_after": "custom_dental_visits_frequency"
			},
			{
				"fieldname": "custom_mouth_wash_use",
				"label": "Use of Mouth Wash",
				"fieldtype": "Select",
				"options": mouth_wash_options,
				"insert_after": "custom_column_break_oral_3"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	print("✅ Added Oral Hygiene direct fields (including Type as Multiselect)")

def remove_oral_habits_child_tables():
	"""Remove Oral Habits History child tables from Patient and Encounter"""
	
	# Remove the table fields from Patient and Encounter
	tables_to_remove = [
		("Patient", "patient_oral_habits_history"),  # Note: plural 'habits'
		("Patient Encounter", "custom_oral_habits_history")  # Note: plural 'habits'
	]
	
	for parent_doctype, fieldname in tables_to_remove:
		# Check if custom field exists
		cf_name = frappe.db.get_value("Custom Field", {"dt": parent_doctype, "fieldname": fieldname}, "name")
		if cf_name:
			try:
				frappe.delete_doc("Custom Field", cf_name, force=1)
				print(f"✅ Removed {fieldname} from {parent_doctype}")
			except Exception as e:
				print(f"⚠️  Could not remove {fieldname} from {parent_doctype}: {str(e)}")
		
		# Also check if it's a standard field
		if frappe.db.exists("DocField", {"parent": parent_doctype, "fieldname": fieldname}):
			try:
				frappe.db.sql("""
					DELETE FROM `tabDocField`
					WHERE parent = %s AND fieldname = %s
				""", (parent_doctype, fieldname))
				print(f"✅ Removed standard field {fieldname} from {parent_doctype}")
			except Exception as e:
				print(f"⚠️  Could not remove standard field {fieldname}: {str(e)}")
	
	# Note: We don't delete the child DocTypes themselves as they might have data
	# User can manually delete them from DocType list if needed
	print("✅ Oral Habits History child tables removed from Patient and Encounter")

def add_gender_to_child_details():
	"""Add Gender field to Patient Relation (Child Details) table"""
	
	custom_fields = {
		"Patient Relation": [
			{
				"fieldname": "gender",
				"label": "Gender",
				"fieldtype": "Select",
				"options": "\nMale\nFemale\nOther\nNot Disclosed",
				"insert_after": "patient"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	print("✅ Added Gender field to Patient Relation (Child Details)")
