import frappe


def execute():
    """
    Fix idx values for Patient Custom Fields based on insert_after chain.
    
    The insert_after chain is correct but idx values are not in order,
    causing fields to display in wrong sequence in the UI.
    """
    
    # Define the correct order of custom fields in Medical History tab
    # Starting idx after marital_status (which is around idx 51 in DocField)
    field_order = [
        # Allergy section - FIRST
        "patient_allergy_section",
        "patient_allergy",
        
        # Immunization section
        "patient_immunization_section",
        "patient_immunization",
        
        # Medical History section
        "patient_medical_history_section",
        "patient_medical_history",
        
        # Surgical History section
        "patient_surgical_history_section",
        "patient_surgical_history",
        
        # Social History section
        "social_history_section_break",
        "patient_smokeless_tobacco_history",
        "patient_smoking_tobacco_history",
        "patient_substance_abuse_history",
        "patient_oral_habits_history",
        "patient_diet_history",
        "patient_occupational_exposure_history",
        "patient_environmental_factors_history",
        
        # Additional Details - LAST
        "custom_additional_details_section",
        "custom_additional_notes",
    ]
    
    # Get the idx of marital_status from DocField
    marital_status_idx = frappe.db.get_value(
        "DocField", 
        {"parent": "Patient", "fieldname": "marital_status"}, 
        "idx"
    ) or 51
    
    # Update idx for each custom field in order
    start_idx = marital_status_idx + 1
    
    for i, fieldname in enumerate(field_order):
        cf_name = frappe.db.get_value("Custom Field", {"dt": "Patient", "fieldname": fieldname})
        if cf_name:
            frappe.db.set_value("Custom Field", cf_name, "idx", start_idx + i, update_modified=False)
    
    frappe.db.commit()
    frappe.clear_cache(doctype="Patient")

