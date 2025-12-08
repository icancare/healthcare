"""
Add ICD-11 Code Value Link Field to Diagnosis

NOTE: This patch is DISABLED - ICD-11 codes are already handled via 
Medical Coding (Codification Table) child table in Diagnosis.
No separate ICD fields needed.
"""

import frappe


def execute():
    """DISABLED - ICD-11 already in Medical Coding section"""
    
    print("\n--- ICD-11 Link Field Patch SKIPPED ---")
    print("  - ICD-11 codes already available in Medical Coding section")
    print("  - No additional fields needed")
    
    # This patch does nothing now
    pass

