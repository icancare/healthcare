import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	print("\n" + "="*70)
	print("ADD REMAINING 4 TESTS: Complete Step 5 with 8 tests total")
	print("="*70)
	
	# Add remaining 4 tests (5-8)
	add_remaining_step5_tests()
	
	frappe.db.commit()
	frappe.clear_cache()
	print("\n✅ Step 5 complete with all 8 tests!")


def add_remaining_step5_tests():
	"""Add tests 5-8 to complete Step 5"""
	
	# Dropdown options for all tests
	test_options = "\nNormal\nLikely inflammatory\nLow Suspicious\nHigh Suspicious of malignancy"
	
	# Visibility condition
	depends_on = "eval:doc.practitioner && doc.show_clinical_examination && !doc.exam_skip_special_tests"
	
	custom_fields = {
		"Patient Encounter": [
			# Test 5: Autofluorescence Test
			{
				"fieldname": "exam_autofluor_section",
				"label": "Autofluorescence Test",
				"fieldtype": "Heading",
				"insert_after": "exam_amber_notes",
				"depends_on": depends_on
			},
			{
				"fieldname": "exam_autofluor_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": test_options,
				"insert_after": "exam_autofluor_section",
				"depends_on": depends_on
			},
			{
				"fieldname": "exam_autofluor_col",
				"fieldtype": "Column Break",
				"insert_after": "exam_autofluor_result"
			},
			{
				"fieldname": "exam_autofluor_notes",
				"label": "Note",
				"fieldtype": "Small Text",
				"insert_after": "exam_autofluor_col",
				"depends_on": depends_on
			},
			
			# Test 6: Spectroscopy Test
			{
				"fieldname": "exam_spectroscopy_section",
				"label": "Spectroscopy Test",
				"fieldtype": "Heading",
				"insert_after": "exam_autofluor_notes",
				"depends_on": depends_on
			},
			{
				"fieldname": "exam_spectroscopy_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": test_options,
				"insert_after": "exam_spectroscopy_section",
				"depends_on": depends_on
			},
			{
				"fieldname": "exam_spectroscopy_col",
				"fieldtype": "Column Break",
				"insert_after": "exam_spectroscopy_result"
			},
			{
				"fieldname": "exam_spectroscopy_notes",
				"label": "Note",
				"fieldtype": "Small Text",
				"insert_after": "exam_spectroscopy_col",
				"depends_on": depends_on
			},
			
			# Test 7: Lung XRAY
			{
				"fieldname": "exam_lung_xray_section",
				"label": "Lung XRAY",
				"fieldtype": "Heading",
				"insert_after": "exam_spectroscopy_notes",
				"depends_on": depends_on
			},
			{
				"fieldname": "exam_lung_xray_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": "\nNormal\nLikely inflammatory\nLow Suspicious\nHigh Suspicious of malignancy\nTuberculosis",
				"insert_after": "exam_lung_xray_section",
				"depends_on": depends_on
			},
			{
				"fieldname": "exam_lung_xray_col",
				"fieldtype": "Column Break",
				"insert_after": "exam_lung_xray_result"
			},
			{
				"fieldname": "exam_lung_xray_notes",
				"label": "Note",
				"fieldtype": "Small Text",
				"insert_after": "exam_lung_xray_col",
				"depends_on": depends_on
			},
			
			# Test 8: AI Lung XRAY Interpretation
			{
				"fieldname": "exam_ai_lung_section",
				"label": "AI Lung XRAY Interpretation",
				"fieldtype": "Heading",
				"insert_after": "exam_lung_xray_notes",
				"depends_on": depends_on
			},
			{
				"fieldname": "exam_ai_lung_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": "\nNormal\nLikely inflammatory\nLow Suspicious\nHigh Suspicious of malignancy\nTuberculosis",
				"insert_after": "exam_ai_lung_section",
				"depends_on": depends_on
			},
			{
				"fieldname": "exam_ai_lung_col",
				"fieldtype": "Column Break",
				"insert_after": "exam_ai_lung_result"
			},
			{
				"fieldname": "exam_ai_lung_notes",
				"label": "Note",
				"fieldtype": "Small Text",
				"insert_after": "exam_ai_lung_col",
				"depends_on": depends_on
			}
		]
	}
	
	print("\n📝 Adding remaining 4 tests (5-8)...")
	create_custom_fields(custom_fields, update=True)
	print("✅ Created 16 fields (4 tests × 4 fields each)")
	print("\nTests 5-8 added:")
	print("  5. Autofluorescence Test")
	print("  6. Spectroscopy Test")
	print("  7. Lung XRAY")
	print("  8. AI Lung XRAY Interpretation")
	print("\n✅ Total: 8 tests in Step 5")
