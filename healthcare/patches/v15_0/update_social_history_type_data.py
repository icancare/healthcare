import frappe
import csv
import os


def execute():
    """
    Update/Insert Social History type data from fixtures:
    - Smokeless Tobacco Types
    - Smoking Tobacco Types
    - Substance Abuse Types
    - Oral Habits Types
    - Diet Types
    - Occupational Exposure Types
    - Environmental Factors Types
    """
    
    fixtures_path = frappe.get_app_path("healthcare", "fixtures")
    
    # Define fixture files and their corresponding doctypes
    fixtures = [
        ("smokeless_tobacco_types.csv", "Smokeless Tobacco Type", ["type_name", "description", "enabled"]),
        ("smoking_tobacco_types.csv", "Smoking Tobacco Type", ["type_name", "description", "enabled"]),
        ("substance_abuse_types.csv", "Substance Abuse Type", ["type_name", "category", "description", "enabled"]),
        ("oral_habits_types.csv", "Oral Habits Type", ["type_name", "description", "enabled"]),
        ("diet_types.csv", "Diet Type", ["type_name", "description", "enabled"]),
        ("occupational_exposure_types.csv", "Occupational Exposure Type", ["type_name", "description", "enabled"]),
        ("environmental_factors_types.csv", "Environmental Factors Type", ["type_name", "description", "enabled"]),
    ]
    
    for filename, doctype, fields in fixtures:
        filepath = os.path.join(fixtures_path, filename)
        
        if not os.path.exists(filepath):
            continue
        
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                type_name = row.get("type_name", "").strip()
                if not type_name:
                    continue
                
                # Check if already exists
                existing = frappe.db.exists(doctype, {"type_name": type_name})
                
                if existing:
                    # Update existing record
                    doc = frappe.get_doc(doctype, existing)
                    for field in fields:
                        if field in row and field != "type_name":
                            value = row[field].strip() if row[field] else ""
                            if field == "enabled":
                                value = int(value) if value else 1
                            setattr(doc, field, value)
                    doc.save(ignore_permissions=True)
                else:
                    # Create new record
                    doc_data = {"doctype": doctype}
                    for field in fields:
                        if field in row:
                            value = row[field].strip() if row[field] else ""
                            if field == "enabled":
                                value = int(value) if value else 1
                            doc_data[field] = value
                    
                    frappe.get_doc(doc_data).insert(ignore_permissions=True)
    
    frappe.db.commit()

