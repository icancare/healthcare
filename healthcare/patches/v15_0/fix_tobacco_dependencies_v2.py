
import frappe

def execute():
	"""
	Fix broken dependencies for Tobacco fields.
	1. Fix trailing '&&' operators.
	2. Ensure Section Breaks have correct logic.
	3. Clear redundant depends_on from inner fields so they inherit Section visibility.
	"""
	print("\n" + "="*60)
	print("Fixing Broken Tobacco Dependencies (v2)")
	print("="*60)

	fix_tobacco_fields()

	frappe.db.commit()
	frappe.clear_cache()
	print("\n" + "="*60)
	print("Tobacco Dependencies Fixed (v2)!")
	print("="*60)


def fix_tobacco_fields():
	fields = frappe.get_all(
		"Custom Field",
		filters={
			"dt": "Patient Encounter",
			"fieldname": ["like", "tobacco_%"]
		},
		fields=["name", "fieldname", "fieldtype", "depends_on"]
	)
	
	for f in fields:
		# 1. Handle Section Breaks (The Checkpoints)
		if f.fieldtype == "Section Break":
			template_name = ""
			if "first_visit" in f.fieldname:
				template_name = "Quit Tobacco First Visit"
			elif "followup_visit" in f.fieldname:
				template_name = "Quit Tobacco Follow-up Visit"
			
			if template_name:
				# Set robust logic for Section Breaks
				new_dep = f"eval:doc.practitioner && doc.exam_examination_template && doc.exam_examination_template.includes('{template_name}')"
				frappe.db.set_value("Custom Field", f.name, "depends_on", new_dep)
				print(f"✓ Fixed Section Break: {f.fieldname}")
		
		# 2. Handle Inner Fields
		else:
			current_dep = f.depends_on or ""
			
			# Check if it is the broken string "eval:doc.practitioner && " (ignoring whitespace)
			if current_dep.strip() == "eval:doc.practitioner &&":
				# Clear it so it uses Section Break visibility
				frappe.db.set_value("Custom Field", f.name, "depends_on", "")
				print(f"✓ Cleared broken dependency from: {f.fieldname}")
			
			# Check if it has specific logic (like 'tobacco_reason_delay')
			elif current_dep and "&&" in current_dep and not current_dep.strip().endswith("&&"):
				# Likely valid logic, e.g. "eval:doc.practitioner && doc.tobacco_stuck_to_quit_date=='No'"
				# Just leave it or ensure it's clean
				pass
			
			# If it has logic but missing practitioner check, we might want to keep it?
			# Actually, if we clear it, it inherits Section visibility which ALREADY checks practitioner.
			# So simpler is better: ONLY keep depends_on if it has INTERNAL field dependencies.
			
			# Logic: If depends_on is just checking practitioner (or broken), clear it.
			# If it checks other fields (like 'tobacco_stuck...'), keep it.
