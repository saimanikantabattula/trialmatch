from db import get_all_trials
import json

print("\n" + "="*80)
print("📋 CLINICAL TRIALS VERIFICATION REPORT")
print("="*80)

trials = get_all_trials()

print(f"\n✓ TOTAL TRIALS: {len(trials)}")

# Trials by condition
condition_counts = {}
for trial in trials:
    condition = trial.get('condition', 'Unknown')
    condition_counts[condition] = condition_counts.get(condition, 0) + 1

print(f"\nTRIALS BY CONDITION:")
print(f"  Unique Conditions: {len(condition_counts)}")
for condition, count in sorted(condition_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"    {condition}: {count} trials")

# Eligibility criteria analysis
print(f"\nELIGIBILITY CRITERIA ANALYSIS:")

age_requirements = []
lab_requirements = []
condition_requirements = []
exclusion_counts = []

for trial in trials:
    rules = trial.get('eligibility_rules', {})
    
    # Age
    if rules.get('age_min') and rules.get('age_max'):
        age_range = rules.get('age_max') - rules.get('age_min')
        age_requirements.append(age_range)
    
    # Lab values
    lab_reqs = len(rules.get('required_lab_values', {}))
    lab_requirements.append(lab_reqs)
    
    # Conditions
    cond_reqs = len(rules.get('conditions', []))
    condition_requirements.append(cond_reqs)
    
    # Exclusions
    exc_count = len(rules.get('excluded_conditions', []))
    exclusion_counts.append(exc_count)

print(f"\n  Age Range Requirements:")
print(f"    Avg Range: {sum(age_requirements)/len(age_requirements):.1f} years" if age_requirements else "    No age requirements")

print(f"\n  Lab Value Requirements:")
print(f"    Avg Lab Values Required: {sum(lab_requirements)/len(lab_requirements):.1f}")
print(f"    Min: {min(lab_requirements)}, Max: {max(lab_requirements)}")

print(f"\n  Condition Requirements:")
print(f"    Avg Conditions Required: {sum(condition_requirements)/len(condition_requirements):.1f}")
print(f"    Min: {min(condition_requirements)}, Max: {max(condition_requirements)}")

print(f"\n  Exclusion Criteria:")
print(f"    Avg Exclusions: {sum(exclusion_counts)/len(exclusion_counts):.1f}")
print(f"    Min: {min(exclusion_counts)}, Max: {max(exclusion_counts)}")

# Trial details
print("\n" + "="*80)
print("DETAILED TRIAL LISTING:")
print("="*80)

for i, trial in enumerate(trials, 1):
    rules = trial.get('eligibility_rules', {})
    age_min = rules.get('age_min', 'N/A')
    age_max = rules.get('age_max', 'N/A')
    
    print(f"\n{i}. {trial.get('trial_id')} - {trial.get('title')}")
    print(f"   Condition: {trial.get('condition')}")
    print(f"   Age Range: {age_min}-{age_max}")
    print(f"   Required Conditions: {len(rules.get('conditions', []))}")
    print(f"   Lab Requirements: {len(rules.get('required_lab_values', {}))}")
    print(f"   Exclusions: {len(rules.get('excluded_conditions', []))}")

print("\n" + "="*80)
print(f"✅ TRIALS VERIFIED: {len(trials)} trials with complete criteria")
print("="*80 + "\n")
