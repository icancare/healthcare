# -*- coding: utf-8 -*-
# Copyright (c) 2024, iCanCare and contributors
# For license information, please see license.txt

import frappe

def execute():
    """
    Merge Family Medical History into Medical History section
    - Move patient_family_medical_history table inside Medical History section
    - Remove the separate Family Medical History section
    """
    
    # ==========================================
    # PATIENT DOCTYPE
    # ==========================================
    
    # Update Family Medical History table to be inside Medical History section
    # Change insert_after from patient_family_medical_history_section to patient_medical_history
    family_table = frappe.db.get_value("Custom Field", 
        {"dt": "Patient", "fieldname": "patient_family_medical_history"},
        "name"
    )
    
    if family_table:
        frappe.db.set_value("Custom Field", family_table, {
            "insert_after": "patient_medical_history",
            "label": "Family Medical History"
        })
        print("✓ Moved patient_family_medical_history table inside Medical History section")
    
    # Delete the separate Family Medical History section
    family_section = frappe.db.get_value("Custom Field",
        {"dt": "Patient", "fieldname": "patient_family_medical_history_section"},
        "name"
    )
    
    if family_section:
        frappe.delete_doc("Custom Field", family_section, force=True)
        print("✓ Removed patient_family_medical_history_section")
    
    # ==========================================
    # PATIENT ENCOUNTER DOCTYPE
    # ==========================================
    
    # Check if Patient Encounter has similar fields
    encounter_family_table = frappe.db.get_value("Custom Field",
        {"dt": "Patient Encounter", "fieldname": "encounter_family_medical_history"},
        "name"
    )
    
    if encounter_family_table:
        # Find the medical history table in encounter
        encounter_medical = frappe.db.get_value("Custom Field",
            {"dt": "Patient Encounter", "fieldname": "custom_medical_history"},
            "name"
        )
        
        if encounter_medical:
            frappe.db.set_value("Custom Field", encounter_family_table, {
                "insert_after": "custom_medical_history",
                "label": "Family Medical History"
            })
            print("✓ Moved encounter_family_medical_history table inside Medical History section")
    
    # Delete the separate Family Medical History section in Encounter
    encounter_family_section = frappe.db.get_value("Custom Field",
        {"dt": "Patient Encounter", "fieldname": "encounter_family_medical_history_section"},
        "name"
    )
    
    if encounter_family_section:
        frappe.delete_doc("Custom Field", encounter_family_section, force=True)
        print("✓ Removed encounter_family_medical_history_section")
    
    frappe.db.commit()
    print("\n✓ Family Medical History merged into Medical History section successfully!")

