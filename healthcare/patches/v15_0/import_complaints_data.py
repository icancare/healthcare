import frappe
import csv
import os


def execute():
    """
    Import Complaints data from CSV file
    """
    print("=" * 60)
    print("Importing Complaints Data")
    print("=" * 60)
    
    # Create missing Medical Departments
    create_missing_departments()
    
    # Get CSV file path
    csv_path = os.path.join(
        os.path.dirname(__file__), 
        "data", 
        "complaints.csv"
    )
    
    if not os.path.exists(csv_path):
        print(f"  ✗ CSV file not found: {csv_path}")
        return
    
    # Read CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        complaints_data = list(reader)
    
    print(f"\n--- Importing {len(complaints_data)} Complaints ---")
    
    created = 0
    updated = 0
    skipped = 0
    
    for complaint in complaints_data:
        try:
            complaint_name = complaint.get("complaint", "").strip()
            complaint_code = complaint.get("complaint_code", "").strip()
            department = complaint.get("department", "").strip()
            
            if not complaint_name:
                continue
            
            # Check if complaint exists by name
            existing = frappe.db.exists("Complaint", {"complaints": complaint_name})
            
            if existing:
                # Update existing complaint with code and department
                frappe.db.set_value("Complaint", existing, {
                    "complaint_code": complaint_code,
                    "department": department if frappe.db.exists("Medical Department", department) else None
                })
                print(f"  ↻ Updated: {complaint_name}")
                updated += 1
            else:
                # Create new complaint
                doc = frappe.get_doc({
                    "doctype": "Complaint",
                    "complaints": complaint_name,
                    "complaint_code": complaint_code,
                    "department": department if frappe.db.exists("Medical Department", department) else None
                })
                doc.insert(ignore_permissions=True)
                print(f"  ✓ Created: {complaint_code} - {complaint_name}")
                created += 1
                
        except Exception as e:
            print(f"  ✗ Error {complaint_name}: {str(e)[:60]}")
            skipped += 1
    
    print(f"\n  ✓ Created: {created}")
    print(f"  ↻ Updated: {updated}")
    print(f"  ✗ Skipped: {skipped}")
    print()
    print("=" * 60)
    print("✓ Complaints Import Complete!")
    print("=" * 60)
    
    frappe.db.commit()


def create_missing_departments():
    """Create missing Medical Departments"""
    print("\n--- Creating Missing Medical Departments ---")
    
    departments = ["General Medicine"]
    
    for dept in departments:
        if not frappe.db.exists("Medical Department", dept):
            doc = frappe.get_doc({
                "doctype": "Medical Department",
                "department": dept
            })
            doc.insert(ignore_permissions=True)
            print(f"  ✓ Created: {dept}")
        else:
            print(f"  - Exists: {dept}")

