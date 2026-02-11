
import frappe

def execute():
	print("\nFixing Tobacco Sub-section Dependencies...")
	
	# First Visit Subsections
	first_visit_template = "Quit Tobacco First Visit"
	first_visit_sections = [
		"tobacco_quit_buddies_section",
		"tobacco_treatment_planning_section"
	]
	
	# Follow-up Visit Subsections
	followup_template = "Quit Tobacco Follow-up Visit"
	followup_sections = [
		"tobacco_consumption_section",
		"tobacco_status_section",
		"tobacco_qol_section"
	]
	
	logic_template = "eval:doc.practitioner && doc.exam_examination_template && doc.exam_examination_template.includes('{}')"

	# Apply logic to First Visit sections
	for section in first_visit_sections:
		logic = logic_template.format(first_visit_template)
		update_dependency(section, logic)
		
	# Apply logic to Follow-up sections
	for section in followup_sections:
		logic = logic_template.format(followup_template)
		update_dependency(section, logic)
		
	frappe.db.commit()
	frappe.clear_cache()
	print("\nTobacco Sub-sections Fixed!")

def update_dependency(fieldname, logic):
	field = frappe.db.get_value("Custom Field", {"dt": "Patient Encounter", "fieldname": fieldname}, "name")
	if field:
		frappe.db.set_value("Custom Field", field, "depends_on", logic)
		print(f"✓ Updated {fieldname}")
	else:
		print(f"⚠ Field {fieldname} not found")
