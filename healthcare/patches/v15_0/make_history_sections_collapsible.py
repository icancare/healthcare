"""
Make history sections collapsible and fix Family Medical History position

This patch:
1. Makes Allergy, Immunization, Medical History, Surgical History sections collapsible in Patient
2. Makes Allergy & Immunization section collapsible in Patient Encounter
3. Moves Family Medical History after Medical History (before Surgical History) in Patient Encounter
"""

import frappe


def execute():
    """Make history sections collapsible and fix positions"""
    
    # 1. Make Patient sections collapsible
    patient_sections_to_make_collapsible = [
        "patient_allergy_section",
        "patient_immunization_section", 
        "patient_medical_history_section",
        "patient_surgical_history_section",
    ]
    
    for fieldname in patient_sections_to_make_collapsible:
        if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": fieldname}):
            frappe.db.set_value("Custom Field", 
                {"dt": "Patient", "fieldname": fieldname},
                "collapsible", 1)
            print(f"Made Patient.{fieldname} collapsible")
    
    # 2. Make Allergy & Immunization section collapsible in Patient Encounter
    # The field is custom_allergy__immunization (Custom Field)
    if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": "custom_allergy__immunization"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient Encounter", "fieldname": "custom_allergy__immunization"},
            "collapsible", 1)
        print("Made Patient Encounter.custom_allergy__immunization collapsible")
    
    # 3. Move Family Medical History after Medical History (before Surgical History)
    # Change insert_after from custom_medical_history to custom_medical_history
    # Then change surgical_history_section to insert_after encounter_family_medical_history
    
    if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": "encounter_family_medical_history_section"}):
        # Family Medical History section should be after custom_medical_history
        frappe.db.set_value("Custom Field",
            {"dt": "Patient Encounter", "fieldname": "encounter_family_medical_history_section"},
            "insert_after", "custom_medical_history")
        print("Set encounter_family_medical_history_section insert_after to custom_medical_history")
    
    # Update surgical_history_section to be after encounter_family_medical_history
    if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": "surgical_history_section"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient Encounter", "fieldname": "surgical_history_section"},
            "insert_after", "encounter_family_medical_history")
        print("Set surgical_history_section insert_after to encounter_family_medical_history")
    
    frappe.db.commit()
    
    # Clear schema cache
    frappe.clear_cache(doctype="Patient")
    frappe.clear_cache(doctype="Patient Encounter")

