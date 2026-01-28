import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	print("\n" + "="*70)
	print("Fixing STEP 5 & STEP 6: Remove duplicates, use existing fields")
	print("="*70)
	
	# Remove the new duplicate fields we created
	remove_duplicate_step5_step6_fields()
	
	# Update existing Step 6 fields to use proper design
	update_existing_step6_advice_fields()
	
	frappe.db.commit()
	frappe.clear_cache()
	print("\n✅ STEP 5 & STEP 6 fixed - using existing fields with improved design")


def remove_duplicate_step5_step6_fields():
	"""Remove the duplicate Step 5 & Step 6 fields we just created"""
	
	# List of new fields to remove
	fields_to_remove = [
		'step5_special_tests_section',
		'skip_special_tests',
		'step5_col_break_1',
		'step5_toluidine_blue_test_heading',
		'step5_toluidine_result',
		'step5_toluidine_note',
		'step5_blue_light_heading',
		'step5_blue_light_result',
		'step5_blue_light_note',
		'step5_col_break_2',
		'step5_green_led_heading',
		'step5_green_led_result',
		'step5_green_led_note',
		'step5_amber_light_heading',
		'step5_amber_light_result',
		'step5_amber_light_note',
		'step5_additional_tests_section',
		'step5_autofluorescence_heading',
		'step5_autofluorescence_result',
		'step5_autofluorescence_note',
		'step5_spectroscopy_heading',
		'step5_spectroscopy_result',
		'step5_spectroscopy_note',
		'step5_col_break_3',
		'step5_lung_xray_heading',
		'step5_lung_xray_result',
		'step5_lung_xray_note',
		'step5_ai_lung_xray_heading',
		'step5_ai_lung_xray_result',
		'step5_ai_lung_xray_note',
		'step6_advice_section',
		'step6_advice_primary',
		'step6_advice_additional_heading',
		'step6_advice_inflammation',
		'step6_advice_nutritional',
		'step6_advice_dental',
		'step6_col_break',
		'step6_advice_tobacco'
	]
	
	for fieldname in fields_to_remove:
		try:
			if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": fieldname}):
				frappe.delete_doc("Custom Field", {"dt": "Patient Encounter", "fieldname": fieldname})
				print(f"✅ Removed duplicate field: {fieldname}")
		except Exception as e:
			print(f"⚠️  Could not remove {fieldname}: {str(e)}")
	
	print(f"\n✅ Removed {len(fields_to_remove)} duplicate fields")


def update_existing_step6_advice_fields():
	"""Update existing Step 6 advice fields - make 1-6 radio buttons, keep 7-10 as checkboxes"""
	
	# Step 6 advice fields 1-6 should be radio buttons (single select)
	# We'll use a Select field with radio display
	
	# First, let's add a new "Primary Advice" select field before exam_advice_1
	custom_fields = {
		"Patient Encounter": [
			{
				"fieldname": "exam_advice_primary",
				"label": "Primary Advice (Select One - Options 1-6)",
				"fieldtype": "Select",
				"options": "\nAdvice: Normal, routine screening after 1 year, continue self-oral examination\nAdvice: Normal with risk factors, screening every six months\nAdvice: Potentially malignant/precancerous lesions, requires treatment.\nAdvice: High risk for malignancy, visit the nearest ICanCare center for further evaluation\nAdvice: Frank malignancy, requires immediate treatment, visit specialized cancer center\nAdvice: Insufficient data, repeat examination",
				"insert_after": "exam_step6_section",
				"description": "Select one primary advice from options 1-6"
			},
			{
				"fieldname": "exam_advice_section_b_heading",
				"label": "Additional Recommendations (Options 7-10)",
				"fieldtype": "Heading",
				"insert_after": "exam_advice_primary"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	
	# Hide the old exam_advice_1 to exam_advice_6 checkboxes
	advice_fields_to_hide = [
		'exam_advice_1',
		'exam_advice_2', 
		'exam_advice_3',
		'exam_advice_4',
		'exam_advice_5',
		'exam_advice_6'
	]
	
	for fieldname in advice_fields_to_hide:
		try:
			field = frappe.get_doc("Custom Field", {"dt": "Patient Encounter", "fieldname": fieldname})
			field.hidden = 1
			field.save()
			print(f"✅ Hidden old checkbox: {fieldname}")
		except Exception as e:
			print(f"⚠️  Could not hide {fieldname}: {str(e)}")
	
	# Update insert_after for exam_advice_7 to come after the new heading
	try:
		field_7 = frappe.get_doc("Custom Field", {"dt": "Patient Encounter", "fieldname": "exam_advice_7"})
		field_7.insert_after = "exam_advice_section_b_heading"
		field_7.save()
		print("✅ Updated exam_advice_7 position")
	except Exception as e:
		print(f"⚠️  Could not update exam_advice_7: {str(e)}")
	
	print("✅ Step 6 advice fields updated - using dropdown for 1-6, checkboxes for 7-10")
