import frappe

def execute():
    """
    Fix Step 2 Physical Findings table visibility - same approach as Step 1.
    Show table when status is Abnormal (using depends_on like Step 1 complaints table).
    """
    
    # Update exam_physical_findings table - same pattern as exam_complaints
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_physical_findings"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_physical_findings",
            {
                "depends_on": "eval:doc.practitioner && doc.show_clinical_examination && doc.exam_step2_status=='Abnormal'",
                "hidden": 0
            }
        )
        print("✓ Updated exam_physical_findings: depends_on set for Abnormal status")
    else:
        print("✗ exam_physical_findings field not found")
    
    # Also update the section field to show when Abnormal
    if frappe.db.exists("Custom Field", "Patient Encounter-exam_findings_section"):
        frappe.db.set_value(
            "Custom Field",
            "Patient Encounter-exam_findings_section",
            {
                "depends_on": "eval:doc.practitioner && doc.show_clinical_examination && doc.exam_step2_status=='Abnormal'",
                "hidden": 0
            }
        )
        print("✓ Updated exam_findings_section: depends_on set for Abnormal status")
    
    frappe.db.commit()
    frappe.clear_cache(doctype="Patient Encounter")
    
    print("✓ Step 2 Physical Findings table visibility fix applied (same as Step 1)!")
