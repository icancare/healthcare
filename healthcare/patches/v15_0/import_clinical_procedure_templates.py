import frappe
import csv
import os


def execute():
    """
    Import Clinical Procedure Templates from CSV file
    """
    print("=" * 60)
    print("Importing Clinical Procedure Templates")
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
    
    print(f"\n--- Importing {len(templates_data)} Templates ---")
    
    created = 0
    skipped = 0
    errors = 0
    
    for template in templates_data:
        try:
            template_name = template.get("Template Name", "").strip()
            if not template_name:
                continue
            
            # Check if template exists
            if frappe.db.exists("Clinical Procedure Template", {"template": template_name}):
                print(f"  - Exists: {template_name[:50]}")
                skipped += 1
                continue
            
            # Get Item code
            item_code = template.get("Item", "").strip()
            
            # Check if linked item exists when link_existing_item is 1
            link_existing = int(template.get("Link existing Item", "0") or "0")
            if link_existing and item_code and not frappe.db.exists("Item", item_code):
                print(f"  ⚠ Item not found for: {template_name[:40]} (Item: {item_code})")
                errors += 1
                continue
            
            # Create Clinical Procedure Template
            doc = frappe.get_doc({
                "doctype": "Clinical Procedure Template",
                "template": template_name,
                "medical_department": template.get("Medical Department", "").strip() or None,
                "description": template.get("Description", "").strip(),
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
            print(f"  ✗ Error {template_name[:30]}: {str(e)[:60]}")
            errors += 1
    
    print(f"\n  ✓ Created: {created}")
    print(f"  - Skipped: {skipped}")
    print(f"  ✗ Errors: {errors}")
    print()
    print("=" * 60)
    print("✓ Clinical Procedure Templates Import Complete!")
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

