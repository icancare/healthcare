"""
Add Extended Fields to Diagnosis DocType

This patch adds custom fields to Diagnosis for comprehensive diagnosis management:
- Chronic/Acute classification
- ICD-11 coding
- Department linking
- Severity levels
- Follow-up settings
- Billing integration
- Reporting flags
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """Add extended fields to Diagnosis doctype"""
    
    print("\n" + "="*60)
    print("Adding Extended Fields to Diagnosis")
    print("="*60)
    
    # NOTE: Removed create_clinical_categories() - not needed
    # Diagnosis Category doctype already exists and user manages it manually
    print("\n--- Skipping Clinical Categories Creation (User Managed) ---")
    
    # Add custom fields to Diagnosis
    add_diagnosis_custom_fields()
    
    frappe.db.commit()
    print("\n" + "="*60)
    print("✓ Diagnosis Extended Fields Added Successfully!")
    print("="*60 + "\n")


def create_clinical_categories():
    """Create Clinical Category doctype data if needed"""
    
    print("\n--- Checking Clinical Categories ---")
    
    # Clinical categories from sheet
    categories = [
        "Gastrointestinal",
        "Medical Disease",
        "Respiratory",
        "Endocrine/Metabolic",
        "Cardiovascular",
        "Neurology",
        "Dermatology",
        "Musculoskeletal",
        "Infectious Disease",
        "Oncology",
        "Hematology",
        "Nephrology",
        "Ophthalmology",
        "ENT",
        "Psychiatry",
        "Oral/Dental",
        "Gynecology",
        "Pediatrics",
        "Other"
    ]
    
    # Check if Diagnosis Category exists and add categories there
    if frappe.db.exists("DocType", "Diagnosis Category"):
        for cat in categories:
            if not frappe.db.exists("Diagnosis Category", cat):
                try:
                    doc = frappe.new_doc("Diagnosis Category")
                    doc.category_name = cat
                    doc.is_active = 1
                    doc.flags.ignore_permissions = True
                    doc.insert()
                    print(f"  ✓ Created Category: {cat}")
                except Exception as e:
                    print(f"  - Category exists or error: {cat}")
            else:
                print(f"  - Category exists: {cat}")
    
    frappe.db.commit()


def add_diagnosis_custom_fields():
    """Add custom fields to Diagnosis doctype"""
    
    print("\n--- Adding Custom Fields to Diagnosis ---")
    
    custom_fields = {
        "Diagnosis": [
            # Basic Classification Section
            {
                "fieldname": "classification_section",
                "fieldtype": "Section Break",
                "label": "Classification",
                "insert_after": "diagnosis_category",
                "collapsible": 0
            },
            {
                "fieldname": "diagnosis_code",
                "fieldtype": "Data",
                "label": "Diagnosis Code",
                "insert_after": "classification_section",
                "read_only": 1,
                "description": "Auto-generated code like DIAG-0001"
            },
            {
                "fieldname": "chronic_or_acute",
                "fieldtype": "Select",
                "label": "Chronic or Acute",
                "insert_after": "diagnosis_code",
                "options": "\nAcute\nChronic",
                "in_list_view": 1,
                "in_standard_filter": 1
            },
            # NOTE: Removed is_chronic - not needed
            # NOTE: Removed clinical_category - using Diagnosis Category instead
            {
                "fieldname": "classification_column",
                "fieldtype": "Column Break",
                "insert_after": "chronic_or_acute"
            },
            {
                "fieldname": "common_name",
                "fieldtype": "Data",
                "label": "Common Name",
                "insert_after": "classification_column",
                "description": "Common/layman name for the diagnosis"
            },
            {
                "fieldname": "synonyms",
                "fieldtype": "Small Text",
                "label": "Synonyms",
                "insert_after": "common_name",
                "description": "Alternative names separated by comma"
            },
            
            # NOTE: Removed ICD-11 Coding Section - already in Medical Coding child table
            
            # Department & Settings Section
            {
                "fieldname": "department_section",
                "fieldtype": "Section Break",
                "label": "Department & Settings",
                "insert_after": "synonyms",
                "collapsible": 1
            },
            {
                "fieldname": "department",
                "fieldtype": "Link",
                "label": "Department",
                "insert_after": "department_section",
                "options": "Medical Department",
                "description": "Primary department for this diagnosis"
            },
            {
                "fieldname": "severity",
                "fieldtype": "Select",
                "label": "Severity",
                "insert_after": "department",
                "options": "\nMild\nModerate\nSevere\nCritical",
                "in_standard_filter": 1
            },
            {
                "fieldname": "default_follow_up_days",
                "fieldtype": "Int",
                "label": "Default Follow-up Days",
                "insert_after": "severity",
                "default": "7",
                "description": "Default number of days for follow-up appointment"
            },
            {
                "fieldname": "department_column",
                "fieldtype": "Column Break",
                "insert_after": "default_follow_up_days"
            },
            {
                "fieldname": "status",
                "fieldtype": "Select",
                "label": "Status",
                "insert_after": "department_column",
                "options": "Draft\nApproved\nDeprecated",
                "default": "Draft",
                "in_standard_filter": 1
            },
            {
                "fieldname": "default_treatment_template",
                "fieldtype": "Link",
                "label": "Default Treatment Template",
                "insert_after": "status",
                "options": "Treatment Plan Template",
                "description": "Default treatment plan template for this diagnosis"
            },
            
            # Billing Section
            {
                "fieldname": "billing_section",
                "fieldtype": "Section Break",
                "label": "Billing",
                "insert_after": "default_treatment_template",
                "collapsible": 1
            },
            {
                "fieldname": "billing_code",
                "fieldtype": "Data",
                "label": "Billing Code",
                "insert_after": "billing_section",
                "description": "Internal billing code"
            },
            
            # Reporting Flags Section
            {
                "fieldname": "reporting_section",
                "fieldtype": "Section Break",
                "label": "Reporting & Compliance",
                "insert_after": "billing_code",
                "collapsible": 1
            },
            {
                "fieldname": "is_reportable",
                "fieldtype": "Check",
                "label": "Is Reportable",
                "insert_after": "reporting_section",
                "default": "0",
                "description": "Check if this diagnosis needs to be reported"
            },
            {
                "fieldname": "notifiable",
                "fieldtype": "Check",
                "label": "Notifiable Disease",
                "insert_after": "is_reportable",
                "default": "0",
                "description": "Check if this is a notifiable disease"
            },
            # NOTE: Removed is_photo_medicine_eligible - not needed
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    print("  ✓ Added all custom fields to Diagnosis")
    
    # Update naming series for diagnosis_code generation
    print("\n--- Setting up Diagnosis Code Generation ---")
    
    # Check if we need to add auto-generation for diagnosis_code
    # This will be handled by a server script or property setter
    
    frappe.db.commit()

