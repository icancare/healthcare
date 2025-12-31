import frappe

def execute():
    """Remove 'Can be filled by' and 'Done by' description from Step 1 and Step 2 section breaks"""
    
    # Remove description from section breaks - this is where the text was showing
    frappe.db.sql("""
        UPDATE `tabCustom Field` 
        SET description = '' 
        WHERE dt = 'Patient Encounter' 
        AND fieldname IN ('exam_step1_section', 'exam_step2_section')
    """)
    
    # Also hide the separate fields if they exist
    frappe.db.sql("""
        UPDATE `tabCustom Field` 
        SET hidden = 1 
        WHERE dt = 'Patient Encounter' 
        AND fieldname IN ('exam_filled_by', 'exam_step2_done_by')
    """)
    
    # Fix exam_physical_findings table position - should be after exam_step2_table_html
    frappe.db.sql("""
        UPDATE `tabCustom Field` 
        SET insert_after = 'exam_step2_table_html' 
        WHERE dt = 'Patient Encounter' 
        AND fieldname = 'exam_physical_findings'
    """)
    
    frappe.db.commit()
    
    # Clear cache to reflect changes
    frappe.clear_cache(doctype="Patient Encounter")

