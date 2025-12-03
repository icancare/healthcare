"""
Add predefined Relation Type data

This patch adds the standard list of relation types for medical history.
"""

import frappe


def execute():
    """Add predefined Relation Type data"""
    
    # Relation Types
    relations = [
        ("Self", "The patient themselves"),
        ("Father", "Patient's father"),
        ("Mother", "Patient's mother"),
        ("Spouse", "Patient's spouse/partner"),
        ("Siblings", "Patient's brothers/sisters"),
        ("Son", "Patient's son"),
        ("Daughter", "Patient's daughter"),
        ("Grandfather", "Patient's grandfather"),
        ("Grandmother", "Patient's grandmother"),
        ("Uncle", "Patient's uncle"),
        ("Aunt", "Patient's aunt"),
        ("Cousin", "Patient's cousin"),
        ("Friend", "Patient's friend"),
        ("Neighbor", "Patient's neighbor"),
        ("Caregiver", "Patient's caregiver"),
        ("Guardian", "Patient's legal guardian"),
        ("Family", "General family member"),
        ("Other", "Other relation"),
    ]
    
    # Insert Relation Types
    for relation_name, description in relations:
        if not frappe.db.exists("Relation Type", relation_name):
            doc = frappe.new_doc("Relation Type")
            doc.relation_name = relation_name
            doc.description = description
            doc.flags.ignore_permissions = True
            doc.insert()
    
    frappe.db.commit()

