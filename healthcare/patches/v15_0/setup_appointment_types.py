"""
Setup Appointment Types for ICanCare

This patch:
1. Adds custom fields to Appointment Type (is_consultation, appointment_description)
2. Creates Healthcare Service Items (Consultation Fees)
3. Adds missing Medical Departments
4. Deletes existing Appointment Types
5. Creates new Appointment Types from the master list
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """Setup Appointment Types"""
    
    print("\n" + "="*60)
    print("Setting up Appointment Types")
    print("="*60)
    
    # Step 1: Add custom fields to Appointment Type
    add_appointment_type_custom_fields()
    
    # Step 2: Create Healthcare Service Items
    create_healthcare_items()
    
    # Step 3: Create missing Medical Departments
    create_missing_departments()
    
    # Step 4: Delete existing Appointment Types
    delete_existing_appointment_types()
    
    # Step 5: Create new Appointment Types
    create_appointment_types()
    
    frappe.db.commit()
    print("\n" + "="*60)
    print("✓ Appointment Types Setup Completed!")
    print("="*60 + "\n")


def add_appointment_type_custom_fields():
    """Add custom fields to Appointment Type doctype"""
    
    print("\n--- Adding Custom Fields to Appointment Type ---")
    
    custom_fields = {
        "Appointment Type": [
            {
                "fieldname": "is_consultation",
                "fieldtype": "Check",
                "label": "Is it Consultation?",
                "insert_after": "color",
                "default": "1",
                "description": "Check if this appointment type is a consultation"
            },
            {
                "fieldname": "appointment_description",
                "fieldtype": "Small Text",
                "label": "Description",
                "insert_after": "is_consultation",
                "description": "Description or notes about this appointment type"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    print("  ✓ Added custom fields: is_consultation, appointment_description")


def create_healthcare_items():
    """Create healthcare service items for consultation fees"""
    
    print("\n--- Creating Healthcare Service Items ---")
    
    # Ensure Services item group exists
    if not frappe.db.exists("Item Group", "Services"):
        doc = frappe.new_doc("Item Group")
        doc.item_group_name = "Services"
        doc.parent_item_group = "All Item Groups"
        doc.is_group = 0
        doc.flags.ignore_permissions = True
        doc.insert()
        print("  ✓ Created Item Group: Services")
    
    # Healthcare Service Items
    items = [
        {
            "item_code": "HC-TOBACCO-SPECIALIST",
            "item_name": "Tobacco Specialist Consultation Fee",
            "item_group": "Services",
            "stock_uom": "Nos",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "standard_rate": 1200,
            "description": "Quit Tobacco Specialist Consultation Fee"
        },
        {
            "item_code": "HC-TOBACCO-COACH",
            "item_name": "Tobacco Coach Counselling Fee",
            "item_group": "Services",
            "stock_uom": "Nos",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "standard_rate": 800,
            "description": "Quit Tobacco Coach Counselling Fee"
        },
        {
            "item_code": "HC-ORAL-CONSULTATION",
            "item_name": "Oral Specialist Consultation Fee",
            "item_group": "Services",
            "stock_uom": "Nos",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "standard_rate": 1000,
            "description": "Oral/Dental Specialist Consultation Fee"
        },
        {
            "item_code": "HC-HEALTH-SCREENING",
            "item_name": "Health Screening Fee",
            "item_group": "Services",
            "stock_uom": "Nos",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "standard_rate": 300,
            "description": "Health/Oral Screening Fee"
        },
        {
            "item_code": "HC-PHOTODIAGNOSTICS",
            "item_name": "Oral PhotoDiagnostics Fee",
            "item_group": "Services",
            "stock_uom": "Nos",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "standard_rate": 1800,
            "description": "Oral PhotoDiagnostics Procedure Fee"
        },
        {
            "item_code": "HC-NUTRITIONIST",
            "item_name": "Nutritionist Consultation Fee",
            "item_group": "Services",
            "stock_uom": "Nos",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "standard_rate": 1200,
            "description": "Nutritionist/Dietitian Consultation Fee"
        },
        {
            "item_code": "HC-AYURVEDA",
            "item_name": "Ayurveda Consultation Fee",
            "item_group": "Services",
            "stock_uom": "Nos",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "standard_rate": 1200,
            "description": "Ayurveda Consultation Fee"
        },
        {
            "item_code": "HC-NATUROPATH",
            "item_name": "Naturopath Consultation Fee",
            "item_group": "Services",
            "stock_uom": "Nos",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "standard_rate": 1200,
            "description": "Naturopath Consultation Fee"
        },
        {
            "item_code": "HC-PROCEDURE",
            "item_name": "Clinical Procedure Fee",
            "item_group": "Services",
            "stock_uom": "Nos",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "standard_rate": 0,
            "description": "Clinical Procedure Fee - Rate as per procedure template"
        },
        {
            "item_code": "HC-FOLLOWUP-FREE",
            "item_name": "Follow-up Consultation (Free)",
            "item_group": "Services",
            "stock_uom": "Nos",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "standard_rate": 0,
            "description": "Free Follow-up Consultation"
        }
    ]
    
    for item_data in items:
        if not frappe.db.exists("Item", item_data["item_code"]):
            doc = frappe.new_doc("Item")
            doc.item_code = item_data["item_code"]
            doc.item_name = item_data["item_name"]
            doc.item_group = item_data["item_group"]
            doc.stock_uom = item_data["stock_uom"]
            doc.is_stock_item = item_data["is_stock_item"]
            doc.is_sales_item = item_data["is_sales_item"]
            doc.standard_rate = item_data["standard_rate"]
            doc.description = item_data["description"]
            doc.flags.ignore_permissions = True
            doc.insert()
            print(f"  ✓ Created Item: {item_data['item_code']} - {item_data['item_name']} (₹{item_data['standard_rate']})")
        else:
            print(f"  - Item exists: {item_data['item_code']}")


def create_missing_departments():
    """Create missing medical departments"""
    
    print("\n--- Creating Missing Medical Departments ---")
    
    departments = [
        {"department": "Traditional Medicine", "patient_care_type": "OPD"},
        {"department": "Tobacco Cessation", "patient_care_type": "OPD"},
        {"department": "Photo Medicine", "patient_care_type": "OPD"},
        {"department": "Diet & Nutrition", "patient_care_type": "OPD"},
        {"department": "Public Health", "patient_care_type": "OPD"},
    ]
    
    for dept in departments:
        if not frappe.db.exists("Medical Department", dept["department"]):
            doc = frappe.new_doc("Medical Department")
            doc.department = dept["department"]
            if dept.get("patient_care_type"):
                doc.patient_care_type = dept["patient_care_type"]
            doc.flags.ignore_permissions = True
            doc.insert()
            print(f"  ✓ Created Department: {dept['department']}")
        else:
            print(f"  - Department exists: {dept['department']}")


def delete_existing_appointment_types():
    """Delete all existing appointment types"""
    
    print("\n--- Deleting Existing Appointment Types ---")
    
    # Get all existing appointment types
    existing_types = frappe.get_all("Appointment Type", pluck="name")
    
    for apt_type in existing_types:
        try:
            # First delete child table entries
            frappe.db.delete("Appointment Type Service Item", {"parent": apt_type})
            # Then delete the appointment type
            frappe.delete_doc("Appointment Type", apt_type, force=True, ignore_permissions=True)
            print(f"  ✓ Deleted: {apt_type}")
        except Exception as e:
            print(f"  ✗ Could not delete {apt_type}: {str(e)}")
    
    frappe.db.commit()


def create_appointment_types():
    """Create appointment types from master list"""
    
    print("\n--- Creating Appointment Types ---")
    
    # Color mapping
    colors = {
        "light grey": "#D3D3D3",
        "dark grey": "#696969",
        "grey": "#808080",
        "blue": "#3498db",
        "green": "#2ecc71",
        "orange": "#e67e22",
        "red": "#e74c3c",
        "light blue": "#87CEEB"
    }
    
    # Appointment Types Master Data with proper items, is_consultation and description
    appointment_types = [
        {
            "appointment_type": "Information/Precounselling",
            "allow_booking_for": "Department",
            "default_duration": 15,
            "color": colors.get("light grey", "#D3D3D3"),
            "price_list": "Standard Selling",
            "is_consultation": 0,
            "appointment_description": "Sales, Support or Receptionist handle precounseling.",
            "items": []
        },
        {
            "appointment_type": "Quit Tobacco Specialist 1st Consultation",
            "allow_booking_for": "Department",
            "default_duration": 60,
            "color": colors.get("dark grey", "#696969"),
            "price_list": "Standard Selling",
            "is_consultation": 1,
            "appointment_description": "",
            "items": [
                {"dt": "Medical Department", "dn": "Tobacco Cessation", "op_consulting_charge": 1200, "op_consulting_charge_item": "HC-TOBACCO-SPECIALIST"}
            ]
        },
        {
            "appointment_type": "Quit Tobacco Specialist Follow up",
            "allow_booking_for": "Department",
            "default_duration": 30,
            "color": colors.get("grey", "#808080"),
            "price_list": "Standard Selling",
            "is_consultation": 1,
            "appointment_description": "",
            "items": [
                {"dt": "Medical Department", "dn": "Tobacco Cessation", "op_consulting_charge": 1200, "op_consulting_charge_item": "HC-TOBACCO-SPECIALIST"}
            ]
        },
        {
            "appointment_type": "Quit Tobacco Coach Counselling",
            "allow_booking_for": "Department",
            "default_duration": 30,
            "color": colors.get("dark grey", "#696969"),
            "price_list": "Standard Selling",
            "is_consultation": 1,
            "appointment_description": "",
            "items": [
                {"dt": "Medical Department", "dn": "Tobacco Cessation", "op_consulting_charge": 800, "op_consulting_charge_item": "HC-TOBACCO-COACH"}
            ]
        },
        {
            "appointment_type": "Quit Tobacco Coach Follow up",
            "allow_booking_for": "Department",
            "default_duration": 20,
            "color": colors.get("grey", "#808080"),
            "price_list": "Standard Selling",
            "is_consultation": 1,
            "appointment_description": "",
            "items": [
                {"dt": "Medical Department", "dn": "Tobacco Cessation", "op_consulting_charge": 800, "op_consulting_charge_item": "HC-TOBACCO-COACH"}
            ]
        },
        {
            "appointment_type": "Oral Specialist Consultation",
            "allow_booking_for": "Practitioner",
            "default_duration": 30,
            "color": colors.get("blue", "#3498db"),
            "price_list": "Standard Selling",
            "is_consultation": 1,
            "appointment_description": "",
            "items": [
                {"dt": "Medical Department", "dn": "Photo Medicine", "op_consulting_charge": 1000, "op_consulting_charge_item": "HC-ORAL-CONSULTATION"}
            ]
        },
        {
            "appointment_type": "Dental Consultation",
            "allow_booking_for": "Department",
            "default_duration": 30,
            "color": "#3498db",
            "price_list": "Standard Selling",
            "is_consultation": 1,
            "appointment_description": "",
            "items": [
                {"dt": "Medical Department", "dn": "Photo Medicine", "op_consulting_charge": 1000, "op_consulting_charge_item": "HC-ORAL-CONSULTATION"}
            ]
        },
        {
            "appointment_type": "Dental Procedure",
            "allow_booking_for": "Practitioner",
            "default_duration": 60,
            "color": "#2980b9",
            "price_list": "Standard Selling",
            "is_consultation": 0,
            "appointment_description": "Procedure charges as per procedure template",
            "items": [
                {"dt": "Medical Department", "dn": "Photo Medicine", "op_consulting_charge": 0, "op_consulting_charge_item": "HC-PROCEDURE"}
            ]
        },
        {
            "appointment_type": "Health Screening",
            "allow_booking_for": "Department",
            "default_duration": 30,
            "color": "#27ae60",
            "price_list": "Standard Selling",
            "is_consultation": 0,
            "appointment_description": "",
            "items": [
                {"dt": "Medical Department", "dn": "Public Health", "op_consulting_charge": 300, "op_consulting_charge_item": "HC-HEALTH-SCREENING"}
            ]
        },
        {
            "appointment_type": "Oral Screening",
            "allow_booking_for": "Department",
            "default_duration": 20,
            "color": "#16a085",
            "price_list": "Standard Selling",
            "is_consultation": 0,
            "appointment_description": "",
            "items": [
                {"dt": "Medical Department", "dn": "Photo Medicine", "op_consulting_charge": 300, "op_consulting_charge_item": "HC-HEALTH-SCREENING"}
            ]
        },
        {
            "appointment_type": "Oral PhotoDiagnostics",
            "allow_booking_for": "Department",
            "default_duration": 20,
            "color": "#8e44ad",
            "price_list": "Standard Selling",
            "is_consultation": 0,
            "appointment_description": "Procedure charges as per procedure template",
            "items": [
                {"dt": "Medical Department", "dn": "Photo Medicine", "op_consulting_charge": 1800, "op_consulting_charge_item": "HC-PHOTODIAGNOSTICS"}
            ]
        },
        {
            "appointment_type": "Oral Follow up - After Procedure (One Time)",
            "allow_booking_for": "Practitioner",
            "default_duration": 20,
            "color": "#95a5a6",
            "price_list": "Standard Selling",
            "is_consultation": 0,
            "appointment_description": "",
            "items": [
                {"dt": "Medical Department", "dn": "Photo Medicine", "op_consulting_charge": 0, "op_consulting_charge_item": "HC-FOLLOWUP-FREE"}
            ]
        },
        {
            "appointment_type": "PBM Treatment Planning",
            "allow_booking_for": "Practitioner",
            "default_duration": 30,
            "color": "#e67e22",
            "price_list": "Standard Selling",
            "is_consultation": 0,
            "appointment_description": "If doing a procedure",
            "items": [
                {"dt": "Medical Department", "dn": "Photo Medicine", "op_consulting_charge": 0, "op_consulting_charge_item": "HC-PROCEDURE"}
            ]
        },
        {
            "appointment_type": "PBM Treatment Sessions",
            "allow_booking_for": "Practitioner",
            "default_duration": 20,
            "color": colors.get("orange", "#e67e22"),
            "price_list": "Standard Selling",
            "is_consultation": 0,
            "appointment_description": "Procedure charges as per procedure template",
            "items": [
                {"dt": "Medical Department", "dn": "Photo Medicine", "op_consulting_charge": 0, "op_consulting_charge_item": "HC-PROCEDURE"}
            ]
        },
        {
            "appointment_type": "PDT Pretreatment Planning",
            "allow_booking_for": "Practitioner",
            "default_duration": 30,
            "color": "#9b59b6",
            "price_list": "Standard Selling",
            "is_consultation": 0,
            "appointment_description": "Step 1 of PDT procedure",
            "items": [
                {"dt": "Medical Department", "dn": "Photo Medicine", "op_consulting_charge": 0, "op_consulting_charge_item": "HC-PROCEDURE"}
            ]
        },
        {
            "appointment_type": "PDT Treatment",
            "allow_booking_for": "Practitioner",
            "default_duration": 30,
            "color": colors.get("red", "#e74c3c"),
            "price_list": "Standard Selling",
            "is_consultation": 0,
            "appointment_description": "Procedure charges as per procedure template",
            "items": [
                {"dt": "Medical Department", "dn": "Photo Medicine", "op_consulting_charge": 0, "op_consulting_charge_item": "HC-PROCEDURE"}
            ]
        },
        {
            "appointment_type": "PDT Treatment Follow up",
            "allow_booking_for": "Practitioner",
            "default_duration": 20,
            "color": "#c0392b",
            "price_list": "Standard Selling",
            "is_consultation": 0,
            "appointment_description": "Procedure charges as per procedure template",
            "items": [
                {"dt": "Medical Department", "dn": "Photo Medicine", "op_consulting_charge": 0, "op_consulting_charge_item": "HC-PROCEDURE"}
            ]
        },
        {
            "appointment_type": "PDT Waiting / Observation",
            "allow_booking_for": "Service Unit",
            "default_duration": 180,
            "color": "#7f8c8d",
            "price_list": "Standard Selling",
            "is_consultation": 0,
            "appointment_description": "Step 2 of PDT procedure",
            "items": [
                {"dt": "Medical Department", "dn": "Photo Medicine", "op_consulting_charge": 0, "op_consulting_charge_item": "HC-PROCEDURE"}
            ]
        },
        {
            "appointment_type": "Nutritionist Consultation",
            "allow_booking_for": "Practitioner",
            "default_duration": 30,
            "color": "#2ecc71",
            "price_list": "Standard Selling",
            "is_consultation": 1,
            "appointment_description": "",
            "items": [
                {"dt": "Medical Department", "dn": "Diet & Nutrition", "op_consulting_charge": 1200, "op_consulting_charge_item": "HC-NUTRITIONIST"}
            ]
        },
        {
            "appointment_type": "Ayurveda Consultation",
            "allow_booking_for": "Practitioner",
            "default_duration": 30,
            "color": "#f39c12",
            "price_list": "Standard Selling",
            "is_consultation": 1,
            "appointment_description": "",
            "items": [
                {"dt": "Medical Department", "dn": "Traditional Medicine", "op_consulting_charge": 1200, "op_consulting_charge_item": "HC-AYURVEDA"}
            ]
        },
        {
            "appointment_type": "Naturopath Consultation",
            "allow_booking_for": "Practitioner",
            "default_duration": 30,
            "color": "#1abc9c",
            "price_list": "Standard Selling",
            "is_consultation": 1,
            "appointment_description": "",
            "items": [
                {"dt": "Medical Department", "dn": "Traditional Medicine", "op_consulting_charge": 1200, "op_consulting_charge_item": "HC-NATUROPATH"}
            ]
        }
    ]
    
    for apt in appointment_types:
        if not frappe.db.exists("Appointment Type", apt["appointment_type"]):
            try:
                doc = frappe.new_doc("Appointment Type")
                doc.appointment_type = apt["appointment_type"]
                doc.allow_booking_for = apt["allow_booking_for"]
                doc.default_duration = apt["default_duration"]
                doc.color = apt.get("color")
                
                # Custom fields
                doc.is_consultation = apt.get("is_consultation", 1)
                doc.appointment_description = apt.get("appointment_description", "")
                
                # Price List
                if apt.get("price_list") and frappe.db.exists("Price List", apt["price_list"]):
                    doc.price_list = apt["price_list"]
                
                # Service Items (child table)
                for item in apt.get("items", []):
                    if item.get("dn") and frappe.db.exists(item["dt"], item["dn"]):
                        # Check if item exists
                        item_code = item.get("op_consulting_charge_item")
                        if item_code and not frappe.db.exists("Item", item_code):
                            item_code = None
                        
                        doc.append("items", {
                            "dt": item["dt"],
                            "dn": item["dn"],
                            "op_consulting_charge_item": item_code,
                            "op_consulting_charge": item.get("op_consulting_charge", 0)
                        })
                
                doc.flags.ignore_permissions = True
                doc.insert()
                consultation_status = "✓ Consultation" if apt.get("is_consultation") else "○ Non-Consultation"
                print(f"  ✓ Created: {apt['appointment_type']} [{consultation_status}]")
            except Exception as e:
                print(f"  ✗ Error creating {apt['appointment_type']}: {str(e)}")
        else:
            print(f"  - Already exists: {apt['appointment_type']}")

