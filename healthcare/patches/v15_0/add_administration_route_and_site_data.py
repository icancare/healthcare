"""
Add predefined Administration Route and Administration Site data

This patch adds the standard list of routes and sites for immunization/medication administration.
"""

import frappe


def execute():
    """Add predefined Administration Route and Administration Site data"""
    
    # Administration Routes
    routes = [
        ("Oral", "Administered by mouth"),
        ("Intramuscular", "Injected into muscle tissue"),
        ("Intravenous", "Injected directly into a vein"),
        ("Subcutaneous", "Injected under the skin"),
        ("Intranasal", "Administered through the nose"),
        ("Topical", "Applied to the skin surface"),
        ("Inhalation", "Breathed into the lungs"),
        ("Rectal", "Administered through the rectum"),
        ("Intradermal", "Injected into the skin"),
        ("Sublingual", "Placed under the tongue"),
        ("Transdermal", "Absorbed through the skin"),
        ("Ophthalmic", "Applied to the eye"),
        ("Otic", "Applied to the ear"),
        ("Nasal", "Applied to the nasal passages"),
        ("Vaginal", "Administered vaginally"),
        ("Buccal", "Placed between gum and cheek"),
    ]
    
    # Administration Sites
    sites = [
        ("Left Upper Arm", "Left deltoid muscle area"),
        ("Right Upper Arm", "Right deltoid muscle area"),
        ("Left Thigh", "Left vastus lateralis muscle"),
        ("Right Thigh", "Right vastus lateralis muscle"),
        ("Left Buttock", "Left gluteal muscle"),
        ("Right Buttock", "Right gluteal muscle"),
        ("Abdomen", "Abdominal area"),
        ("Left Forearm", "Left forearm area"),
        ("Right Forearm", "Right forearm area"),
        ("Left Hand", "Left hand area"),
        ("Right Hand", "Right hand area"),
        ("Left Foot", "Left foot area"),
        ("Right Foot", "Right foot area"),
    ]
    
    # Insert Administration Routes
    for route_name, description in routes:
        if not frappe.db.exists("Administration Route", route_name):
            doc = frappe.new_doc("Administration Route")
            doc.route_name = route_name
            doc.description = description
            doc.flags.ignore_permissions = True
            doc.insert()
    
    # Insert Administration Sites
    for site_name, description in sites:
        if not frappe.db.exists("Administration Site", site_name):
            doc = frappe.new_doc("Administration Site")
            doc.site_name = site_name
            doc.description = description
            doc.flags.ignore_permissions = True
            doc.insert()
    
    frappe.db.commit()

