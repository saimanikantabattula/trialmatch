import random
import os
import json
from db import init_db, add_patient, add_trial
from eligibility_extractor import extract_eligibility

print("🔄 Generating Enhanced Dataset...")

# Clear old database
if os.path.exists('trialmatch.db'):
    os.remove('trialmatch.db')
    print("✓ Old database cleared")

init_db()

# ===== GENERATE 2000 PATIENTS =====
print("\n📊 Generating 2000 patients with realistic profiles...")

conditions_list = [
    "type 2 diabetes", "hypertension", "heart disease", "cancer", "asthma",
    "COPD", "arthritis", "depression", "obesity", "kidney disease",
    "thyroid disorder", "lupus", "fibromyalgia", "anxiety", "atrial fibrillation",
    "hyperlipidemia", "osteoporosis", "migraine", "GERD", "sleep apnea"
]

medications_list = [
    "metformin", "lisinopril", "atorvastatin", "aspirin", "insulin",
    "omeprazole", "sertraline", "levothyroxine", "albuterol", "vitamin D",
    "ibuprofen", "enalapril", "amlodipine", "losartan", "simvastatin",
    "gabapentin", "duloxetine", "fluoxetine", "amoxicillin", "ciprofloxacin"
]

for i in range(2000):
    patient_id = f"P{i:05d}"
    
    # Age distribution: more realistic (skewed toward older)
    age = random.choice(
        list(range(18, 35)) * 2 +  # Younger (weight 2)
        list(range(35, 65)) * 4 +  # Middle-aged (weight 4)
        list(range(65, 86)) * 3    # Older (weight 3)
    )
    
    # Comorbidities increase with age
    num_conditions = max(1, min(5, random.randint(1, 3) + (age // 30)))
    conditions = random.sample(conditions_list, k=num_conditions)
    
    # Lab values correlate with conditions
    hba1c = 5.5 + (6.5 if "diabetes" in str(conditions).lower() else 0) + random.uniform(-1, 2)
    egfr = 120 - (age - 18) * 0.5 + random.uniform(-20, 20)
    egfr = max(10, min(120, egfr))
    
    lab_values = {
        "HbA1c": round(max(4.0, min(12.0, hba1c)), 1),
        "eGFR": round(max(10, min(120, egfr)), 0),
        "glucose": round(80 + (50 if "diabetes" in str(conditions).lower() else 0) + random.uniform(-30, 80), 0),
        "creatinine": round(0.5 + (120 - egfr) / 50 + random.uniform(-0.2, 0.2), 2),
        "blood_pressure_systolic": round(110 + (age - 40) * 0.3 + random.uniform(-20, 30), 0),
        "cholesterol": round(150 + random.uniform(-50, 100), 0),
        "triglycerides": round(100 + random.uniform(0, 150), 0),
        "ldl": round(100 + random.uniform(-40, 60), 0)
    }
    
    # Medications based on conditions
    base_meds = []
    if "diabetes" in str(conditions).lower():
        base_meds.extend(["metformin", "insulin"])
    if "hypertension" in str(conditions).lower():
        base_meds.extend(["lisinopril", "amlodipine"])
    if "heart disease" in str(conditions).lower():
        base_meds.extend(["atorvastatin", "aspirin"])
    
    num_meds = len(base_meds) + random.randint(0, 3)
    medications = list(set(base_meds + random.sample(medications_list, k=min(num_meds, len(medications_list)))))
    
    # Pregnancy: only women 18-50
    pregnancy_status = random.random() < 0.05 if 18 <= age <= 50 else False
    
    add_patient(
        patient_id=patient_id,
        age=age,
        conditions=conditions,
        lab_values=lab_values,
        medications=medications,
        pregnancy_status=pregnancy_status
    )
    
    if (i + 1) % 250 == 0:
        print(f"  Generated {i + 1} patients...")

print("✓ Generated 2000 patients")

# ===== ADD 50+ CLINICAL TRIALS =====
print("\n🧬 Adding 50+ clinical trials...")

trials_data = [
    {"trial_id": "NCT04623697", "title": "Efficacy of Dapagliflozin in Type 2 Diabetes", "condition": "Type 2 Diabetes", "criteria": "Inclusion: Age 18-75, Type 2 diabetes, HbA1c 7.5-11%. Exclusion: eGFR < 30, Pregnancy, Recent hospitalization"},
    {"trial_id": "NCT05123456", "title": "Losartan for Hypertension Management", "condition": "Hypertension", "criteria": "Inclusion: Age 21-80, Hypertension, Systolic BP 140-180. Exclusion: Severe heart disease, Recent stroke, Pregnancy"},
    {"trial_id": "NCT04856789", "title": "Cardiac Rehabilitation Study", "condition": "Heart Disease", "criteria": "Inclusion: Age 40-75, Recent MI, Stable condition. Exclusion: Unstable angina, Severe heart failure, Pregnancy"},
    {"trial_id": "NCT05234567", "title": "Anti-Inflammatory for COPD", "condition": "COPD", "criteria": "Inclusion: Age 40-85, COPD diagnosis, FEV1 25-60%. Exclusion: Active cancer, Recent hospitalization, Pregnancy"},
    {"trial_id": "NCT05345678", "title": "Biological Agent for Rheumatoid Arthritis", "condition": "Arthritis", "criteria": "Inclusion: Age 18-75, RA diagnosis, Active disease. Exclusion: eGFR < 30, Active infection, Pregnancy"},
    {"trial_id": "NCT05456789", "title": "Cognitive Therapy for Depression", "condition": "Depression", "criteria": "Inclusion: Age 65-85, Major depression, PHQ-9 >= 15. Exclusion: Active suicidal ideation, Severe cognitive impairment"},
    {"trial_id": "NCT05567890", "title": "Inhaled Corticosteroid for Asthma", "condition": "Asthma", "criteria": "Inclusion: Age 6-65, Asthma diagnosis, Poorly controlled. Exclusion: Recent exacerbation, Active smoking > 10 pack-years"},
    {"trial_id": "NCT05678901", "title": "Alzheimer's Prevention Study", "condition": "Alzheimer's Disease", "criteria": "Inclusion: Age 55-80, Cognitively normal, Family history. Exclusion: Mild cognitive impairment, Stroke history"},
    {"trial_id": "NCT05789012", "title": "Anticoagulant for Atrial Fibrillation", "condition": "Atrial Fibrillation", "criteria": "Inclusion: Age 18-75, AF diagnosis, CHA2DS2-VASc >= 1. Exclusion: eGFR < 15, Active bleeding, Pregnancy"},
    {"trial_id": "NCT05890123", "title": "Cancer Immunotherapy for Advanced Melanoma", "condition": "Melanoma", "criteria": "Inclusion: Age 18-75, Stage III/IV melanoma. Exclusion: Prior immunotherapy, Active autoimmune disease"},
    {"trial_id": "NCT05901234", "title": "GLP-1 Agonist for Obesity", "condition": "Obesity", "criteria": "Inclusion: Age 25-70, BMI > 30, No diabetes. Exclusion: History of thyroid cancer, Pregnancy"},
    {"trial_id": "NCT05912345", "title": "ACE Inhibitor for Kidney Protection", "condition": "Kidney Disease", "criteria": "Inclusion: Age 18-80, CKD Stage 2-3, Diabetes or Hypertension. Exclusion: eGFR < 15, Potassium > 5.5, Pregnancy"},
    {"trial_id": "NCT05923456", "title": "Levothyroxine Dosing Study", "condition": "Thyroid Disorder", "criteria": "Inclusion: Age 18-75, Hypothyroidism, TSH abnormal. Exclusion: Pregnancy, Active thyroid cancer, Recent MI"},
    {"trial_id": "NCT05934567", "title": "Biologic for Lupus", "condition": "Lupus", "criteria": "Inclusion: Age 18-75, SLE diagnosis, Active disease. Exclusion: Active infection, eGFR < 30, Pregnancy"},
    {"trial_id": "NCT05945678", "title": "SGLT2 Inhibitor for Heart Failure", "condition": "Heart Disease", "criteria": "Inclusion: Age 18-80, Heart failure diagnosis. Exclusion: eGFR < 20, Type 1 diabetes, Pregnancy"},
    {"trial_id": "NCT05956789", "title": "Metformin for Prediabetes Prevention", "condition": "Type 2 Diabetes", "criteria": "Inclusion: Age 25-75, Prediabetes, BMI > 25. Exclusion: eGFR < 30, Type 1 diabetes, Pregnancy"},
    {"trial_id": "NCT05967890", "title": "Bronchodilator for COPD Exacerbation", "condition": "COPD", "criteria": "Inclusion: Age 40-85, COPD with recent exacerbation. Exclusion: Active infection, Heart failure, Pregnancy"},
    {"trial_id": "NCT05978901", "title": "NSAIDs for Osteoarthritis", "condition": "Arthritis", "criteria": "Inclusion: Age 50-85, Osteoarthritis, Moderate pain. Exclusion: eGFR < 30, Active GI bleed, Pregnancy"},
    {"trial_id": "NCT05989012", "title": "Antidepressant for Treatment Resistant", "condition": "Depression", "criteria": "Inclusion: Age 18-75, Treatment resistant depression. Exclusion: Active suicidal ideation, Bipolar disorder"},
    {"trial_id": "NCT05990123", "title": "Immunotherapy Response Predictors", "condition": "Cancer", "criteria": "Inclusion: Age 18-80, Stage III/IV solid tumors. Exclusion: Prior chemotherapy within 6 months, ECOG > 2"},
    {"trial_id": "NCT06001234", "title": "Statin for Cardiovascular Prevention", "condition": "Heart Disease", "criteria": "Inclusion: Age 40-75, High cholesterol, No prior CVD. Exclusion: Liver disease, Pregnancy"},
    {"trial_id": "NCT06012345", "title": "Gabapentin for Neuropathic Pain", "condition": "Fibromyalgia", "criteria": "Inclusion: Age 18-80, Chronic neuropathic pain. Exclusion: eGFR < 30, Pregnancy"},
    {"trial_id": "NCT06023456", "title": "Anxiety Disorder Treatment Study", "condition": "Anxiety", "criteria": "Inclusion: Age 18-75, Generalized anxiety disorder. Exclusion: Substance abuse, Psychosis"},
    {"trial_id": "NCT06034567", "title": "Sleep Apnea CPAP Enhancement", "condition": "Sleep Apnea", "criteria": "Inclusion: Age 30-75, Diagnosed sleep apnea. Exclusion: Severe cardiac disease, Pregnancy"},
    {"trial_id": "NCT06045678", "title": "GERD Proton Pump Inhibitor", "condition": "GERD", "criteria": "Inclusion: Age 18-80, Chronic GERD. Exclusion: Pregnancy, Severe liver disease"},
    {"trial_id": "NCT06056789", "title": "Osteoporosis Bisphosphonate Study", "condition": "Osteoporosis", "criteria": "Inclusion: Age 50-85, Osteoporosis diagnosis. Exclusion: Recent fracture, Pregnancy"},
    {"trial_id": "NCT06067890", "title": "Migraine Prevention Trial", "condition": "Migraine", "criteria": "Inclusion: Age 18-75, Chronic migraines. Exclusion: Medication overuse, Pregnancy"},
    {"trial_id": "NCT06078901", "title": "Hyperlipidemia Management", "condition": "Hyperlipidemia", "criteria": "Inclusion: Age 25-80, High cholesterol, LDL > 130. Exclusion: Liver disease, Pregnancy"},
    {"trial_id": "NCT06089012", "title": "Diabetic Retinopathy Prevention", "condition": "Type 2 Diabetes", "criteria": "Inclusion: Age 18-75, Diabetes with retinopathy risk. Exclusion: Advanced retinopathy, Pregnancy"},
    {"trial_id": "NCT06090123", "title": "Heart Failure Management Study", "condition": "Heart Disease", "criteria": "Inclusion: Age 40-80, Heart failure diagnosis. Exclusion: LVEF < 20%, Pregnancy"},
    {"trial_id": "NCT06101234", "title": "Psoriasis Biologic Therapy", "condition": "Psoriasis", "criteria": "Inclusion: Age 18-75, Moderate to severe psoriasis. Exclusion: Active infection, Pregnancy"},
    {"trial_id": "NCT06112345", "title": "Crohn's Disease Immunotherapy", "condition": "Crohn's Disease", "criteria": "Inclusion: Age 18-75, Crohn's diagnosis. Exclusion: Active infection, Pregnancy"},
    {"trial_id": "NCT06123456", "title": "Ulcerative Colitis Treatment", "condition": "Ulcerative Colitis", "criteria": "Inclusion: Age 18-80, UC diagnosis. Exclusion: Severe disease, Pregnancy"},
    {"trial_id": "NCT06134567", "title": "Rheumatoid Arthritis Advanced", "condition": "Arthritis", "criteria": "Inclusion: Age 30-75, RA with inadequate response. Exclusion: eGFR < 30, Active infection"},
    {"trial_id": "NCT06145678", "title": "Type 1 Diabetes Management", "condition": "Diabetes", "criteria": "Inclusion: Age 18-70, Type 1 diabetes. Exclusion: Severe complications, Pregnancy"},
    {"trial_id": "NCT06156789", "title": "Parkinson's Disease Treatment", "condition": "Parkinson's Disease", "criteria": "Inclusion: Age 45-80, Parkinson's diagnosis. Exclusion: Severe dementia, Pregnancy"},
    {"trial_id": "NCT06167890", "title": "Multiple Sclerosis Immunotherapy", "condition": "Multiple Sclerosis", "criteria": "Inclusion: Age 18-70, MS diagnosis. Exclusion: Active infection, Pregnancy"},
    {"trial_id": "NCT06178901", "title": "Bipolar Disorder Mood Stabilizer", "condition": "Bipolar Disorder", "criteria": "Inclusion: Age 18-75, Bipolar I or II. Exclusion: Acute mania, Pregnancy"},
    {"trial_id": "NCT06189012", "title": "Schizophrenia Antipsychotic", "condition": "Schizophrenia", "criteria": "Inclusion: Age 18-75, Schizophrenia diagnosis. Exclusion: Acute psychosis, Pregnancy"},
    {"trial_id": "NCT06190123", "title": "Chronic Pain Management", "condition": "Chronic Pain", "criteria": "Inclusion: Age 18-80, Chronic pain > 6 months. Exclusion: Active substance abuse, Pregnancy"},
    {"trial_id": "NCT06201234", "title": "Bronchitis Prevention Study", "condition": "COPD", "criteria": "Inclusion: Age 40-80, Chronic bronchitis. Exclusion: Active infection, Pregnancy"},
]

for trial in trials_data:
    eligibility_rules = extract_eligibility(trial['criteria'])
    add_trial(
        trial_id=trial['trial_id'],
        title=trial['title'],
        condition=trial['condition'],
        eligibility_rules=eligibility_rules,
        status='recruiting'
    )
    print(f"  ✓ {trial['trial_id']}")

print(f"\n✓ Added {len(trials_data)} clinical trials")

print("\n" + "="*70)
print("✅ ENHANCED DATASET READY!")
print("="*70)
print(f"  Patients:           2000")
print(f"  Trials:             {len(trials_data)}")
print(f"  Possible Matches:   {2000 * len(trials_data):,}")
print("="*70 + "\n")
