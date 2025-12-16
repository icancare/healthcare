"""
Update Vital Signs Labels

This patch updates the field labels in Vital Signs doctype:
- Changes 'Waist' to 'Waist Circumference'
- Changes 'Hip' to 'Hip Circumference'

The 'Waist Circumference' row in Computed Values table is removed via JS changes.
"""

import frappe


def execute():
    """Update Vital Signs field labels"""
    
    print("\n" + "="*60)
    print("Updating Vital Signs Labels")
    print("="*60)
    
    # Update waist_circumference label
    print("\n--- Updating Field Labels ---")
    
    try:
        # Update the DocField directly
        frappe.db.set_value(
            "DocField",
            {"parent": "Vital Signs", "fieldname": "waist_circumference"},
            "label",
            "Waist Circumference"
        )
        print("  ✓ Updated 'waist_circumference' label to 'Waist Circumference'")
    except Exception as e:
        print(f"  ✗ Error updating waist_circumference label: {str(e)}")
    
    try:
        # Update the DocField directly
        frappe.db.set_value(
            "DocField",
            {"parent": "Vital Signs", "fieldname": "hip_circumference"},
            "label",
            "Hip Circumference"
        )
        print("  ✓ Updated 'hip_circumference' label to 'Hip Circumference'")
    except Exception as e:
        print(f"  ✗ Error updating hip_circumference label: {str(e)}")
    
    # Clear cache to reflect changes
    frappe.clear_cache(doctype="Vital Signs")
    
    frappe.db.commit()
    
    print("\n" + "="*60)
    print("✓ Vital Signs Labels Updated Successfully!")
    print("="*60 + "\n")

