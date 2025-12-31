import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    """Add exam_step2_status field and exam_lesion_examination child table for Step 2 and Step 3"""
    
    # Create Lesion Examination child doctype if not exists
    if not frappe.db.exists('DocType', 'Clinical Exam Lesion'):
        frappe.get_doc({
            'doctype': 'DocType',
            'name': 'Clinical Exam Lesion',
            'module': 'Healthcare',
            'custom': 0,
            'istable': 1,
            'editable_grid': 1,
            'track_changes': 0,
            'fields': [
                {'fieldname': 'location', 'fieldtype': 'Data', 'label': 'Location', 'in_list_view': 1},
                {'fieldname': 'size_length', 'fieldtype': 'Int', 'label': 'Length (mm)', 'in_list_view': 1},
                {'fieldname': 'size_width', 'fieldtype': 'Int', 'label': 'Width (mm)', 'in_list_view': 1},
                {'fieldname': 'color', 'fieldtype': 'Data', 'label': 'Color', 'in_list_view': 1},
                {'fieldname': 'shape', 'fieldtype': 'Data', 'label': 'Shape'},
                {'fieldname': 'margin', 'fieldtype': 'Data', 'label': 'Margin'},
                {'fieldname': 'description', 'fieldtype': 'Data', 'label': 'Description'},
                {'fieldname': 'palpation', 'fieldtype': 'Data', 'label': 'Palpation'},
                {'fieldname': 'note', 'fieldtype': 'Small Text', 'label': 'Notes'}
            ],
            'permissions': []
        }).insert(ignore_permissions=True)
        frappe.db.commit()
    
    # Add custom fields to Patient Encounter
    custom_fields = {
        'Patient Encounter': [
            {
                'fieldname': 'exam_step2_status',
                'fieldtype': 'Select',
                'label': 'Step 2 Status',
                'options': '\nNormal\nAbnormal',
                'insert_after': 'exam_step2_section',
                'hidden': 1
            },
            {
                'fieldname': 'exam_lesion_examination',
                'fieldtype': 'Table',
                'label': 'Lesion Examination Details',
                'options': 'Clinical Exam Lesion',
                'insert_after': 'exam_diagram_lesions',
                'hidden': 1
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    frappe.db.commit()


