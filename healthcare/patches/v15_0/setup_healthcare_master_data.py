"""
Setup Healthcare Master Data

This patch creates:
1. Healthcare related Designations (Senior Doctor, Staff Nurse, etc.)
2. Sample Healthcare Practitioners with complete details
3. Practitioner Schedules for appointment booking
4. Link Users to Practitioners
"""

import frappe


def execute():
    """Setup Healthcare Master Data"""
    
    print("\n" + "="*60)
    print("Setting up Healthcare Master Data")
    print("="*60)
    
    # Step 1: Create Designations
    create_designations()
    
    # Step 2: Create Practitioner Schedules
    create_practitioner_schedules()
    
    # Step 3: Create Healthcare Practitioners
    create_healthcare_practitioners()
    
    frappe.db.commit()
    print("\n" + "="*60)
    print("✓ Healthcare Master Data Setup Completed!")
    print("="*60 + "\n")


def create_designations():
    """Create healthcare related designations"""
    
    print("\n--- Creating Designations ---")
    
    designations = [
        "Senior Doctor",
        "Junior Doctor",
        "Consultant",
        "Staff Nurse",
        "Head Nurse",
        "Receptionist",
        "Lab Technician",
        "Pharmacist",
        "Physiotherapist",
        "Dental Surgeon",
        "Ophthalmologist",
        "General Physician"
    ]
    
    for designation_name in designations:
        if not frappe.db.exists("Designation", designation_name):
            doc = frappe.new_doc("Designation")
            doc.designation_name = designation_name
            doc.flags.ignore_permissions = True
            doc.insert()
            print(f"  ✓ Created Designation: {designation_name}")
        else:
            print(f"  - Designation exists: {designation_name}")


def create_practitioner_schedules():
    """Create practitioner schedules for appointment slots"""
    
    print("\n--- Creating Practitioner Schedules ---")
    
    schedules = [
        {
            "name": "Morning Schedule (9 AM - 1 PM)",
            "schedule_name": "Morning Schedule (9 AM - 1 PM)",
            "time_slots": [
                {"from_time": "09:00:00", "to_time": "13:00:00"}
            ]
        },
        {
            "name": "Evening Schedule (4 PM - 8 PM)",
            "schedule_name": "Evening Schedule (4 PM - 8 PM)",
            "time_slots": [
                {"from_time": "16:00:00", "to_time": "20:00:00"}
            ]
        },
        {
            "name": "Full Day Schedule (9 AM - 5 PM)",
            "schedule_name": "Full Day Schedule (9 AM - 5 PM)",
            "time_slots": [
                {"from_time": "09:00:00", "to_time": "13:00:00"},
                {"from_time": "14:00:00", "to_time": "17:00:00"}
            ]
        }
    ]
    
    for schedule in schedules:
        if not frappe.db.exists("Practitioner Schedule", schedule["name"]):
            doc = frappe.new_doc("Practitioner Schedule")
            doc.schedule_name = schedule["schedule_name"]
            
            for slot in schedule["time_slots"]:
                doc.append("time_slots", {
                    "from_time": slot["from_time"],
                    "to_time": slot["to_time"]
                })
            
            doc.flags.ignore_permissions = True
            doc.insert()
            print(f"  ✓ Created Schedule: {schedule['schedule_name']}")
        else:
            print(f"  - Schedule exists: {schedule['name']}")


