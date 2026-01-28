import frappe

def execute():
	print("\n" + "="*70)
	print("Fix Step 5 Layout: Correct field positioning for proper display")
	print("="*70)
	
	# Fix the insert_after positions to ensure proper row layout
	fix_step5_field_positions()
	
	frappe.db.commit()
	frappe.clear_cache()
	print("\n✅ Step 5 layout fixed!")


def fix_step5_field_positions():
	"""Fix field positions so each test appears in one row: Heading | Result | Note"""
	
	# The correct layout should be:
	# Toluidine: section -> result -> col -> notes
	# Blue Light: section -> result -> col -> notes  
	# (After bluelight_notes, we need section break to start new row)
	
	# Green LED should start on new row after Blue Light
	try:
		# Add section break after Blue Light to force new row
		if not frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": "exam_greenled_row_break"}):
			frappe.get_doc({
				"doctype": "Custom Field",
				"dt": "Patient Encounter",
				"fieldname": "exam_greenled_row_break",
				"fieldtype": "Section Break",
				"insert_after": "exam_bluelight_notes"
			}).insert()
			print("✅ Added section break before Green LED")
		
		# Green LED section should come after the section break
		field = frappe.get_doc("Custom Field", {"dt": "Patient Encounter", "fieldname": "exam_greenled_section"})
		field.insert_after = "exam_greenled_row_break"
		field.save()
		
		# Remove the column break after greenled_result (it should be after notes)
		field = frappe.get_doc("Custom Field", {"dt": "Patient Encounter", "fieldname": "exam_greenled_col"})
		field.insert_after = "exam_greenled_result"
		field.save()
		
		print("✅ Fixed Green LED positioning")
	except Exception as e:
		print(f"⚠️  Could not fix Green LED: {str(e)}")
	
	# Amber should be on same row as Green LED
	try:
		field = frappe.get_doc("Custom Field", {"dt": "Patient Encounter", "fieldname": "exam_amber_section"})
		field.insert_after = "exam_greenled_col"
		field.save()
		
		field = frappe.get_doc("Custom Field", {"dt": "Patient Encounter", "fieldname": "exam_amber_result"})
		field.insert_after = "exam_amber_section"
		field.save()
		
		field = frappe.get_doc("Custom Field", {"dt": "Patient Encounter", "fieldname": "exam_amber_col"})
		field.insert_after = "exam_amber_result"
		field.save()
		
		field = frappe.get_doc("Custom Field", {"dt": "Patient Encounter", "fieldname": "exam_amber_notes"})
		field.insert_after = "exam_amber_col"
		field.save()
		
		print("✅ Fixed Amber Light positioning")
	except Exception as e:
		print(f"⚠️  Could not fix Amber: {str(e)}")
	
	# Autofluorescence and Spectroscopy should be on next row
	try:
		# Add section break before Autofluorescence
		if not frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": "exam_autofluor_row_break"}):
			frappe.get_doc({
				"doctype": "Custom Field",
				"dt": "Patient Encounter",
				"fieldname": "exam_autofluor_row_break",
				"fieldtype": "Section Break",
				"insert_after": "exam_amber_notes"
			}).insert()
			print("✅ Added section break before Autofluorescence")
		
		field = frappe.get_doc("Custom Field", {"dt": "Patient Encounter", "fieldname": "exam_autofluor_section"})
		field.insert_after = "exam_autofluor_row_break"
		field.save()
		
		print("✅ Fixed Autofluorescence positioning")
	except Exception as e:
		print(f"⚠️  Could not fix Autofluorescence: {str(e)}")
	
	# Spectroscopy should be on same row as Autofluorescence
	try:
		field = frappe.get_doc("Custom Field", {"dt": "Patient Encounter", "fieldname": "exam_spectroscopy_section"})
		field.insert_after = "exam_autofluor_col"
		field.save()
		
		print("✅ Fixed Spectroscopy positioning")
	except Exception as e:
		print(f"⚠️  Could not fix Spectroscopy: {str(e)}")
	
	# Lung XRAY and AI Lung XRAY on next row
	try:
		# Add section break before Lung XRAY
		if not frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": "exam_lung_row_break"}):
			frappe.get_doc({
				"doctype": "Custom Field",
				"dt": "Patient Encounter",
				"fieldname": "exam_lung_row_break",
				"fieldtype": "Section Break",
				"insert_after": "exam_spectroscopy_notes"
			}).insert()
			print("✅ Added section break before Lung XRAY")
		
		field = frappe.get_doc("Custom Field", {"dt": "Patient Encounter", "fieldname": "exam_lung_xray_section"})
		field.insert_after = "exam_lung_row_break"
		field.save()
		
		# AI Lung XRAY should be on same row
		field = frappe.get_doc("Custom Field", {"dt": "Patient Encounter", "fieldname": "exam_ai_lung_section"})
		field.insert_after = "exam_lung_xray_col"
		field.save()
		
		print("✅ Fixed Lung XRAY positioning")
	except Exception as e:
		print(f"⚠️  Could not fix Lung XRAY: {str(e)}")
