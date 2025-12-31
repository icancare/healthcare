import frappe

def execute():
    """
    Fix Step 1 field order properly:
    1. exam_step1_section
    2. exam_step1_table_html (HTML form)
    3. exam_complaints (Table) - THIS MUST COME AFTER HTML
    4. exam_step2_section
    """
    
    # 1. exam_step1_table_html should be after exam_step1_section
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_step1_table_html"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_step1_table_html",
            {"insert_after": "exam_step1_section", "hidden": 0}
        )
    
    # 2. exam_complaints should be after exam_step1_table_html
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_complaints"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_complaints",
            {"insert_after": "exam_step1_table_html", "hidden": 0, "depends_on": ""}
        )
    
    # 3. exam_step2_section should be after exam_complaints
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_step2_section"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_step2_section",
            {"insert_after": "exam_complaints"}
        )
    
    # 4. Hide exam_physical_section (duplicate)
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_physical_section"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_physical_section",
            {"hidden": 1}
        )
    
    # 5. Hide exam_filled_by
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_filled_by"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_filled_by",
            {"hidden": 1, "insert_after": "exam_complaints_status"}  # Move it away
        )
    
    # 6. Hide exam_complaints_section (duplicate)
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_complaints_section"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_complaints_section",
            {"hidden": 1}
        )
    
    frappe.db.commit()
    
    # Rebuild field order
    frappe.clear_cache(doctype="Patient Encounter")
    
    print("Fixed Step 1 field order - exam_complaints now after exam_step1_table_html")


