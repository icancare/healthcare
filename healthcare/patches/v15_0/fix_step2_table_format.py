import frappe

def execute():
    """
    Fix Step 2 Physical Findings table to match Step 1 format:
    - Add body_part Select field
    - Change location to Select with all locations
    - Change abnormality to Select with all abnormalities
    - Hide unnecessary fields (side, status, lesion fields)
    """
    
    # All body parts for Step 2
    body_parts = "\nFace\nNeck\nMouth\nTeeth\nThroat"
    
    # All locations - will be filtered by JS based on body_part
    all_locations = ""
    
    # All abnormalities - will be filtered by JS based on body_part
    all_abnormalities = ""
    
    # Check if body_part field exists in Clinical Exam Finding
    existing_fields = frappe.db.sql("""
        SELECT fieldname FROM `tabDocField` 
        WHERE parent='Clinical Exam Finding'
    """, as_dict=True)
    existing_fieldnames = [f['fieldname'] for f in existing_fields]
    
    # Add body_part field if not exists
    if 'body_part' not in existing_fieldnames:
        # Get max idx
        max_idx = frappe.db.sql("""
            SELECT MAX(idx) as max_idx FROM `tabDocField` 
            WHERE parent='Clinical Exam Finding'
        """)[0][0] or 0
        
        # Insert body_part field at beginning
        frappe.db.sql("""
            UPDATE `tabDocField` SET idx = idx + 1 
            WHERE parent='Clinical Exam Finding'
        """)
        
        frappe.db.sql("""
            INSERT INTO `tabDocField` 
            (name, parent, parenttype, parentfield, fieldname, label, fieldtype, options, idx, reqd)
            VALUES 
            (%s, 'Clinical Exam Finding', 'DocType', 'fields', 'body_part', 'Body Part', 'Select', %s, 1, 1)
        """, (frappe.generate_hash(length=10), body_parts))
    else:
        # Update body_part field
        frappe.db.sql("""
            UPDATE `tabDocField` 
            SET fieldtype='Select', options=%s, hidden=0, reqd=1
            WHERE parent='Clinical Exam Finding' AND fieldname='body_part'
        """, body_parts)
    
    # Change location field to Data (text) - options will be set dynamically by JS
    frappe.db.sql("""
        UPDATE `tabDocField` 
        SET fieldtype='Data', options='', hidden=0, label='Location'
        WHERE parent='Clinical Exam Finding' AND fieldname='location'
    """)
    
    # Change abnormality field to Data (text) - options will be set dynamically by JS
    frappe.db.sql("""
        UPDATE `tabDocField` 
        SET fieldtype='Data', options='', hidden=0, label='Abnormality'
        WHERE parent='Clinical Exam Finding' AND fieldname='abnormality'
    """)
    
    # Unhide note field
    frappe.db.sql("""
        UPDATE `tabDocField` 
        SET hidden=0
        WHERE parent='Clinical Exam Finding' AND fieldname='note'
    """)
    
    # Hide unnecessary fields
    fields_to_hide = [
        'side',
        'status', 
        'column_break_1',
        'section_break_1',
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
            SET hidden=1 
            WHERE parent='Clinical Exam Finding' AND fieldname=%s
        """, fieldname)
    
    # Fix field order - body_part should be first, then location, then abnormality, then note
    frappe.db.sql("""
        UPDATE `tabDocField` SET idx=1, in_list_view=1, columns=2 WHERE parent='Clinical Exam Finding' AND fieldname='body_part'
    """)
    frappe.db.sql("""
        UPDATE `tabDocField` SET idx=2, in_list_view=1, columns=3 WHERE parent='Clinical Exam Finding' AND fieldname='location'
    """)
    frappe.db.sql("""
        UPDATE `tabDocField` SET idx=3, in_list_view=1, columns=3 WHERE parent='Clinical Exam Finding' AND fieldname='abnormality'
    """)
    frappe.db.sql("""
        UPDATE `tabDocField` SET idx=4, in_list_view=0 WHERE parent='Clinical Exam Finding' AND fieldname='note'
    """)
    
    frappe.db.commit()
    
    # Clear cache
    frappe.clear_cache(doctype="Patient Encounter")
    frappe.clear_cache(doctype="Clinical Exam Finding")

