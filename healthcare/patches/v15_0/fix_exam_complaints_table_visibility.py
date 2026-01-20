import frappe

def execute():
    """Fix exam_complaints table visibility - show only when Abnormal status"""
    
    # Update the exam_complaints field to show only when status is Abnormal
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_complaints"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_complaints",
            {
                "depends_on": "eval:doc.practitioner && doc.show_clinical_examination && doc.exam_complaints_status=='Complaints - Abnormal'",
                "hidden": 0
            }
        )
        
    # Also update exam_complaints_status to be visible (not hidden)
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_complaints_status"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_complaints_status",
            {
                "hidden": 0,
                "depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
            }
        )
    
    frappe.db.commit()
    frappe.clear_cache(doctype="Patient Encounter")
    
    print("Updated exam_complaints table visibility")






