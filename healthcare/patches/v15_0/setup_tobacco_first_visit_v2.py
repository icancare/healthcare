
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
	print("\nCreating New Tobacco Cessation Fields (First Visit v2 + Follow-up)...")
	
	create_first_visit_fields()
	create_followup_fields()
	
	frappe.db.commit()
	frappe.clear_cache()
	print("\nFields Created Successfully!")


def create_first_visit_fields():
	fv_logic = "eval:doc.practitioner && doc.exam_examination_template && doc.exam_examination_template.includes('Quit Tobacco First Visit')"
	
	fields = [
		{
			"fieldname": "tobacco_fv_section",
			"label": "Tobacco Cessation - First Visit",
			"fieldtype": "Section Break",
			"insert_after": "exam_examination_template",
			"depends_on": fv_logic,
			"collapsible": 0
		},
		{
			"fieldname": "tobacco_fv_header",
			"fieldtype": "HTML",
			"label": "Addiction Assessment Questionnaire",
			"options": "<div style='background-color: var(--bg-color); padding: 10px; font-weight: bold; border-bottom: 1px solid var(--border-color); display: flex;'><div style='flex: 3;'>Criteria / Question</div><div style='flex: 1; text-align: center;'>Score</div></div>",
			"insert_after": "tobacco_fv_section"
		}
	]
	
	# Questions List
	# Format: (fieldname, label, options, description)
	questions = [
		("tobacco_fv_q1", "1. Age of starting tobacco use (Computed)", 
		 "Under 18 years\n18-24 years\nOver 24 years", 
		 "(Calculation: take earliest age of smoking or smokeless tobacco)"),
		 
		("tobacco_fv_q2", "2. Number of years using tobacco (Computed)", 
		 "Less than 5 years\n5-10 years\n10-20 years\nMore than 20 years", 
		 "(Calculation: take latest age - earliest age)"),
		 
		("tobacco_fv_q3", "3. Number of quit attempts", 
		 "None\nLess than 3 times\n3-5 times\nMore than 5 times", ""),
		 
		("tobacco_fv_q4", "4. Longest period of quitting", 
		 "More than 1 year\n1 month – 1 year\n6-30 days\nLess than 5 days", ""),
		 
		("tobacco_fv_q5", "5. Do you smoke/chew/vape because it's hard to quit?", 
		 "Yes\nNo", ""),
		 
		("tobacco_fv_q6", "6. Has the doctor advised you to quit due to medical issues?", 
		 "Yes\nNo", ""),
		 
		("tobacco_fv_q7", "7. Previous reasons for relapse (Highest Score Taken)", 
		 "Withdrawals or Cravings\nMedications didn't work\nNo/Inadequate Guidance\nSelf-initiated relapse\nSocial Influence\nNo relapse experience", 
		 "Select the primary reason or highest scoring factor"),
		 
		("tobacco_fv_q8", "8. Alternating between smoking and chewing", 
		 "Using both at present\nChewing to smoking\nSmoking to chewing\nNot Alternating", ""),
		 
		("tobacco_fv_q9", "9. How many cigarettes/bidis/hukkah/vapes per day? (Computed)", 
		 "None\nLess than 10\n11-20\n21-30\nMore than 31", ""),
		 
		("tobacco_fv_q10", "10. How many pouches of chewing tobacco per day? (Computed)", 
		 "None\nLess than 1\n1-3\nMore than 3", 
		 "(1 pouch = 1 Gram approx)"),
		 
		("tobacco_fv_q11", "11. How soon after waking do you use tobacco?", 
		 "Within 5 minutes\n6-30 minutes\n31-60 minutes\nMore than 60 minutes", ""),
		 
		("tobacco_fv_q12", "12. Ever felt a strong need for tobacco/vape? Severe craving one cannot stop", 
		 "Yes\nNo", ""),
		 
		("tobacco_fv_q13", "13. Is it hard for you to avoid tobacco where it's prohibited?", 
		 "Yes\nNo", ""),
		 
		("tobacco_fv_q14", "14. Do you experience difficulty concentrating without tobacco?", 
		 "Yes\nNo", ""),
		 
		("tobacco_fv_q15", "15. Do you reach for tobacco without thinking?", 
		 "Yes\nNo", "")
	]
	
	prev_field = "tobacco_fv_header"
	
	for i, q in enumerate(questions):
		fieldname_q = q[0]
		label_q = q[1]
		options_q = q[2]
		desc_q = q[3]
		fieldname_s = f"{fieldname_q}_score"
		
		# Question Field (Select)
		fields.append({
			"fieldname": fieldname_q,
			"label": label_q,
			"fieldtype": "Select",
			"options": options_q,
			"description": desc_q,
			"insert_after": prev_field,
			"columns": 8 # Trying to influence width if possible, but standard is 6
		})
		
		# Score Field (Int, Read Only)
		fields.append({
			"fieldname": fieldname_s,
			"label": "Score",
			"fieldtype": "Int",
			"read_only": 1,
			"default": 0,
			"insert_after": fieldname_q,
			"columns": 4
		})
		
		# Add a Section Break (Empty) to force new row? No, ERPNext wraps automatically at 12 cols.
		# Default col is 6. So Q (6) + Score (6) = 12 (Full Row). This is PERFECT.
		
		prev_field = fieldname_s
		
	# Total Score
	fields.append({
		"fieldname": "tobacco_fv_total_score_section",
		"fieldtype": "Section Break",
		"label": "",
		"insert_after": prev_field
	})
	
	fields.append({
		"fieldname": "tobacco_fv_total_score",
		"label": "Total Addiction Score",
		"fieldtype": "Int",
		"read_only": 1,
		"insert_after": "tobacco_fv_total_score_section"
	})
	
	fields.append({
		"fieldname": "tobacco_fv_addiction_level",
		"label": "Addiction Level",
		"fieldtype": "Data", # Or HTML for color
		"read_only": 1,
		"insert_after": "tobacco_fv_total_score"
	})

	for f in fields:
		create_custom_field("Patient Encounter", f)
		print(f"✓ Created: {f['fieldname']}")


def create_followup_fields():
	# Recreating the Follow-up fields as they were (renamed to avoid conflict if any partials exist, but we wiped them)
	# Using 'tobacco_fu_' prefix for clarity
	
	fu_logic = "eval:doc.practitioner && doc.exam_examination_template && doc.exam_examination_template.includes('Quit Tobacco Follow-up Visit')"
	
	fields = [
		{
			"fieldname": "tobacco_fu_section",
			"label": "Tobacco Cessation - Follow-up Visit",
			"fieldtype": "Section Break",
			"insert_after": "tobacco_fv_addiction_level", # After FV section
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
			"label": "Quit Date", # If they quit? Or follow up date? Assuming standard Quit Date tracking
			"fieldtype": "Date", 
			"insert_after": "tobacco_fu_col_break"
		},
		# Consumption Sections
		{
			"fieldname": "tobacco_fu_consumption_section",
			"label": "Consumption Details",
			"fieldtype": "Section Break",
			"insert_after": "tobacco_fu_date",
			"depends_on": fu_logic # Explicit logic again to be safe
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
		create_custom_field("Patient Encounter", f)
		print(f"✓ Created: {f['fieldname']}")
