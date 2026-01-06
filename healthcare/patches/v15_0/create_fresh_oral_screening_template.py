import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    """
    Create fresh Oral Screening template with all fields properly ordered.
    This ensures production has same working setup as localhost.
    """
    print("\n" + "="*60)
    print("Creating Fresh Oral Screening Template")
    print("="*60)
    
    # Step 1: Create the template if not exists
    create_oral_screening_template()
    
    # Step 2: Delete and recreate the Physical Findings table field
    fix_physical_findings_field()
    
    frappe.db.commit()
    frappe.clear_cache()
    
    print("\n" + "="*60)
    print("Fresh Oral Screening Template Created Successfully!")
    print("="*60)


def create_oral_screening_template():
    """Create the Oral Screening template"""
    template_name = "Oral Screening"
    
    if not frappe.db.exists("Clinical Examination Template", template_name):
        doc = frappe.get_doc({
            "doctype": "Clinical Examination Template",
            "template_name": template_name,
            "examination_type": "Oral Screening",
            "is_active": 1
        })
        doc.insert(ignore_permissions=True)
        print(f"✓ Created template: {template_name}")
    else:
        print(f"⏭ Template already exists: {template_name}")


def fix_physical_findings_field():
    """Delete and recreate Physical Findings field with correct settings"""
    
    field_name = "Patient Encounter-exam_physical_findings"
    
    # Delete if exists
    if frappe.db.exists("Custom Field", field_name):
        frappe.delete_doc("Custom Field", field_name, force=True)
        print(f"✓ Deleted old field: exam_physical_findings")
    
    # Create fresh field
    create_custom_field("Patient Encounter", {
        "fieldname": "exam_physical_findings",
        "label": "Physical Findings",
        "fieldtype": "Table",
        "options": "Clinical Exam Finding",
        "insert_after": "exam_step2_table_html",
        "hidden": 0,
        "depends_on": ""
    })
    print(f"✓ Created fresh field: exam_physical_findings")
    
    # Verify the field is in correct position
    # Get idx of exam_step2_table_html and set exam_physical_findings idx to be right after
    step2_html_idx = frappe.db.get_value("Custom Field", "Patient Encounter-exam_step2_table_html", "idx")
    if step2_html_idx:
        new_idx = int(step2_html_idx) + 1
        frappe.db.set_value("Custom Field", field_name, "idx", new_idx)
        print(f"✓ Set idx to {new_idx} (after exam_step2_table_html)")

