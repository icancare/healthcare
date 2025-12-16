import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """
    Add custom fields to Complaint DocType:
    - complaint_code
    - department (Link to Medical Department)
    """
    print("=" * 60)
    print("Adding Custom Fields to Complaint")
    print("=" * 60)
    
    custom_fields = {
        "Complaint": [
            {
                "fieldname": "complaint_code",
                "label": "Complaint Code",
                "fieldtype": "Data",
                "insert_after": "complaints",
                "unique": 1,
                "in_list_view": 1,
                "in_standard_filter": 1,
            },
            {
                "fieldname": "department",
                "label": "Department",
                "fieldtype": "Link",
                "options": "Medical Department",
                "insert_after": "complaint_code",
                "in_list_view": 1,
                "in_standard_filter": 1,
            },
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    
    print("  ✓ Added complaint_code field")
    print("  ✓ Added department field")
    print()
    print("=" * 60)
    print("✓ Complaint Custom Fields Added!")
    print("=" * 60)
    
    frappe.db.commit()


