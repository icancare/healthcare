import frappe

def execute():
    """
    Final fix for Step 1 complaints:
    1. exam_complaints table - visible, no depends_on, JS controls visibility
    2. Hide duplicate fields
    3. Ensure correct field order
    """
    
    # 1. exam_complaints table - VISIBLE, NO depends_on - JS will control visibility
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_complaints"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_complaints",
            {
                "insert_after": "exam_step1_table_html",
                "hidden": 0,  # Visible - JS will hide when needed
                "depends_on": ""  # No depends_on - JS controls this
            }
        )
    
    # 2. Hide duplicate section - keep only exam_step1_section
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_complaints_section"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_complaints_section",
            {"hidden": 1}
        )
    
    # 3. Hide exam_complaints_status - we use HTML dropdown
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_complaints_status"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_complaints_status",
            {"hidden": 1}
        )
    
    # 4. Hide exam_filled_by - removed from requirements
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_filled_by"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_filled_by",
            {"hidden": 1}
        )
    
    # 5. Ensure exam_step2_section comes after exam_complaints
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_step2_section"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_step2_section",
            {"insert_after": "exam_complaints"}
        )
    
    frappe.db.commit()
    frappe.clear_cache(doctype="Patient Encounter")
    
    print("Fixed Step 1 complaints configuration - table visible, no depends_on")

