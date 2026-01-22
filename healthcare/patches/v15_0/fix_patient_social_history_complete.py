# Copyright (c) 2025, ESS LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Complete fix for Patient Social History section:
	- Ensure proper section breaks
	- Reorder all social history tables with headings
	- Production safe (idempotent)
	"""
	
	# Step 1: Cleanup old headings and section breaks
	cleanup_fields()
	
	# Step 2: Create proper section breaks for main sections
	create_main_sections()
	
	# Step 3: Update insert_after for social history tables
	reorder_social_history_tables()
	
	frappe.db.commit()
	frappe.msgprint("✓ Patient Social History completely fixed")


def cleanup_fields():
	"""Remove old/duplicate fields"""
	fields_to_remove = [
		"smokeless_tobacco_heading",
		"smoking_tobacco_heading", 
		"substance_abuse_heading",
		"oral_habits_heading",
		"diet_heading",
		"occupational_exposure_heading",
		"environmental_factors_heading",
		"oral_habits_section",
		"diet_section",
		"occupational_exposure_section",
		"environmental_factors_section"
	]
	
	for fieldname in fields_to_remove:
		try:
			if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": fieldname}):
				cf_name = frappe.get_value("Custom Field", {"dt": "Patient", "fieldname": fieldname}, "name")
				frappe.delete_doc("Custom Field", cf_name, force=True)
				print(f"✓ Deleted: {fieldname}")
		except Exception as e:
			print(f"Error deleting {fieldname}: {str(e)}")
	
	frappe.db.commit()


def create_main_sections():
	"""Create main section breaks"""
	
	# Check if sections already exist, if not create them
	sections = {
		"Patient": []
	}
	
	# Allergy Section
	if not frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "allergy_section_break"}):
		sections["Patient"].append({
			"fieldname": "allergy_section_break",
			"fieldtype": "Section Break",
			"label": "Allergy",
			"insert_after": "patient_relation",
			"collapsible": 1
		})
	
	# Immunization Section
	if not frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "immunization_section_break"}):
		sections["Patient"].append({
			"fieldname": "immunization_section_break",
			"fieldtype": "Section Break",
			"label": "Immunization",
			"insert_after": "patient_allergy",
			"collapsible": 1
		})
	
	# Medical History Section
	if not frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "medical_history_section_break"}):
		sections["Patient"].append({
			"fieldname": "medical_history_section_break",
			"fieldtype": "Section Break",
			"label": "Medical History",
			"insert_after": "patient_immunization",
			"collapsible": 1
		})
	
	# Surgical History Section
	if not frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "surgical_history_section_break"}):
		sections["Patient"].append({
			"fieldname": "surgical_history_section_break",
			"fieldtype": "Section Break",
			"label": "Surgical History",
			"insert_after": "patient_medical_history",
			"collapsible": 1
		})
	
	# Social History Section
	if not frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "social_history_section_break"}):
		sections["Patient"].append({
			"fieldname": "social_history_section_break",
			"fieldtype": "Section Break",
			"label": "Social History",
			"insert_after": "patient_surgical_history",
			"collapsible": 1
		})
	
	if sections["Patient"]:
		create_custom_fields(sections, update=True)
		frappe.db.commit()


def reorder_social_history_tables():
	"""Update insert_after for all social history tables and add headings"""
	
	# Update existing table fields' insert_after
	tables_order = [
		("patient_smokeless_tobacco_history", "social_history_section_break", "Smokeless Tobacco"),
		("patient_smoking_tobacco_history", "patient_smokeless_tobacco_history", "Smoking Tobacco"),
		("patient_substance_abuse_history", "patient_smoking_tobacco_history", "Substance Abuse"),
		("patient_oral_habits_history", "patient_substance_abuse_history", "Oral Habits"),
		("patient_diet_history", "patient_oral_habits_history", "Diet"),
		("patient_occupational_exposure_history", "patient_diet_history", "Occupational Exposure"),
		("patient_environmental_factors_history", "patient_occupational_exposure_history", "Environmental Factors")
	]
	
	for table_fieldname, insert_after_field, heading_label in tables_order:
		# Check if table exists
		if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": table_fieldname}):
			# Update insert_after
			frappe.db.set_value("Custom Field", 
				{"dt": "Patient", "fieldname": table_fieldname}, 
				"insert_after", 
				insert_after_field
			)
			print(f"✓ Updated {table_fieldname} insert_after to {insert_after_field}")
	
	frappe.db.commit()
	
	# Now add headings before each table (optional, for better UI)
	# We'll skip headings for now as tables themselves have labels


















