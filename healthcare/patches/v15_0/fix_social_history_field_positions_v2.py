import frappe
from frappe import _

def execute():
	"""
	Fix field positions properly using frappe.get_meta and reordering
	Move age/years fields BEFORE Additional Information section
	"""
	try:
		# Fix Smokeless Tobacco
		fix_smokeless_tobacco()
		
		# Fix Substance Abuse
		fix_substance_abuse()
		
		# Fix Alcohol
		fix_alcohol()
		
		# Fix Smoking (add pack years in correct position)
		fix_smoking_pack_years()
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Successfully fixed all field positions")
		print("   - Age fields now appear BEFORE Additional Information")
		print("   - Years fields now appear BEFORE Additional Information")
		print("   - Pack Years fields in correct position")
		
	except Exception as e:
		print(f"❌ Error: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

def fix_smokeless_tobacco():
	"""Move age fields before Additional Information section"""
	tables = [
		"Patient Smokeless Tobacco History",
		"Patient Encounter Smokeless Tobacco History"
	]
	
	for table in tables:
		# Get the DocType
		doc = frappe.get_doc("DocType", table)
		
		# Find section_break_10 (Additional Information)
		section_idx = None
		age_fields = []
		
		for field in doc.fields:
			if field.fieldname == "section_break_10":
				section_idx = field.idx
			elif field.fieldname in ["started_at_age", "discontinued_at_age", "used_for_years", "column_break_age"]:
				age_fields.append(field)
		
		if section_idx and age_fields:
			# Move age fields before section_break
			# First, move them after quantity_unit
			for field in doc.fields:
				if field.fieldname == "quantity_unit":
					target_idx = field.idx
					
					# Update age fields to come after quantity_unit
					for i, age_field in enumerate(age_fields):
						frappe.db.sql("""
							UPDATE `tabDocField`
							SET idx = %s
							WHERE name = %s
						""", (target_idx + i + 1, age_field.name))
					
					# Update section_break to come after age fields
					frappe.db.sql("""
						UPDATE `tabDocField`
						SET idx = %s
						WHERE parent = %s AND fieldname = 'section_break_10'
					""", (target_idx + len(age_fields) + 1, table))
					
					# Update comment to come after section_break
					frappe.db.sql("""
						UPDATE `tabDocField`
						SET idx = %s
						WHERE parent = %s AND fieldname = 'comment'
					""", (target_idx + len(age_fields) + 2, table))
					
					break
		
		print(f"✅ Fixed field positions: {table}")

def fix_substance_abuse():
	"""Move age fields before Additional Information section"""
	tables = [
		"Patient Substance Abuse History",
		"Patient Encounter Substance Abuse History"
	]
	
	for table in tables:
		doc = frappe.get_doc("DocType", table)
		
		for field in doc.fields:
			if field.fieldname == "quantity_unit":
				target_idx = field.idx
				
				# Update age fields
				frappe.db.sql("""
					UPDATE `tabDocField`
					SET idx = %s
					WHERE parent = %s AND fieldname = 'column_break_age'
				""", (target_idx + 1, table))
				
				frappe.db.sql("""
					UPDATE `tabDocField`
					SET idx = %s
					WHERE parent = %s AND fieldname = 'started_at_age'
				""", (target_idx + 2, table))
				
				frappe.db.sql("""
					UPDATE `tabDocField`
					SET idx = %s
					WHERE parent = %s AND fieldname = 'discontinued_at_age'
				""", (target_idx + 3, table))
				
				frappe.db.sql("""
					UPDATE `tabDocField`
					SET idx = %s
					WHERE parent = %s AND fieldname = 'used_for_years'
				""", (target_idx + 4, table))
				
				# Update section_break
				frappe.db.sql("""
					UPDATE `tabDocField`
					SET idx = %s
					WHERE parent = %s AND fieldname = 'section_break_10'
				""", (target_idx + 5, table))
				
				# Update comment
				frappe.db.sql("""
					UPDATE `tabDocField`
					SET idx = %s
					WHERE parent = %s AND fieldname = 'comment'
				""", (target_idx + 6, table))
				
				break
		
		print(f"✅ Fixed field positions: {table}")

def fix_alcohol():
	"""Move years fields before Additional Information section"""
	tables = [
		"Patient Alcohol History",
		"Patient Encounter Alcohol History"
	]
	
	for table in tables:
		doc = frappe.get_doc("DocType", table)
		
		for field in doc.fields:
			if field.fieldname == "quantity_unit":
				target_idx = field.idx
				
				# Update years fields
				frappe.db.sql("""
					UPDATE `tabDocField`
					SET idx = %s
					WHERE parent = %s AND fieldname = 'column_break_years'
				""", (target_idx + 1, table))
				
				frappe.db.sql("""
					UPDATE `tabDocField`
					SET idx = %s
					WHERE parent = %s AND fieldname = 'years_of_use'
				""", (target_idx + 2, table))
				
				frappe.db.sql("""
					UPDATE `tabDocField`
					SET idx = %s
					WHERE parent = %s AND fieldname = 'alcohol_years'
				""", (target_idx + 3, table))
				
				# Update section_break
				frappe.db.sql("""
					UPDATE `tabDocField`
					SET idx = %s
					WHERE parent = %s AND fieldname = 'section_break_10'
				""", (target_idx + 4, table))
				
				# Update comment
				frappe.db.sql("""
					UPDATE `tabDocField`
					SET idx = %s
					WHERE parent = %s AND fieldname = 'comment'
				""", (target_idx + 5, table))
				
				break
		
		print(f"✅ Fixed field positions: {table}")

def fix_smoking_pack_years():
	"""Move pack years fields before Additional Information section"""
	tables = [
		"Patient Smoking Tobacco History",
		"Patient Encounter Smoking Tobacco History"
	]
	
	for table in tables:
		doc = frappe.get_doc("DocType", table)
		
		for field in doc.fields:
			if field.fieldname == "used_for_years":
				target_idx = field.idx
				
				# Update pack years fields
				frappe.db.sql("""
					UPDATE `tabDocField`
					SET idx = %s
					WHERE parent = %s AND fieldname = 'pack_years'
				""", (target_idx + 1, table))
				
				frappe.db.sql("""
					UPDATE `tabDocField`
					SET idx = %s
					WHERE parent = %s AND fieldname = 'bidi_pack_years'
				""", (target_idx + 2, table))
				
				# Update section_break
				frappe.db.sql("""
					UPDATE `tabDocField`
					SET idx = %s
					WHERE parent = %s AND fieldname = 'section_break_10'
				""", (target_idx + 3, table))
				
				# Update comment
				frappe.db.sql("""
					UPDATE `tabDocField`
					SET idx = %s
					WHERE parent = %s AND fieldname = 'comment'
				""", (target_idx + 4, table))
				
				break
		
		print(f"✅ Fixed field positions: {table}")

