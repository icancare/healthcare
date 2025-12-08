"""
Setup Healthcare Service Units as per Client Requirements

Structure:
- All Healthcare Service Units (Root)
  ├── Max Vaishali Clinic (Location)
  │   ├── Photo Medicine OPD Room
  │   ├── Tobacco Control OPD Room
  │   ├── Waiting Area
  │   └── Pharmacy - Max Vaishali
  │
  ├── Green Valley Back Office (Location)
  │   ├── Online Pharmacy
  │   ├── Pharmacy Inventory
  │   ├── Accounts
  │   └── Call Center
  │
  ├── Green Valley Lab (Location)
  │   └── Lab Collection
  │
  └── Green Valley Clinic (Location)
"""

import frappe


def execute():
    """Setup Service Units as per client requirements"""
    
    print("\n" + "="*60)
    print("Setting up Healthcare Service Units (Client Requirements)")
    print("="*60)
    
    # Get company
    company = frappe.db.get_single_value("Global Defaults", "default_company")
    if not company:
        company = frappe.db.get_value("Company", {}, "name")
    
    print(f"\n  Company: {company}")
    
    # Step 1: Create missing Service Unit Types
    create_service_unit_types()
    
    # Step 2: Create/Update Service Units
    create_service_units(company)
    
    # Step 3: Update Practitioner Schedules with correct Service Unit
    update_practitioner_schedules(company)
    
    frappe.db.commit()
    
    print("\n" + "="*60)
    print("✓ Healthcare Service Units Setup Completed!")
    print("="*60 + "\n")


def create_service_unit_types():
    """Create missing Service Unit Types"""
    
    print("\n--- Creating/Updating Service Unit Types ---")
    
    unit_types = [
        # Existing ones - just verify
        {"service_unit_type": "OPD Clinic", "allow_appointments": 1, "overlap_appointments": 1},
        {"service_unit_type": "Back Office", "allow_appointments": 1, "overlap_appointments": 0},
        {"service_unit_type": "Lab Collection", "allow_appointments": 1, "overlap_appointments": 0},
        {"service_unit_type": "Health Camp", "allow_appointments": 1, "overlap_appointments": 1},
        {"service_unit_type": "Waiting Area", "allow_appointments": 1, "overlap_appointments": 0},
        # New ones - all need allow_appointments=1 due to ERPNext restriction
        {"service_unit_type": "Warehouse", "allow_appointments": 1, "overlap_appointments": 0},
        {"service_unit_type": "Pharmacy", "allow_appointments": 1, "overlap_appointments": 0},
        {"service_unit_type": "Call Center", "allow_appointments": 1, "overlap_appointments": 0},
        {"service_unit_type": "Accounts", "allow_appointments": 1, "overlap_appointments": 0},
        {"service_unit_type": "Online Pharmacy", "allow_appointments": 1, "overlap_appointments": 0},
        {"service_unit_type": "Tobacco Control OPD", "allow_appointments": 1, "overlap_appointments": 1},
    ]
    
    for ut in unit_types:
        if not frappe.db.exists("Healthcare Service Unit Type", ut["service_unit_type"]):
            try:
                doc = frappe.new_doc("Healthcare Service Unit Type")
                doc.service_unit_type = ut["service_unit_type"]
                doc.allow_appointments = ut.get("allow_appointments", 0)
                doc.overlap_appointments = ut.get("overlap_appointments", 0)
                doc.flags.ignore_permissions = True
                doc.insert()
                print(f"  ✓ Created: {ut['service_unit_type']}")
            except Exception as e:
                print(f"  ✗ Error: {ut['service_unit_type']} - {str(e)}")
        else:
            # Update existing
            try:
                frappe.db.set_value(
                    "Healthcare Service Unit Type",
                    ut["service_unit_type"],
                    {
                        "allow_appointments": ut.get("allow_appointments", 0),
                        "overlap_appointments": ut.get("overlap_appointments", 0)
                    }
                )
                print(f"  - Updated: {ut['service_unit_type']}")
            except Exception as e:
                print(f"  - Exists: {ut['service_unit_type']}")


