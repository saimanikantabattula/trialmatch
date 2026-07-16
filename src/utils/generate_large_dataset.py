import random
import os
from db import init_db, add_patient, add_trial
from eligibility_extractor import extract_eligibility

# Clear old database
if os.path.exists('trialmatch.db'):
    os.remove('trialmatch.db')
    print("✓ Old database cleared")

init_db()

# Generate 500 patients
print("\nGenerating 500 synthetic patients...")

conditions_list = [
    "type 2 diabetes", "hypertension", "heart disease",
    "cancer", "asthma", "COPD", "arthritis", "depression",
    "obesity", "kidney disease", "thyroid disorder", "lupus"
]

medications_list = [
    "metformin", "lisinopril", "atorvastatin", "aspirin",
    "insulin", "omeprazole", "sertraline", "levothyroxine",
    "albuterol", "vitamin D", "ibuprofen", "enalapril"
]

for i in range(500):
    patient_id = f"P{i:04d}"
    age = random.randint(18, 85)
    conditions = random.sample(conditions_list, k=random.randint(1, 4))
    lab_values = {
        "HbA1c": round(random.uniform(5.0, 10.0), 1),
        "eGFR": random.randint(15, 120),
        "glucose": random.randint(70, 350),
        "creatinine": round(random.uniform(0.5, 3.0), 2),
        "blood_pressure_systolic": random.randint(100, 180)
    }
    medications = random.sample(medications_list, k=random.randint(0, 6))
    pregnancy_status = random.choice([True, False]) if age < 50 else False
    
    add_patient(
        patient_id=patient_id,
        age=age,
        conditions=conditions,
        lab_values=lab_values,
        medications=medications,
        pregnancy_status=pregnancy_status
    )
    
    if (i + 1) % 100 == 0:
        print(f"  Generated {i + 1} patients...")

print("✓ Generated 500 patients")

# Add 20 realistic trials
print("\nAdding 20 clinical trials...")

