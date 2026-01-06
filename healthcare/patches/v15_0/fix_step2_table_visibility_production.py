import frappe

def execute():
    """
    Fix Step 2 Physical Findings table visibility - same as Step 1.
    Set depends_on to empty and hidden=0. JS will control visibility.
    """
    
    # Update exam_physical_findings table - same as exam_complaints (empty depends_on)
    field_name = "Patient Encounter-exam_physical_findings"
    if frappe.db.exists("Custom Field", field_name):
        frappe.db.sql("""
            UPDATE `tabCustom Field`
            SET depends_on = '', hidden = 0
            WHERE name = %s
        """, (field_name,))
        print(f"✓ Updated {field_name}: depends_on='', hidden=0")
    else:
        print(f"✗ {field_name} not found")
    
    frappe.db.commit()
    frappe.clear_cache(doctype="Patient Encounter")
    frappe.clear_cache(doctype="Custom Field")
    
    print("✓ Step 2 Physical Findings table fix applied!")
