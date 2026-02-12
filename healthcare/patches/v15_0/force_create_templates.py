
from healthcare.patches.v15_0.setup_tobacco_cessation_templates import create_templates, update_examination_type_options
import frappe

def execute():
	print("Forcing Template Creation...")
	
	try:
		update_examination_type_options()
	except Exception as e:
		print(f"Error updating options: {e}")
		
	try:
		create_templates()
	except Exception as e:
		print(f"Error creating templates: {e}")
		
	frappe.db.commit()
