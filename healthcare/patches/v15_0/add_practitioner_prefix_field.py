"""
Add Prefix field to Healthcare Practitioner

This patch adds:
- Prefix field (Dr, Mr, Mrs, Ms, Prof, etc.)
- Makes Designation editable
- Adds common prefixes as options
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """Add Prefix field and update Designation"""
    
    print("\n" + "="*60)
    print("Adding Prefix Field to Healthcare Practitioner")
    print("="*60)
    
    # Add Prefix custom field
    add_prefix_field()
    
    # Make Designation editable
    make_designation_editable()
    
    # Create common prefixes in Salutation doctype
    create_common_prefixes()
    
    frappe.db.commit()
    
    print("\n" + "="*60)
    print("✓ Healthcare Practitioner Fields Updated!")
    print("="*60 + "\n")


def add_prefix_field():
    """Add Prefix field before First Name"""
    
    print("\n--- Adding Prefix Field ---")
    
    custom_fields = {
        "Healthcare Practitioner": [
            {
                "fieldname": "prefix",
                "fieldtype": "Link",
                "label": "Prefix",
                "options": "Salutation",
                "insert_after": "naming_series",
                "in_list_view": 0,
                "in_standard_filter": 0
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    print("  ✓ Added Prefix field (Link to Salutation)")


def make_designation_editable():
    """Make Designation field editable using Property Setter"""
    
    print("\n--- Updating Designation Field ---")
    
    from frappe.custom.doctype.property_setter.property_setter import make_property_setter
    
    try:
        # Remove read_only
        make_property_setter(
            "Healthcare Practitioner",
            "designation",
            "read_only",
            0,
            "Check"
        )
        print("  ✓ Removed read_only from Designation")
        
        # Remove fetch_from
        make_property_setter(
            "Healthcare Practitioner",
            "designation",
            "fetch_from",
            "",
            "Data"
        )
        print("  ✓ Removed fetch_from from Designation")
        
    except Exception as e:
        print(f"  - Error: {str(e)}")


def create_common_prefixes():
    """Create common prefixes/salutations"""
    
    print("\n--- Creating Common Prefixes ---")
    
    prefixes = [
        {"salutation": "Dr", "description": "Doctor"},
        {"salutation": "Mr", "description": "Mister"},
        {"salutation": "Mrs", "description": "Married Woman"},
        {"salutation": "Ms", "description": "Woman"},
        {"salutation": "Prof", "description": "Professor"},
        {"salutation": "Er", "description": "Engineer"},
        {"salutation": "CA", "description": "Chartered Accountant"},
    ]
    
    for prefix in prefixes:
        if not frappe.db.exists("Salutation", prefix["salutation"]):
            try:
                doc = frappe.new_doc("Salutation")
                doc.salutation = prefix["salutation"]
                doc.flags.ignore_permissions = True
                doc.insert()
                print(f"  ✓ Created: {prefix['salutation']}")
            except Exception as e:
                print(f"  - Error creating {prefix['salutation']}: {str(e)}")
        else:
            print(f"  - Exists: {prefix['salutation']}")

