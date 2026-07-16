from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db import get_all_patients, get_all_trials, get_patient, get_trial
from matcher import match_patients_to_trials
import json

app = FastAPI(title="TrialMatch API")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MatchRequest(BaseModel):
    patient_id: str

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "TrialMatch API - Clinical Trial Eligibility Matching",
        "endpoints": [
            "/docs - Interactive API docs",
            "/matches/{patient_id} - Get trials for a patient",
            "/stats - Overall statistics",
            "/patients - All patients",
            "/trials - All trials"
        ]
    }

@app.get("/stats")
async def get_stats():
    """Get overall matching statistics."""
    patients = get_all_patients()
    trials = get_all_trials()
    matches = match_patients_to_trials(patients, trials)
    
    total_matches = sum(len(m) for m in matches.values())
    patients_with_matches = sum(1 for p in matches.values() if len(p) > 0)
    
    return {
        "total_patients": len(patients),
        "total_trials": len(trials),
        "total_matches": total_matches,
        "avg_matches_per_patient": round(total_matches / len(patients), 2),
        "patients_with_matches": patients_with_matches,
        "percentage_matched": round((patients_with_matches / len(patients)) * 100, 1)
    }

@app.get("/matches/{patient_id}")
async def get_patient_matches(patient_id: str):
    """Get eligible trials for a specific patient."""
    
    patient = get_patient(patient_id)
    if not patient:
        return {"error": f"Patient {patient_id} not found"}
    
    trials = get_all_trials()
    
    from matcher import check_eligibility
    
    eligible_trials = []
    for trial in trials:
        is_eligible, reason = check_eligibility(patient, trial['eligibility_rules'])
        if is_eligible:
            eligible_trials.append({
                'trial_id': trial['trial_id'],
                'title': trial['title'],
                'condition': trial['condition'],
                'reason': reason
            })
    
    return {
        "patient_id": patient_id,
        "age": patient['age'],
        "conditions": patient['conditions'],
        "eligible_trial_count": len(eligible_trials),
        "eligible_trials": eligible_trials
    }

@app.get("/patients")
async def list_patients():
    """Get all patients."""
    patients = get_all_patients()
    return {
        "total": len(patients),
        "patients": [
            {
                "patient_id": p['patient_id'],
                "age": p['age'],
                "conditions": p['conditions']
            }
            for p in patients[:20]  # Return first 20
        ]
    }

@app.get("/trials")
async def list_trials():
    """Get all trials."""
    trials = get_all_trials()
    return {
        "total": len(trials),
        "trials": [
            {
                "trial_id": t['trial_id'],
                "title": t['title'],
                "condition": t['condition']
            }
            for t in trials
        ]
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