sample_trials = [
    {"trial_id": "NCT04623697", "title": "Efficacy of Dapagliflozin in Type 2 Diabetes", "condition": "Type 2 Diabetes", "criteria": """
    Inclusion: Age 18-75, Type 2 diabetes, HbA1c 7.5-11%
    Exclusion: eGFR < 30, Pregnancy, Recent hospitalization
    """},
    {"trial_id": "NCT05123456", "title": "Losartan for Hypertension Management", "condition": "Hypertension", "criteria": """
    Inclusion: Age 21-80, Hypertension, Systolic BP 140-180
    Exclusion: Severe heart disease, Recent stroke, Pregnancy
    """},
    {"trial_id": "NCT04856789", "title": "Cardiac Rehabilitation Study", "condition": "Heart Disease", "criteria": """
    Inclusion: Age 40-75, Recent MI, Stable condition
    Exclusion: Unstable angina, Severe heart failure, Pregnancy
    """},
    {"trial_id": "NCT05234567", "title": "Anti-Inflammatory for COPD", "condition": "COPD", "criteria": """
    Inclusion: Age 40-85, COPD diagnosis, FEV1 25-60%
    Exclusion: Active cancer, Recent hospitalization, Pregnancy
    """},
    {"trial_id": "NCT05345678", "title": "Biological Agent for Rheumatoid Arthritis", "condition": "Arthritis", "criteria": """
    Inclusion: Age 18-75, RA diagnosis, Active disease
    Exclusion: eGFR < 30, Active infection, Pregnancy
    """},
    {"trial_id": "NCT05456789", "title": "Cognitive Therapy for Depression", "condition": "Depression", "criteria": """
    Inclusion: Age 65-85, Major depression, PHQ-9 >= 15
    Exclusion: Active suicidal ideation, Severe cognitive impairment
    """},
    {"trial_id": "NCT05567890", "title": "Inhaled Corticosteroid for Asthma", "condition": "Asthma", "criteria": """
    Inclusion: Age 6-65, Asthma diagnosis, Poorly controlled
    Exclusion: Recent exacerbation, Active smoking > 10 pack-years
    """},
    {"trial_id": "NCT05678901", "title": "Alzheimer's Prevention Study", "condition": "Alzheimer's Disease", "criteria": """
    Inclusion: Age 55-80, Cognitively normal, Family history
    Exclusion: Mild cognitive impairment, Stroke history
    """},
    {"trial_id": "NCT05789012", "title": "Anticoagulant for Atrial Fibrillation", "condition": "Atrial Fibrillation", "criteria": """
    Inclusion: Age 18-75, AF diagnosis, CHA2DS2-VASc >= 1
    Exclusion: eGFR < 15, Active bleeding, Pregnancy
    """},
    {"trial_id": "NCT05890123", "title": "Immunotherapy for Advanced Melanoma", "condition": "Cancer", "criteria": """
    Inclusion: Age 18-75, Stage III/IV melanoma
    Exclusion: Prior immunotherapy, Active autoimmune disease
    """},
    {"trial_id": "NCT05901234", "title": "GLP-1 Agonist for Obesity", "condition": "Obesity", "criteria": """
    Inclusion: Age 25-70, BMI > 30, No diabetes
    Exclusion: History of thyroid cancer, Pregnancy
    """},
    {"trial_id": "NCT05912345", "title": "ACE Inhibitor for Kidney Protection", "condition": "Kidney Disease", "criteria": """
    Inclusion: Age 18-80, CKD Stage 2-3, Diabetes or Hypertension
    Exclusion: eGFR < 15, Potassium > 5.5, Pregnancy
    """},
    {"trial_id": "NCT05923456", "title": "Levothyroxine Dosing Study", "condition": "Thyroid Disorder", "criteria": """
    Inclusion: Age 18-75, Hypothyroidism, TSH abnormal
    Exclusion: Pregnancy, Active thyroid cancer, Recent MI
    """},
    {"trial_id": "NCT05934567", "title": "Biologic for Lupus", "condition": "Lupus", "criteria": """
    Inclusion: Age 18-75, SLE diagnosis, Active disease
    Exclusion: Active infection, eGFR < 30, Pregnancy
    """},
    {"trial_id": "NCT05945678", "title": "SGLT2 Inhibitor for Heart Failure", "condition": "Heart Disease", "criteria": """
    Inclusion: Age 18-80, Heart failure diagnosis
    Exclusion: eGFR < 20, Type 1 diabetes, Pregnancy
    """},
    {"trial_id": "NCT05956789", "title": "Metformin for Prediabetes Prevention", "condition": "Type 2 Diabetes", "criteria": """
    Inclusion: Age 25-75, Prediabetes, BMI > 25
    Exclusion: eGFR < 30, Type 1 diabetes, Pregnancy
    """},
    {"trial_id": "NCT05967890", "title": "Bronchodilator for COPD Exacerbation", "condition": "COPD", "criteria": """
    Inclusion: Age 40-85, COPD with recent exacerbation
    Exclusion: Active infection, Heart failure, Pregnancy
    """},
    {"trial_id": "NCT05978901", "title": "NSAIDs for Osteoarthritis", "condition": "Arthritis", "criteria": """
    Inclusion: Age 50-85, Osteoarthritis, Moderate pain
    Exclusion: eGFR < 30, Active GI bleed, Pregnancy
    """},
    {"trial_id": "NCT05989012", "title": "Antidepressant for Treatment Resistant", "condition": "Depression", "criteria": """
    Inclusion: Age 18-75, Treatment resistant depression
    Exclusion: Active suicidal ideation, Bipolar disorder
    """},
    {"trial_id": "NCT05990123", "title": "Immunotherapy Response Predictors", "condition": "Cancer", "criteria": """
    Inclusion: Age 18-80, Stage III/IV solid tumors
    Exclusion: Prior chemotherapy within 6 months, ECOG > 2
    """},
]

for trial in sample_trials:
    eligibility_rules = extract_eligibility(trial['criteria'])
    add_trial(
        trial_id=trial['trial_id'],
        title=trial['title'],
        condition=trial['condition'],
        eligibility_rules=eligibility_rules,
        status='recruiting'
    )
    print(f"  ✓ {trial['trial_id']}: {trial['title'][:50]}...")

print(f"\n✓ Added {len(sample_trials)} clinical trials")
print("\n" + "="*60)
print("✓ DATASET READY!")
print(f"  - 500 patients")
print(f"  - {len(sample_trials)} trials")
print(f"  - {500 * len(sample_trials):,} possible matches")
print("="*60)
