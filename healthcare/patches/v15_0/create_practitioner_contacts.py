import frappe


def execute():
    """
    Create Contact records for Healthcare Practitioners who have email_id
    This is required for Google Calendar to send invitations
    """
    print("=" * 60)
    print("Creating Contacts for Healthcare Practitioners")
    print("=" * 60)
    
    practitioners = frappe.get_all(
        "Healthcare Practitioner",
        filters={"email_id": ["is", "set"]},
        fields=["name", "practitioner_name", "email_id", "mobile_phone"]
    )
    
    created = 0
    skipped = 0
    
    for prac in practitioners:
        # Check if contact already exists for this practitioner
        existing_contact = frappe.db.exists(
            "Dynamic Link",
            {
                "parenttype": "Contact",
                "link_doctype": "Healthcare Practitioner",
                "link_name": prac.name
            }
        )
        
        if existing_contact:
            print(f"  - Contact exists: {prac.practitioner_name}")
            skipped += 1
            continue
        
        # Create new contact
        try:
            # Split practitioner name into first and last name
            name_parts = prac.practitioner_name.split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            contact = frappe.get_doc({
                "doctype": "Contact",
                "first_name": first_name,
                "last_name": last_name,
                "is_primary_contact": 1,
            })
            
            # Add link to Healthcare Practitioner
            contact.append("links", {
                "link_doctype": "Healthcare Practitioner",
                "link_name": prac.name
            })
            
            # Add email
            if prac.email_id:
                contact.append("email_ids", {
                    "email_id": prac.email_id,
                    "is_primary": 1
                })
            
            # Add mobile if available
            if prac.mobile_phone:
                contact.append("phone_nos", {
                    "phone": prac.mobile_phone,
                    "is_primary_mobile_no": 1
                })
            
            contact.insert(ignore_permissions=True)
            print(f"  ✓ Created Contact: {prac.practitioner_name} ({prac.email_id})")
            created += 1
            
        except Exception as e:
            print(f"  ✗ Error creating contact for {prac.practitioner_name}: {str(e)}")
    
    print()
    print(f"  ✓ Created: {created}")
    print(f"  - Skipped: {skipped}")
    print()
    print("=" * 60)
    print("✓ Practitioner Contacts Created!")
    print("=" * 60)
    
    frappe.db.commit()

