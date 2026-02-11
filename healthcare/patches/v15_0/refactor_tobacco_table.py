
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
	print("\nRefactoring to Child Table for Perfect Grid Layout...")
	
	# 1. Create Child Doctype
	create_child_doctype()
	
	# 2. Cleanup old fields (Again) and Add Table Field
	update_parent_doctype()
	
	frappe.db.commit()
	frappe.clear_cache()
	print("\nRefactor Complete!")

def create_child_doctype():
	dt_name = "Tobacco Service Question"
	if not frappe.db.exists("DocType", dt_name):
		doc = frappe.get_doc({
			"doctype": "DocType",
			"module": "Healthcare",
			"custom": 1,
			"name": dt_name,
			"istable": 1,
			"editable_grid": 1,
			"fields": [
				{
					"fieldname": "question_text",
					"fieldtype": "Data", # or Small Text
					"label": "Criteria / Question",
					"reqd": 1,
					"read_only": 1,
					"in_list_view": 1,
					"columns": 4
				},
				{
					"fieldname": "response",
					"fieldtype": "Select",
					"label": "Response",
					"options": " \n", # Will be set dynamically row by row or generic set?
					# Issues: Different questions have DIFFERENT options.
					# Select field in Child Table shares Options across rows unless we use "Link" or dynamic.
					# Standard 'Select' options are static per DocType.
					# WORKAROUND: Include ALL possible options in the list?
					# OR: Use "Data" field and provide options via JS (Autocomplete)?
					# If we use Select with ALL options, it's messy.
					# "Under 18 years", "Less than 5 years", "Yes", "No"...
					# It's fine to have a superset list.
					"in_list_view": 1,
					"columns": 3
				},
				{
					"fieldname": "score",
					"fieldtype": "Int",
					"label": "Score",
					"read_only": 1,
					"in_list_view": 1,
					"columns": 1
				},
				{
					"fieldname": "computed_value",
					"fieldtype": "Data",
					"label": "History",
					"read_only": 1,
					"in_list_view": 1,
					"columns": 3
				},
				{
					"fieldname": "question_id", # Hidden ID to map logic (q1, q2...)
					"fieldtype": "Data",
					"hidden": 1
				}
			]
		})
		doc.insert(ignore_permissions=True)
		print("  ✓ Created Child Doctype: Tobacco Service Question")
	else:
		# Update options if needed
		pass

def update_parent_doctype():
	# Cleanup only FV grid fields
	cleanup_fields()
	
	fv_logic = "eval:doc.practitioner && doc.exam_examination_template && doc.exam_examination_template.includes('Quit Tobacco First Visit')"
	
	# Create Section
	create_custom_field("Patient Encounter", {
		"fieldname": "tobacco_fv_section",
		"label": "Step 1: Addiction Assessment Questionnaire",
		"fieldtype": "Section Break",
		"insert_after": "exam_examination_template",
		"depends_on": fv_logic,
		"collapsible": 0
	})
	
	# Create Table Field
	create_custom_field("Patient Encounter", {
		"fieldname": "tobacco_fv_questions",
		"label": "Questions",
		"fieldtype": "Table",
		"options": "Tobacco Service Question",
		"insert_after": "tobacco_fv_section",
		"depends_on": fv_logic
	})
	
	# Footer Scores
	create_custom_field("Patient Encounter", {
		"fieldname": "tobacco_fv_footer_section",
		"fieldtype": "Section Break",
		"label": "",
		"insert_after": "tobacco_fv_questions"
	})
	
	create_custom_field("Patient Encounter", {
		"fieldname": "tobacco_fv_total_score",
		"label": "Total Addiction Score",
		"fieldtype": "Int",
		"read_only": 1,
		"insert_after": "tobacco_fv_footer_section"
	})
	
	create_custom_field("Patient Encounter", {
		"fieldname": "tobacco_fv_addiction_level",
		"label": "Addiction Level",
		"fieldtype": "HTML",
		"insert_after": "tobacco_fv_total_score"
	})

def cleanup_fields():
	# Delete the 60+ fields we made
	fields = frappe.get_all("Custom Field", filters=[["dt", "=", "Patient Encounter"], ["fieldname", "like", "tobacco_fv_q%"]], pluck="name")
	for f in fields:
		frappe.delete_doc("Custom Field", f, force=True)
		
	# Also delete the header html fields
	frappe.delete_doc("Custom Field", "tobacco_fv_header", force=True) 

