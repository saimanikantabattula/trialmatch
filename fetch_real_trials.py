import requests
import json
from db import add_trial
from eligibility_extractor import extract_eligibility

def fetch_real_trials(condition="diabetes", num_trials=20):
    """
    Fetch real clinical trials from ClinicalTrials.gov API.
    No authentication needed - it's a free public API.
    """
    
    url = "https://clinicaltrials.gov/api/query/full_studies"
    
    params = {
        "expr": condition,
        "fmt": "json",
        "pageSize": num_trials
    }
    
    print(f"Fetching {num_trials} real trials for '{condition}' from ClinicalTrials.gov...")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        trials = data.get('FullStudiesResponse', {}).get('NStudiesReturned', 0)
        
        if trials == 0:
            print("No trials found")
            return 0
        
        studies = data['FullStudiesResponse']['AllPublicMasterStudies']
        
        added_count = 0
        for study in studies[:num_trials]:
            try:
                protocol_section = study['ProtocolSection']
                
                # Extract basic info
                trial_id = protocol_section['IdentificationModule']['NCTId']
                title = protocol_section['IdentificationModule']['OfficialTitle']
                
                # Get condition
                condition_list = protocol_section.get('ConditionsModule', {}).get('ConditionList', {}).get('Condition', [])
                condition_name = condition_list[0] if condition_list else "Unknown"
                
                # Get eligibility criteria
                eligibility_module = protocol_section.get('EligibilityModule', {})
                criteria_text = eligibility_module.get('EligibilityCriteria', '')
                
                # Get status
                status_module = protocol_section.get('StatusModule', {})
                recruitment_status = status_module.get('RecruitmentStatus', 'Unknown')
                
                if criteria_text:
                    # Extract structured eligibility rules using Claude
                    eligibility_rules = extract_eligibility(criteria_text)
                    
                    # Add to database
                    add_trial(
                        trial_id=trial_id,
                        title=title[:200],  # Truncate long titles
                        condition=condition_name[:100],
                        eligibility_rules=eligibility_rules,
                        status=recruitment_status
                    )
                    added_count += 1
                    print(f"  ✓ {trial_id}: {title[:60]}...")
                    
            except KeyError as e:
                continue
        
        print(f"\n✓ Successfully added {added_count} real trials to database")
        return added_count
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching trials: {e}")
        return 0

if __name__ == '__main__':
    # Fetch real trials for different conditions
    print("=" * 60)
    fetch_real_trials(condition="diabetes", num_trials=10)
    print("\n" + "=" * 60)
    fetch_real_trials(condition="hypertension", num_trials=10)
    print("\n" + "=" * 60)
    print("Real trials fetched and added to database!")
