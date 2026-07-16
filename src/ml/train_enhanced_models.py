import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import json
from db import get_all_patients, get_all_trials

print("🤖 Training Enhanced ML Models...\n")

patients = get_all_patients()
trials = get_all_trials()

print(f"Dataset: {len(patients)} patients, {len(trials)} trials\n")

# ===== MODEL 1: Trial Success Prediction =====
print("="*70)
print("MODEL 1: Trial Success Predictor (Gradient Boosting)")
print("="*70)

trial_features = []
trial_labels = []

for trial in trials:
    rules = trial['eligibility_rules']
    
    # Feature engineering
    num_restrictions = len(rules.get('excluded_conditions', []))
    has_age_limits = int(rules.get('age_min') is not None or rules.get('age_max') is not None)
    has_lab_reqs = int(len(rules.get('required_lab_values', {})) > 0)
    num_conditions = len(rules.get('conditions', []))
    age_range = 0
    if rules.get('age_min') and rules.get('age_max'):
        age_range = rules.get('age_max') - rules.get('age_min')
    
    features = [
        num_restrictions,
        has_age_limits,
        has_lab_reqs,
        num_conditions,
        age_range
    ]
    
    trial_features.append(features)
    # Label: restrictive trials often have better success
    label = int(num_restrictions > 1 and has_lab_reqs and num_conditions > 0)
    trial_labels.append(label)

X_trial = np.array(trial_features)
y_trial = np.array(trial_labels)

if len(X_trial) > 5:
    X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(
        X_trial, y_trial, test_size=0.2, random_state=42
    )
    
    trial_model = GradientBoostingClassifier(n_estimators=50, max_depth=4, learning_rate=0.1, random_state=42)
    trial_model.fit(X_train_t, y_train_t)
    
    y_pred_t = trial_model.predict(X_test_t)
    y_pred_proba_t = trial_model.predict_proba(X_test_t)[:, 1]
    
    print(f"Samples: {len(X_trial)} trials")
    print(f"Features: {X_trial.shape[1]}")
    print(f"\nPerformance Metrics:")
    print(f"  Precision:  {precision_score(y_test_t, y_pred_t, zero_division=0):.3f}")
    print(f"  Recall:     {recall_score(y_test_t, y_pred_t, zero_division=0):.3f}")
    print(f"  F1-Score:   {f1_score(y_test_t, y_pred_t, zero_division=0):.3f}")
    if len(np.unique(y_test_t)) > 1:
        print(f"  ROC-AUC:    {roc_auc_score(y_test_t, y_pred_proba_t):.3f}")
    
    with open('trial_success_model.pkl', 'wb') as f:
        pickle.dump(trial_model, f)
    print("\n✓ Model saved: trial_success_model.pkl\n")

# ===== MODEL 2: Patient Completion Risk =====
print("="*70)
print("MODEL 2: Patient Completion Risk Predictor (Gradient Boosting)")
print("="*70)

patient_features = []
completion_labels = []

for patient in patients:
    age = patient['age']
    num_conditions = len(patient['conditions'])
    num_meds = len(patient['medications'])
    pregnancy = int(patient['pregnancy_status'])
    
    # Additional features
    lab_vals = patient.get('lab_values', {})
    has_severe_conditions = int(any(c in ['kidney disease', 'heart disease', 'cancer'] for c in patient['conditions']))
    
    features = [
        age,
        num_conditions,
        num_meds,
        pregnancy,
        has_severe_conditions,
        lab_vals.get('eGFR', 90) < 30
    ]
    
    patient_features.append(features)
    # Label: older, more meds, severe conditions = higher dropout risk
    risk = int(age > 65 or num_conditions > 3 or num_meds > 5)
    completion_labels.append(risk)

X_patient = np.array(patient_features)
y_patient = np.array(completion_labels)

