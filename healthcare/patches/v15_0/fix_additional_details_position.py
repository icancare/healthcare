import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """
    Move Additional Details section to the very end of Medical History tab,
    after all Social History custom fields (which end at patient_environmental_factors_history).
    
    Since additional_details_section is in DocField and we need it after Custom Fields,
    we'll create Custom Fields for these and hide the DocField versions.
    """
    
    # First, hide the DocField versions by setting hidden=1 via Property Setter
    from frappe.custom.doctype.property_setter.property_setter import make_property_setter
    
    # Hide the original DocField additional_details_section
    make_property_setter(
        "Patient", 
        "additional_details_section", 
        "hidden", 
        1, 
        "Check",
        for_doctype=False
    )
    
    # Hide the original DocField additional_notes
    make_property_setter(
        "Patient", 
        "additional_notes", 
        "hidden", 
        1, 
        "Check",
        for_doctype=False
    )
    
    # Now create Custom Fields at the correct position
    custom_fields = {
        "Patient": [
            {
                "fieldname": "custom_additional_details_section",
                "fieldtype": "Section Break",
                "label": "Additional Details",
                "insert_after": "patient_environmental_factors_history"
            },
            {
                "fieldname": "custom_additional_notes",
                "fieldtype": "Text Editor",
                "label": "Additional Notes",
                "description": "Additional comments, notes or details about the patient",
                "insert_after": "custom_additional_details_section"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    frappe.db.commit()