def create_service_units(company):
    """Create Service Units hierarchy"""
    
    print("\n--- Creating/Updating Service Units ---")
    
    # Get company abbreviation for naming
    abbr = frappe.db.get_value("Company", company, "abbr") or "ICCARP"
    
    # Root unit
    root_name = f"All Healthcare Service Units - {abbr}"
    
    # Check if root exists
    if not frappe.db.exists("Healthcare Service Unit", root_name):
        create_service_unit(
            name="All Healthcare Service Units",
            unit_type=None,
            company=company,
            is_group=1,
            parent=None
        )
    else:
        print(f"  - Exists: All Healthcare Service Units")
    
    # Location Groups (Level 1)
    locations = [
        {
            "name": "Max Vaishali Clinic",
            "is_group": 1,
            "unit_type": None,
            "parent": root_name
        },
        {
            "name": "Green Valley Back Office",
            "is_group": 1,
            "unit_type": None,
            "parent": root_name
        },
        {
            "name": "Green Valley Lab",
            "is_group": 1,
            "unit_type": None,
            "parent": root_name
        },
        {
            "name": "Green Valley Clinic",
            "is_group": 1,
            "unit_type": None,
            "parent": root_name
        },
    ]
    
    for loc in locations:
        create_service_unit(
            name=loc["name"],
            unit_type=loc["unit_type"],
            company=company,
            is_group=loc["is_group"],
            parent=loc["parent"]
        )
    
    # Get parent names with abbreviation
    max_vaishali = f"Max Vaishali Clinic - {abbr}"
    green_valley_office = f"Green Valley Back Office - {abbr}"
    green_valley_lab = f"Green Valley Lab - {abbr}"
    green_valley_clinic = f"Green Valley Clinic - {abbr}"
    
    # Service Units under Max Vaishali Clinic
    max_vaishali_units = [
        {"name": "Photo Medicine OPD Room", "unit_type": "OPD Clinic", "is_group": 0, "capacity": 5},
        {"name": "Tobacco Control OPD Room", "unit_type": "OPD Clinic", "is_group": 0, "capacity": 5},
        {"name": "Waiting Area - Max Vaishali", "unit_type": "Waiting Area", "is_group": 0},
        {"name": "Pharmacy - Max Vaishali", "unit_type": "Pharmacy", "is_group": 0},
    ]
    
    for unit in max_vaishali_units:
        create_service_unit(
            name=unit["name"],
            unit_type=unit["unit_type"],
            company=company,
            is_group=unit["is_group"],
            parent=max_vaishali,
            capacity=unit.get("capacity", 0)
        )
    
    # Service Units under Green Valley Back Office
    green_valley_office_units = [
        {"name": "Online Pharmacy", "unit_type": "Online Pharmacy", "is_group": 0},
        {"name": "Pharmacy Inventory", "unit_type": "Warehouse", "is_group": 0},
        {"name": "Accounts Department", "unit_type": "Accounts", "is_group": 0},
        {"name": "Call Center", "unit_type": "Call Center", "is_group": 0},
    ]
    
    for unit in green_valley_office_units:
        create_service_unit(
            name=unit["name"],
            unit_type=unit["unit_type"],
            company=company,
            is_group=unit["is_group"],
            parent=green_valley_office
        )
    
    # Service Units under Green Valley Lab
    green_valley_lab_units = [
        {"name": "Lab Collection Room", "unit_type": "Lab Collection", "is_group": 0},
    ]
    
    for unit in green_valley_lab_units:
        create_service_unit(
            name=unit["name"],
            unit_type=unit["unit_type"],
            company=company,
            is_group=unit["is_group"],
            parent=green_valley_lab
        )
    
    # Update existing "Photo Medicine Room" to correct parent if needed
    update_existing_units(company, abbr)


def create_service_unit(name, unit_type, company, is_group, parent, capacity=0):
    """Create a single service unit if not exists"""
    
    abbr = frappe.db.get_value("Company", company, "abbr") or "ICCARP"
    full_name = f"{name} - {abbr}"
    
    if frappe.db.exists("Healthcare Service Unit", full_name):
        # Update parent if different
        current_parent = frappe.db.get_value("Healthcare Service Unit", full_name, "parent_healthcare_service_unit")
        if current_parent != parent and parent:
            try:
                frappe.db.set_value("Healthcare Service Unit", full_name, "parent_healthcare_service_unit", parent)
                print(f"  ↳ Moved: {name} → {parent}")
            except Exception as e:
                print(f"  - Exists: {name}")
        else:
            print(f"  - Exists: {name}")
        return full_name
    
    try:
        doc = frappe.new_doc("Healthcare Service Unit")
        doc.healthcare_service_unit_name = name
        doc.company = company
        doc.is_group = is_group
        
        if unit_type:
            doc.service_unit_type = unit_type
        
        if parent:
            doc.parent_healthcare_service_unit = parent
        
        # Set capacity for overlapping appointments
        if capacity > 0:
            doc.service_unit_capacity = capacity
        
        doc.flags.ignore_permissions = True
        doc.insert()
        print(f"  ✓ Created: {name}")
        return doc.name
        
    except Exception as e:
        print(f"  ✗ Error: {name} - {str(e)}")
        return None


