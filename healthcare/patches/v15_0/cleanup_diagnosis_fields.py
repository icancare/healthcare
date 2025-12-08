"""
Cleanup Diagnosis Fields

This patch removes unwanted custom fields from Diagnosis:
- is_chronic (not needed)
- clinical_category (already have Diagnosis Category)
- icd11_code_value, icd11_code, icd11_uri (already in Medical Coding section)
- icd_coding_section (not needed)
"""

import frappe


def execute():
    """Remove unwanted custom fields from Diagnosis"""
    
    print("\n" + "="*60)
    print("Cleaning up Diagnosis Fields")
    print("="*60)
    
    # Fields to remove
    fields_to_remove = [
        "is_chronic",
        "clinical_category",
        "icd11_code_value",
        "icd11_code",
        "icd11_uri",
        "icd_coding_section",
        "is_photo_medicine_eligible",
        "reporting_column"
    ]
    
    print("\n--- Removing Unwanted Custom Fields ---")
    
    for fieldname in fields_to_remove:
        # Check if custom field exists
        custom_field_name = f"Diagnosis-{fieldname}"
        if frappe.db.exists("Custom Field", custom_field_name):
            try:
                frappe.delete_doc("Custom Field", custom_field_name, force=True, ignore_permissions=True)
                print(f"  ✓ Removed field: {fieldname}")
            except Exception as e:
                print(f"  ✗ Error removing {fieldname}: {str(e)}")
        else:
            print(f"  - Field not found: {fieldname}")
    
    # Also drop columns from database if they exist
    print("\n--- Cleaning Database Columns ---")
    
    try:
        # Check which columns exist
        columns = frappe.db.sql("DESCRIBE `tabDiagnosis`", as_dict=True)
        column_names = [c['Field'] for c in columns]
        
        for fieldname in fields_to_remove:
            if fieldname in column_names:
                try:
                    frappe.db.sql(f"ALTER TABLE `tabDiagnosis` DROP COLUMN `{fieldname}`")
                    print(f"  ✓ Dropped column: {fieldname}")
                except Exception as e:
                    print(f"  - Column {fieldname} might be in use or already dropped")
            else:
                print(f"  - Column not in DB: {fieldname}")
    except Exception as e:
        print(f"  - Database cleanup skipped: {str(e)}")
    
    frappe.db.commit()
    
    print("\n" + "="*60)
    print("✓ Diagnosis Fields Cleanup Completed!")
    print("="*60 + "\n")

