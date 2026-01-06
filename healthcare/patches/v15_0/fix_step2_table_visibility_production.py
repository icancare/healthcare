import frappe

def execute():
    """
    Force fix Step 2 Physical Findings table visibility in production.
    The table should always be visible (hidden=0) - JS controls show/hide based on status.
    """
    
    # Update Custom Field directly in database
    custom_field_name = "Patient Encounter-exam_physical_findings"
    
    if frappe.db.exists("Custom Field", custom_field_name):
        # Force update hidden=0 and remove any depends_on
        frappe.db.sql("""
            UPDATE `tabCustom Field`
            SET hidden = 0, depends_on = ''
            WHERE name = %s
        """, (custom_field_name,))
        
        print(f"✓ Updated {custom_field_name}: hidden=0, depends_on=''")
    else:
        print(f"✗ Custom Field {custom_field_name} not found")
    
    # Also update the section field if it exists
    section_field_name = "Patient Encounter-exam_findings_section"
    if frappe.db.exists("Custom Field", section_field_name):
        frappe.db.sql("""
            UPDATE `tabCustom Field`
            SET hidden = 0, depends_on = ''
            WHERE name = %s
        """, (section_field_name,))
        print(f"✓ Updated {section_field_name}: hidden=0, depends_on=''")
    
    frappe.db.commit()
    
    # Clear all caches
    frappe.clear_cache(doctype="Patient Encounter")
    frappe.clear_cache(doctype="Custom Field")
    
    print("✓ Step 2 Physical Findings table visibility fix applied!")

