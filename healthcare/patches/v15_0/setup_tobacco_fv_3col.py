
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
	print("\nSetting up Tobacco First Visit (3-Column Layout)...")
	
	# 1. Cleanup old fields first to avoid collisions/ordering issues
	cleanup_fields()
	
	# 2. Create Section and Columns
	create_layout()
	
	# 3. Create Follow-up Fields (Standard layout)
	# create_followup_fields() # Keeping them basic for now or as per previous
	
	frappe.db.commit()
	frappe.clear_cache()
	print("\nLayout Setup Complete!")

def cleanup_fields():
	print("  Deleting old tobacco_fv_ fields...")
	fields = frappe.get_all("Custom Field", filters=[["dt", "=", "Patient Encounter"], ["fieldname", "like", "tobacco_fv_%"]], pluck="name")
	for f in fields:
		frappe.delete_doc("Custom Field", f, force=True)

def create_layout():
	fv_logic = "eval:doc.practitioner && doc.exam_examination_template && doc.exam_examination_template.includes('Quit Tobacco First Visit')"
	
	# Main Section
	create_custom_field("Patient Encounter", {
		"fieldname": "tobacco_fv_section",
		"label": "Tobacco Cessation - First Visit",
		"fieldtype": "Section Break",
		"insert_after": "exam_examination_template",
		"depends_on": fv_logic,
		"collapsible": 0
	})
	
	# --- COLUMN 1: QUESTIONS ---
	create_custom_field("Patient Encounter", {
		"fieldname": "tobacco_fv_col1_header",
		"fieldtype": "HTML",
		"label": "Criteria Header",
		"options": "<div style='font-weight: bold; margin-bottom: 10px; height: 20px;'>Criteria / Question</div>",
		"insert_after": "tobacco_fv_section"
	})
	
	questions = get_questions()
	prev_field = "tobacco_fv_col1_header"
	
	for i, q in enumerate(questions):
		fieldname_text = f"tobacco_fv_q{i+1}_text"
		# Using fixed height to match form controls (approx 36px + 10px margin = ~46px)
		# Standard control height is ~30px, margin-bottom 15px. Total ~45px.
		# Let's try 40px?
		html_content = f"<div style='height: 28px; display: flex; align-items: center; margin-top: 5px; font-size: 13px;'>{q[1]}</div>"
		
		create_custom_field("Patient Encounter", {
			"fieldname": fieldname_text,
			"fieldtype": "HTML",
			"label": "", # Hidden Label
			"options": html_content,
			"insert_after": prev_field
		})
		prev_field = fieldname_text

	# --- COLUMN 2: RESPONSE OPTIONS ---
	create_custom_field("Patient Encounter", {
		"fieldname": "tobacco_fv_col2_break",
		"fieldtype": "Column Break",
		"insert_after": prev_field
	})
	
	create_custom_field("Patient Encounter", {
		"fieldname": "tobacco_fv_col2_header",
		"fieldtype": "HTML",
		"label": "Response Header",
		"options": "<div style='font-weight: bold; margin-bottom: 10px; height: 20px;'>Response Options</div>",
		"insert_after": "tobacco_fv_col2_break"
	})
	
	prev_field = "tobacco_fv_col2_header"
	for i, q in enumerate(questions):
		fieldname_select = f"tobacco_fv_q{i+1}"
		create_custom_field("Patient Encounter", {
			"fieldname": fieldname_select,
			"fieldtype": "Select",
			"label": " ", # Space to hide label but keep alignment space? No, label takes vertical space.
			# If we want alignment with the HTML col, we should hide the label completely.
			# But " " still renders a label block.
			# We can use "hidden_label" property? No such property.
			# We'll use a blank label and hope. OR inject CSS to hide these labels.
			"options": q[2],
			"insert_after": prev_field
		})
		prev_field = fieldname_select

	# --- COLUMN 3: SCORES ---
	create_custom_field("Patient Encounter", {
		"fieldname": "tobacco_fv_col3_break",
		"fieldtype": "Column Break",
		"insert_after": prev_field
	})
	
	create_custom_field("Patient Encounter", {
		"fieldname": "tobacco_fv_col3_header",
		"fieldtype": "HTML",
		"label": "Score Header",
		"options": "<div style='font-weight: bold; margin-bottom: 10px; height: 20px;'>Score</div>",
		"insert_after": "tobacco_fv_col3_break"
	})
	
	prev_field = "tobacco_fv_col3_header"
	for i, q in enumerate(questions):
		fieldname_score = f"tobacco_fv_q{i+1}_score"
		create_custom_field("Patient Encounter", {
			"fieldname": fieldname_score,
			"fieldtype": "Int",
			"label": " ",
			"read_only": 1,
			"default": 0,
			"insert_after": prev_field
		})
		prev_field = fieldname_score
		
	# --- Footer: Total Score ---
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