if len(X_patient) > 5:
    scaler = StandardScaler()
    X_patient_scaled = scaler.fit_transform(X_patient)
    
    X_train_p, X_test_p, y_train_p, y_test_p = train_test_split(
        X_patient_scaled, y_patient, test_size=0.2, random_state=42
    )
    
    completion_model = GradientBoostingClassifier(n_estimators=50, max_depth=4, learning_rate=0.1, random_state=42)
    completion_model.fit(X_train_p, y_train_p)
    
    y_pred_p = completion_model.predict(X_test_p)
    y_pred_proba_p = completion_model.predict_proba(X_test_p)[:, 1]
    
    print(f"Samples: {len(X_patient)} patients")
    print(f"Features: {X_patient.shape[1]}")
    print(f"\nPerformance Metrics:")
    print(f"  Precision:  {precision_score(y_test_p, y_pred_p, zero_division=0):.3f}")
    print(f"  Recall:     {recall_score(y_test_p, y_pred_p, zero_division=0):.3f}")
    print(f"  F1-Score:   {f1_score(y_test_p, y_pred_p, zero_division=0):.3f}")
    if len(np.unique(y_test_p)) > 1:
        print(f"  ROC-AUC:    {roc_auc_score(y_test_p, y_pred_proba_p):.3f}")
    
    with open('completion_model.pkl', 'wb') as f:
        pickle.dump(completion_model, f)
    with open('scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    print("\n✓ Model saved: completion_model.pkl\n")

# ===== MODEL 3: Compatibility Scorer =====
print("="*70)
print("MODEL 3: Compatibility Scorer (Gradient Boosting)")
print("="*70)

compatibility_features = []
compatibility_labels = []

# Create training data from patient-trial pairs
for patient in patients[:500]:  # Use subset for faster training
    for trial in trials:
        # Age compatibility
        age_min = trial['eligibility_rules'].get('age_min', 0)
        age_max = trial['eligibility_rules'].get('age_max', 120)
        age_match = int(age_min <= patient['age'] <= age_max)
        
        # Condition compatibility
        patient_conds = [c.lower() for c in patient['conditions']]
        trial_conds = [c.lower() for c in trial['eligibility_rules'].get('conditions', [])]
        condition_match = int(any(tc in patient_conds for tc in trial_conds))
        
        # Lab value compatibility
        lab_match = 1
        lab_reqs = trial['eligibility_rules'].get('required_lab_values', {})
        patient_labs = patient.get('lab_values', {})
        
        for lab_name, req_range in lab_reqs.items():
            patient_val = patient_labs.get(lab_name, 0)
            if req_range.get('min') and patient_val < req_range['min']:
                lab_match = 0
            if req_range.get('max') and patient_val > req_range['max']:
                lab_match = 0
        
        features = [
            age_match,
            condition_match,
            lab_match,
            len(patient['conditions']),
            len(trial['eligibility_rules'].get('conditions', [])),
            abs(patient['age'] - np.mean([age_min, age_max])) / 50 if age_min else 0
        ]
        
        compatibility_features.append(features)
        label = int(age_match and condition_match and lab_match)
        compatibility_labels.append(label)

X_compat = np.array(compatibility_features)
y_compat = np.array(compatibility_labels)

if len(X_compat) > 5:
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
        X_compat, y_compat, test_size=0.2, random_state=42
    )
    
    compat_model = GradientBoostingClassifier(n_estimators=50, max_depth=4, learning_rate=0.1, random_state=42)
    compat_model.fit(X_train_c, y_train_c)
    
    y_pred_c = compat_model.predict(X_test_c)
    y_pred_proba_c = compat_model.predict_proba(X_test_c)[:, 1]
    
    print(f"Samples: {len(X_compat)} patient-trial pairs")
    print(f"Features: {X_compat.shape[1]}")
    print(f"\nPerformance Metrics:")
    print(f"  Precision:  {precision_score(y_test_c, y_pred_c, zero_division=0):.3f}")
    print(f"  Recall:     {recall_score(y_test_c, y_pred_c, zero_division=0):.3f}")
    print(f"  F1-Score:   {f1_score(y_test_c, y_pred_c, zero_division=0):.3f}")
    if len(np.unique(y_test_c)) > 1:
        print(f"  ROC-AUC:    {roc_auc_score(y_test_c, y_pred_proba_c):.3f}")
    
    with open('compatibility_model.pkl', 'wb') as f:
        pickle.dump(compat_model, f)
    print("\n✓ Model saved: compatibility_model.pkl\n")

# Save model performance report
report = {
    "training_date": str(pd.Timestamp.now()),
    "dataset": {
        "patients": len(patients),
        "trials": len(trials),
        "patient_trial_combinations": len(patients) * len(trials)
    },
    "models": {
        "trial_success": "GradientBoostingClassifier (50 estimators, max_depth=4)",
        "completion_risk": "GradientBoostingClassifier (50 estimators, max_depth=4) + StandardScaler",
        "compatibility": "GradientBoostingClassifier (50 estimators, max_depth=4)"
    }
}

with open('model_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("="*70)
print("✅ ALL MODELS TRAINED & ENHANCED!")
print("="*70)
print("\nModels saved:")
print("  ✓ trial_success_model.pkl")
print("  ✓ completion_model.pkl")
print("  ✓ compatibility_model.pkl")
print("  ✓ scaler.pkl")
print("  ✓ model_report.json")
print("\nPerformance metrics included for each model")
print("="*70 + "\n")
