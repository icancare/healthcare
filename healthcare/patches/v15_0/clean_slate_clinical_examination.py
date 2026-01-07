import frappe


def execute():
    """
    Clean Slate Clinical Examination Setup:
    1. Delete old template 'ICanCaRe Oral Screening Form'
    2. Delete ALL exam_* custom fields from Patient Encounter
    3. Create only essential ~51 custom fields
    4. Keep 'Oral Screening' template
    """
    
    print("=" * 60)
    print("CLEAN SLATE: Clinical Examination Setup")
    print("=" * 60)
    
    # Step 1: Delete old template
    delete_old_template()
    
    # Step 2: Delete all exam_* custom fields
    delete_all_exam_fields()
    
    # Step 3: Create essential custom fields
    create_essential_fields()
    
    # Commit and clear cache
    frappe.db.commit()
    frappe.clear_cache(doctype="Patient Encounter")
    
    print("=" * 60)
    print("Clean Slate Setup Complete!")
    print("=" * 60)


def delete_old_template():
    """Delete old template 'ICanCaRe Oral Screening Form'"""
    print("\n[Step 1] Deleting old template...")
    
    template_name = "ICanCaRe Oral Screening Form"
    
    if frappe.db.exists("Clinical Examination Template", template_name):
        # First delete child table entries
        frappe.db.delete("Clinical Exam Template Practitioner", {"parent": template_name})
        # Then delete the template
        frappe.delete_doc("Clinical Examination Template", template_name, force=True)
        print(f"  ✓ Deleted template: {template_name}")
    else:
        print(f"  - Template not found: {template_name}")


def delete_all_exam_fields():
    """Delete ALL exam_* custom fields from Patient Encounter"""
    print("\n[Step 2] Deleting all exam_* custom fields...")
    
    # Get all exam_* custom fields
    exam_fields = frappe.db.get_all(
        "Custom Field",
        filters={
            "dt": "Patient Encounter",
            "fieldname": ["like", "exam_%"]
        },
        pluck="name"
    )
    
    # Also get show_clinical_examination field
    show_clinical = frappe.db.get_value(
        "Custom Field",
        {"dt": "Patient Encounter", "fieldname": "show_clinical_examination"},
        "name"
    )
    
    if show_clinical:
        exam_fields.append(show_clinical)
    
    print(f"  Found {len(exam_fields)} custom fields to delete")
    
    # Delete all fields
    for field_name in exam_fields:
        try:
            frappe.delete_doc("Custom Field", field_name, force=True)
        except Exception as e:
            print(f"  ! Error deleting {field_name}: {str(e)}")
    
    print(f"  ✓ Deleted {len(exam_fields)} custom fields")


def create_essential_fields():
    """Create only essential ~51 custom fields"""
    print("\n[Step 3] Creating essential custom fields...")
    
    # Define all essential fields
    fields = get_essential_fields()
    
    created = 0
    for field in fields:
        field["dt"] = "Patient Encounter"
        field["module"] = "Healthcare"
        
        # Check if already exists
        existing = frappe.db.exists("Custom Field", f"Patient Encounter-{field['fieldname']}")
        
        if existing:
            # Update existing
            frappe.db.set_value("Custom Field", existing, field)
        else:
            # Create new
            doc = frappe.get_doc({"doctype": "Custom Field", **field})
            doc.insert(ignore_permissions=True)
            created += 1
    
    print(f"  ✓ Created/Updated {len(fields)} essential fields ({created} new)")


