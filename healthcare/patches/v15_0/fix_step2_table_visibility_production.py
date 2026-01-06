import frappe

def execute():
    """
    Fix Step 2 Physical Findings table visibility - same approach as Step 1.
    Show table when status is Abnormal (using depends_on like Step 1 complaints table).
    """
    
    depends_on_value = "eval:doc.practitioner && doc.show_clinical_examination && doc.exam_step2_status=='Abnormal'"
    
    # Update exam_physical_findings table - same pattern as exam_complaints
    field_name = "Patient Encounter-exam_physical_findings"
    if frappe.db.exists("Custom Field", field_name):
        frappe.db.sql("""
            UPDATE `tabCustom Field`
            SET depends_on = %s, hidden = 0
            WHERE name = %s
        """, (depends_on_value, field_name))
        print(f"✓ Updated {field_name}")
    else:
        print(f"✗ {field_name} not found")
    
    # Also update the section field
    section_name = "Patient Encounter-exam_findings_section"
    if frappe.db.exists("Custom Field", section_name):
        frappe.db.sql("""
            UPDATE `tabCustom Field`
            SET depends_on = %s, hidden = 0
            WHERE name = %s
        """, (depends_on_value, section_name))
        print(f"✓ Updated {section_name}")
    
    frappe.db.commit()
    frappe.clear_cache(doctype="Patient Encounter")
    frappe.clear_cache(doctype="Custom Field")
    
    print("✓ Step 2 Physical Findings table visibility fix applied!")
