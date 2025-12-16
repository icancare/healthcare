import frappe
import csv
import os


def execute():
    """
    Re-import Diagnosis data from client's CSV file
    1. Delete all existing Diagnosis records
    2. Delete all existing Diagnosis Category records
    3. Create new Diagnosis Categories from CSV
    4. Import new Diagnosis records from CSV
    """
    print("=" * 60)
    print("Re-importing Diagnosis Data from Client CSV")
    print("=" * 60)
    
    # Get CSV file path
    csv_path = os.path.join(
        os.path.dirname(__file__), 
        "data", 
        "Diagnosis_List.csv"
    )
    
    if not os.path.exists(csv_path):
        print(f"  ✗ CSV file not found: {csv_path}")
        return
    
    # Read CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        diagnosis_data = list(reader)
    
    print(f"\n--- Found {len(diagnosis_data)} diagnoses in CSV ---")
    
    # Step 1: Delete existing Diagnosis records
    print("\n--- Deleting Existing Diagnosis Records ---")
    existing_count = frappe.db.count("Diagnosis")
    print(f"  Found {existing_count} existing records")
    
    frappe.db.sql("DELETE FROM `tabDiagnosis`")
    frappe.db.commit()
    print(f"  ✓ Deleted {existing_count} Diagnosis records")
    
    # Step 2: Delete existing Diagnosis Category records
    print("\n--- Deleting Existing Diagnosis Category Records ---")
    existing_cat_count = frappe.db.count("Diagnosis Category")
    print(f"  Found {existing_cat_count} existing categories")
    
    frappe.db.sql("DELETE FROM `tabDiagnosis Category`")
    frappe.db.commit()
    print(f"  ✓ Deleted {existing_cat_count} Diagnosis Category records")
    
    # Step 3: Get unique categories from CSV and create them
    print("\n--- Creating Diagnosis Categories from CSV ---")
    categories = set()
    for row in diagnosis_data:
        cat = row.get("clinical_category", "").strip()
        if cat:
            categories.add(cat)
    
    for cat in sorted(categories):
        try:
            doc = frappe.get_doc({
                "doctype": "Diagnosis Category",
                "category_name": cat
            })
            doc.insert(ignore_permissions=True)
            print(f"  ✓ Created: {cat}")
        except Exception as e:
            print(f"  ✗ Error creating {cat}: {str(e)[:50]}")
    
    frappe.db.commit()
    print(f"  ✓ Created {len(categories)} categories")
    
    # Step 4: Import Diagnosis records
    print("\n--- Importing Diagnosis Records ---")
    created = 0
    errors = 0
    
    for row in diagnosis_data:
        try:
            diagnosis_name = row.get("diagnosis_name", "").strip()
            if not diagnosis_name:
                continue
            
            # Map CSV fields to DocType fields
            chronic_or_acute = row.get("ChronicOrAcute", "").strip()
            is_chronic = 1 if row.get("is_chronic", "").strip().lower() == "yes" else 0
            clinical_category = row.get("clinical_category", "").strip()
            common_name = row.get("common_name", "").strip()
            synonyms = row.get("synonyms", "").strip()
            department = row.get("department", "").strip()
            
            # Check if category exists by category_name
            category_exists = frappe.db.exists("Diagnosis Category", {"category_name": clinical_category})
            
            doc = frappe.get_doc({
                "doctype": "Diagnosis",
                "diagnosis": diagnosis_name,
                "diagnosis_category": clinical_category if category_exists else None,
                "chronic_or_acute": chronic_or_acute if chronic_or_acute in ["Chronic", "Acute"] else None,
                "common_name": common_name,
                "synonyms": synonyms,
                "department": department if frappe.db.exists("Medical Department", department) else None,
            })
            doc.insert(ignore_permissions=True)
            created += 1
            
            if created % 50 == 0:
                print(f"  ... imported {created} records")
                frappe.db.commit()
                
        except Exception as e:
            print(f"  ✗ Error: {diagnosis_name} - {str(e)[:60]}")
            errors += 1
    
    frappe.db.commit()
    
    print(f"\n  ✓ Created: {created}")
    print(f"  ✗ Errors: {errors}")
    print()
    print("=" * 60)
    print("✓ Diagnosis Data Re-import Complete!")
    print("=" * 60)

