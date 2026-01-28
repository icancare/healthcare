import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	print("\n" + "="*70)
	print("ADD SKIP SPECIAL TESTS CHECKBOX")
	print("="*70)
	
	# Add Skip checkbox
	add_skip_checkbox()
	
	frappe.db.commit()
	frappe.clear_cache()
	print("\n✅ Skip Special Tests checkbox added!")


def add_skip_checkbox():
	"""Add Skip Special Tests checkbox to Step 5"""
	
	custom_fields = {
		"Patient Encounter": [
			{
				"fieldname": "exam_skip_special_tests",
				"label": "Skip Special Tests",
				"fieldtype": "Check",
				"insert_after": "exam_step5_section",
				"depends_on": "eval:doc.practitioner && doc.show_clinical_examination",
				"description": "Check this to skip all special tests"
			}
		]
	}
	
	print("\n📝 Adding Skip Special Tests checkbox...")
	create_custom_fields(custom_fields, update=True)
	print("✅ Skip checkbox added after Step 5 section")
