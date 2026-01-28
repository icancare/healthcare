import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	print("\n" + "="*70)
	print("Final Step 5 & 6 Fixes: Add missing tests, rename, cleanup")
	print("="*70)
	
	# 1. Add missing Step 5 fields (Green LED, Amber, Lung XRAY, AI Lung XRAY)
	add_missing_step5_tests()
	
	# 2. Rename Step 6 section title
	rename_step6_title()
	
	# 3. Update Step 6 field labels (remove brackets)
	update_step6_labels()
	
	# 4. Physically delete any remaining duplicate fields from database
	cleanup_duplicate_fields()
	
	frappe.db.commit()
	frappe.clear_cache()
	print("\n✅ Final Step 5 & 6 fixes completed!")


def add_missing_step5_tests():
	"""Add missing 4 tests to Step 5 as per client requirements"""
	
	custom_fields = {
		"Patient Encounter": [
			# Green LED/Laser Test (after Blue Light)
			{
				"fieldname": "exam_greenled_section",
				"label": "Green LED/Laser (~530-550 nm)",
				"fieldtype": "Heading",
				"insert_after": "exam_bluelight_notes",
				"description": "Highlights superficial vasculature (capillaries)"
			},
			{
				"fieldname": "exam_greenled_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": "\nNormal\nLikely inflammatory\nLow Suspicious\nHigh Suspicious of malignancy",
				"insert_after": "exam_greenled_section"
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
				"insert_after": "exam_greenled_col"
			},
			
			# Amber Light Test (after Green LED)
			{
				"fieldname": "exam_amber_section",
				"label": "Amber Light (around 590 nm)",
				"fieldtype": "Heading",
				"insert_after": "exam_greenled_notes",
				"description": "Highlights vascularity and hemoglobin absorption → helps confirm whether dark areas are due to inflammation vs neoplasia"
			},
			{
				"fieldname": "exam_amber_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": "\nNormal\nLikely inflammatory\nLow Suspicious\nHigh Suspicious of malignancy",
				"insert_after": "exam_amber_section"
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
				"insert_after": "exam_amber_col"
			},
			
			# Lung XRAY Test (after Spectroscopy)
			{
				"fieldname": "exam_lung_xray_section",
				"label": "Lung XRAY",
				"fieldtype": "Heading",
				"insert_after": "exam_spectroscopy_notes"
			},
			{
				"fieldname": "exam_lung_xray_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": "\nNormal\nLikely inflammatory\nLow Suspicious\nHigh Suspicious of malignancy\nTuberculosis",
				"insert_after": "exam_lung_xray_section"
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
				"insert_after": "exam_lung_xray_col"
			},
			
			# AI Lung XRAY Interpretation (after Lung XRAY)
			{
				"fieldname": "exam_ai_lung_section",
				"label": "AI Lung XRAY Interpretation",
				"fieldtype": "Heading",
				"insert_after": "exam_lung_xray_notes"
			},
			{
				"fieldname": "exam_ai_lung_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": "\nNormal\nLikely inflammatory\nLow Suspicious\nHigh Suspicious of malignancy\nTuberculosis",
				"insert_after": "exam_ai_lung_section"
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
				"insert_after": "exam_ai_lung_col"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	print("✅ Added 4 missing Step 5 tests (Green LED, Amber, Lung XRAY, AI Lung XRAY)")


def rename_step6_title():
	"""Rename Step 6 section title"""
	try:
		field = frappe.get_doc("Custom Field", {"dt": "Patient Encounter", "fieldname": "exam_step6_section"})
		field.label = "STEP 6 - Advice - Camp / Screening Only"
		field.save()
		print("✅ Renamed Step 6 section title")
	except Exception as e:
		print(f"⚠️  Could not rename Step 6 title: {str(e)}")


def update_step6_labels():
	"""Update Step 6 field labels - remove bracket text"""
	
	fields_to_update = {
		"exam_advice_primary": "Primary Advice",
		"exam_advice_section_b_heading": "Additional Recommendations"
	}
	
	for fieldname, new_label in fields_to_update.items():
		try:
			if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": fieldname}):
				field = frappe.get_doc("Custom Field", {"dt": "Patient Encounter", "fieldname": fieldname})
				field.label = new_label
				field.description = ""  # Remove description too
				field.save()
				print(f"✅ Updated label: {fieldname} → {new_label}")
		except Exception as e:
			print(f"⚠️  Could not update {fieldname}: {str(e)}")


def cleanup_duplicate_fields():
	"""Physically delete any remaining step5_/step6_ duplicate fields from database"""
	
	# Get all step5_ and step6_ fields
	duplicate_fields = frappe.db.sql("""
		SELECT name, fieldname 
		FROM `tabCustom Field` 
		WHERE dt = 'Patient Encounter' 
		AND (fieldname LIKE 'step5_%' OR fieldname LIKE 'step6_%')
	""", as_dict=1)
	
	if duplicate_fields:
		print(f"\n🗑️  Found {len(duplicate_fields)} duplicate fields to delete")
		for field in duplicate_fields:
			try:
				frappe.db.delete("Custom Field", {"name": field.name})
				print(f"✅ Deleted: {field.fieldname}")
			except Exception as e:
				print(f"⚠️  Could not delete {field.fieldname}: {str(e)}")
	else:
		print("✅ No duplicate step5_/step6_ fields found")