def get_essential_fields():
    """Return list of essential custom fields"""
    
    fields = []
    
    # ==================== HEADER FIELDS ====================
    # show_clinical_examination - Main toggle (after diagnosis_notes in Encounter Impression section)
    fields.append({
        "fieldname": "show_clinical_examination",
        "label": "Show Clinical Examination",
        "fieldtype": "Check",
        "insert_after": "diagnosis_notes",
        "depends_on": "eval:doc.practitioner",
        "hidden": 0
    })
    
    # Clinical Examination Section
    fields.append({
        "fieldname": "clinical_examination_section",
        "label": "Clinical Examination",
        "fieldtype": "Section Break",
        "insert_after": "show_clinical_examination",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination",
        "collapsible": 0
    })
    
    # Case Type
    fields.append({
        "fieldname": "exam_case_type",
        "label": "Case Type",
        "fieldtype": "Select",
        "options": "\nNew Case\nFollow Up Case",
        "insert_after": "clinical_examination_section",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
    })
    
    # Examination Type
    fields.append({
        "fieldname": "exam_examination_type",
        "label": "Examination Type",
        "fieldtype": "Select",
        "options": "\nOral Screening\nDermatology\nGeneral Physical\nENT\nOphthalmology\nCardiology\nOther",
        "insert_after": "exam_case_type",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination",
        "read_only": 1
    })
    
    # Column Break
    fields.append({
        "fieldname": "exam_header_col_break",
        "fieldtype": "Column Break",
        "insert_after": "exam_examination_type"
    })
    
    # Follow Up Status
    fields.append({
        "fieldname": "exam_follow_up_status",
        "label": "Follow Up Status",
        "fieldtype": "Select",
        "options": "\nNo New Complaints\nNo New Lesion\nNew Complaints\nNew Lesion",
        "insert_after": "exam_header_col_break",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination && doc.exam_case_type == 'Follow Up Case'"
    })
    
    # ==================== STEP 1 - PATIENT COMPLAINTS ====================
    fields.append({
        "fieldname": "exam_step1_section",
        "label": "STEP 1 - Patient Complaints",
        "fieldtype": "Section Break",
        "insert_after": "exam_follow_up_status",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
    })
    
    # Step 1 HTML Container
    fields.append({
        "fieldname": "exam_step1_table_html",
        "label": "",
        "fieldtype": "HTML",
        "insert_after": "exam_step1_section",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
    })
    
    # Complaints Status (hidden - JS sets this)
    fields.append({
        "fieldname": "exam_complaints_status",
        "label": "Complaints Status",
        "fieldtype": "Select",
        "options": "\nNo Complaints - Normal\nComplaints - Abnormal",
        "insert_after": "exam_step1_table_html",
        "hidden": 1
    })
    
    # Complaints Table
    fields.append({
        "fieldname": "exam_complaints",
        "label": "Complaints",
        "fieldtype": "Table",
        "options": "Clinical Exam Complaint",
        "insert_after": "exam_complaints_status",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination",
        "hidden": 1  # JS controls visibility
    })
    
    # ==================== STEP 2 - PHYSICAL EXAMINATION ====================
    fields.append({
        "fieldname": "exam_step2_section",
        "label": "STEP 2 - Physical Examination",
        "fieldtype": "Section Break",
        "insert_after": "exam_complaints",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
    })
    
    # Step 2 HTML Container
    fields.append({
        "fieldname": "exam_step2_table_html",
        "label": "",
        "fieldtype": "HTML",
        "insert_after": "exam_step2_section",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
    })
    
    # Step 2 Status (hidden - JS sets this)
    fields.append({
        "fieldname": "exam_step2_status",
        "label": "Examination Status",
        "fieldtype": "Select",
        "options": "\nNormal\nAbnormal",
        "insert_after": "exam_step2_table_html",
        "hidden": 1
    })
    
    # Physical Findings Table
    fields.append({
        "fieldname": "exam_physical_findings",
        "label": "Physical Findings",
        "fieldtype": "Table",
        "options": "Clinical Exam Finding",
        "insert_after": "exam_step2_status",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination",
        "hidden": 1  # JS controls visibility
    })
    
    # Hidden fields for Mouth popup data
    fields.append({
        "fieldname": "exam_mouth_opening_fingers",
        "label": "Mouth Opening (Fingers)",
        "fieldtype": "Select",
        "options": "\nOne\nTwo\nThree\nFour",
        "insert_after": "exam_physical_findings",
        "hidden": 1
    })
    
    fields.append({
        "fieldname": "exam_mouth_opening_mm",
        "label": "Mouth Opening (mm)",
        "fieldtype": "Float",
        "insert_after": "exam_mouth_opening_fingers",
        "hidden": 1
    })
    
    # ==================== STEP 3 - DIAGRAM MARKING ====================
    fields.append({
        "fieldname": "exam_step3_section",
        "label": "STEP 3 - Representation MARKING on Diagram",
        "fieldtype": "Section Break",
        "insert_after": "exam_mouth_opening_mm",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
    })
    
    # Interactive Diagram HTML
    fields.append({
        "fieldname": "exam_diagram_interactive",
        "label": "Interactive Diagrams",
        "fieldtype": "HTML",
        "insert_after": "exam_step3_section",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
    })
    
    # Diagram Lesions Table
    fields.append({
        "fieldname": "exam_diagram_lesions",
        "label": "Diagram Lesions",
        "fieldtype": "Table",
        "options": "Clinical Exam Lesion",
        "insert_after": "exam_diagram_interactive",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination",
        "hidden": 1
    })
    
    # Lesion Present (for Lesion Examination section)
    fields.append({
        "fieldname": "exam_lesion_present",
        "label": "Lesion Present",
        "fieldtype": "Select",
        "options": "\nNo\nYes",
        "insert_after": "exam_diagram_lesions",
        "hidden": 1
    })
    
    # ==================== STEP 4 - PICTURES ====================
    fields.append({
        "fieldname": "exam_step4_section",
        "label": "STEP 4 - PICTURES TO BE TAKEN FOR RECORD AND COMPARISON",
        "fieldtype": "Section Break",
        "insert_after": "exam_lesion_present",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
    })
    
    # Pictures Taken By
    fields.append({
        "fieldname": "exam_pictures_taken_by",
        "label": "Pictures Taken By",
        "fieldtype": "Select",
        "options": "\nDoctor's Assistant\nDoctor\nPatient",
        "insert_after": "exam_step4_section",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
    })
    
    # Pictures HTML Container
    fields.append({
        "fieldname": "exam_pictures_html",
        "label": "Pictures Upload",
        "fieldtype": "HTML",
        "insert_after": "exam_pictures_taken_by",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
    })
    
    # 10 Picture Fields
    picture_fields = [
        ("exam_pic_1_face_neck", "1. Face and Neck"),
        ("exam_pic_2_open_mouth", "2. Open Mouth with Scale"),
        ("exam_pic_3_central_arch", "3. Central Arch with Lips"),
        ("exam_pic_4_right_cheek", "4. Right Cheek with Alveolus"),
        ("exam_pic_5_left_cheek", "5. Left Cheek with Alveolus"),
        ("exam_pic_6_tongue", "6. Tongue Protruded"),
        ("exam_pic_7_tongue_floor", "7. Tongue with Floor of Mouth"),
        ("exam_pic_8_palate", "8. Hard and Soft Palate"),
        ("exam_pic_9_abnormal", "9. Abnormal Area Focused"),
        ("exam_pic_10_special", "10. Special Tests")
    ]
    
    prev_field = "exam_pictures_html"
    for fieldname, label in picture_fields:
        fields.append({
            "fieldname": fieldname,
            "label": label,
            "fieldtype": "Attach Image",
            "insert_after": prev_field,
            "hidden": 1  # JS shows via custom UI
        })
        prev_field = fieldname
    
    # ==================== STEP 5 - SPECIAL TESTS ====================
    fields.append({
        "fieldname": "exam_step5_section",
        "label": "STEP 5 - SPECIAL TESTS",
        "fieldtype": "Section Break",
        "insert_after": prev_field,
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
    })
    
    # Skip Special Tests
    fields.append({
        "fieldname": "exam_skip_special_tests",
        "label": "Skip Special Tests",
        "fieldtype": "Check",
        "insert_after": "exam_step5_section",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
    })
    
    # Toluidine Blue Test
    fields.append({
        "fieldname": "exam_toluidine_section",
        "label": "Toluidine Blue Test",
        "fieldtype": "Section Break",
        "insert_after": "exam_skip_special_tests",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination && !doc.exam_skip_special_tests"
    })
    
    fields.append({
        "fieldname": "exam_toluidine_result",
        "label": "Result",
        "fieldtype": "Select",
        "options": "\nNormal\nLow Suspicious\nHigh Suspicious",
        "insert_after": "exam_toluidine_section"
    })
    
    fields.append({
        "fieldname": "exam_toluidine_col",
        "fieldtype": "Column Break",
        "insert_after": "exam_toluidine_result"
    })
    
    fields.append({
        "fieldname": "exam_toluidine_notes",
        "label": "Notes",
        "fieldtype": "Small Text",
        "insert_after": "exam_toluidine_col"
    })
    
    # Blue Light Test
    fields.append({
        "fieldname": "exam_bluelight_section",
        "label": "Blue Light Test",
        "fieldtype": "Section Break",
        "insert_after": "exam_toluidine_notes",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination && !doc.exam_skip_special_tests"
    })
    
    fields.append({
        "fieldname": "exam_bluelight_result",
        "label": "Result",
        "fieldtype": "Select",
        "options": "\nNormal\nLow Suspicious\nHigh Suspicious",
        "insert_after": "exam_bluelight_section"
    })
    
    fields.append({
        "fieldname": "exam_bluelight_col",
        "fieldtype": "Column Break",
        "insert_after": "exam_bluelight_result"
    })
    
    fields.append({
        "fieldname": "exam_bluelight_notes",
        "label": "Notes",
        "fieldtype": "Small Text",
        "insert_after": "exam_bluelight_col"
    })
    
    # Autofluorescence Test
    fields.append({
        "fieldname": "exam_autofluor_section",
        "label": "Autofluorescence Test",
        "fieldtype": "Section Break",
        "insert_after": "exam_bluelight_notes",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination && !doc.exam_skip_special_tests"
    })
    
    fields.append({
        "fieldname": "exam_autofluor_result",
        "label": "Result",
        "fieldtype": "Select",
        "options": "\nNormal\nLow Suspicious\nHigh Suspicious",
        "insert_after": "exam_autofluor_section"
    })
    
    fields.append({
        "fieldname": "exam_autofluor_col",
        "fieldtype": "Column Break",
        "insert_after": "exam_autofluor_result"
    })
    
    fields.append({
        "fieldname": "exam_autofluor_notes",
        "label": "Notes",
        "fieldtype": "Small Text",
        "insert_after": "exam_autofluor_col"
    })
    
    # Spectroscopy Test
    fields.append({
        "fieldname": "exam_spectroscopy_section",
        "label": "Spectroscopy Test",
        "fieldtype": "Section Break",
        "insert_after": "exam_autofluor_notes",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination && !doc.exam_skip_special_tests"
    })
    
    fields.append({
        "fieldname": "exam_spectroscopy_result",
        "label": "Result",
        "fieldtype": "Select",
        "options": "\nNormal\nLow Suspicious\nHigh Suspicious",
        "insert_after": "exam_spectroscopy_section"
    })
    
    fields.append({
        "fieldname": "exam_spectroscopy_col",
        "fieldtype": "Column Break",
        "insert_after": "exam_spectroscopy_result"
    })
    
    fields.append({
        "fieldname": "exam_spectroscopy_notes",
        "label": "Notes",
        "fieldtype": "Small Text",
        "insert_after": "exam_spectroscopy_col"
    })
    
    # ==================== STEP 6 - INTERPRETATION/ADVICE ====================
    fields.append({
        "fieldname": "exam_step6_section",
        "label": "STEP 6 - Interpretation/Advice (Provisional Diagnosis)",
        "fieldtype": "Section Break",
        "insert_after": "exam_spectroscopy_notes",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
    })
    
    # Special Tests Summary
    fields.append({
        "fieldname": "exam_special_tests_summary",
        "label": "Special Tests Summary/Notes",
        "fieldtype": "Text",
        "insert_after": "exam_step6_section",
        "depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
    })
    
    # Interpretation Checkboxes
    interpretation_fields = [
        ("exam_interp_normal", "Normal, routine screening after 1 year, continue self-oral examination"),
        ("exam_interp_normal_risk", "Normal with risk factors, close screening every six months"),
        ("exam_interp_potentially_malignant", "Potentially Malignant lesions, precancerous lesions, need further management"),
        ("exam_interp_high_risk", "High risk, need to see the nearest center for further evaluation"),
        ("exam_interp_suspicious", "Suspicious for cancer, need to see the nearest center for further evaluation"),
        ("exam_interp_frank_malignancy", "Frank malignancy, requires immediate treatment visit specialized cancer center"),
        ("exam_interp_insufficient", "Insufficient data for any comments, repeat examination"),
        ("exam_interp_inflammation", "Inflammation or infection or nutritional factors to be ruled out or treated and then repeat examination"),
        ("exam_interp_tobacco_consult", "High Risk factors needs consultation for Tobacco de-addiction"),
        ("exam_interp_alcohol_advice", "Recommend advice regarding Alcohol Use"),
        ("exam_interp_dental_care", "Recommend Dental Care")
    ]
    
    prev_field = "exam_special_tests_summary"
    for fieldname, label in interpretation_fields:
        fields.append({
            "fieldname": fieldname,
            "label": label,
            "fieldtype": "Check",
            "insert_after": prev_field,
            "depends_on": "eval:doc.practitioner && doc.show_clinical_examination"
        })
        prev_field = fieldname
    
    return fields

