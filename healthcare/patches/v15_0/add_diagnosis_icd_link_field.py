"""
Add ICD-11 Code Value Link Field to Diagnosis

This patch adds the icd11_code_value Link field that connects to Code Value
for proper ICD-11 code selection with auto-fetch of code and URI.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """Add ICD-11 Code Value Link field to Diagnosis"""
    
    print("\n--- Adding ICD-11 Code Value Link Field ---")
    
    custom_fields = {
        "Diagnosis": [
            {
                "fieldname": "icd11_code_value",
                "fieldtype": "Link",
                "label": "ICD-11 Code (Select)",
                "insert_after": "icd_coding_section",
                "options": "Code Value",
                "description": "Select ICD-11 code from Code Value master"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    
    # Update icd11_code field to fetch from icd11_code_value
    if frappe.db.exists("Custom Field", {"dt": "Diagnosis", "fieldname": "icd11_code"}):
        frappe.db.set_value("Custom Field", 
            {"dt": "Diagnosis", "fieldname": "icd11_code"},
            {
                "fetch_from": "icd11_code_value.code_value",
                "read_only": 1,
                "label": "ICD-11 Code"
            }
        )
        print("  ✓ Updated icd11_code to fetch from icd11_code_value")
    
    # Update icd11_uri field to fetch from icd11_code_value
    if frappe.db.exists("Custom Field", {"dt": "Diagnosis", "fieldname": "icd11_uri"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Diagnosis", "fieldname": "icd11_uri"},
            {
                "fetch_from": "icd11_code_value.official_url",
                "read_only": 1
            }
        )
        print("  ✓ Updated icd11_uri to fetch from icd11_code_value")
    
    frappe.db.commit()
    print("  ✓ Added icd11_code_value Link field to Diagnosis")

