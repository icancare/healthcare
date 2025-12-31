import frappe

def execute():
    """Hide duplicate exam fields - we use HTML form instead"""
    
    # Hide the ERPNext exam_complaints_status field (we use HTML dropdown)
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_complaints_status"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_complaints_status",
            {
                "hidden": 1
            }
        )
    
    # Hide exam_filled_by field (removed from requirements)
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_filled_by"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_filled_by",
            {
                "hidden": 1
            }
        )
    
    # Make sure exam_complaints table is visible when Abnormal
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_complaints"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_complaints",
            {
                "hidden": 0,
                "depends_on": "eval:doc.practitioner && doc.show_clinical_examination && doc.exam_complaints_status=='Complaints - Abnormal'"
            }
        )
    
    frappe.db.commit()
    frappe.clear_cache(doctype="Patient Encounter")
    
    print("Hidden duplicate exam fields")


