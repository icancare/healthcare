"""
Make Allergy & Immunization section collapsible in Patient Encounter

This patch makes the custom_allergy__immunization section collapsible.
"""

import frappe


def execute():
    """Make Allergy & Immunization section collapsible"""
    
    # Make Allergy & Immunization section collapsible in Patient Encounter
    if frappe.db.exists("Custom Field", {"dt": "Patient Encounter", "fieldname": "custom_allergy__immunization"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient Encounter", "fieldname": "custom_allergy__immunization"},
            "collapsible", 1)
        print("Made Patient Encounter.custom_allergy__immunization collapsible")
        frappe.db.commit()

