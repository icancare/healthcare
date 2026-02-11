
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
	print("\nRestoring Tobacco Follow-up Fields...")
	create_followup_fields()
	frappe.db.commit()
	frappe.clear_cache()
	print("\nFollow-up Fields Restored!")

def create_followup_fields():
	fu_logic = "eval:doc.practitioner && doc.exam_examination_template && doc.exam_examination_template.includes('Quit Tobacco Follow-up Visit')"
	
	# We need to insert after the last field of First Visit or just after template if FV is hidden.
	# But Custom Field 'insert_after' is relative.
	# The last FV field was 'tobacco_fv_addiction_level'.
	
	fields = [
		{
			"fieldname": "tobacco_fu_section",
			"label": "Tobacco Cessation - Follow-up Visit",
			"fieldtype": "Section Break",
			"insert_after": "tobacco_fv_addiction_level", 
			"depends_on": fu_logic,
			"collapsible": 0
		},
		{
			"fieldname": "tobacco_fu_visit_mode",
			"label": "Mode",
			"fieldtype": "Select",
			"options": "Online\nIn clinic",
			"default": "Online",
			"insert_after": "tobacco_fu_section",
			"reqd": 1
		},
		{
			"fieldname": "tobacco_fu_col_break",
			"fieldtype": "Column Break",
			"insert_after": "tobacco_fu_visit_mode"
		},
		{
			"fieldname": "tobacco_fu_date",
			"label": "Quit Date", 
			"fieldtype": "Date", 
			"insert_after": "tobacco_fu_col_break"
		},
		# Consumption Sections
		{
			"fieldname": "tobacco_fu_consumption_section",
			"label": "Consumption Details",
			"fieldtype": "Section Break",
			"insert_after": "tobacco_fu_date",
			"depends_on": fu_logic
		},
		{
			"fieldname": "tobacco_fu_smoking_history",
			"label": "Smoking Consumption",
			"fieldtype": "Table",
			"options": "Patient Smoking Tobacco History",
			"insert_after": "tobacco_fu_consumption_section"
		},
		{
			"fieldname": "tobacco_fu_smokeless_history",
			"label": "Smokeless Consumption",
			"fieldtype": "Table",
			"options": "Patient Smokeless Tobacco History",
			"insert_after": "tobacco_fu_smoking_history"
		},
		# Status Section
		{
			"fieldname": "tobacco_fu_status_section",
			"label": "Quit Status",
			"fieldtype": "Section Break",
			"insert_after": "tobacco_fu_smokeless_history",
			"depends_on": fu_logic
		},
		{
			"fieldname": "tobacco_fu_stuck_to_quit",
			"label": "Has the patient stuck to the quit date?",
			"fieldtype": "Select",
			"options": "Yes\nNo",
			"insert_after": "tobacco_fu_status_section",
			"reqd": 1
		},
		{
			"fieldname": "tobacco_fu_reason_delay",
			"label": "Reason for delay",
			"fieldtype": "Small Text",
			"insert_after": "tobacco_fu_stuck_to_quit",
			"depends_on": "eval:doc.tobacco_fu_stuck_to_quit=='No'"
		},
		# QOL Section
		{
			"fieldname": "tobacco_fu_qol_section",
			"label": "Quality of Life Assessment",
			"fieldtype": "Section Break",
			"insert_after": "tobacco_fu_reason_delay",
			"depends_on": fu_logic
		},
		{
			"fieldname": "tobacco_fu_qol_score",
			"label": "QOL Score (1-10)",
			"fieldtype": "Int",
			"insert_after": "tobacco_fu_qol_section"
		},
		{
			"fieldname": "tobacco_fu_emotional_score",
			"label": "Emotional Well Being Score (1-10)",
			"fieldtype": "Int",
			"insert_after": "tobacco_fu_qol_score"
		},
		{
			"fieldname": "tobacco_fu_feeling_score",
			"label": "Overall Feeling Score (1-10)",
			"fieldtype": "Int",
			"insert_after": "tobacco_fu_emotional_score"
		}
	]
	
	for f in fields:
		try:
			create_custom_field("Patient Encounter", f)
			print(f"✓ Created: {f['fieldname']}")
		except Exception as e:
			print(f"⚠ Error creating {f['fieldname']}: {e}")