def create_healthcare_practitioners():
    """Create healthcare practitioners with complete details"""
    
    print("\n--- Creating Healthcare Practitioners ---")
    
    # Get existing consultation item
    consultation_item = None
    if frappe.db.exists("Item", "DR001"):
        consultation_item = "DR001"
    elif frappe.db.exists("Item", "ICCR004"):
        consultation_item = "ICCR004"
    
    # Get existing users
    doctor_user = None
    if frappe.db.exists("User", "vivek+doctor1@icancare.com"):
        doctor_user = "vivek+doctor1@icancare.com"
    
    nurse_user = None
    if frappe.db.exists("User", "vivek+nurse1@icancare.com"):
        nurse_user = "vivek+nurse1@icancare.com"
    
    practitioners = [
        {
            "first_name": "Priya",
            "last_name": "Verma",
            "gender": "Female",
            "department": "Oral Prosthodontics",
            "designation": "Senior Doctor",
            "mobile_phone": "9876543210",
            "op_consulting_charge": 500,
            "op_consulting_charge_item": consultation_item,
            "user_id": doctor_user,
            "schedule": "Morning Schedule (9 AM - 1 PM)"
        },
        {
            "first_name": "Amit",
            "last_name": "Sharma",
            "gender": "Male",
            "department": "General Surgery",
            "designation": "Consultant",
            "mobile_phone": "9876543211",
            "op_consulting_charge": 600,
            "op_consulting_charge_item": consultation_item,
            "user_id": None,
            "schedule": "Evening Schedule (4 PM - 8 PM)"
        },
        {
            "first_name": "Rahul",
            "last_name": "Singh",
            "gender": "Male",
            "department": "Physiotherapy",
            "designation": "Physiotherapist",
            "mobile_phone": "9876543212",
            "op_consulting_charge": 400,
            "op_consulting_charge_item": consultation_item,
            "user_id": None,
            "schedule": "Full Day Schedule (9 AM - 5 PM)"
        }
    ]
    
    for prac in practitioners:
        # Check multiple conditions to see if practitioner already exists
        practitioner_name = f"{prac['first_name']} {prac['last_name']}"
        
        # Check by name (with or without Dr. prefix)
        existing = frappe.db.exists("Healthcare Practitioner", {"practitioner_name": practitioner_name})
        if not existing:
            existing = frappe.db.exists("Healthcare Practitioner", {"practitioner_name": f"Dr. {practitioner_name}"})
        
        # Also check by user_id if provided
        if not existing and prac.get("user_id"):
            existing = frappe.db.exists("Healthcare Practitioner", {"user_id": prac["user_id"]})
        
        # Also check by first_name and last_name combination
        if not existing:
            existing = frappe.db.exists("Healthcare Practitioner", {
                "first_name": prac["first_name"],
                "last_name": prac["last_name"]
            })
        
        if not existing:
            try:
                doc = frappe.new_doc("Healthcare Practitioner")
                doc.first_name = prac["first_name"]
                doc.last_name = prac["last_name"]
                doc.gender = prac["gender"]
                doc.status = "Active"
                doc.practitioner_type = "Internal"
                
                # Department
                if prac["department"] and frappe.db.exists("Medical Department", prac["department"]):
                    doc.department = prac["department"]
                
                # Contact
                doc.mobile_phone = prac["mobile_phone"]
                
                # Charges
                if prac.get("op_consulting_charge_item") and frappe.db.exists("Item", prac["op_consulting_charge_item"]):
                    doc.op_consulting_charge_item = prac["op_consulting_charge_item"]
                    doc.op_consulting_charge = prac["op_consulting_charge"]
                
                # User link - only if user exists and not already assigned
                if prac.get("user_id") and frappe.db.exists("User", prac["user_id"]):
                    # Check if user is already assigned to another practitioner
                    user_assigned = frappe.db.exists("Healthcare Practitioner", {"user_id": prac["user_id"]})
                    if not user_assigned:
                        doc.user_id = prac["user_id"]
                
                doc.flags.ignore_permissions = True
                doc.insert()
                
                # Add schedule after insert
                if prac.get("schedule") and frappe.db.exists("Practitioner Schedule", prac["schedule"]):
                    doc.append("practitioner_schedules", {
                        "schedule": prac["schedule"]
                    })
                    doc.save()
                
                print(f"  ✓ Created Practitioner: {practitioner_name}")
            except Exception as e:
                print(f"  ✗ Error creating {practitioner_name}: {str(e)}")
        else:
            print(f"  - Practitioner exists: {practitioner_name}")



