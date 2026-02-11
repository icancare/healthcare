
import frappe

def execute():
	print("\nDeep Inspection of ALL Custom Field depends_on...")
	
	fields = frappe.get_all(
		"Custom Field",
		filters={"dt": "Patient Encounter"},
		fields=["name", "fieldname", "depends_on"]
	)
	
	broken_fields = []
	non_eval_appended = []
	
	for f in fields:
		if not f.depends_on:
			continue
			
		dep = f.depends_on.strip()
		
		# Check 1: Trailing operators
		if dep.endswith("&&") or dep.endswith("||"):
			print(f"❌ INVALID SYNTAX (Trailing operator): {f.fieldname} -> {dep}")
			broken_fields.append(f)
			
		# Check 2: Appended logic to non-eval field
		# If it contains "&&" or "includes" but DOES NOT start with "eval:"
		if ("&&" in dep or "includes" in dep) and not dep.startswith("eval:"):
			print(f"❌ INVALID FORMAT (Not eval): {f.fieldname} -> {dep}")
			non_eval_appended.append(f)

	print("\nSummary:")
	print(f"Fields with Syntax Errors (Trailing): {len(broken_fields)}")
	print(f"Fields with Format Errors (Not eval): {len(non_eval_appended)}")
	
	if not broken_fields and not non_eval_appended:
		print("✅ No obvious errors found. Double check logic.")

