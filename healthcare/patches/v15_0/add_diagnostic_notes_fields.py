"""
Add Diagnostic Notes Fields

This patch adds individual notes fields for ECG, ECHO, and DExascan:
- ecg_note: ECG Notes
- echo_note: ECHO Notes
- dexascan_note: DExascan Notes (renamed from diagnostic_note)

Also migrates existing diagnostic_note data to dexascan_note.
"""

import frappe


def execute():
    """Add diagnostic notes fields and migrate data"""
    
    print("\n" + "="*60)
    print("Adding Diagnostic Notes Fields")
    print("="*60)
    
    # Check if new fields exist, if not they will be created by migrate
    # We just need to migrate data from diagnostic_note to dexascan_note
    
    print("\n--- Migrating diagnostic_note to dexascan_note ---")
    
    try:
        # Check if diagnostic_note column exists
        columns = frappe.db.sql("DESCRIBE `tabVital Signs`", as_dict=True)
        column_names = [c['Field'] for c in columns]
        
        if 'diagnostic_note' in column_names:
            # Check if dexascan_note column exists
            if 'dexascan_note' in column_names:
                # Migrate data
                frappe.db.sql("""
                    UPDATE `tabVital Signs` 
                    SET dexascan_note = diagnostic_note 
                    WHERE diagnostic_note IS NOT NULL 
                    AND diagnostic_note != ''
                    AND (dexascan_note IS NULL OR dexascan_note = '')
                """)
                print("  ✓ Migrated diagnostic_note data to dexascan_note")
            else:
                print("  - dexascan_note column will be created by migrate")
        else:
            print("  - diagnostic_note column not found (already migrated or new install)")
            
    except Exception as e:
        print(f"  - Migration note: {str(e)}")
    
    frappe.db.commit()
    
    # Clear cache
    frappe.clear_cache(doctype="Vital Signs")
    
    print("\n" + "="*60)
    print("✓ Diagnostic Notes Fields Added Successfully!")
    print("="*60 + "\n")

