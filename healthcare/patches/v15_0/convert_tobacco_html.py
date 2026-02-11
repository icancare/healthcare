
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
	print("\nRemoving field labels to fix alignment...")

	# We need to hide labels for fields in the grid to make them align with headers.
	# We can't set "hidden_label" in standard Custom Field.
	# But we can set label to " " (space) which we did.
	# The issue is likely that "Data" or "Small Text" fields render differently than "Select".
	# Or the User is seeing them stacked?
	
	# If stacked: columns property is failing?
	# Standard Form: If screen width is small, it stacks.
	# But if desktop, it should flow.
	# UNLESS: Section Break has 'collapsible' or something executing.
	
	# Strategy:
	# 1. Ensure columns add up to 12.
	# 2. Add "Column Break" field to force column? No, standard grid doesn't use col break for 12-grid system.
	
	# The User image shows:
	# Question Text (Full Width?)
	# Select (Full Width?)
	# Score (Full Width?)
	# Computed (Full Width?)
	# They are stacked vertically! This means columns=4 etc is ignored.
	
	# Why ignored?
	# In standard Frappe, fields ONLY flow in grid if they are contiguous and fit.
	# If one field is "Small Text", it might force full width?
	# "Small Text" fieldtype often defaults to full width in some versions or if "Table" layout isn't active.
	# "Data" usually flows.
	
	# I will change "Small Text" fields back to "Data" (Question & Computed).
	# BUT I hit Row Size limit with Data.
	
	# ALTERNATIVE: Use "Read Only" Checkbox? No.
	# Use "Int" for Computed (if number)? No, it's text.
	# Use "Code" field? No.
	
	# What if I use "HTML" field for Question Text?
	# HTML field doesn't store data in row! It's just UI.
	# AND I can put the text in "options".
	# So "Question Text" field can be HTML.
	# This SAVES ROW SPACE (0 bytes).
	# And HTML field respects columns? Yes usually.
	
	# Setup:
	# Col 1: HTML (Question Text). Options = "<div>...</div>". Cols: 4.
	# Col 2: Select (Response). Cols: 3.
	# Col 3: Int (Score). Cols: 2.
	# Col 4: HTML (Computed Value)? No, Computed Value needs to be SET by JS.
	# HTML field content can be set by `frm.set_df_property(fieldname, "options", val)`.
	# So YES, Computed Value can be HTML field too!
	# This saves ROW SPACE for Computed Value too!
	
	# So:
	# Q Text -> HTML.
	# Computed -> HTML.
	# Response -> Select (Data).
	# Score -> Int (Data).
	
	# This solves Row Size AND Layout (HTML fields flow well).
	
	update_fields_to_html()
	
	frappe.db.commit()
	frappe.clear_cache()
	print("\nConverted to HTML fields for layout & space.")

def update_fields_to_html():
	# questions map
	questions = get_questions()
	
	for i, q in enumerate(questions):
		idx = i + 1
		f_text = f"tobacco_fv_q{idx}_text"
		f_computed = f"tobacco_fv_q{idx}_computed"
		
		# Update Question Text to HTML
		# We set 'options' to the question text inside a div
		text_html = f"<div style='padding-top: 5px;'>{q[1]}</div>"
		frappe.db.set_value("Custom Field", {"dt": "Patient Encounter", "fieldname": f_text}, "fieldtype", "HTML")
		frappe.db.set_value("Custom Field", {"dt": "Patient Encounter", "fieldname": f_text}, "options", text_html)
		frappe.db.set_value("Custom Field", {"dt": "Patient Encounter", "fieldname": f_text}, "columns", 4)

		# Update Computed Value to HTML
		# Initial options empty or placeholder. JS will update it.
		frappe.db.set_value("Custom Field", {"dt": "Patient Encounter", "fieldname": f_computed}, "fieldtype", "HTML")
		frappe.db.set_value("Custom Field", {"dt": "Patient Encounter", "fieldname": f_computed}, "options", "<div id='computed_" + str(idx) + "'></div>")
		frappe.db.set_value("Custom Field", {"dt": "Patient Encounter", "fieldname": f_computed}, "columns", 3)

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
