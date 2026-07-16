import json
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()

EXTRACTION_PROMPT = """Parse these clinical trial eligibility criteria and extract structured rules.

Return ONLY valid JSON (no markdown, no code blocks) with:
- age_min: minimum age or null
- age_max: maximum age or null  
- conditions: list of required disease/conditions
- excluded_conditions: list of conditions that disqualify
- required_lab_values: dict like {{"test_name": {{"min": value, "max": value}}}}
- exclude_pregnant: true if pregnant patients excluded
- other_restrictions: list of other text restrictions

Eligibility criteria:
{criteria}

Return valid JSON only."""

def extract_eligibility(criteria_text):
    """Use Claude to parse eligibility criteria into structured format."""
    
    if not criteria_text or len(criteria_text.strip()) < 10:
        return {
            'age_min': None,
            'age_max': None,
            'conditions': [],
            'excluded_conditions': [],
            'required_lab_values': {},
            'exclude_pregnant': False,
            'other_restrictions': []
        }
    
    message = client.messages.create(
        model="claude-opus-4-1-20250805",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": EXTRACTION_PROMPT.format(criteria=criteria_text)
        }]
    )
    
    response_text = message.content[0].text
    response_text = response_text.replace('```json', '').replace('```', '').strip()
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        print(f"Failed to parse: {response_text}")
        return {
            'age_min': None,
            'age_max': None,
            'conditions': [],
            'excluded_conditions': [],
            'required_lab_values': {},
            'exclude_pregnant': False,
            'other_restrictions': []
        }

if __name__ == '__main__':
    test_criteria = """
    Inclusion Criteria:
    - Age 18 to 75 years
    - Diagnosed with type 2 diabetes
    - HbA1c between 7.5% and 11%
    
    Exclusion Criteria:
    - Severe kidney disease (eGFR < 30)
    - Pregnant or nursing
    - Recent hospitalization within 30 days
    """
    
    print("Testing eligibility extraction with Claude...")
    result = extract_eligibility(test_criteria)
    print(json.dumps(result, indent=2))
