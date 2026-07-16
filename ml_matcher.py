import pickle
import numpy as np
from db import get_all_trials

# Load trained models
try:
    with open('trial_success_model.pkl', 'rb') as f:
        trial_success_model = pickle.load(f)
    with open('completion_model.pkl', 'rb') as f:
        completion_model = pickle.load(f)
    with open('scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    with open('compatibility_model.pkl', 'rb') as f:
        compatibility_model = pickle.load(f)
except FileNotFoundError:
    print("Warning: ML models not found. Run train_ml_models.py first")
    trial_success_model = None
    completion_model = None
    scaler = None
    compatibility_model = None

def predict_trial_success(trial):
    """Predict if trial will have good outcomes (0-100 score)"""
    if trial_success_model is None:
        return 50
    
    rules = trial['eligibility_rules']
    num_restrictions = len(rules.get('excluded_conditions', []))
    has_age_limits = int(rules.get('age_min') is not None or rules.get('age_max') is not None)
    has_lab_reqs = int(len(rules.get('required_lab_values', {})) > 0)
    num_conditions = len(rules.get('conditions', []))
    
    features = np.array([[num_restrictions, has_age_limits, has_lab_reqs, num_conditions]])
    prob = trial_success_model.predict_proba(features)[0][1]
    return int(prob * 100)

def predict_completion_risk(patient):
    """Predict completion risk (0-100, higher = more risk)"""
    if completion_model is None or scaler is None:
        return 30
    
    age = patient['age']
    num_conditions = len(patient['conditions'])
    num_meds = len(patient['medications'])
    pregnancy = int(patient['pregnancy_status'])
    
    features = np.array([[age, num_conditions, num_meds, pregnancy]])
    features_scaled = scaler.transform(features)
    prob = completion_model.predict_proba(features_scaled)[0][1]
    return int(prob * 100)

def predict_compatibility_score(patient, trial):
    """Score patient-trial compatibility (0-100)"""
    if compatibility_model is None:
        return 50
    
    age_match = int(
        (trial['eligibility_rules'].get('age_min') is None or 
         patient['age'] >= trial['eligibility_rules'].get('age_min', 0)) and
        (trial['eligibility_rules'].get('age_max') is None or 
         patient['age'] <= trial['eligibility_rules'].get('age_max', 120))
    )
    
    condition_match = int(any(
        tc.lower() in ' '.join([c.lower() for c in patient['conditions']])
        for tc in trial['eligibility_rules'].get('conditions', [])
    ))
    
    features = np.array([[
        age_match,
        condition_match,
        len(patient['conditions']),
        len(trial['eligibility_rules'].get('conditions', [])),
    ]])
    
    prob = compatibility_model.predict_proba(features)[0][1]
    return int(prob * 100)

def get_ml_predictions(patient, trial):
    """Get all ML predictions for a patient-trial pair"""
    return {
        'trial_success_score': predict_trial_success(trial),
        'completion_risk': predict_completion_risk(patient),
        'compatibility_score': predict_compatibility_score(patient, trial)
    }

if __name__ == '__main__':
    from db import get_patient, get_trial
    
    patient = get_patient('P0000')
    trial = get_trial('NCT04623697')
    
    if patient and trial:
        preds = get_ml_predictions(patient, trial)
        print(f"Patient: {patient['patient_id']}, Trial: {trial['trial_id']}")
        print(f"Trial Success Score: {preds['trial_success_score']}%")
        print(f"Completion Risk: {preds['completion_risk']}%")
        print(f"Compatibility Score: {preds['compatibility_score']}%")
