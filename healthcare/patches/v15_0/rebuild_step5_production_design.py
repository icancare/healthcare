import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	print("\n" + "="*70)
	print("REBUILD STEP 5: Production-style design with 4 tests")
	print("="*70)
	
	# Create Step 5 fields matching production
	create_step5_fields_production_style()
	
	frappe.db.commit()
	frappe.clear_cache()
	print("\n✅ Step 5 rebuilt with production design!")


def create_step5_fields_production_style():
	"""Create 4 tests exactly as in production - single row layout"""
	
	# Dropdown options for all tests
	test_options = "\nNormal\nLikely inflammatory\nLow Suspicious\nHigh Suspicious of malignancy"
	
	# Visibility condition - show after practitioner selected
	depends_on = "eval:doc.practitioner && doc.show_clinical_examination && !doc.exam_skip_special_tests"
	
	custom_fields = {
		"Patient Encounter": [
			# Test 1: Toluidine Blue Test
			{
				"fieldname": "exam_toluidine_section",
				"label": "Toluidine Blue Test",
				"fieldtype": "Heading",
				"insert_after": "exam_skip_special_tests",
				"depends_on": depends_on
			},
			{
				"fieldname": "exam_toluidine_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": test_options,
				"insert_after": "exam_toluidine_section",
				"depends_on": depends_on
			},
			{
				"fieldname": "exam_toluidine_col",
				"fieldtype": "Column Break",
				"insert_after": "exam_toluidine_result"
			},
			{
				"fieldname": "exam_toluidine_notes",
				"label": "Note",
				"fieldtype": "Small Text",
				"insert_after": "exam_toluidine_col",
				"depends_on": depends_on
			},
			
			# Test 2: Blue/Violet Light Test
			{
				"fieldname": "exam_bluelight_section",
				"label": "Blue/Violet light (around 400-450 nm)",
				"fieldtype": "Heading",
				"insert_after": "exam_toluidine_notes",
				"depends_on": depends_on
			},
			{
				"fieldname": "exam_bluelight_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": test_options,
				"insert_after": "exam_bluelight_section",
				"depends_on": depends_on
			},
			{
				"fieldname": "exam_bluelight_col",
				"fieldtype": "Column Break",
				"insert_after": "exam_bluelight_result"
			},
			{
				"fieldname": "exam_bluelight_notes",
				"label": "Note",
				"fieldtype": "Small Text",
				"insert_after": "exam_bluelight_col",
				"depends_on": depends_on
			},
			
			# Test 3: Green LED/Laser Test
			{
				"fieldname": "exam_greenled_section",
				"label": "Green LED/Laser (~530-550 nm)",
				"fieldtype": "Heading",
				"insert_after": "exam_bluelight_notes",
				"depends_on": depends_on
			},
			{
				"fieldname": "exam_greenled_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": test_options,
				"insert_after": "exam_greenled_section",
				"depends_on": depends_on
			},
			{
				"fieldname": "exam_greenled_col",
				"fieldtype": "Column Break",
				"insert_after": "exam_greenled_result"
			},
			{
				"fieldname": "exam_greenled_notes",
				"label": "Note",
				"fieldtype": "Small Text",
				"insert_after": "exam_greenled_col",
				"depends_on": depends_on
			},
			
			# Test 4: Amber Light Test
			{
				"fieldname": "exam_amber_section",
				"label": "Amber light (around 590 nm)",
				"fieldtype": "Heading",
				"insert_after": "exam_greenled_notes",
				"depends_on": depends_on
			},
			{
				"fieldname": "exam_amber_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": test_options,
				"insert_after": "exam_amber_section",
				"depends_on": depends_on
			},
			{
				"fieldname": "exam_amber_col",
				"fieldtype": "Column Break",
				"insert_after": "exam_amber_result"
			},
			{
				"fieldname": "exam_amber_notes",
				"label": "Note",
				"fieldtype": "Small Text",
				"insert_after": "exam_amber_col",
				"depends_on": depends_on
			}
		]
	}
	
	print("\n📝 Creating Step 5 fields (4 tests, production layout)...")
	create_custom_fields(custom_fields, update=True)
	print("✅ Created 16 fields (4 tests × 4 fields each)")
	print("\nTests created:")
	print("  1. Toluidine Blue Test")
	print("  2. Blue/Violet light (around 400-450 nm)")
	print("  3. Green LED/Laser (~530-550 nm)")
	print("  4. Amber light (around 590 nm)")
	print("\nEach test has: Heading → Result (Select) → Column Break → Note (Small Text)")
