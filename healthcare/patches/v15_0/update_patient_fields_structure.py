import frappe


def execute():
	"""
	Migration patch to:
	1. Add Top Up Amount and Co-Pay Amount fields to Patient Insurance  
	2. Move Occupation and Marital Status from Medical History tab to Details tab Personal Information section
	3. Clean up all old field entries before reload
	"""
	
	# Step 1: Delete ALL existing DocField entries for Patient
	# This ensures a clean slate before reload
	frappe.db.sql("DELETE FROM `tabDocField` WHERE parent='Patient'")
	frappe.db.commit()
	
	# Step 2: Force reload Patient doctype - will recreate fields from JSON
	frappe.reload_doctype("Patient", force=True)
	frappe.reload_doctype("Patient Insurance", force=True)
	
	# Step 3: Clear cache
	frappe.clear_cache()
	
	print("✅ Patient fields cleaned and reloaded from JSON successfully")

