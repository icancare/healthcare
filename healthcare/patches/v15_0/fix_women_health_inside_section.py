"""
Fix Women Health - Children Details and Note should be INSIDE Women Health collapsible section
NOT as separate sections.

Also fix Social History section position.
"""

import frappe


def execute():
    """Fix Women Health structure - all inside one collapsible section"""
    
    # ============ DELETE EXTRA SECTION BREAKS ============
    # These section breaks are causing Children Details and Note to appear outside Women Health
    sections_to_delete = [
        {"dt": "Patient", "fieldname": "women_health_children_section"},
        {"dt": "Patient Encounter", "fieldname": "encounter_women_health_children_section"},
    ]
    
    for section in sections_to_delete:
        if frappe.db.exists("Custom Field", section):
            cf_name = frappe.db.get_value("Custom Field", section, "name")
            frappe.delete_doc("Custom Field", cf_name, force=True)
            print(f"Deleted {section['dt']}.{section['fieldname']}")
    
    # ============ PATIENT ============
    # Order: genitourinary_symptoms -> patient_children_details -> women_health_note
    # All inside Women Health section (no extra section breaks)
    
    if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "patient_children_details"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient", "fieldname": "patient_children_details"},
            {
                "insert_after": "genitourinary_symptoms",
                "label": "Children Details"
            })
        print("Fixed Patient.patient_children_details")
    
    if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "women_health_note"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient", "fieldname": "women_health_note"},
            "insert_after", "patient_children_details")
        print("Fixed Patient.women_health_note")
    
    # Additional Details after women_health_note
    if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "custom_additional_details_section"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient", "fieldname": "custom_additional_details_section"},
            "insert_after", "women_health_note")
        print("Fixed Patient.custom_additional_details_section")
    
    # ============ PATIENT ENCOUNTER ============
    # Fix Women Health section to be after Social History's last table (custom_environmental_factors_history)
    
    if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": "encounter_women_health_section"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient Encounter", "fieldname": "encounter_women_health_section"},
            "insert_after", "custom_environmental_factors_history")
        print("Fixed Patient Encounter.encounter_women_health_section")
    
    # Order: encounter_genitourinary_symptoms -> encounter_children_details -> encounter_women_health_note
    if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": "encounter_children_details"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient Encounter", "fieldname": "encounter_children_details"},
            {
                "insert_after": "encounter_genitourinary_symptoms",
                "label": "Children Details"
            })
        print("Fixed Patient Encounter.encounter_children_details")
    
    if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": "encounter_women_health_note"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient Encounter", "fieldname": "encounter_women_health_note"},
            "insert_after", "encounter_children_details")
        print("Fixed Patient Encounter.encounter_women_health_note")
    
    frappe.db.commit()
    
    # Clear cache
    frappe.clear_cache(doctype="Patient")
    frappe.clear_cache(doctype="Patient Encounter")

