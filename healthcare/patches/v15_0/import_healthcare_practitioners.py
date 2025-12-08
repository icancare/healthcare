"""
Import Healthcare Practitioners from Master Data

This patch imports practitioners with:
- Prefix (Dr, Mr, Mrs)
- First Name, Middle Name, Last Name
- Status, Gender
- Mobile, Phone (Office)
- Practitioner Type (Internal/External)
- Designation
- Medical Department
"""

import frappe


def execute():
    """Import Healthcare Practitioners"""
    
    print("\n" + "="*60)
    print("Importing Healthcare Practitioners")
    print("="*60)
    
    # Practitioner data from sheet
    practitioners = [
        {"prefix": "Dr", "first_name": "Pawan", "last_name": "Gupta", "status": "Active", "gender": "Male", "mobile": "98112-90152", "practitioner_type": "Internal", "designation": "Founder", "department": "Photo Medicine"},
        {"prefix": "Mrs", "first_name": "Shruti", "last_name": "Agrawal", "status": "Active", "gender": "Female", "mobile": "8238432146", "office_phone": "6309437912", "practitioner_type": "Internal", "designation": "Chief Strategy Officer", "department": ""},
        {"prefix": "Mr", "first_name": "Rishabh", "last_name": "Agrawal", "status": "Active", "gender": "Male", "mobile": "9971011169", "practitioner_type": "Internal", "designation": "Director", "department": ""},
        {"prefix": "Mr", "first_name": "Sohan", "last_name": "Lal", "status": "Active", "gender": "Male", "mobile": "89298 82724", "office_phone": "97738 92478", "practitioner_type": "Internal", "designation": "Support Staff", "department": ""},
        {"prefix": "Mr", "first_name": "Pushpender", "last_name": "Kumar", "status": "Active", "gender": "Male", "mobile": "95602 76098", "office_phone": "97738 96491", "practitioner_type": "Internal", "designation": "Pharmacist", "department": "Pharmacy"},
        {"prefix": "Mr", "first_name": "Kaushal", "last_name": "Chaudhary", "status": "Active", "gender": "Male", "mobile": "84109 19459", "office_phone": "97738 92480", "practitioner_type": "Internal", "designation": "Phlebotomist", "department": "Pathology"},
        {"prefix": "Mr", "first_name": "Rohit", "last_name": "Thakur", "status": "Active", "gender": "Male", "mobile": "99711 95808", "office_phone": "97738 56663", "practitioner_type": "Internal", "designation": "Doctor Assistant", "department": "Photo Medicine"},
        {"prefix": "Dr", "first_name": "Shama", "last_name": "", "status": "Active", "gender": "Female", "mobile": "", "practitioner_type": "External", "designation": "Dental Surgeon", "department": "Photo Medicine"},
        {"prefix": "Dr", "first_name": "Ganesh", "last_name": "Dubey", "status": "Active", "gender": "Male", "mobile": "7065224422", "practitioner_type": "External", "designation": "Dental Surgeon", "department": "Dental Medicine"},
        {"prefix": "Dr", "first_name": "Supriya", "last_name": "Wadhwa", "status": "Active", "gender": "Female", "mobile": "70074 14309", "practitioner_type": "External", "designation": "Tobacco Cessation Specialist", "department": "Photo Medicine"},
        {"prefix": "Dr", "first_name": "Shipra", "last_name": "Sharma", "status": "Active", "gender": "Female", "mobile": "82735 34558", "practitioner_type": "External", "designation": "Dental Surgeon", "department": "Photo Medicine"},
        {"prefix": "Dr", "first_name": "Deeksha", "last_name": "Sharma", "status": "Active", "gender": "Female", "mobile": "94251 15415", "practitioner_type": "External", "designation": "Dental Surgeon", "department": "Photo Medicine"},
        {"prefix": "Dr", "first_name": "Minu", "last_name": "Kumari", "status": "Active", "gender": "Female", "mobile": "866 086 1209", "practitioner_type": "External", "designation": "Dental Surgeon", "department": "Photo Medicine"},
    ]
    
    # First ensure required designations exist
    create_designations(practitioners)
    
    # Create Medical Departments if not exist
    create_departments(practitioners)
    
    # Import practitioners
    import_practitioners(practitioners)
    
    frappe.db.commit()
    
    print("\n" + "="*60)
    print("✓ Healthcare Practitioners Import Completed!")
    print("="*60 + "\n")


