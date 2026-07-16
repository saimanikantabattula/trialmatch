from db import get_all_patients, get_all_trials
from matcher import match_patients_to_trials
import sqlite3
import json

def save_matches():
    """Run matching engine and save results."""
    
    print("Fetching all patients and trials...")
    patients = get_all_patients()
    trials = get_all_trials()
    
    print(f"Matching {len(patients)} patients against {len(trials)} trials...")
    print("=" * 60)
    
    matches = match_patients_to_trials(patients, trials)
    
    total_matches = 0
    for patient_id, eligible_trials in matches.items():
        if eligible_trials:
            total_matches += len(eligible_trials)
            print(f"\n{patient_id}: {len(eligible_trials)} eligible trial(s)")
            for trial in eligible_trials[:2]:
                print(f"  • {trial['trial_id']}: {trial['trial_title']}")
    
    print("\n" + "=" * 60)
    print(f"RESULTS:")
    print(f"  Total patients: {len(patients)}")
    print(f"  Total trials: {len(trials)}")
    print(f"  Total matches found: {total_matches}")
    print(f"  Average matches per patient: {total_matches / len(patients):.1f}")
    
    # Calculate statistics
    patients_with_matches = sum(1 for p in matches.values() if len(p) > 0)
    print(f"  Patients with at least 1 match: {patients_with_matches}/{len(patients)}")
    
    return matches

if __name__ == '__main__':
    matches = save_matches()
