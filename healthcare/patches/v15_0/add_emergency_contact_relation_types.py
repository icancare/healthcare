"""
Add additional Relation Types for Emergency Contact

This patch adds Friend, Neighbor, Caregiver, Guardian relation types.
"""

import frappe


def execute():
    """Add additional Relation Types for Emergency Contact"""
    
    # Additional Relation Types for Emergency Contact
    relations = [
        ("Friend", "Patient's friend"),
        ("Neighbor", "Patient's neighbor"),
        ("Caregiver", "Patient's caregiver"),
        ("Guardian", "Patient's legal guardian"),
        ("Child", "Patient's child (general)"),
        ("Sibling", "Patient's sibling (singular)"),
    ]
    
    # Insert Relation Types if not exists
    for relation_name, description in relations:
        if not frappe.db.exists("Relation Type", relation_name):
            doc = frappe.new_doc("Relation Type")
            doc.relation_name = relation_name
            doc.description = description
            doc.flags.ignore_permissions = True
            doc.insert()
    
    frappe.db.commit()

