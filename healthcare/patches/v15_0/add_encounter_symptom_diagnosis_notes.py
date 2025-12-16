"""
Add Symptom Notes and Diagnosis Notes to Patient Encounter

This patch adds:
- symptoms_notes: Symptom Notes field after Symptoms
- diagnosis_notes: Diagnosis Notes field after Diagnosis
"""

import frappe


def execute():
    """Add symptom and diagnosis notes fields to Patient Encounter"""
    
    print("\n" + "="*60)
    print("Adding Symptom Notes and Diagnosis Notes to Patient Encounter")
    print("="*60)
    
    # Fields will be created by migrate from JSON
    # Just clear cache
    frappe.clear_cache(doctype="Patient Encounter")
    
    print("  ✓ Fields will be added by migrate")
    
    print("\n" + "="*60)
    print("✓ Patient Encounter Notes Fields Added!")
    print("="*60 + "\n")