def update_existing_units(company, abbr):
    """Update existing units to correct hierarchy"""
    
    print("\n--- Updating Existing Units ---")
    
    # Move "Photo Medicine Room" under Max Vaishali Clinic if not already
    photo_room = f"Photo Medicine Room - {abbr}"
    max_vaishali = f"Max Vaishali Clinic - {abbr}"
    
    if frappe.db.exists("Healthcare Service Unit", photo_room):
        current_parent = frappe.db.get_value("Healthcare Service Unit", photo_room, "parent_healthcare_service_unit")
        if current_parent != max_vaishali:
            # Rename to new naming convention
            try:
                new_name = f"Photo Medicine OPD Room - {abbr}"
                if not frappe.db.exists("Healthcare Service Unit", new_name):
                    frappe.rename_doc("Healthcare Service Unit", photo_room, new_name)
                    print(f"  ✓ Renamed: Photo Medicine Room → Photo Medicine OPD Room")
            except Exception as e:
                print(f"  - Could not rename Photo Medicine Room: {str(e)}")
    
    # Move "Waiting Area" under Max Vaishali Clinic
    waiting_area = f"Waiting Area - {abbr}"
    if frappe.db.exists("Healthcare Service Unit", waiting_area):
        current_parent = frappe.db.get_value("Healthcare Service Unit", waiting_area, "parent_healthcare_service_unit")
        if current_parent != max_vaishali:
            try:
                frappe.db.set_value("Healthcare Service Unit", waiting_area, "parent_healthcare_service_unit", max_vaishali)
                print(f"  ✓ Moved: Waiting Area → Max Vaishali Clinic")
            except Exception as e:
                print(f"  - Could not move Waiting Area: {str(e)}")


def update_practitioner_schedules(company):
    """Update Practitioner Schedules with default Service Unit"""
    
    print("\n--- Updating Practitioner Schedules ---")
    
    abbr = frappe.db.get_value("Company", company, "abbr") or "ICCARP"
    
    # Default service unit for OPD appointments
    default_unit = f"Photo Medicine OPD Room - {abbr}"
    
    # Fallback to existing Photo Medicine Room if new one doesn't exist
    if not frappe.db.exists("Healthcare Service Unit", default_unit):
        default_unit = f"Photo Medicine Room - {abbr}"
    
    if not frappe.db.exists("Healthcare Service Unit", default_unit):
        print(f"  ✗ Default Service Unit not found!")
        return
    
    # Get all practitioner schedule entries without service unit
    schedules = frappe.get_all(
        "Practitioner Service Unit Schedule",
        filters=[
            ["service_unit", "is", "not set"]
        ],
        fields=["name", "parent", "schedule"]
    )
    
    if not schedules:
        # Try with empty string
        schedules = frappe.db.sql("""
            SELECT name, parent, schedule 
            FROM `tabPractitioner Service Unit Schedule`
            WHERE service_unit IS NULL OR service_unit = ''
        """, as_dict=True)
    
    updated = 0
    for sch in schedules:
        try:
            frappe.db.set_value(
                "Practitioner Service Unit Schedule",
                sch.name,
                "service_unit",
                default_unit
            )
            prac_name = frappe.db.get_value("Healthcare Practitioner", sch.parent, "practitioner_name")
            print(f"  ✓ Updated: {prac_name}")
            updated += 1
        except Exception as e:
            print(f"  ✗ Error: {sch.parent} - {str(e)}")
    
    if updated == 0:
        print("  - All schedules already have Service Unit assigned")
    else:
        print(f"\n  ✓ Updated: {updated} schedules")

