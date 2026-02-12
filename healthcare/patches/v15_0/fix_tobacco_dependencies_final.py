
import frappe

def execute():
	print("Fixing Tobacco Field Dependency Syntax & Logic...")
	
	fields = frappe.get_all(
		"Custom Field", 
		filters={"dt": "Patient Encounter", "fieldname": ["like", "tobacco_%"]}, 
		fields=["name", "fieldname", "depends_on"]
	)
	
	tobacco_templates_check = "['Quit Tobacco First Visit', 'Quit Tobacco Follow-up Visit'].includes(doc.exam_examination_template)"
	
	for f in fields:
		original = f.depends_on or ""
		fixed = original.strip()
		
		# 1. Fix Trailing Syntax Error (&&)
		while fixed.endswith("&&"):
			fixed = fixed[:-2].strip()
			
		# 2. Add Missing Logic
		# If dependency is empty or jus "eval:doc.practitioner", it might show globally.
		# We must restrict to Tobacco templates.
		
		# Check if it mentions "Quit Tobacco"
		if "Quit Tobacco" not in fixed:
			# It's a generic field (e.g. tobacco_diagnosis_notes)
			# We enforce Tobacco Templates constraint.
			
			prefix = ""
			if not fixed.startswith("eval:"):
				prefix = "eval:"
			
			# Ensure doc.practitioner check
			if "doc.practitioner" not in fixed:
				fixed = f"doc.practitioner && {fixed}".replace("eval:", "").strip()
				if fixed.endswith("&&"): fixed = fixed[:-2].strip() # Safety
			
			# Append Template Check
			if fixed == "eval:doc.practitioner" or fixed == "doc.practitioner":
				# Simple case
				fixed = f"eval:doc.practitioner && {tobacco_templates_check}"
			else:
				# Complex case or empty
				if not fixed or fixed == "eval:":
					fixed = f"eval:doc.practitioner && {tobacco_templates_check}"
				else:
					# Append
					if not fixed.startswith("eval:"): fixed = f"eval:{fixed}"
					fixed = f"{fixed} && {tobacco_templates_check}"
		
		# Update if changed
		if fixed != original:
			frappe.db.set_value("Custom Field", f.name, "depends_on", fixed)
			print(f"✓ Fixed {f.fieldname}")
			
	frappe.db.commit()
