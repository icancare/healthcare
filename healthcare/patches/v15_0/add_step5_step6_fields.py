import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	print("\n" + "="*70)
	print("Adding STEP 5 (Special Tests) and STEP 6 (Advice) Fields")
	print("="*70)
	
	# Add Step 5 and Step 6 custom fields
	add_step5_special_tests_fields()
	add_step6_advice_fields()
	
	frappe.db.commit()
	frappe.clear_cache()
	print("\n✅ STEP 5 & STEP 6 fields added successfully...")


def add_step5_special_tests_fields():
	"""Add STEP 5 - Special Tests fields to Patient Encounter"""
	
	custom_fields = {
		"Patient Encounter": [
			# Section Break for Step 5
			{
				"fieldname": "step5_special_tests_section",
				"label": "STEP 5 - SPECIAL TESTS",
				"fieldtype": "Section Break",
				"insert_after": "diagnosis_notes",
				"collapsible": 1
			},
			
			# Skip Special Tests Checkbox
			{
				"fieldname": "skip_special_tests",
				"label": "Skip Special Tests",
				"fieldtype": "Check",
				"insert_after": "step5_special_tests_section",
				"default": "0"
			},
			
			# Column Break
			{
				"fieldname": "step5_col_break_1",
				"fieldtype": "Column Break",
				"insert_after": "skip_special_tests"
			},
			
			# Toluidine Blue Test
			{
				"fieldname": "step5_toluidine_blue_test_heading",
				"label": "Toluidine Blue Test",
				"fieldtype": "Heading",
				"insert_after": "step5_col_break_1"
			},
			{
				"fieldname": "step5_toluidine_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": "\nNormal\nLikely inflammatory\nLow Suspicious\nHigh Suspicious of malignancy",
				"insert_after": "step5_toluidine_blue_test_heading"
			},
			{
				"fieldname": "step5_toluidine_note",
				"label": "Note",
				"fieldtype": "Small Text",
				"insert_after": "step5_toluidine_result"
			},
			
			# Blue Light Test (400-450 nm)
			{
				"fieldname": "step5_blue_light_heading",
				"label": "Blue/Violet Light Test (around 400-450 nm)",
				"fieldtype": "Heading",
				"insert_after": "step5_toluidine_note"
			},
			{
				"fieldname": "step5_blue_light_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": "\nNormal\nLikely inflammatory\nLow Suspicious\nHigh Suspicious of malignancy",
				"insert_after": "step5_blue_light_heading",
				"description": "Detects loss of autofluorescence → suspicious for dysplasia/cancer."
			},
			{
				"fieldname": "step5_blue_light_note",
				"label": "Note",
				"fieldtype": "Small Text",
				"insert_after": "step5_blue_light_result"
			},
			
			# Column Break 2
			{
				"fieldname": "step5_col_break_2",
				"fieldtype": "Column Break",
				"insert_after": "step5_blue_light_note"
			},
			
			# Green LED/Laser Test (530-550 nm)
			{
				"fieldname": "step5_green_led_heading",
				"label": "Green LED/Laser (~530-550 nm)",
				"fieldtype": "Heading",
				"insert_after": "step5_col_break_2"
			},
			{
				"fieldname": "step5_green_led_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": "\nNormal\nLikely inflammatory\nLow Suspicious\nHigh Suspicious of malignancy",
				"insert_after": "step5_green_led_heading",
				"description": "Highlights superficial vasculature (capillaries)"
			},
			{
				"fieldname": "step5_green_led_note",
				"label": "Note",
				"fieldtype": "Small Text",
				"insert_after": "step5_green_led_result"
			},
			
			# Amber Light Test (590 nm)
			{
				"fieldname": "step5_amber_light_heading",
				"label": "Amber Light (around 590 nm)",
				"fieldtype": "Heading",
				"insert_after": "step5_green_led_note"
			},
			{
				"fieldname": "step5_amber_light_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": "\nNormal\nLikely inflammatory\nLow Suspicious\nHigh Suspicious of malignancy",
				"insert_after": "step5_amber_light_heading",
				"description": "Highlights vascularity and hemoglobin absorption → helps confirm whether dark areas are due to inflammation vs neoplasia"
			},
			{
				"fieldname": "step5_amber_light_note",
				"label": "Note",
				"fieldtype": "Small Text",
				"insert_after": "step5_amber_light_result"
			},
			
			# Section Break for Additional Tests
			{
				"fieldname": "step5_additional_tests_section",
				"fieldtype": "Section Break",
				"insert_after": "step5_amber_light_note"
			},
			
			# Autofluorescence Test
			{
				"fieldname": "step5_autofluorescence_heading",
				"label": "Autofluorescence Test",
				"fieldtype": "Heading",
				"insert_after": "step5_additional_tests_section"
			},
			{
				"fieldname": "step5_autofluorescence_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": "\nNormal\nLikely inflammatory\nLow Suspicious\nHigh Suspicious of malignancy",
				"insert_after": "step5_autofluorescence_heading"
			},
			{
				"fieldname": "step5_autofluorescence_note",
				"label": "Note",
				"fieldtype": "Small Text",
				"insert_after": "step5_autofluorescence_result"
			},
			
			# Spectroscopy Test
			{
				"fieldname": "step5_spectroscopy_heading",
				"label": "Spectroscopy Test",
				"fieldtype": "Heading",
				"insert_after": "step5_autofluorescence_note"
			},
			{
				"fieldname": "step5_spectroscopy_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": "\nNormal\nLikely inflammatory\nLow Suspicious\nHigh Suspicious of malignancy",
				"insert_after": "step5_spectroscopy_heading"
			},
			{
				"fieldname": "step5_spectroscopy_note",
				"label": "Note",
				"fieldtype": "Small Text",
				"insert_after": "step5_spectroscopy_result"
			},
			
			# Column Break 3
			{
				"fieldname": "step5_col_break_3",
				"fieldtype": "Column Break",
				"insert_after": "step5_spectroscopy_note"
			},
			
			# Lung XRAY
			{
				"fieldname": "step5_lung_xray_heading",
				"label": "Lung XRAY",
				"fieldtype": "Heading",
				"insert_after": "step5_col_break_3"
			},
			{
				"fieldname": "step5_lung_xray_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": "\nNormal\nLikely inflammatory\nLow Suspicious\nHigh Suspicious of malignancy\nTuberculosis",
				"insert_after": "step5_lung_xray_heading"
			},
			{
				"fieldname": "step5_lung_xray_note",
				"label": "Note",
				"fieldtype": "Small Text",
				"insert_after": "step5_lung_xray_result"
			},
			
			# AI Lung XRAY Interpretation
			{
				"fieldname": "step5_ai_lung_xray_heading",
				"label": "AI Lung XRAY Interpretation",
				"fieldtype": "Heading",
				"insert_after": "step5_lung_xray_note"
			},
			{
				"fieldname": "step5_ai_lung_xray_result",
				"label": "Result",
				"fieldtype": "Select",
				"options": "\nNormal\nLikely inflammatory\nLow Suspicious\nHigh Suspicious of malignancy\nTuberculosis",
				"insert_after": "step5_ai_lung_xray_heading"
			},
			{
				"fieldname": "step5_ai_lung_xray_note",
				"label": "Note",
				"fieldtype": "Small Text",
				"insert_after": "step5_ai_lung_xray_result"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	print("✅ STEP 5 - Special Tests fields created")


def add_step6_advice_fields():
	"""Add STEP 6 - Advice fields to Patient Encounter"""
	
	custom_fields = {
		"Patient Encounter": [
			# Section Break for Step 6
			{
				"fieldname": "step6_advice_section",
				"label": "STEP 6 - Advice - Camp / Screening Only",
				"fieldtype": "Section Break",
				"insert_after": "step5_ai_lung_xray_note",
				"collapsible": 1
			},
			
			# Section A: Single Select (Radio Buttons) - Options 1-6
			{
				"fieldname": "step6_advice_primary",
				"label": "Primary Advice (Select One)",
				"fieldtype": "Select",
				"options": "\nAdvice: Normal, routine screening after 1 year, continue self-oral examination\nAdvice: Normal with risk factors, screening every six months\nAdvice: Potentially malignant/precancerous lesions, requires treatment.\nAdvice: High risk for malignancy, visit the nearest ICanCare center for further evaluation\nAdvice: Frank malignancy, requires immediate treatment, visit specialized cancer center\nAdvice: Insufficient data, repeat examination",
				"insert_after": "step6_advice_section"
			},
			
			# Section B: Multiple Select (Checkboxes) - Options 7-9
			{
				"fieldname": "step6_advice_additional_heading",
				"label": "Additional Recommendations (Select Multiple if Applicable)",
				"fieldtype": "Heading",
				"insert_after": "step6_advice_primary"
			},
			{
				"fieldname": "step6_advice_inflammation",
				"label": "Advice: Inflammation, requires treatment and then repeat examination",
				"fieldtype": "Check",
				"insert_after": "step6_advice_additional_heading",
				"default": "0"
			},
			{
				"fieldname": "step6_advice_nutritional",
				"label": "Advice: Nutritional deficiency, requires treatment",
				"fieldtype": "Check",
				"insert_after": "step6_advice_inflammation",
				"default": "0"
			},
			{
				"fieldname": "step6_advice_dental",
				"label": "Advice: Recommend Dental Care",
				"fieldtype": "Check",
				"insert_after": "step6_advice_nutritional",
				"default": "0"
			},
			
			# Column Break
			{
				"fieldname": "step6_col_break",
				"fieldtype": "Column Break",
				"insert_after": "step6_advice_dental"
			},
			
			# High Risk Tobacco Consultation (from client sheet - option 10)
			{
				"fieldname": "step6_advice_tobacco",
				"label": "High Risk factors needs consultation for Tobacco de-addiction",
				"fieldtype": "Check",
				"insert_after": "step6_col_break",
				"default": "0"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	print("✅ STEP 6 - Advice fields created")
