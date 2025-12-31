import frappe

def execute():
    """Migrate pattern field data to option field in Clinical Exam Complaint"""
    
    # Check if pattern column exists
    if frappe.db.has_column("Clinical Exam Complaint", "pattern"):
        # Copy pattern data to option where option is empty
        frappe.db.sql("""
            UPDATE `tabClinical Exam Complaint`
            SET `option` = `pattern`
            WHERE (`option` IS NULL OR `option` = '') 
            AND `pattern` IS NOT NULL 
            AND `pattern` != ''
        """)
        frappe.db.commit()
        
        print("Migrated pattern data to option field in Clinical Exam Complaint")


