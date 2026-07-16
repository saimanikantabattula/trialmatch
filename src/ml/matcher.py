from typing import Dict, List, Tuple

def check_eligibility(patient: Dict, trial_rules: Dict) -> Tuple[bool, str]:
    """
    Check if patient meets trial eligibility criteria.
    Returns (is_eligible, reason)
    """
    
    if trial_rules.get('age_min') is not None:
        if patient['age'] < trial_rules['age_min']:
            return False, f"Age {patient['age']} below minimum {trial_rules['age_min']}"
    
    if trial_rules.get('age_max') is not None:
        if patient['age'] > trial_rules['age_max']:
            return False, f"Age {patient['age']} above maximum {trial_rules['age_max']}"
    
    required_conditions = trial_rules.get('conditions', [])
    patient_conditions = [c.lower() for c in patient['conditions']]
    
    if required_conditions:
        has_condition = any(
            any(req.lower() in pc for req in required_conditions)
            for pc in patient_conditions
        )
        if not has_condition:
            return False, f"Missing required condition. Trial requires: {required_conditions}"
    
    excluded = trial_rules.get('excluded_conditions', [])
    for exc in excluded:
        if any(exc.lower() in pc for pc in patient_conditions):
            return False, f"Has excluded condition: {exc}"
    
    req_labs = trial_rules.get('required_lab_values', {})
    for lab_name, limits in req_labs.items():
        if lab_name not in patient['lab_values']:
            continue
        
        patient_value = patient['lab_values'][lab_name]
        
        if 'min' in limits and limits['min'] is not None and patient_value < limits['min']:
            return False, f"{lab_name} {patient_value} below minimum {limits['min']}"
        
        if 'max' in limits and limits['max'] is not None and patient_value > limits['max']:
            return False, f"{lab_name} {patient_value} above maximum {limits['max']}"
    
    if trial_rules.get('exclude_pregnant', False) and patient.get('pregnancy_status', False):
        return False, "Pregnant patients excluded"
    
    return True, "Eligible: meets all criteria"


def match_patients_to_trials(patients: List[Dict], trials: List[Dict]) -> Dict:
    """
    For each patient, find eligible trials.
    Returns dict: patient_id -> list of eligible trials
    """
    
    results = {}
    
    for patient in patients:
        eligible_trials = []
        
        for trial in trials:
            is_eligible, reason = check_eligibility(patient, trial['eligibility_rules'])
            
            if is_eligible:
                eligible_trials.append({
                    'trial_id': trial['trial_id'],
                    'trial_title': trial['title'],
                    'reason': reason
                })
        
        results[patient['patient_id']] = eligible_trials
    
    return results


if __name__ == '__main__':
    test_patient = {
        'patient_id': 'P0001',
        'age': 45,
        'conditions': ['type 2 diabetes', 'hypertension'],
        'lab_values': {'HbA1c': 8.2, 'eGFR': 75},
        'medications': ['metformin', 'lisinopril'],
        'pregnancy_status': False
    }
    
    test_trial_rules = {
        'age_min': 18,
        'age_max': 75,
        'conditions': ['diabetes'],
        'excluded_conditions': [],
        'required_lab_values': {'HbA1c': {'min': 7.5, 'max': 11}},
        'exclude_pregnant': False
    }
    
    is_eligible, reason = check_eligibility(test_patient, test_trial_rules)
    print(f"Patient P0001 eligible: {is_eligible}")
    print(f"Reason: {reason}")
