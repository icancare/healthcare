
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
	print("\nSetting up Tobacco JSON Layout (HTML Table)...")
	
	# 1. Cleanup
	cleanup_fields()
	
	# 2. Create Fields
	create_json_layout()
	
	frappe.db.commit()
	frappe.clear_cache()
	print("\nJSON Layout Setup Complete!")

def cleanup_fields():
	# Delete all tobacco_fv_q* fields
	fields = frappe.get_all("Custom Field", filters=[["dt", "=", "Patient Encounter"], ["fieldname", "like", "tobacco_fv_%"]], pluck="name")
	for f in fields:
		frappe.delete_doc("Custom Field", f, force=True)

def create_json_layout():
	fv_logic = "eval:doc.practitioner && doc.exam_examination_template && doc.exam_examination_template.includes('Quit Tobacco First Visit')"
	
	create_custom_field("Patient Encounter", {
		"fieldname": "tobacco_fv_section",
		"label": "Step 1: Addiction Assessment Questionnaire",
		"fieldtype": "Section Break",
		"insert_after": "exam_examination_template",
		"depends_on": fv_logic,
		"collapsible": 0
	})
	
	# The UI Container
	create_custom_field("Patient Encounter", {
		"fieldname": "tobacco_fv_ui",
		"fieldtype": "HTML",
		"label": "Assessment UI",
		"insert_after": "tobacco_fv_section"
	})
	
	# The Data Store (Hidden)
	create_custom_field("Patient Encounter", {
		"fieldname": "tobacco_fv_data",
		"fieldtype": "Long Text",
		"label": "Tobacco Data JSON",
		"hidden": 1,
		"insert_after": "tobacco_fv_ui"
	})
	
	# Footer
	# We still keep Total Score as a standard field for easy reporting/viewing
	create_custom_field("Patient Encounter", {
		"fieldname": "tobacco_fv_footer_section",
		"fieldtype": "Section Break",
		"label": "",
		"insert_after": "tobacco_fv_data"
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
