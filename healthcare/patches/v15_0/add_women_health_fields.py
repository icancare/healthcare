"""
Add Women Health section to Patient and Patient Encounter

This patch adds Women Health fields including:
- Breast Fed, Contraceptive Pills, Hormone Replacement RX
- Breast Symptoms, Age At Menarche, Age at Menopause
- Abortion, Genitourinary Symptoms, Note
- Children Details (child table)
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """Add Women Health fields to Patient and Patient Encounter"""
    
    # Common Women Health fields structure
    patient_women_health_fields = [
        {
            "fieldname": "women_health_section",
            "fieldtype": "Section Break",
            "label": "Women Health",
            "insert_after": "patient_environmental_factors_history",
            "collapsible": 1,
            "depends_on": "eval:doc.sex=='Female'"
        },
        {
            "fieldname": "breast_fed",
            "fieldtype": "Select",
            "label": "Breast Fed",
            "options": "\nYes\nNo",
            "insert_after": "women_health_section"
        },
        {
            "fieldname": "contraceptive_pills",
            "fieldtype": "Select",
            "label": "Contraceptive Pills",
            "options": "\nYes\nNo",
            "insert_after": "breast_fed"
        },
        {
            "fieldname": "hormone_replacement_rx",
            "fieldtype": "Select",
            "label": "Hormone Replacement RX",
            "options": "\nYes\nNo",
            "insert_after": "contraceptive_pills"
        },
        {
            "fieldname": "breast_symptoms",
            "fieldtype": "Select",
            "label": "Breast Symptoms",
            "options": "\nYes\nNo",
            "insert_after": "hormone_replacement_rx"
        },
        {
            "fieldname": "women_health_column_break_1",
            "fieldtype": "Column Break",
            "insert_after": "breast_symptoms"
        },
        {
            "fieldname": "age_at_menarche",
            "fieldtype": "Int",
            "label": "Age At Menarche",
            "insert_after": "women_health_column_break_1"
        },
        {
            "fieldname": "age_at_menopause",
            "fieldtype": "Int",
            "label": "Age at Menopause",
            "insert_after": "age_at_menarche"
        },
        {
            "fieldname": "abortion_count",
            "fieldtype": "Int",
            "label": "Abortion",
            "insert_after": "age_at_menopause"
        },
        {
            "fieldname": "genitourinary_symptoms",
            "fieldtype": "Select",
            "label": "Genitourinary Symptoms",
            "options": "\nYes\nNo",
            "insert_after": "abortion_count"
        },
        {
            "fieldname": "women_health_section_2",
            "fieldtype": "Section Break",
            "insert_after": "genitourinary_symptoms",
            "depends_on": "eval:doc.sex=='Female'"
        },
        {
            "fieldname": "women_health_note",
            "fieldtype": "Small Text",
            "label": "Note",
            "insert_after": "women_health_section_2"
        },
        {
            "fieldname": "children_details_section",
            "fieldtype": "Section Break",
            "label": "Children Details",
            "insert_after": "women_health_note",
            "collapsible": 1,
            "depends_on": "eval:doc.sex=='Female'"
        },
        {
            "fieldname": "patient_children_details",
            "fieldtype": "Table",
            "label": "Children",
            "options": "Patient Children Details",
            "insert_after": "children_details_section"
        },
    ]
    
    # Patient Encounter Women Health fields
    encounter_women_health_fields = [
        {
            "fieldname": "encounter_women_health_section",
            "fieldtype": "Section Break",
            "label": "Women Health",
            "insert_after": "custom_environmental_factors_history",
            "collapsible": 1,
            "depends_on": "eval:doc.patient_sex=='Female'"
        },
        {
            "fieldname": "encounter_breast_fed",
            "fieldtype": "Select",
            "label": "Breast Fed",
            "options": "\nYes\nNo",
            "insert_after": "encounter_women_health_section"
        },
        {
            "fieldname": "encounter_contraceptive_pills",
            "fieldtype": "Select",
            "label": "Contraceptive Pills",
            "options": "\nYes\nNo",
            "insert_after": "encounter_breast_fed"
        },
        {
            "fieldname": "encounter_hormone_replacement_rx",
            "fieldtype": "Select",
            "label": "Hormone Replacement RX",
            "options": "\nYes\nNo",
            "insert_after": "encounter_contraceptive_pills"
        },
        {
            "fieldname": "encounter_breast_symptoms",
            "fieldtype": "Select",
            "label": "Breast Symptoms",
            "options": "\nYes\nNo",
            "insert_after": "encounter_hormone_replacement_rx"
        },
        {
            "fieldname": "encounter_women_health_column_break_1",
            "fieldtype": "Column Break",
            "insert_after": "encounter_breast_symptoms"
        },
        {
            "fieldname": "encounter_age_at_menarche",
            "fieldtype": "Int",
            "label": "Age At Menarche",
            "insert_after": "encounter_women_health_column_break_1"
        },
        {
            "fieldname": "encounter_age_at_menopause",
            "fieldtype": "Int",
            "label": "Age at Menopause",
            "insert_after": "encounter_age_at_menarche"
        },
        {
            "fieldname": "encounter_abortion_count",
            "fieldtype": "Int",
            "label": "Abortion",
            "insert_after": "encounter_age_at_menopause"
        },
        {
            "fieldname": "encounter_genitourinary_symptoms",
            "fieldtype": "Select",
            "label": "Genitourinary Symptoms",
            "options": "\nYes\nNo",
            "insert_after": "encounter_abortion_count"
        },
        {
            "fieldname": "encounter_women_health_section_2",
            "fieldtype": "Section Break",
            "insert_after": "encounter_genitourinary_symptoms",
            "depends_on": "eval:doc.patient_sex=='Female'"
        },
        {
            "fieldname": "encounter_women_health_note",
            "fieldtype": "Small Text",
            "label": "Note",
            "insert_after": "encounter_women_health_section_2"
        },
        {
            "fieldname": "encounter_children_details_section",
            "fieldtype": "Section Break",
            "label": "Children Details",
            "insert_after": "encounter_women_health_note",
            "collapsible": 1,
            "depends_on": "eval:doc.patient_sex=='Female'"
        },
        {
            "fieldname": "encounter_children_details",
            "fieldtype": "Table",
            "label": "Children",
            "options": "Patient Encounter Children Details",
            "insert_after": "encounter_children_details_section"
        },
    ]
    
    custom_fields = {
        "Patient": patient_women_health_fields,
        "Patient Encounter": encounter_women_health_fields,
    }
    
    create_custom_fields(custom_fields, update=True)
    
    # Fix Additional Details section to be after Women Health
    if frappe.db.exists("Custom Field", {"dt": "Patient", "fieldname": "custom_additional_details_section"}):
        frappe.db.set_value("Custom Field",
            {"dt": "Patient", "fieldname": "custom_additional_details_section"},
            "insert_after", "patient_children_details")
    
    frappe.db.commit()

