import frappe
import csv
import os


def execute():
    """
    Import Procedure Items from CSV file
    """
    print("=" * 60)
    print("Importing Procedure Items")
    print("=" * 60)
    
    # Create missing Item Groups
    create_missing_item_groups()
    
    # Get CSV file path
    csv_path = os.path.join(
        os.path.dirname(__file__), 
        "data", 
        "procedure_items.csv"
    )
    
    if not os.path.exists(csv_path):
        print(f"  ✗ CSV file not found: {csv_path}")
        return
    
    # Read and parse CSV
    items_data = parse_csv_file(csv_path)
    
    print(f"\n--- Importing {len(items_data)} Items ---")
    
    created = 0
    skipped = 0
    errors = 0
    
    for item in items_data:
        try:
            item_code = item.get("Item Code", "").strip()
            if not item_code:
                continue
            
            # Check if item exists
            if frappe.db.exists("Item", item_code):
                print(f"  - Exists: {item_code}")
                skipped += 1
                continue
            
            # Clean and prepare data
            standard_rate = clean_price(item.get("Standard Selling Rate", "0"))
            
            # Create Item
            doc = frappe.get_doc({
                "doctype": "Item",
                "item_code": item_code,
                "item_name": item.get("Item Name", "").strip(),
                "item_group": item.get("Item Group", "Services").strip(),
                "description": item.get("Description", "").strip(),
                "stock_uom": item.get("Default Unit of Measure", "Visit").strip(),
                "is_stock_item": int(item.get("Maintain Stock", "0")),
                "standard_rate": float(standard_rate) if standard_rate else 0,
                "gst_hsn_code": item.get("HSN/SAC", "999312").strip(),
                "grant_commission": int(item.get("Grant Commission", "1")),
                "is_sales_item": int(item.get("Allow Sales", "1")),
                "is_purchase_item": int(item.get("Allow Purchase", "0")),
                "max_discount": float(item.get("Max Discount (%)", "0") or "0"),
            })
            
            # Add Item Default for Price List
            price_list = item.get("Default Price List (Item Defaults)", "").strip()
            if price_list and frappe.db.exists("Price List", price_list):
                doc.append("item_defaults", {
                    "company": frappe.defaults.get_defaults().get("company"),
                    "default_price_list": price_list
                })
            
            # Add Item Tax
            tax_template = item.get("Item Tax Template (Taxes)", "").strip()
            if tax_template and frappe.db.exists("Item Tax Template", tax_template):
                doc.append("taxes", {
                    "item_tax_template": tax_template
                })
            
            doc.insert(ignore_permissions=True)
            print(f"  ✓ Created: {item_code} - {item.get('Item Name', '')[:40]}")
            created += 1
            
        except Exception as e:
            print(f"  ✗ Error {item_code}: {str(e)[:80]}")
            errors += 1
    
    print(f"\n  ✓ Created: {created}")
    print(f"  - Skipped: {skipped}")
    print(f"  ✗ Errors: {errors}")
    print()
    print("=" * 60)
    print("✓ Procedure Items Import Complete!")
    print("=" * 60)
    
    frappe.db.commit()


def create_missing_item_groups():
    """Create missing Item Groups"""
    print("\n--- Creating Missing Item Groups ---")
    
    groups = ["PBMPDT"]
    
    for group in groups:
        if not frappe.db.exists("Item Group", group):
            doc = frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": group,
                "parent_item_group": "All Item Groups",
                "is_group": 0
            })
            doc.insert(ignore_permissions=True)
            print(f"  ✓ Created Item Group: {group}")
        else:
            print(f"  - Item Group exists: {group}")


def parse_csv_file(csv_path):
    """Parse CSV file handling multiline descriptions"""
    items = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Use csv reader with proper quoting
    reader = csv.DictReader(content.splitlines())
    
    for row in reader:
        items.append(row)
    
    return items


def clean_price(price_str):
    """Clean price string - remove ₹ and commas"""
    if not price_str:
        return "0"
    
    # Remove ₹, commas, quotes, and whitespace
    cleaned = str(price_str).replace('₹', '').replace(',', '').replace('"', '').strip()
    
    # Return 0 if empty or not numeric
    try:
        return str(float(cleaned))
    except ValueError:
        return "0"

