"""
Remove Photo Medicine Eligible Field from Diagnosis

This patch removes:
- is_photo_medicine_eligible field
- reporting_column field (not needed)
"""

import frappe


def execute():
    """Remove is_photo_medicine_eligible and reporting_column from Diagnosis"""
    
    print("\n--- Removing Photo Medicine Eligible Field ---")
    
    fields_to_remove = [
        "is_photo_medicine_eligible",
        "reporting_column"
    ]
    
    for fieldname in fields_to_remove:
        custom_field_name = f"Diagnosis-{fieldname}"
        if frappe.db.exists("Custom Field", custom_field_name):
            try:
                frappe.delete_doc("Custom Field", custom_field_name, force=True, ignore_permissions=True)
                print(f"  ✓ Removed field: {fieldname}")
            except Exception as e:
                print(f"  ✗ Error removing {fieldname}: {str(e)}")
        else:
            print(f"  - Field not found: {fieldname}")
    
    frappe.db.commit()
    print("  ✓ Cleanup completed!")

