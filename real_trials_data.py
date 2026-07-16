from db import add_trial
from eligibility_extractor import extract_eligibility

def add_realistic_trials():
    """
    Add realistic clinical trials based on real trial patterns from ClinicalTrials.gov.
    These are representative of actual trials.
    """
    
    real_trials = [
        {
            "trial_id": "NCT04623697",
            "title": "Efficacy and Safety of Dapagliflozin in Type 2 Diabetes",
            "condition": "Type 2 Diabetes",
            "criteria": """
            Inclusion Criteria:
            - Age 18 to 75 years
            - Diagnosed with type 2 diabetes mellitus
            - HbA1c 7.5% to 11.0%
            - Stable on current diabetes medications for at least 8 weeks
            
            Exclusion Criteria:
            - Type 1 diabetes
            - eGFR < 30 mL/min/1.73m2
            - Severe kidney disease
            - Recent myocardial infarction (within 3 months)
            - Pregnant or nursing
            - Active malignancy
            """
        },
        {
            "trial_id": "NCT05123456",
            "title": "A Study of Losartan in Patients with Hypertension",
            "condition": "Hypertension",
            "criteria": """
            Inclusion Criteria:
            - Age 21 to 80 years
            - Diagnosed with hypertension (systolic BP 140-180 mmHg)
            - Able to take oral medications
            
            Exclusion Criteria:
            - Severe heart disease
            - Recent stroke within 6 months
            - Liver disease
            - Pregnancy
            - Allergy to ACE inhibitors
            """
        },
        {
            "trial_id": "NCT04856789",
            "title": "Cardiac Rehabilitation after Heart Attack",
            "condition": "Heart Disease",
            "criteria": """
            Inclusion Criteria:
            - Age 40 to 75 years
            - Recent myocardial infarction (within 4 weeks)
            - Stable cardiac condition
            - Able to participate in exercise program
            
            Exclusion Criteria:
            - Unstable angina
            - Severe heart failure (NYHA Class IV)
            - Uncontrolled arrhythmias
            - Recent bypass surgery
            - Pregnancy
            """
        },
        {
            "trial_id": "NCT05234567",
            "title": "A Study of Anti-Inflammatory Drug in COPD Patients",
            "condition": "COPD",
            "criteria": """
            Inclusion Criteria:
            - Age 40 to 85 years
            - COPD diagnosis (moderate to severe)
            - FEV1 between 25% and 60% of predicted
            - Smoking history of at least 10 pack-years
            
            Exclusion Criteria:
            - Active cancer treatment
            - Recent hospitalization within 2 weeks
            - Severe liver disease
            - Pregnancy
            - Active tuberculosis
            """
        },
        {
            "trial_id": "NCT05345678",
            "title": "Arthritis Treatment with Biological Agent",
            "condition": "Rheumatoid Arthritis",
            "criteria": """
            Inclusion Criteria:
            - Age 18 to 75 years
            - Confirmed rheumatoid arthritis diagnosis
            - Active disease (DAS28 > 3.2)
            - Previous DMARD therapy
            
            Exclusion Criteria:
            - eGFR < 30
            - Active infection
            - TB (active or latent without prophylaxis)
            - Pregnancy or nursing
            - Hepatitis B or C
            """
        },
        {
            "trial_id": "NCT05456789",
            "title": "Cognitive Therapy for Depression in Elderly",
            "condition": "Depression",
            "criteria": """
            Inclusion Criteria:
            - Age 65 to 85 years
            - Major depressive disorder diagnosis
            - PHQ-9 score >= 15
            - Able to attend weekly sessions
            
            Exclusion Criteria:
            - Active suicidal ideation
            - Bipolar disorder
            - Active substance abuse
            - Severe cognitive impairment (MMSE < 24)
            - Recent hospitalization for psychiatry
            """
        },
        {
            "trial_id": "NCT05567890",
            "title": "Asthma Control Study with Inhaled Corticosteroid",
            "condition": "Asthma",
            "criteria": """
            Inclusion Criteria:
            - Age 6 to 65 years
            - Asthma diagnosis for at least 1 year
            - Poorly controlled asthma (ACQ score >= 1.5)
            
            Exclusion Criteria:
            - Severe asthma exacerbation within 4 weeks
            - Respiratory tract infection within 2 weeks
            - Smoking history > 10 pack-years
            - Pregnancy
            - Use of oral corticosteroids regularly
            """
        },
        {
            "trial_id": "NCT05678901",
            "title": "Prevention of Alzheimer's Disease in Cognitively Normal",
            "condition": "Alzheimer's Disease",
            "criteria": """
            Inclusion Criteria:
            - Age 55 to 80 years
            - Cognitively normal but with family history
            - MMSE score >= 28
            - Willing to undergo PET scan
            
            Exclusion Criteria:
            - Mild cognitive impairment
            - Dementia diagnosis
            - Stroke history
            - Uncontrolled hypertension
            - Contraindication to MRI
            """
        },
        {
            "trial_id": "NCT05789012",
            "title": "New Anticoagulant for Atrial Fibrillation",
            "condition": "Atrial Fibrillation",
            "criteria": """
            Inclusion Criteria:
            - Age 18 to 75 years
            - Atrial fibrillation diagnosis
            - CHA2DS2-VASc score >= 1
            - No prior anticoagulant use
            
            Exclusion Criteria:
            - Severe kidney disease (eGFR < 15)
            - Active bleeding disorder
            - Recent GI bleed within 3 months
            - Pregnancy
            - Thrombocytopenia
            """
        },
        {
            "trial_id": "NCT05890123",
            "title": "Cancer Immunotherapy for Advanced Melanoma",
            "condition": "Melanoma",
            "criteria": """
            Inclusion Criteria:
            - Age 18 to 75 years
            - Stage III or IV melanoma diagnosis
            - Measurable disease per RECIST criteria
            - ECOG performance status 0-1
            
            Exclusion Criteria:
            - Prior immunotherapy treatment
            - Active autoimmune disease
            - Uncontrolled brain metastases
            - Pregnancy
            - Active infection
            """
        },
    ]
    
    print("Adding realistic clinical trials to database...")
    for trial in real_trials:
        eligibility_rules = extract_eligibility(trial['criteria'])
        add_trial(
            trial_id=trial['trial_id'],
            title=trial['title'],
            condition=trial['condition'],
            eligibility_rules=eligibility_rules,
            status='recruiting'
        )
        print(f"✓ {trial['trial_id']}: {trial['title']}")
    
    print(f"\n✓ Successfully added {len(real_trials)} realistic trials to database")

if __name__ == '__main__':
    add_realistic_trials()
