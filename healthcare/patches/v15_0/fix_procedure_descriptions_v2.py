import frappe
import csv
import os
import html


def execute():
    """
    Fix Procedure Items and Clinical Procedure Templates descriptions - v2
    - Change Clinical Procedure Template description field to Text Editor
    - Re-import descriptions with proper HTML formatting
    """
    print("=" * 60)
    print("Fixing Procedure Descriptions - v2")
    print("=" * 60)
    
    # Step 1: Change Clinical Procedure Template description field to Text Editor
    change_template_description_field_type()
    
    # Step 2: Fix Items descriptions
    fix_item_descriptions()
    
    # Step 3: Fix Clinical Procedure Templates descriptions (with HTML)
    fix_template_descriptions()
    
    frappe.db.commit()
    
    print()
    print("=" * 60)
    print("✓ Procedure Descriptions Fixed - v2!")
    print("=" * 60)


def change_template_description_field_type():
    """Change Clinical Procedure Template description field from Small Text to Text Editor"""
    print("\n--- Changing Clinical Procedure Template Description Field Type ---")
    
    # Use Property Setter to change field type
    property_name = "Clinical Procedure Template-description-fieldtype"
    
    if frappe.db.exists("Property Setter", property_name):
        print("  - Property Setter already exists, updating...")
        frappe.db.set_value("Property Setter", property_name, "value", "Text Editor", update_modified=False)
    else:
        print("  - Creating Property Setter...")
        ps = frappe.get_doc({
            "doctype": "Property Setter",
            "name": property_name,
            "doctype_or_field": "DocField",
            "doc_type": "Clinical Procedure Template",
            "field_name": "description",
            "property": "fieldtype",
            "value": "Text Editor",
            "property_type": "Select"
        })
        ps.insert(ignore_permissions=True)
    
    frappe.db.commit()
    
    # Clear cache
    frappe.clear_cache(doctype="Clinical Procedure Template")
    print("  ✓ Changed description field to Text Editor")


def fix_item_descriptions():
    """Fix Item descriptions from CSV"""
    print("\n--- Fixing Item Descriptions ---")
    
    csv_path = os.path.join(
        os.path.dirname(__file__), 
        "data", 
        "procedure_items.csv"
    )
    
    if not os.path.exists(csv_path):
        print(f"  ✗ CSV file not found: {csv_path}")
        return
    
    # Parse CSV properly handling multiline
    items_data = parse_csv_with_multiline(csv_path)
    
    updated = 0
    not_found = 0
    
    for item in items_data:
        item_code = item.get("Item Code", "").strip()
        description = item.get("Description", "").strip()
        
        if not item_code or not description:
            continue
        
        # Decode HTML entities
        description = html.unescape(description)
        
        # Convert newlines to HTML <br> for proper rendering in Text Editor
        description = convert_to_html(description)
        
        # Check if item exists
        if not frappe.db.exists("Item", item_code):
            not_found += 1
            continue
        
        # Update description
        frappe.db.set_value("Item", item_code, "description", description, update_modified=False)
        updated += 1
        
        if updated % 50 == 0:
            print(f"  ... updated {updated} items")
    
    print(f"  ✓ Updated: {updated}")
    print(f"  - Not found: {not_found}")


def fix_template_descriptions():
    """Fix Clinical Procedure Template descriptions from CSV"""
    print("\n--- Fixing Clinical Procedure Template Descriptions ---")
    
    csv_path = os.path.join(
        os.path.dirname(__file__), 
        "data", 
        "clinical_procedure_templates.csv"
    )
    
    if not os.path.exists(csv_path):
        print(f"  ✗ CSV file not found: {csv_path}")
        return
    
    # Parse CSV properly handling multiline
    templates_data = parse_csv_with_multiline(csv_path)
    
    updated = 0
    not_found = 0
    
    for template in templates_data:
        template_name = template.get("Template Name", "").strip()
        description = template.get("Description", "").strip()
        
        if not template_name or not description:
            continue
        
        # Decode HTML entities and clean special chars
        description = html.unescape(description)
        
        # Convert to HTML for Text Editor field
        description = convert_to_html(description)
        
        template_name_clean = clean_template_name(template_name)
        
        # Check if template exists
        if not frappe.db.exists("Clinical Procedure Template", template_name_clean):
            # Try with original name
            if not frappe.db.exists("Clinical Procedure Template", template_name):
                not_found += 1
                continue
            template_name_clean = template_name
        
        # Update description
        frappe.db.set_value("Clinical Procedure Template", template_name_clean, "description", description, update_modified=False)
        updated += 1
        
        if updated % 50 == 0:
            print(f"  ... updated {updated} templates")
    
    print(f"  ✓ Updated: {updated}")
    print(f"  - Not found: {not_found}")


def parse_csv_with_multiline(csv_path):
    """Parse CSV file properly handling multiline quoted fields"""
    items = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        # Use csv.reader which handles quoted multiline fields correctly
        reader = csv.DictReader(f)
        for row in reader:
            items.append(row)
    
    return items


def clean_template_name(name):
    """Clean template name - remove special characters"""
    if not name:
        return name
    
    # Replace special characters
    cleaned = name.replace("'", "").replace("'", "")
    cleaned = cleaned.replace("–", "-").replace("—", "-")
    cleaned = cleaned.replace("<", "less than ").replace(">", "greater than ")
    
    return cleaned.strip()


def convert_to_html(text):
    """Convert plain text with newlines to HTML with <br> tags for Text Editor fields"""
    if not text:
        return text
    
    # Split by newlines and create HTML paragraphs
    lines = text.split('\n')
    
    # Build HTML with proper formatting
    html_parts = []
    for line in lines:
        line = line.strip()
        if line:
            # Check if it's a header line (like "Description:", "Indications:", etc.)
            if line.endswith(':') and len(line.split()) <= 2:
                html_parts.append(f"<strong>{line}</strong>")
            elif ':' in line and line.split(':')[0].strip() in ['Description', 'Indications', 'Frequency', 'Repeat For', '# Sessions', 'Sessions']:
                # Format key-value lines
                parts = line.split(':', 1)
                if len(parts) == 2:
                    html_parts.append(f"<strong>{parts[0].strip()}:</strong> {parts[1].strip()}")
                else:
                    html_parts.append(line)
            else:
                html_parts.append(line)
        else:
            # Empty line - add a break
            html_parts.append("")
    
    # Join with <br> tags
    return "<br>".join(html_parts)

