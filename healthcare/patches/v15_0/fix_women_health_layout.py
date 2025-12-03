"""
Fix Women Health layout:
1. Patient: Children Details full width with Section Break, Note at end
2. Patient Encounter: Fix insert_after to show after Social History section
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """Fix Women Health layout"""
    
    # ============ PATIENT ============
    # Add Section Break before Children Details for full width
    # Reorder: genitourinary_symptoms -> children_section -> children_details -> note
    
    # Create/Update children section break
    patient_children_section = {
        "Patient": [
            {
                "fieldname": "women_health_children_section",
                "fieldtype": "Section Break",
                "label": "Children Details",
                "insert_after": "genitourinary_symptoms",
            },
        ]
    }
    create_custom_fields(patient_children_section, update=True)
    
    # Update patient_children_details to be after the section
    if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "patient_children_details"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient", "fieldname": "patient_children_details"},
            {
                "insert_after": "women_health_children_section",
                "label": "Children"
            })
    
    # Update Note to be after children_details (at the end)
    if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "women_health_note"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient", "fieldname": "women_health_note"},
            "insert_after", "patient_children_details")
    
    # Update Additional Details to be after Note
    if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "custom_additional_details_section"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient", "fieldname": "custom_additional_details_section"},
            "insert_after", "women_health_note")
    
    # ============ PATIENT ENCOUNTER ============
    # Fix Women Health section to be after social_history_section (not inside it)
    
    # First, find the correct insert_after - should be after social history section's last field
    if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": "encounter_women_health_section"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient Encounter", "fieldname": "encounter_women_health_section"},
            "insert_after", "social_history_section")
    
    # Add Section Break before Children Details for full width in Encounter
    encounter_children_section = {
        "Patient Encounter": [
            {
                "fieldname": "encounter_women_health_children_section",
                "fieldtype": "Section Break",
                "label": "Children Details",
                "insert_after": "encounter_genitourinary_symptoms",
            },
        ]
    }
    create_custom_fields(encounter_children_section, update=True)
    
    # Update encounter_children_details to be after the section
    if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": "encounter_children_details"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient Encounter", "fieldname": "encounter_children_details"},
            {
                "insert_after": "encounter_women_health_children_section",
                "label": "Children"
            })
    
    # Update Note to be after children_details (at the end)
    if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": "encounter_women_health_note"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient Encounter", "fieldname": "encounter_women_health_note"},
            "insert_after", "encounter_children_details")
    
    frappe.db.commit()
    
    # Clear cache
    frappe.clear_cache(doctype="Patient")
    frappe.clear_cache(doctype="Patient Encounter")

