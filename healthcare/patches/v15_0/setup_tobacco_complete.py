
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
	print("\nSetting up Tobacco Cessation Complete (Grid Layout + Follow-up)...")
	
	# 1. Cleanup ALL old tobacco fields
	cleanup_fields()
	
	# 2. Create First Visit Grid Layout
	create_first_visit_grid()
	
	# 3. Create Follow-up Fields
	create_followup_fields()
	
	frappe.db.commit()
	frappe.clear_cache()
	print("\nTobacco Cessation Setup Complete!")

def cleanup_fields():
	print("  Deleting ALL old tobacco_ fields...")
	# Filter broadly for any field starting with tobacco_
	fields = frappe.get_all("Custom Field", filters=[["dt", "=", "Patient Encounter"], ["fieldname", "like", "tobacco_%"]], pluck="name")
	for f in fields:
		frappe.delete_doc("Custom Field", f, force=True)
	print(f"  ✓ Deleted {len(fields)} fields.")

def create_first_visit_grid():
	fv_logic = "eval:doc.practitioner && doc.exam_examination_template && doc.exam_examination_template.includes('Quit Tobacco First Visit')"
	
	# Main Section - Step 1
	create_custom_field("Patient Encounter", {
		"fieldname": "tobacco_fv_section",
		"label": "Step 1: Addiction Assessment Questionnaire",
		"fieldtype": "Section Break",
		"insert_after": "exam_examination_template",
		"depends_on": fv_logic,
		"collapsible": 0
	})
	
	# Header Row (HTML)
	header_html = """
	<div style="display: flex; font-weight: bold; padding-bottom: 5px; border-bottom: 1px solid var(--border-color); margin-bottom: 10px;">
		<div style="flex: 4; padding-right: 10px;">Criteria / Question</div>
		<div style="flex: 3; padding-right: 10px;">Response Options</div>
		<div style="flex: 2; padding-right: 10px;">Score</div>
		<div style="flex: 3;">Computed Value (History)</div>
	</div>
	"""
	create_custom_field("Patient Encounter", {
		"fieldname": "tobacco_fv_header",
		"fieldtype": "HTML",
		"label": "Headers",
		"options": header_html,
		"insert_after": "tobacco_fv_section"
	})
	
	questions = get_questions()
	prev_field = "tobacco_fv_header"
	
	for i, q in enumerate(questions):
		idx = i + 1
		f_text = f"tobacco_fv_q{idx}_text"
		f_select = f"tobacco_fv_q{idx}"
		f_score = f"tobacco_fv_q{idx}_score"
		f_computed = f"tobacco_fv_q{idx}_computed"
		
		# 1. Question Text (Read Only Data) - Cols: 4
		create_custom_field("Patient Encounter", {
			"fieldname": f_text,
			"fieldtype": "Small Text",
			"label": " ", 
			"default": q[1], 
			"read_only": 1,
			"columns": 4,
			"insert_after": prev_field
		})
		
		# 2. Response Options (Select) - Cols: 3
		create_custom_field("Patient Encounter", {
			"fieldname": f_select,
			"fieldtype": "Select",
			"label": " ",
			"options": q[2],
			"columns": 3,
			"insert_after": f_text
		})
		
		# 3. Score (Int) - Cols: 2
		create_custom_field("Patient Encounter", {
			"fieldname": f_score,
			"fieldtype": "Int",
			"label": " ",
			"read_only": 1,
			"default": 0,
			"columns": 2,
			"insert_after": f_select
		})
		
		# 4. Computed Value (Data) - Cols: 3
		create_custom_field("Patient Encounter", {
			"fieldname": f_computed,
			"fieldtype": "Small Text",
			"label": " ",
			"read_only": 1,
			"columns": 3,
			"insert_after": f_score
		})
		
		prev_field = f_computed

	# Footer
	create_custom_field("Patient Encounter", {
		"fieldname": "tobacco_fv_footer_section",
		"fieldtype": "Section Break",
		"label": "",
		"insert_after": prev_field
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
	
	print("  ✓ Created Step 1 Grid Layout.")

def create_followup_fields():
	fu_logic = "eval:doc.practitioner && doc.exam_examination_template && doc.exam_examination_template.includes('Quit Tobacco Follow-up Visit')"
	
	# Insert after FV section
	prev_field = "tobacco_fv_addiction_level"
	
	fields = [
		{
			"fieldname": "tobacco_fu_section",
			"label": "Tobacco Cessation - Follow-up Visit",
			"fieldtype": "Section Break",
			"depends_on": fu_logic,
			"collapsible": 0
		},
		{
			"fieldname": "tobacco_fu_visit_mode",
			"label": "Mode",
			"fieldtype": "Select",
			"options": "Online\nIn clinic",
			"default": "Online",
			"reqd": 1
		},
		{
			"fieldname": "tobacco_fu_col_break",
			"fieldtype": "Column Break"
		},
		{
			"fieldname": "tobacco_fu_date",
			"label": "Quit Date", 
			"fieldtype": "Date"
		},
		# Consumption
		{
			"fieldname": "tobacco_fu_consumption_section",
			"label": "Consumption Details",
			"fieldtype": "Section Break",
			"depends_on": fu_logic
		},
		{
			"fieldname": "tobacco_fu_smoking_history",
			"label": "Smoking Consumption",
			"fieldtype": "Table",
			"options": "Patient Smoking Tobacco History"
		},
		{
			"fieldname": "tobacco_fu_smokeless_history",
			"label": "Smokeless Consumption",
			"fieldtype": "Table",
			"options": "Patient Smokeless Tobacco History"
		},
		# Status
		{
			"fieldname": "tobacco_fu_status_section",
			"label": "Quit Status",
			"fieldtype": "Section Break",
			"depends_on": fu_logic
		},
		{
			"fieldname": "tobacco_fu_stuck_to_quit",
			"label": "Has the patient stuck to the quit date?",
			"fieldtype": "Select",
			"options": "Yes\nNo",
			"reqd": 1
		},
		{
			"fieldname": "tobacco_fu_reason_delay",
			"label": "Reason for delay",
			"fieldtype": "Small Text",
			"depends_on": "eval:doc.tobacco_fu_stuck_to_quit=='No'"
		},
		# QOL
		{
			"fieldname": "tobacco_fu_qol_section",
			"label": "Quality of Life Assessment",
			"fieldtype": "Section Break",
			"depends_on": fu_logic
		},
		{
			"fieldname": "tobacco_fu_qol_score",
			"label": "QOL Score (1-10)",
			"fieldtype": "Int"
		},
		{
			"fieldname": "tobacco_fu_emotional_score",
			"label": "Emotional Well Being Score (1-10)",
			"fieldtype": "Int"
		},
		{
			"fieldname": "tobacco_fu_feeling_score",
			"label": "Overall Feeling Score (1-10)",
			"fieldtype": "Int"
		}
	]
	
	for f in fields:
		f["insert_after"] = prev_field
		create_custom_field("Patient Encounter", f)
		prev_field = f["fieldname"]
		
	print("  ✓ Created Follow-up Fields.")

def get_questions():
	return [
		("q1", "1. Age of starting tobacco use", "Under 18 years\n18-24 years\nOver 24 years"),
		("q2", "2. Years using tobacco", "Less than 5 years\n5-10 years\n10-20 years\nMore than 20 years"),
		("q3", "3. Number of quit attempts", "None\nLess than 3 times\n3-5 times\nMore than 5 times"),
		("q4", "4. Longest period of quitting", "More than 1 year\n1 month – 1 year\n6-30 days\nLess than 5 days"),
		("q5", "5. Hard to quit?", "Yes\nNo"),
		("q6", "6. Doctor advised to quit?", "Yes\nNo"),
		("q7", "7. Previous reasons for relapse", "Withdrawals or Cravings\nMedications didn't work\nNo/Inadequate Guidance\nSelf-initiated relapse\nSocial Influence\nNo relapse experience"),
		("q8", "8. Alternating smoking/chewing", "Using both at present\nChewing to smoking\nSmoking to chewing\nNot Alternating"),
		("q9", "9. Smoking qty/day", "None\nLess than 10\n11-20\n21-30\nMore than 31"),
		("q10", "10. Chewing pouches/day", "None\nLess than 1\n1-3\nMore than 3"),
		("q11", "11. Use after waking", "Within 5 minutes\n6-30 minutes\n31-60 minutes\nMore than 60 minutes"),
		("q12", "12. Severe craving?", "Yes\nNo"),
		("q13", "13. Hard to avoid where prohibited?", "Yes\nNo"),
		("q14", "14. Diff. concentrating?", "Yes\nNo"),
		("q15", "15. Reach without thinking?", "Yes\nNo")
	]
