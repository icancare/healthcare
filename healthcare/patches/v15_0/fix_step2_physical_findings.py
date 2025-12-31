import frappe

def execute():
    """
    Fix Step 2 Physical Examination:
    1. Remove 'Can be filled by' and 'Done by' descriptions from section breaks
    2. Fix exam_physical_findings table position
    3. Hide unnecessary fields in Clinical Exam Finding (for Step 2 use)
    4. Make Location a Select field with body part options
    """
    
    # 1. Remove description from section breaks
    frappe.db.sql("""
        UPDATE `tabCustom Field` 
        SET description = '' 
        WHERE dt = 'Patient Encounter' 
        AND fieldname IN ('exam_step1_section', 'exam_step2_section')
    """)
    
    # 2. Hide the separate filled_by and done_by fields
    frappe.db.sql("""
        UPDATE `tabCustom Field` 
        SET hidden = 1 
        WHERE dt = 'Patient Encounter' 
        AND fieldname IN ('exam_filled_by', 'exam_step2_done_by')
    """)
    
    # 3. Fix exam_physical_findings table position - should be after exam_step2_table_html
    frappe.db.sql("""
        UPDATE `tabCustom Field` 
        SET insert_after = 'exam_step2_table_html' 
        WHERE dt = 'Patient Encounter' 
        AND fieldname = 'exam_physical_findings'
    """)
    
    # 4. Hide ALL unnecessary fields in Clinical Exam Finding doctype for Step 2
    # Only keep: location, abnormality, note
    fields_to_hide = [
        'side',             # Not needed - location already includes side info
        'status',           # Not needed - always Abnormal in Step 2
        'column_break_1',   # Column break
        'section_break_1',  # Lesion Details section
        'size_length',
        'size_width',
        'size_height',
        'column_break_2',
        'color',
        'shape',
        'texture',
        'section_break_2',
        'description',
        'palpation'
    ]
    
    for fieldname in fields_to_hide:
        frappe.db.sql("""
            UPDATE `tabDocField` 
            SET hidden = 1 
            WHERE parent = 'Clinical Exam Finding' 
            AND fieldname = %s
        """, fieldname)
    
    frappe.db.commit()
    
    # Clear cache to reflect changes
    frappe.clear_cache(doctype="Patient Encounter")
    frappe.clear_cache(doctype="Clinical Exam Finding")

