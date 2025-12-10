import frappe
import csv
import os


def execute():
    """
    Import missing Clinical Procedure Templates from CSV file
    Only creates templates that don't exist yet
    """
    print("=" * 60)
    print("Importing Missing Clinical Procedure Templates")
    print("=" * 60)
    
    # Get CSV file path
    csv_path = os.path.join(
        os.path.dirname(__file__), 
        "data", 
        "clinical_procedure_templates.csv"
    )
    
    if not os.path.exists(csv_path):
        print(f"  ✗ CSV file not found: {csv_path}")
        return
    
    # Read and parse CSV
    templates_data = parse_csv_file(csv_path)
    
    print(f"\n--- Processing {len(templates_data)} Templates ---")
    
    created = 0
    skipped = 0
    errors = 0
    
    for template in templates_data:
        try:
            template_name = template.get("Template Name", "").strip()
            if not template_name:
                continue
            
            # Clean template name - remove special characters
            template_name = clean_name(template_name)
            
            # Check if template exists
            if frappe.db.exists("Clinical Procedure Template", {"template": template_name}):
                skipped += 1
                continue
            
            # Get Item code
            item_code = template.get("Item", "").strip()
            
            # Check if linked item exists when link_existing_item is 1
            link_existing = int(template.get("Link existing Item", "0") or "0")
            if link_existing and item_code and not frappe.db.exists("Item", item_code):
                print(f"  ⚠ Item not found: {item_code} for {template_name[:40]}")
                errors += 1
                continue
            
            # Create Clinical Procedure Template
            doc = frappe.get_doc({
                "doctype": "Clinical Procedure Template",
                "template": template_name,
                "medical_department": template.get("Medical Department", "").strip() or None,
                "description": clean_name(template.get("Description", "").strip()),
                "link_existing_item": link_existing,
                "item": item_code if link_existing else None,
                "item_code": item_code if not link_existing else None,
                "item_group": template.get("Item Group", "").strip() or None,
                "is_billable": int(template.get("Is Billable", "1") or "1"),
                "consume_stock": int(template.get("Allow Stock Consumption", "0") or "0"),
                "sample": template.get("Sample", "").strip() or None,
                "patient_care_type": template.get("Patient Care Type", "").strip() or None,
                "gst_hsn_code": template.get("HSN/SAC", "999312").strip(),
            })
            
            doc.insert(ignore_permissions=True)
            print(f"  ✓ Created: {template_name[:50]}")
            created += 1
            
        except Exception as e:
            error_msg = str(e)[:60]
            print(f"  ✗ Error {template_name[:30]}: {error_msg}")
            errors += 1
    
    print(f"\n  ✓ Created: {created}")
    print(f"  - Skipped (exists): {skipped}")
    print(f"  ✗ Errors: {errors}")
    print()
    print("=" * 60)
    print("✓ Missing Templates Import Complete!")
    print("=" * 60)
    
    frappe.db.commit()


def parse_csv_file(csv_path):
    """Parse CSV file handling multiline descriptions"""
    templates = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Use csv reader with proper quoting
    reader = csv.DictReader(content.splitlines())
    
    for row in reader:
        templates.append(row)
    
    return templates


def clean_name(text):
    """Clean special characters from text"""
    if not text:
        return text
    
    replacements = {
        "'": "'",
        "'": "'",
        "–": "-",
        "—": "-",
        """: '"',
        """: '"',
        "…": "...",
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

