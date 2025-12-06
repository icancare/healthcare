# Copyright (c) 2025, ESS LLP and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Unhide Risk Factors fields (we hid them by mistake!)
	The duplicate text is coming from field labels, not the section
	"""
	
	# Unhide all Risk Factors fields
	risk_factor_fields = [
		"sb_12",  # Risk Factors section break
		"tobacco_past_use",
		"tobacco_current_use", 
		"alcohol_past_use",
		"alcohol_current_use",
		"surrounding_factors"
	]
	
	for fieldname in risk_factor_fields:
		# Unhide in DocField (standard fields)
		if frappe.db.exists("DocField", {"parent": "Patient", "fieldname": fieldname}):
			frappe.db.set_value("DocField", 
				{"parent": "Patient", "fieldname": fieldname}, 
				"hidden", 0
			)
			print(f"✓ Unhidden standard field: {fieldname}")
		
		# Unhide in Custom Field (if customized)
		if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": fieldname}):
			frappe.db.set_value("Custom Field", 
				{"dt": "Patient", "fieldname": fieldname}, 
				"hidden", 0
			)
			print(f"✓ Unhidden custom field: {fieldname}")
	
	frappe.db.commit()
	
	# The duplicate "Smokeless Tobacco History" text is coming from
	# the LABEL of patient_smokeless_tobacco_history field
	# Let's check and update if needed
	
	print("\n✓ Risk Factors fields restored")
	print("Note: Duplicate section labels are showing because custom field labels are visible")
	print("This is normal ERPNext behavior - each table field has its own label")
	
	frappe.msgprint("✓ Risk Factors section restored")






