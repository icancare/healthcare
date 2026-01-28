# Copyright (c) 2025, ESS LLP and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Hide old Risk Factors section from Patient Medical History tab
	as we now have detailed Social History section
	"""
	
	# Hide Risk Factors section break
	if frappe.db.exists("DocField", {"parent": "Patient", "fieldname": "sb_12"}):
		frappe.db.set_value("DocField", 
			{"parent": "Patient", "fieldname": "sb_12"}, 
			"hidden", 1
		)
		print("✓ Hidden Risk Factors section break (sb_12)")
	
	# Find and hide all fields in Risk Factors section
	risk_factor_fields = [
		"sb_12",  # Risk Factors section break
		"tobacco_past_use",
		"tobacco_current_use",
		"alcohol_past_use",
		"alcohol_current_use",
		"surrounding_factors"
	]
	
	for fieldname in risk_factor_fields:
		# Check in DocField (standard fields)
		if frappe.db.exists("DocField", {"parent": "Patient", "fieldname": fieldname}):
			frappe.db.set_value("DocField", 
				{"parent": "Patient", "fieldname": fieldname}, 
				"hidden", 1
			)
			print(f"✓ Hidden standard field: {fieldname}")
		
		# Check in Custom Field (if customized)
		if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": fieldname}):
			frappe.db.set_value("Custom Field", 
				{"dt": "Patient", "fieldname": fieldname}, 
				"hidden", 1
			)
			print(f"✓ Hidden custom field: {fieldname}")
	
	frappe.db.commit()
	frappe.msgprint("✓ Old Risk Factors section hidden successfully")





















