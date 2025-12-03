"""
Add Family Medical History fields to Patient and Patient Encounter

This patch adds the Family Medical History child table to both Patient and Patient Encounter doctypes.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """Add Family Medical History fields to Patient and Patient Encounter"""
    
    custom_fields = {
        "Patient": [
            {
                "fieldname": "patient_family_medical_history_section",
                "fieldtype": "Section Break",
                "label": "Family Medical History",
                "insert_after": "patient_medical_history",
                "collapsible": 1,
            },
            {
                "fieldname": "patient_family_medical_history",
                "fieldtype": "Table",
                "label": "Family Medical History",
                "options": "Patient Family Medical History",
                "insert_after": "patient_family_medical_history_section",
            },
        ],
        "Patient Encounter": [
            {
                "fieldname": "encounter_family_medical_history_section",
                "fieldtype": "Section Break",
                "label": "Family Medical History",
                "insert_after": "custom_medical_history",
                "collapsible": 1,
            },
            {
                "fieldname": "encounter_family_medical_history",
                "fieldtype": "Table",
                "label": "Family Medical History",
                "options": "Patient Encounter Family Medical History",
                "insert_after": "encounter_family_medical_history_section",
            },
        ],
    }
    
    create_custom_fields(custom_fields, update=True)
    
    # Fix insert_after if it was set incorrectly before
    if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": "encounter_family_medical_history_section"}):
        frappe.db.set_value("Custom Field", 
            {"dt": "Patient Encounter", "fieldname": "encounter_family_medical_history_section"},
            "insert_after", "custom_medical_history")
    
    # Add more relation types for family medical history
    additional_relations = [
        ("Grandfather (Paternal)", "Patient's paternal grandfather"),
        ("Grandmother (Paternal)", "Patient's paternal grandmother"),
        ("Grandfather (Maternal)", "Patient's maternal grandfather"),
        ("Grandmother (Maternal)", "Patient's maternal grandmother"),
        ("Brother", "Patient's brother"),
        ("Sister", "Patient's sister"),
        ("Nephew", "Patient's nephew"),
        ("Niece", "Patient's niece"),
        ("Great Grandfather", "Patient's great grandfather"),
        ("Great Grandmother", "Patient's great grandmother"),
    ]
    
    for relation_name, description in additional_relations:
        if not frappe.db.exists("Relation Type", relation_name):
            doc = frappe.new_doc("Relation Type")
            doc.relation_name = relation_name
            doc.description = description
            doc.flags.ignore_permissions = True
            doc.insert()
    
    frappe.db.commit()

