"""
Add predefined Allergen and Allergen Reaction data

This patch adds the standard list of allergens and reactions from medical standards.
"""

import frappe


def execute():
    """Add predefined Allergen and Allergen Reaction data"""
    
    # Allergen list from screenshot
    allergens = [
        ("Penicillin", "Antibiotic allergy"),
        ("Sulfa Drugs", "Sulfonamide antibiotics allergy"),
        ("NSAIDs", "Non-steroidal anti-inflammatory drugs allergy"),
        ("Latex", "Natural rubber latex allergy"),
        ("Contrast Dye (Iodinated)", "Iodine-based contrast media allergy"),
        ("Shellfish", "Shellfish allergy"),
        ("Seafood", "Seafood allergy"),
        ("Peanuts", "Peanut allergy"),
        ("Tree Nuts", "Tree nuts allergy (almonds, cashews, walnuts, etc.)"),
        ("Eggs", "Egg allergy"),
        ("Milk", "Milk/dairy allergy"),
        ("Gluten", "Gluten intolerance/allergy"),
        ("Bee/Wasp Sting", "Insect sting allergy"),
        ("Pollen", "Pollen allergy (hay fever)"),
        ("Dust Mites", "Dust mite allergy"),
        ("Animal Dander", "Pet dander allergy"),
        ("Mold/Fungi", "Mold and fungi allergy"),
        ("Fish", "Fish allergy"),
        ("Soy", "Soy allergy"),
        ("Wheat", "Wheat allergy"),
        ("Sesame Seeds", "Sesame allergy"),
        ("MSG/Additives", "Food additives allergy"),
        ("Fragrances", "Fragrance/perfume allergy"),
        ("Nickel", "Nickel metal allergy"),
        ("Cosmetics/Hair Dye", "Cosmetic products allergy"),
        ("Food Colourings", "Food dye allergy"),
        ("ACE-Inhibitors", "ACE inhibitor medication allergy"),
        ("ARBs", "Angiotensin receptor blocker allergy"),
        ("Cockroach Allergen", "Cockroach allergy"),
        ("Aspirin", "Aspirin allergy"),
        ("Codeine", "Codeine/opioid allergy"),
        ("Local Anesthetics", "Local anesthetic allergy"),
    ]
    
    # Allergen Reaction list from screenshot (Stanford list)
    reactions = [
        ("Altered mental status", "Changes in consciousness or mental state"),
        ("Anaphylaxis", "Severe life-threatening allergic reaction"),
        ("Angioedema", "Swelling beneath the skin"),
        ("Anxiety", "Feelings of anxiety or panic"),
        ("Blood product incompatibility", "Reaction to blood products"),
        ("Cardiovascular Arrest", "Heart stops beating"),
        ("Constipation", "Difficulty passing stool"),
        ("Cough", "Persistent coughing"),
        ("Delirium Red Man Syndrome", "Red flushing reaction"),
        ("Diaphoresis", "Excessive sweating"),
        ("Diarrhea", "Loose or watery stools"),
        ("Dizziness", "Feeling lightheaded or unsteady"),
        ("Fever", "Elevated body temperature"),
        ("Headache", "Pain in head"),
        ("Hematologic", "Blood-related reaction"),
        ("Hives 3 or more", "Multiple hives/urticaria"),
        ("Hives/urticaria", "Itchy welts on skin"),
        ("Hypertension", "High blood pressure"),
        ("Hypotension", "Low blood pressure"),
        ("Insomnia", "Difficulty sleeping"),
        ("Interstitial nephritis", "Kidney inflammation"),
        ("Itching, pruritus", "Skin itching"),
        ("Lightheadedness", "Feeling faint"),
        ("Malignant hyperthermia", "Dangerous rise in body temperature"),
        ("Migraine", "Severe headache"),
        ("Nausea, Vomiting", "Feeling sick or vomiting"),
        ("Palpitations", "Rapid or irregular heartbeat"),
        ("Rash", "Skin eruption"),
        ("Rhinitis", "Nasal inflammation"),
        ("Serum sickness", "Immune reaction to medications"),
        ("Shortness of Breath", "Difficulty breathing"),
        ("Stridor", "High-pitched breathing sound"),
        ("Swelling", "Tissue swelling"),
        ("Wheezing/bronchospasm", "Airway constriction"),
        ("Unknown", "Unknown reaction type"),
        ("Other mild (Specify with Comments)", "Other mild reaction - specify in comments"),
        ("Other (Specify with Comments)", "Other reaction - specify in comments"),
    ]
    
    # Insert Allergens
    for allergen_name, description in allergens:
        if not frappe.db.exists("Allergen", allergen_name):
            doc = frappe.new_doc("Allergen")
            doc.allergen_name = allergen_name
            doc.description = description
            doc.flags.ignore_permissions = True
            doc.insert()
    
    # Insert Allergen Reactions
    for reaction_name, description in reactions:
        if not frappe.db.exists("Allergen Reaction", reaction_name):
            doc = frappe.new_doc("Allergen Reaction")
            doc.reaction_name = reaction_name
            doc.description = description
            doc.flags.ignore_permissions = True
            doc.insert()
    
    frappe.db.commit()

