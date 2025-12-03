"""
Remove 'who' field from Social History and Medical/Surgical History child tables
and rename 'relation_type' label to 'Who'

This patch:
1. Removes the 'who' field from Patient and Patient Encounter History tables
2. The 'relation_type' field label is already renamed to 'Who' in the doctype JSON files
"""

import frappe


def execute():
    """Remove 'who' field from History child tables"""
    
    # List of doctypes that need the 'who' field removed
    doctypes_to_update = [
        # Medical and Surgical History
        "Patient Medical History",
        "Patient Surgical History",
        "Patient Encounter Medical History",
        "Patient Encounter Surgical History",
        # Tobacco and Substance History
        "Patient Smokeless Tobacco History",
        "Patient Smoking Tobacco History",
        "Patient Substance Abuse History",
        "Patient Oral Habits History",
        "Patient Encounter Smokeless Tobacco History",
        "Patient Encounter Smoking Tobacco History",
        "Patient Encounter Substance Abuse History",
        "Patient Encounter Oral Habits History",
        # Extended Social History
        "Patient Diet History",
        "Patient Occupational Exposure History",
        "Patient Environmental Factors History",
        "Patient Encounter Diet History",
        "Patient Encounter Occupational Exposure History",
        "Patient Encounter Environmental Factors History",
    ]
    
    for doctype in doctypes_to_update:
        # Check if the doctype exists
        if not frappe.db.exists("DocType", doctype):
            continue
            
        # Remove Custom Field if exists
        custom_field_name = f"{doctype}-who"
        if frappe.db.exists("Custom Field", custom_field_name):
            frappe.delete_doc("Custom Field", custom_field_name, force=True)
            frappe.db.commit()
        
        # Check if 'who' column exists in the table
        table_name = f"tab{doctype}"
        if frappe.db.has_column(doctype, "who"):
            # We don't delete the column here as it might have data
            # The column will be ignored by the system since it's not in the doctype definition
            # If you want to completely remove it, uncomment the following:
            # frappe.db.sql(f"ALTER TABLE `{table_name}` DROP COLUMN `who`")
            pass
    
    # Clear cache to reflect changes
    frappe.clear_cache()
