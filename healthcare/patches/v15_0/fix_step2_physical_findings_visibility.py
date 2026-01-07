import frappe

def execute():
    """
    Fix Step 2 Physical Findings table visibility:
    1. exam_physical_findings table - visible, no depends_on, JS controls visibility
    2. exam_physical_section - HIDE this old section that interferes with Step 2
    Same approach as Step 1 complaints table fix
    """
    
    # 1. exam_physical_findings table - VISIBLE, NO depends_on - JS will control visibility
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_physical_findings"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_physical_findings",
            {
                "hidden": 0,  # Visible - JS will hide when needed
                "depends_on": ""  # No depends_on - JS controls this
            }
        )
        print("✓ Fixed exam_physical_findings - removed depends_on, JS will control visibility")
    else:
        print("✗ exam_physical_findings field not found")
    
    # 2. HIDE exam_physical_section - this old section interferes with Step 2 layout
    # The new Step 2 uses exam_step2_section instead
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_physical_section"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_physical_section",
            {
                "hidden": 1  # Hide this old section
            }
        )
        print("✓ Hidden exam_physical_section - old section that interferes with Step 2")
    else:
        print("✗ exam_physical_section field not found")
    
    frappe.db.commit()
    frappe.clear_cache(doctype="Patient Encounter")
    
    print("Step 2 Physical Findings table visibility fix completed!")



