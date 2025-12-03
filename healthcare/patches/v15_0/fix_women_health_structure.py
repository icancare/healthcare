"""
Fix Women Health structure - Note and Children Details inside Women Health section

This patch removes separate sections and puts Note and Children Details inside Women Health section.
"""

import frappe


def execute():
    """Fix Women Health structure"""
    
    # Delete the separate section breaks that were created incorrectly
    sections_to_delete = [
        # Patient
        {"dt": "Patient", "fieldname": "women_health_section_2"},
        {"dt": "Patient", "fieldname": "children_details_section"},
        # Patient Encounter
        {"dt": "Patient Encounter", "fieldname": "encounter_women_health_section_2"},
        {"dt": "Patient Encounter", "fieldname": "encounter_children_details_section"},
    ]
    
    for section in sections_to_delete:
        if frappe.db.exists("Custom Field", section):
            frappe.delete_doc("Custom Field", frappe.db.get_value("Custom Field", section, "name"))
            print(f"Deleted {section['dt']}.{section['fieldname']}")
    
    # Update Note field to be after genitourinary_symptoms (no section break)
    if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "women_health_note"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient", "fieldname": "women_health_note"},
            "insert_after", "genitourinary_symptoms")
    
    # Update Children Details table to be after Note
    if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "patient_children_details"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient", "fieldname": "patient_children_details"},
            {
                "insert_after": "women_health_note",
                "label": "Children Details"
            })
    
    # Same for Patient Encounter
    if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": "encounter_women_health_note"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient Encounter", "fieldname": "encounter_women_health_note"},
            "insert_after", "encounter_genitourinary_symptoms")
    
    if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": "encounter_children_details"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient Encounter", "fieldname": "encounter_children_details"},
            {
                "insert_after": "encounter_women_health_note",
                "label": "Children Details"
            })
    
    # Fix Additional Details section to be after patient_children_details
    if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "custom_additional_details_section"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient", "fieldname": "custom_additional_details_section"},
            "insert_after", "patient_children_details")
    
    frappe.db.commit()
    
    # Clear cache
    frappe.clear_cache(doctype="Patient")
    frappe.clear_cache(doctype="Patient Encounter")

