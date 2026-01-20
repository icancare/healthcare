import frappe

def execute():
    """Fix exam_complaints table position - should be after exam_step1_table_html"""
    
    # Update exam_complaints to be inserted after exam_step1_table_html
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_complaints"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_complaints",
            {
                "insert_after": "exam_step1_table_html",
                "hidden": 0,
                "depends_on": "eval:doc.practitioner && doc.show_clinical_examination && doc.exam_complaints_status=='Complaints - Abnormal'"
            }
        )
    
    # Update exam_step2_section to be after exam_complaints
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_step2_section"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_step2_section",
            {
                "insert_after": "exam_complaints"
            }
        )
    
    frappe.db.commit()
    frappe.clear_cache(doctype="Patient Encounter")
    
    print("Fixed exam_complaints table position")






