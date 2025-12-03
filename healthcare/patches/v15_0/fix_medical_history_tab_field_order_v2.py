import frappe


def execute():
    """
    Fix the field order in Medical History tab of Patient doctype - Version 2.
    
    The DocField structure is:
    1. allergy_medical_and_surgical_history (Section Break)
       - allergies, medication, medical_history, surgical_history
    2. personal_and_social_history (Section Break)  
       - occupation, marital_status
    
    Problem: Custom Fields with insert_after='surgical_history' appear AFTER 
    personal_and_social_history section in the UI because that DocField section 
    comes after surgical_history.
    
    And social_history_section_break has insert_after='marital_status' which is 
    AFTER surgical_history, so Social History appears BEFORE Allergy tables!
    
    Solution: Chain ALL custom fields after marital_status in correct order:
    1. Allergy section + table
    2. Immunization section + table
    3. Medical History section + table  
    4. Surgical History section + table
    5. Social History section + all tables
    6. Additional Details section (LAST)
    """
    
    # Define the correct insert_after chain - ALL after marital_status in correct order
    field_updates = {
        # Allergy section - FIRST after marital_status
        "patient_allergy_section": "marital_status",
        "patient_allergy": "patient_allergy_section",
        
        # Immunization section - after patient_allergy
        "patient_immunization_section": "patient_allergy",
        "patient_immunization": "patient_immunization_section",
        
        # Medical History section - after patient_immunization
        "patient_medical_history_section": "patient_immunization",
        "patient_medical_history": "patient_medical_history_section",
        
        # Surgical History section - after patient_medical_history
        "patient_surgical_history_section": "patient_medical_history",
        "patient_surgical_history": "patient_surgical_history_section",
        
        # Social History section - after patient_surgical_history (custom table)
        "social_history_section_break": "patient_surgical_history",
        "patient_smokeless_tobacco_history": "social_history_section_break",
        "patient_smoking_tobacco_history": "patient_smokeless_tobacco_history",
        "patient_substance_abuse_history": "patient_smoking_tobacco_history",
        "patient_oral_habits_history": "patient_substance_abuse_history",
        "patient_diet_history": "patient_oral_habits_history",
        "patient_occupational_exposure_history": "patient_diet_history",
        "patient_environmental_factors_history": "patient_occupational_exposure_history",
        
        # Additional Details - at the very end after all social history
        "custom_additional_details_section": "patient_environmental_factors_history",
        "custom_additional_notes": "custom_additional_details_section",
    }
    
    # Update insert_after for all fields
    for fieldname, insert_after in field_updates.items():
        cf_name = frappe.db.get_value("Custom Field", {"dt": "Patient", "fieldname": fieldname})
        if cf_name:
            frappe.db.set_value("Custom Field", cf_name, "insert_after", insert_after)
    
    frappe.db.commit()
    frappe.clear_cache(doctype="Patient")

