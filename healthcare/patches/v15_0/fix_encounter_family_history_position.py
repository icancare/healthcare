"""
Fix Family Medical History position in Patient Encounter

This patch fixes the insert_after for encounter_family_medical_history_section
to point to custom_medical_history instead of encounter_medical_history.
"""

import frappe


def execute():
    """Fix Family Medical History position in Patient Encounter"""
    
    # Fix insert_after for encounter_family_medical_history_section
    if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": "encounter_family_medical_history_section"}):
        frappe.db.set_value("Custom Field", 
            {"dt": "Patient Encounter", "fieldname": "encounter_family_medical_history_section"},
            "insert_after", "custom_medical_history")
        
        frappe.db.commit()
        print("Fixed insert_after for encounter_family_medical_history_section to custom_medical_history")

