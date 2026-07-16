import random
from db import add_patient, add_trial
from eligibility_extractor import extract_eligibility

def generate_synthetic_patients(n=50):
    """Generate n realistic patient profiles and add to database."""
    
    conditions_list = [
        "type 2 diabetes", "hypertension", "heart disease",
        "cancer", "asthma", "COPD", "arthritis", "depression"
    ]
    medications_list = [
        "metformin", "lisinopril", "atorvastatin", "aspirin",
        "insulin", "omeprazole", "sertraline", "levothyroxine"
    ]
    
    for i in range(n):
        patient_id = f"P{i:04d}"
        age = random.randint(18, 85)
        conditions = random.sample(conditions_list, k=random.randint(1, 3))
        lab_values = {
            "HbA1c": round(random.uniform(5.0, 10.0), 1),
            "eGFR": random.randint(20, 120),
            "glucose": random.randint(80, 300),
            "creatinine": round(random.uniform(0.6, 2.5), 2)
        }
        medications = random.sample(medications_list, k=random.randint(1, 4))
        pregnancy_status = random.choice([True, False]) if age < 50 else False
        
        add_patient(
            patient_id=patient_id,
            age=age,
            conditions=conditions,
            lab_values=lab_values,
            medications=medications,
            pregnancy_status=pregnancy_status
        )
    
    print(f"✓ Generated {n} synthetic patients")


def generate_sample_trials():
    """Generate sample trials and add to database."""
    
    sample_trials = [
        {
            "trial_id": "NCT04000001",
            "title": "Type 2 Diabetes Management Study",
            "condition": "Type 2 Diabetes",
            "criteria": """
            Inclusion Criteria:
            - Age 18 to 75 years
            - Confirmed type 2 diabetes diagnosis
            - HbA1c between 7.5% and 11%
            
            Exclusion Criteria:
            - Severe kidney disease (eGFR < 30)
            - Pregnant or nursing women
            - Type 1 diabetes
            """
        },
        {
            "trial_id": "NCT04000002",
            "title": "Hypertension Treatment Trial",
            "condition": "Hypertension",
            "criteria": """
            Inclusion Criteria:
            - Age 21 to 80 years
            - Diagnosed with hypertension
            
            Exclusion Criteria:
            - Severe heart disease
            - Recent stroke within 6 months
            """
        },
        {
            "trial_id": "NCT04000003",
            "title": "Heart Disease Prevention Study",
            "condition": "Heart Disease",
            "criteria": """
            Inclusion Criteria:
            - Age 40 to 75 years
            - History of heart disease or major risk factors
            
            Exclusion Criteria:
            - Unstable angina
            - Recent heart attack within 3 months
            - Pregnancy
            """
        },
        {
            "trial_id": "NCT04000004",
            "title": "Arthritis Management Study",
            "condition": "Arthritis",
            "criteria": """
            Inclusion Criteria:
            - Age 18 to 85 years
            - Confirmed arthritis diagnosis
            
            Exclusion Criteria:
            - Severe kidney disease (eGFR < 30)
            - Recent surgery within 3 months
            """
        },
        {
            "trial_id": "NCT04000005",
            "title": "COPD Treatment Trial",
            "condition": "COPD",
            "criteria": """
            Inclusion Criteria:
            - Age 40 to 80 years
            - Diagnosed with COPD
            
            Exclusion Criteria:
            - Active cancer
            - Recent hospitalization within 2 weeks
            - Pregnant women
            """
        }
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
    
    print(f"✓ Generated {len(sample_trials)} sample trials")


if __name__ == '__main__':
    print("Generating synthetic data...")
    generate_sample_trials()
    generate_synthetic_patients(50)
    print("✓ All synthetic data generated")
