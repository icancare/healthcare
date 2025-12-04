"""
Add Diagnosis Categories and update existing Diagnoses

This patch creates common diagnosis categories and optionally links existing diagnoses.
"""

import frappe


def execute():
    """Add Diagnosis Categories"""
    
    # Define diagnosis categories with their common diagnoses
    categories = {
        "Respiratory": [
            "Acute upper respiratory infection",
            "Community-acquired pneumonia",
            "Bronchitis",
            "Asthma",
            "COPD",
            "Tuberculosis",
            "Pulmonary Fibrosis",
            "Sleep Apnea",
            "Pneumonia",
            "Bronchiectasis",
            "Emphysema",
            "Pleurisy",
            "Respiratory Failure"
        ],
        "Cardiovascular": [
            "Blood Pressure (Hypertension)",
            "Hypertension",
            "Heart Disease",
            "Coronary Artery Disease",
            "Heart Failure",
            "Arrhythmia",
            "Atrial Fibrillation",
            "Myocardial Infarction",
            "Angina",
            "Stroke",
            "Peripheral Vascular Disease",
            "Deep Vein Thrombosis",
            "Pulmonary Embolism"
        ],
        "Metabolic": [
            "Diabetes",
            "Diabetes Type 1",
            "Diabetes Type 2",
            "Thyroid Disorder",
            "Hypothyroidism",
            "Hyperthyroidism",
            "Obesity",
            "High Cholesterol",
            "Hyperlipidemia",
            "Metabolic Syndrome",
            "Gout"
        ],
        "Neurological": [
            "Neurological disease (Epilepsy)",
            "Epilepsy",
            "Alzheimer's Disease",
            "Parkinson's Disease",
            "Multiple Sclerosis",
            "Migraine",
            "Neuropathy",
            "Stroke",
            "Dementia",
            "Seizure Disorder",
            "Bell's Palsy"
        ],
        "Gastrointestinal": [
            "Liver Disease",
            "Renal Disease",
            "Gastritis",
            "GERD",
            "Peptic Ulcer",
            "Crohn's Disease",
            "Ulcerative Colitis",
            "Irritable Bowel Syndrome",
            "Hepatitis",
            "Cirrhosis",
            "Pancreatitis",
            "Cholecystitis"
        ],
        "Immunosuppressive Conditions": [
            "Immunosuppressive Condition HIV, transplant, steroids",
            "HIV/AIDS",
            "Organ Transplant",
            "Immunodeficiency",
            "Lupus",
            "Rheumatoid Arthritis",
            "Psoriasis"
        ],
        "Autoimmune": [
            "Rheumatoid Arthritis",
            "Lupus",
            "Psoriasis",
            "Crohn's Disease",
            "Celiac Disease",
            "Multiple Sclerosis",
            "Hashimoto's Thyroiditis",
            "Graves' Disease",
            "Sjogren's Syndrome"
        ],
        "Oncological": [
            "CANCER PAST - on treatment",
            "Breast Cancer",
            "Colon Cancer",
            "Lung Cancer",
            "Prostate Cancer",
            "Ovarian Cancer",
            "Skin Cancer",
            "Leukemia",
            "Lymphoma",
            "Oral Cancer",
            "Pancreatic Cancer"
        ],
        "Ophthalmological": [
            "Eye Problem",
            "Glaucoma",
            "Cataract",
            "Macular Degeneration",
            "Diabetic Retinopathy",
            "Dry Eye Syndrome"
        ],
        "Oral/Dental": [
            "ORAL PML - on treatment",
            "Restricted Mouth Opening",
            "Oral Submucous Fibrosis",
            "Leukoplakia",
            "Oral Lichen Planus",
            "Periodontitis",
            "Dental Caries"
        ],
        "Reproductive": [
            "Infertility",
            "Polycystic Ovary Syndrome",
            "Endometriosis",
            "Erectile Dysfunction",
            "Prostate Hyperplasia"
        ],
        "Musculoskeletal": [
            "Osteoarthritis",
            "Osteoporosis",
            "Rheumatoid Arthritis",
            "Fibromyalgia",
            "Back Pain",
            "Herniated Disc",
            "Scoliosis"
        ],
        "Mental Health": [
            "Depression",
            "Anxiety",
            "Bipolar Disorder",
            "Schizophrenia",
            "OCD",
            "PTSD",
            "ADHD",
            "Insomnia"
        ],
        "Infectious Diseases": [
            "Cholera",
            "Typhoid",
            "Malaria",
            "Dengue",
            "COVID-19",
            "Influenza",
            "Hepatitis A",
            "Hepatitis B",
            "Hepatitis C"
        ],
        "Allergic Conditions": [
            "Allergies Drug / food / chemical sensitivity",
            "Drug Allergy",
            "Food Allergy",
            "Allergic Rhinitis",
            "Urticaria",
            "Anaphylaxis",
            "Contact Dermatitis"
        ],
        "Genetic Disorders": [
            "Sickle Cell Disease",
            "Thalassemia",
            "Hemophilia",
            "Cystic Fibrosis",
            "Down Syndrome",
            "Muscular Dystrophy",
            "Huntington's Disease"
        ],
        "Other": [
            "Medical Disease",
            "Any Surgery Done",
            "Other Relevant Conditions e.g., Autoimmune, anemia, thyroid",
            "Anemia",
            "Chronic Fatigue Syndrome"
        ]
    }
    
    # Create Diagnosis Categories
    for category_name in categories.keys():
        if not frappe.db.exists("Diagnosis Category", category_name):
            doc = frappe.new_doc("Diagnosis Category")
            doc.category_name = category_name
            doc.is_active = 1
            doc.flags.ignore_permissions = True
            doc.insert()
            print(f"✓ Created Diagnosis Category: {category_name}")
    
    frappe.db.commit()
    
    # Create Diagnoses and link to categories
    for category_name, diagnoses in categories.items():
        for diagnosis_name in diagnoses:
            if not frappe.db.exists("Diagnosis", diagnosis_name):
                doc = frappe.new_doc("Diagnosis")
                doc.diagnosis = diagnosis_name
                doc.diagnosis_category = category_name
                doc.flags.ignore_permissions = True
                try:
                    doc.insert()
                    print(f"  ✓ Created Diagnosis: {diagnosis_name} -> {category_name}")
                except Exception as e:
                    print(f"  ✗ Could not create Diagnosis: {diagnosis_name} - {str(e)}")
            else:
                # Update existing diagnosis with category
                frappe.db.set_value("Diagnosis", diagnosis_name, "diagnosis_category", category_name)
                print(f"  ✓ Updated Diagnosis: {diagnosis_name} -> {category_name}")
    
    frappe.db.commit()
    print("\n✓ Diagnosis Categories setup completed!")

