import frappe


def execute():
    """
    Final fix for Patient custom field order in Medical History tab.
    
    The issue is that insert_after chain is not being resolved correctly because
    multiple custom fields have insert_after pointing to fields that come later.
    
    Current problem:
    - patient_allergy_section has insert_after='marital_status' (idx 67)
    - social_history_section_break has insert_after='patient_surgical_history' (idx 77)
    - But patient_allergy_section is rendering AFTER social_history because
      the chain resolution puts it at idx 88!
    
    Solution: Change the insert_after chain so that:
    1. All Allergy/Immunization/Medical/Surgical custom tables come BEFORE Social History
    2. Social History comes after all the above
    3. Additional Details comes LAST
    
    New chain (all after marital_status):
    marital_status → patient_allergy_section → patient_allergy → 
    patient_immunization_section → patient_immunization →
    patient_medical_history_section → patient_medical_history →
    patient_surgical_history_section → patient_surgical_history →
    social_history_section_break → (all tobacco/substance/oral/diet/etc) →
    custom_additional_details_section → custom_additional_notes
    """
    
    # The correct insert_after chain - each field points to the previous one
    field_chain = [
        ("patient_allergy_section", "marital_status"),
        ("patient_allergy", "patient_allergy_section"),
        ("patient_immunization_section", "patient_allergy"),
        ("patient_immunization", "patient_immunization_section"),
        ("patient_medical_history_section", "patient_immunization"),
        ("patient_medical_history", "patient_medical_history_section"),
        ("patient_surgical_history_section", "patient_medical_history"),
        ("patient_surgical_history", "patient_surgical_history_section"),
        ("social_history_section_break", "patient_surgical_history"),
        ("patient_smokeless_tobacco_history", "social_history_section_break"),
        ("patient_smoking_tobacco_history", "patient_smokeless_tobacco_history"),
        ("patient_substance_abuse_history", "patient_smoking_tobacco_history"),
        ("patient_oral_habits_history", "patient_substance_abuse_history"),
        ("patient_diet_history", "patient_oral_habits_history"),
        ("patient_occupational_exposure_history", "patient_diet_history"),
        ("patient_environmental_factors_history", "patient_occupational_exposure_history"),
        ("custom_additional_details_section", "patient_environmental_factors_history"),
        ("custom_additional_notes", "custom_additional_details_section"),
    ]
    
    # Get marital_status idx from meta
    marital_status_idx = frappe.db.get_value(
        "DocField",
        {"parent": "Patient", "fieldname": "marital_status"},
        "idx"
    ) or 51
    
    # Update each custom field with correct insert_after AND idx
    for i, (fieldname, insert_after) in enumerate(field_chain):
        cf_name = frappe.db.get_value("Custom Field", {"dt": "Patient", "fieldname": fieldname})
        if cf_name:
            # Update both insert_after and idx
            frappe.db.sql("""
                UPDATE `tabCustom Field` 
                SET insert_after = %s, idx = %s 
                WHERE name = %s
            """, (insert_after, marital_status_idx + i + 1, cf_name))
    
    frappe.db.commit()
    
    # Clear all caches
    frappe.clear_cache(doctype="Patient")
    
    # Also clear the doctype cache specifically
    if frappe.db.exists("DocType", "Patient"):
        frappe.clear_document_cache("DocType", "Patient")

