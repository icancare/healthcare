import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	print("\n" + "="*70)
	print("FIX STEP 5 LAYOUT: 1 Test = 1 Row")
	print("="*70)
	
	# Add section breaks to force new rows
	fix_step5_row_layout()
	
	frappe.db.commit()
	frappe.clear_cache()
	print("\n✅ Step 5 layout fixed - each test in separate row!")


def fix_step5_row_layout():
	"""Add section breaks before each test heading to force new rows"""
	
	depends_on = "eval:doc.practitioner && doc.show_clinical_examination && !doc.exam_skip_special_tests"
	
	# We need to add Section Breaks BEFORE each test heading
	# and update insert_after for headings to come after section breaks
	
	custom_fields = {
		"Patient Encounter": [
			# Row break before Test 2 (Blue Light)
			{
				"fieldname": "exam_bluelight_row_break",
				"fieldtype": "Section Break",
				"insert_after": "exam_toluidine_notes",
				"depends_on": depends_on
			},
			
			# Row break before Test 3 (Green LED)
			{
				"fieldname": "exam_greenled_row_break",
				"fieldtype": "Section Break",
				"insert_after": "exam_bluelight_notes",
				"depends_on": depends_on
			},
			
			# Row break before Test 4 (Amber)
			{
				"fieldname": "exam_amber_row_break",
				"fieldtype": "Section Break",
				"insert_after": "exam_greenled_notes",
				"depends_on": depends_on
			},
			
			# Row break before Test 5 (Autofluorescence)
			{
				"fieldname": "exam_autofluor_row_break",
				"fieldtype": "Section Break",
				"insert_after": "exam_amber_notes",
				"depends_on": depends_on
			},
			
			# Row break before Test 6 (Spectroscopy)
			{
				"fieldname": "exam_spectroscopy_row_break",
				"fieldtype": "Section Break",
				"insert_after": "exam_autofluor_notes",
				"depends_on": depends_on
			},
			
			# Row break before Test 7 (Lung XRAY)
			{
				"fieldname": "exam_lung_xray_row_break",
				"fieldtype": "Section Break",
				"insert_after": "exam_spectroscopy_notes",
				"depends_on": depends_on
			},
			
			# Row break before Test 8 (AI Lung)
			{
				"fieldname": "exam_ai_lung_row_break",
				"fieldtype": "Section Break",
				"insert_after": "exam_lung_xray_notes",
				"depends_on": depends_on
			}
		]
	}
	
	print("\n📝 Adding Section Breaks for row layout...")
	create_custom_fields(custom_fields, update=True)
	print("✅ Created 7 section breaks (for tests 2-8)")
	
	# Now update insert_after for test headings to come after section breaks
	print("\n📝 Updating test heading positions...")
	
	updates = [
		("exam_bluelight_section", "exam_bluelight_row_break"),
		("exam_greenled_section", "exam_greenled_row_break"),
		("exam_amber_section", "exam_amber_row_break"),
		("exam_autofluor_section", "exam_autofluor_row_break"),
		("exam_spectroscopy_section", "exam_spectroscopy_row_break"),
		("exam_lung_xray_section", "exam_lung_xray_row_break"),
		("exam_ai_lung_section", "exam_ai_lung_row_break")
	]
	
	for fieldname, new_insert_after in updates:
		try:
			doc = frappe.get_doc("Custom Field", {
				"dt": "Patient Encounter",
				"fieldname": fieldname
			})
			doc.insert_after = new_insert_after
			doc.save()
			print(f"✅ Updated {fieldname} → insert_after: {new_insert_after}")
		except Exception as e:
			print(f"⚠️  Could not update {fieldname}: {str(e)}")
	
	print("\n✅ Layout fixed: Each test now appears in separate row")
