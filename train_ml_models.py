import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from db import get_all_patients, get_all_trials

print("Training ML Models...")

# ===== MODEL 1: Trial Success Prediction =====
print("\n1. Training Trial Success Predictor...")

# Create synthetic trial features
trials = get_all_trials()
trial_features = []
trial_success_labels = []

for trial in trials:
    rules = trial['eligibility_rules']
    
    # Features: how restrictive is the trial
    num_restrictions = len(rules.get('excluded_conditions', []))
    has_age_limits = rules.get('age_min') is not None or rules.get('age_max') is not None
    has_lab_reqs = len(rules.get('required_lab_values', {})) > 0
    num_conditions = len(rules.get('conditions', []))
    
    features = [
        num_restrictions,
        int(has_age_limits),
        int(has_lab_reqs),
        num_conditions,
    ]
    
    trial_features.append(features)
    # Synthetic: more restrictive trials tend to have better success rates
    success = int(num_restrictions > 1 and has_lab_reqs)
    trial_success_labels.append(success)

if len(trial_features) > 2:
    X_trial = np.array(trial_features)
    y_trial = np.array(trial_success_labels)
    
    trial_success_model = RandomForestClassifier(n_estimators=10, random_state=42, max_depth=3)
    trial_success_model.fit(X_trial, y_trial)
    
    with open('trial_success_model.pkl', 'wb') as f:
        pickle.dump(trial_success_model, f)
    print("   ✓ Trial Success Model trained")

# ===== MODEL 2: Patient Completion Risk =====
print("\n2. Training Patient Completion Risk Predictor...")

patients = get_all_patients()
patient_features = []
completion_labels = []

for patient in patients:
    age = patient['age']
    num_conditions = len(patient['conditions'])
    num_meds = len(patient['medications'])
    
    features = [
        age,
        num_conditions,
        num_meds,
        int(patient['pregnancy_status']),
    ]
    
    patient_features.append(features)
    # Synthetic: younger, healthier patients more likely to complete
    completion_risk = int(age > 60 or num_conditions > 3)
    completion_labels.append(completion_risk)

if len(patient_features) > 2:
    X_patient = np.array(patient_features)
    y_patient = np.array(completion_labels)
    
    scaler = StandardScaler()
    X_patient_scaled = scaler.fit_transform(X_patient)
    
    completion_model = RandomForestClassifier(n_estimators=10, random_state=42, max_depth=3)
    completion_model.fit(X_patient_scaled, y_patient)
    
    with open('completion_model.pkl', 'wb') as f:
        pickle.dump(completion_model, f)
    with open('scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    print("   ✓ Completion Risk Model trained")

# ===== MODEL 3: Compatibility Scorer =====
print("\n3. Training Compatibility Scorer...")

# Create training data for compatibility
compatibility_features = []
compatibility_labels = []

for patient in patients[:min(10, len(patients))]:
    for trial in trials[:min(10, len(trials))]:
        # Features: patient-trial compatibility
        age_match = int(
            (trial['eligibility_rules'].get('age_min') is None or 
             patient['age'] >= trial['eligibility_rules'].get('age_min', 0)) and
            (trial['eligibility_rules'].get('age_max') is None or 
             patient['age'] <= trial['eligibility_rules'].get('age_max', 120))
        )
        
        condition_match = any(
            tc.lower() in ' '.join([c.lower() for c in patient['conditions']])
            for tc in trial['eligibility_rules'].get('conditions', [])
        )
        
        features = [
            age_match,
            int(condition_match),
            len(patient['conditions']),
            len(trial['eligibility_rules'].get('conditions', [])),
        ]
        
        compatibility_features.append(features)
        label = int(age_match and condition_match)
        compatibility_labels.append(label)

if len(compatibility_features) > 2:
    X_compat = np.array(compatibility_features)
    y_compat = np.array(compatibility_labels)
    
    compat_model = RandomForestClassifier(n_estimators=10, random_state=42, max_depth=3)
    compat_model.fit(X_compat, y_compat)
    
    with open('compatibility_model.pkl', 'wb') as f:
        pickle.dump(compat_model, f)
    print("   ✓ Compatibility Model trained")

print("\n" + "="*50)
print("✓ All ML models trained and saved!")
print("  - trial_success_model.pkl")
print("  - completion_model.pkl")
print("  - compatibility_model.pkl")
print("  - scaler.pkl")
print("="*50)
