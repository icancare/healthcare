"""
Update Medical History When Label

This patch updates the 'when' field label in Patient Medical History:
- Changes label from 'When' to 'Since When'
- Updates description/help text
"""

import frappe


def execute():
    """Update Medical History when field label"""
    
    print("\n" + "="*60)
    print("Updating Medical History When Label")
    print("="*60)
    
    try:
        # Update the DocField directly
        frappe.db.set_value(
            "DocField",
            {"parent": "Patient Medical History", "fieldname": "when"},
            {
                "label": "Since When",
                "description": "Enter year, month and day, eg: 2023, Jan 3, 2023"
            }
        )
        print("  ✓ Updated 'when' field label to 'Since When'")
    except Exception as e:
        print(f"  - Note: {str(e)}")
    
    # Clear cache
    frappe.clear_cache(doctype="Patient Medical History")
    frappe.clear_cache(doctype="Patient")
    
    frappe.db.commit()
    
    print("\n" + "="*60)
    print("✓ Medical History When Label Updated!")
    print("="*60 + "\n")