def create_designations(practitioners):
    """Create Designations if they don't exist"""
    
    print("\n--- Creating Designations ---")
    
    designations = set()
    for p in practitioners:
        if p.get("designation"):
            designations.add(p["designation"])
    
    for designation in sorted(designations):
        if not frappe.db.exists("Designation", designation):
            try:
                doc = frappe.new_doc("Designation")
                doc.designation_name = designation
                doc.flags.ignore_permissions = True
                doc.insert()
                print(f"  ✓ Created: {designation}")
            except Exception as e:
                print(f"  - Error: {designation} - {str(e)}")
        else:
            print(f"  - Exists: {designation}")


def create_departments(practitioners):
    """Create Medical Departments if they don't exist"""
    
    print("\n--- Creating Medical Departments ---")
    
    departments = set()
    for p in practitioners:
        if p.get("department"):
            departments.add(p["department"])
    
    for dept in sorted(departments):
        if dept and not frappe.db.exists("Medical Department", dept):
            try:
                doc = frappe.new_doc("Medical Department")
                doc.department = dept
                doc.flags.ignore_permissions = True
                doc.insert()
                print(f"  ✓ Created: {dept}")
            except Exception as e:
                print(f"  - Error: {dept} - {str(e)}")
        elif dept:
            print(f"  - Exists: {dept}")


def import_practitioners(practitioners):
    """Import Healthcare Practitioners"""
    
    print("\n--- Importing Healthcare Practitioners ---")
    
    created = 0
    skipped = 0
    
    for p in practitioners:
        first_name = p.get("first_name", "")
        last_name = p.get("last_name", "")
        
        # Check if practitioner already exists by name
        practitioner_name = f"{first_name} {last_name}".strip()
        
        existing = frappe.db.exists("Healthcare Practitioner", {
            "first_name": first_name,
            "last_name": last_name or ""
        })
        
        if existing:
            print(f"  - Exists: {practitioner_name}")
            skipped += 1
            continue
        
        try:
            doc = frappe.new_doc("Healthcare Practitioner")
            doc.first_name = first_name
            doc.last_name = last_name or ""
            doc.status = p.get("status", "Active")
            doc.practitioner_type = p.get("practitioner_type", "Internal")
            
            # Set prefix if exists
            if p.get("prefix") and frappe.db.exists("Salutation", p["prefix"]):
                doc.prefix = p["prefix"]
            
            # Set gender if exists
            if p.get("gender") and frappe.db.exists("Gender", p["gender"]):
                doc.gender = p["gender"]
            
            # Clean phone numbers (remove spaces)
            if p.get("mobile"):
                doc.mobile_phone = p["mobile"].replace(" ", "").replace("-", "")
            
            if p.get("office_phone"):
                doc.office_phone = p["office_phone"].replace(" ", "").replace("-", "")
            
            # Set designation if exists
            if p.get("designation") and frappe.db.exists("Designation", p["designation"]):
                doc.designation = p["designation"]
            
            # Set department if exists
            if p.get("department") and frappe.db.exists("Medical Department", p["department"]):
                doc.department = p["department"]
            
            doc.flags.ignore_permissions = True
            doc.insert()
            
            print(f"  ✓ Created: {practitioner_name}")
            created += 1
            
        except Exception as e:
            print(f"  ✗ Error creating {practitioner_name}: {str(e)}")
    
    print(f"\n  ✓ Created: {created}")
    print(f"  - Skipped: {skipped}")

