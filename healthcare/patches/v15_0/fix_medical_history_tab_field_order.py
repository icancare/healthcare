import frappe


def execute():
    """
    Fix the field order in Medical History tab of Patient doctype.
    
    Correct order should be:
    1. Allergies, Medical and Surgical History section (DocField)
       - allergies, medication (DocField)
       - medical_history, surgical_history (DocField)
       - patient_allergy_section → patient_allergy (Custom)
       - patient_immunization_section → patient_immunization (Custom)
       - patient_medical_history_section → patient_medical_history (Custom)
       - patient_surgical_history_section → patient_surgical_history (Custom)
    
    2. Personal and Social History section (DocField)
       - occupation, marital_status (DocField)
       - social_history_section_break (Custom)
       - patient_smokeless_tobacco_history (Custom)
       - patient_smoking_tobacco_history (Custom)
       - patient_substance_abuse_history (Custom)
       - patient_oral_habits_history (Custom)
       - patient_diet_history (Custom)
       - patient_occupational_exposure_history (Custom)
       - patient_environmental_factors_history (Custom)
    
    3. Additional Details section (Custom - at the very end)
       - custom_additional_details_section
       - custom_additional_notes
    """
    
    # Define the correct insert_after chain for all custom fields
    field_updates = {
        # Allergy section - after surgical_history (DocField)
        "patient_allergy_section": "surgical_history",
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
        
        # Social History section - after marital_status (which is in personal_and_social_history DocField section)
        "social_history_section_break": "marital_status",
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
    
    # Remove old/duplicate section breaks that are not needed
    fields_to_delete = [
        "allergy_section_break",
        "immunization_section_break", 
        "medical_history_section_break",
        "surgical_history_section_break",
    ]
    
    for fieldname in fields_to_delete:
        cf_name = frappe.db.get_value("Custom Field", {"dt": "Patient", "fieldname": fieldname})
        if cf_name:
            frappe.delete_doc("Custom Field", cf_name, force=True)
    
    # Update insert_after for all fields
    for fieldname, insert_after in field_updates.items():
        cf_name = frappe.db.get_value("Custom Field", {"dt": "Patient", "fieldname": fieldname})
        if cf_name:
            frappe.db.set_value("Custom Field", cf_name, "insert_after", insert_after)
    
    frappe.db.commit()
    frappe.clear_cache(doctype="Patient")

