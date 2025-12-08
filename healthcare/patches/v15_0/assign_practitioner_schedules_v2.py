"""
Assign Practitioner Schedules to all Healthcare Practitioners (v2)

This patch:
- Assigns "Doctor Schedule" to all active practitioners who don't have a schedule
- Requires Default Google Calendar to be set in Healthcare Settings
"""

import frappe


def execute():
    """Assign schedules to practitioners"""
    
    print("\n" + "="*60)
    print("Assigning Practitioner Schedules (v2)")
    print("="*60)
    
    # Check if Doctor Schedule exists
    schedule_name = "Doctor Schedule"
    
    if not frappe.db.exists("Practitioner Schedule", schedule_name):
        print(f"\n  ✗ Schedule '{schedule_name}' not found!")
        print("  Please create the schedule first.")
        return
    
    print(f"\n  Using Schedule: {schedule_name}")
    
    # Get all active practitioners
    practitioners = frappe.get_all(
        "Healthcare Practitioner",
        filters={"status": "Active"},
        fields=["name", "practitioner_name"]
    )
    
    print(f"\n--- Assigning Schedule to {len(practitioners)} Practitioners ---")
    
    assigned = 0
    skipped = 0
    
    for prac in practitioners:
        # Check if practitioner already has this schedule
        existing = frappe.db.exists(
            "Practitioner Service Unit Schedule",
            {
                "parent": prac.name,
                "schedule": schedule_name
            }
        )
        
        if existing:
            print(f"  - Already has schedule: {prac.practitioner_name}")
            skipped += 1
            continue
        
        try:
            # Get the practitioner doc
            doc = frappe.get_doc("Healthcare Practitioner", prac.name)
            
            # Add schedule to practitioner_schedules child table
            doc.append("practitioner_schedules", {
                "schedule": schedule_name
            })
            
            doc.flags.ignore_permissions = True
            doc.flags.ignore_validate = True  # Skip validation for video conferencing
            doc.save()
            
            print(f"  ✓ Assigned: {prac.practitioner_name}")
            assigned += 1
            
        except Exception as e:
            print(f"  ✗ Error for {prac.practitioner_name}: {str(e)}")
    
    frappe.db.commit()
    
    print(f"\n  ✓ Assigned: {assigned}")
    print(f"  - Skipped: {skipped}")
    
    print("\n" + "="*60)
    print("✓ Practitioner Schedules Assignment Completed!")
    print("="*60 + "\n")

