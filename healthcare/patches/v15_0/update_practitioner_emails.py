"""
Update Healthcare Practitioner email_id from User ID or sheet data

This patch:
- Updates email_id field from user_id for practitioners who have user linked
- Adds email for practitioners from client sheet data
"""

import frappe


def execute():
    """Update Practitioner emails"""
    
    print("\n" + "="*60)
    print("Updating Healthcare Practitioner Emails")
    print("="*60)
    
    # Email data from client sheet
    practitioner_emails = {
        "Pawan Gupta": "pawan@icancare.com",
        "Shruti Agrawal": "shruti@icancare.com",
        "Rishabh Agrawal": "rishabh@icancare.com",
        "Sohan Lal": "support@icancare.com",
        "Pushpender Kumar": "pushpender.kumar@icancare.com",
        "Kaushal Chaudhary": "maxlabgv@gmail.com",
        "Rohit Thakur": "maxvshtcc@icancare.com",
        "Ganesh Dubey": "dubeyganesh01@gmail.com",
        "Supriya Wadhwa": "supriya.6583@gmail.com",
        # These don't have email in sheet
        # "Shama": None,
        # "Shipra Sharma": None,
        # "Deeksha Sharma": None,
        # "Minu Kumari": None,
    }
    
    # Get all practitioners
    practitioners = frappe.get_all(
        "Healthcare Practitioner",
        fields=["name", "practitioner_name", "user_id", "email_id"]
    )
    
    print(f"\n--- Updating {len(practitioners)} Practitioners ---")
    
    updated = 0
    skipped = 0
    
    for prac in practitioners:
        new_email = None
        
        # First check if email exists in our data
        if prac.practitioner_name in practitioner_emails:
            new_email = practitioner_emails[prac.practitioner_name]
        # If not in sheet, try to get from user_id
        elif prac.user_id:
            new_email = prac.user_id
        
        # Skip if no email found or already has email
        if not new_email:
            print(f"  - No email: {prac.practitioner_name}")
            skipped += 1
            continue
        
        if prac.email_id == new_email:
            print(f"  - Already set: {prac.practitioner_name}")
            skipped += 1
            continue
        
        # Update email_id
        try:
            frappe.db.set_value(
                "Healthcare Practitioner",
                prac.name,
                "email_id",
                new_email
            )
            print(f"  ✓ Updated: {prac.practitioner_name} → {new_email}")
            updated += 1
        except Exception as e:
            print(f"  ✗ Error: {prac.practitioner_name} - {str(e)}")
    
    frappe.db.commit()
    
    print(f"\n  ✓ Updated: {updated}")
    print(f"  - Skipped: {skipped}")
    
    print("\n" + "="*60)
    print("✓ Practitioner Emails Updated!")
    print("="*60 + "\n")

