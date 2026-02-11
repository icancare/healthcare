
import frappe
from healthcare.patches.v15_0 import setup_tobacco_cessation_templates
from healthcare.patches.v15_0 import setup_tobacco_followup_fields
from healthcare.patches.v15_0 import setup_tobacco_json_layout
from healthcare.patches.v15_0 import fix_tobacco_template_dependencies

def execute():
	print("Forcing Tobacco Setup Execution on Production...")
	
	# 1. Base Templates & Options (Fields are disabled in source file now)
	try:
		setup_tobacco_cessation_templates.execute()
	except Exception as e:
		print(f"Error in templates: {e}")

	# 2. Fix Dependencies
	try:
		fix_tobacco_template_dependencies.execute()
	except Exception as e:
		print(f"Error in dependencies: {e}")

	# 3. Followup Fields
	try:
		setup_tobacco_followup_fields.execute()
	except Exception as e:
		print(f"Error in followup fields: {e}")

	# 4. JSON Layout (Step 1 Grid)
	try:
		setup_tobacco_json_layout.execute()
	except Exception as e:
		print(f"Error in JSON layout: {e}")
		
	frappe.db.commit()
