import streamlit as st
import requests
import pandas as pd
from ml_matcher import get_ml_predictions
from db import get_patient, get_trial, get_all_trials, get_all_patients

st.set_page_config(page_title="TrialMatch", layout="wide")

# Professional minimal styling
st.markdown("""
<style>
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.stMetric { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

API_BASE = "http://localhost:8000"

try:
    stats = requests.get(f"{API_BASE}/stats").json()
except:
    st.error("API server not running. Run: python main.py")
    st.stop()

# Header
st.title("🏥 TrialMatch")
st.markdown("**AI-Powered Clinical Trial Eligibility Matching System**")
st.divider()

# Navigation
page = st.selectbox("Select View", ["Dashboard", "Patient Search", "Clinical Trials", "ML Models"])

# ===== DASHBOARD =====
if page == "Dashboard":
    st.header("System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Patients", stats['total_patients'])
    col2.metric("Clinical Trials", stats['total_trials'])
    col3.metric("Matches Found", stats['total_matches'])
    col4.metric("Match Success Rate", f"{stats['percentage_matched']:.1f}%")
    
    st.divider()
    
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    
    col1.metric(
        "Patients with Eligible Trials",
        f"{stats['patients_with_matches']}/{stats['total_patients']}",
        f"{stats['percentage_matched']:.1f}%"
    )
    
    col2.metric(
        "Average Matches per Patient",
        f"{stats['avg_matches_per_patient']:.2f}",
        "trials per patient"
    )
    
    possible = stats['total_patients'] * stats['total_trials']
    match_pct = (stats['total_matches'] / possible * 100) if possible > 0 else 0
    col3.metric(
        "Overall Match Rate",
        f"{match_pct:.2f}%",
        f"of {possible:,} combinations"
    )
    
    st.divider()
    
    st.subheader("System Statistics")
    stats_data = {
        "Metric": [
            "Total Patients",
            "Total Trials", 
            "Possible Combinations",
            "Actual Matches",
            "Match Success Rate",
            "Average Matches/Patient"
        ],
        "Value": [
            stats['total_patients'],
            stats['total_trials'],
            f"{possible:,}",
            stats['total_matches'],
            f"{match_pct:.2f}%",
            f"{stats['avg_matches_per_patient']:.2f}"
        ]
    }
    st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)

# ===== PATIENT SEARCH =====
elif page == "Patient Search":
    st.header("Find Eligible Trials for Patient")
    
    patients = get_all_patients()
    patient_ids = sorted([p['patient_id'] for p in patients])
    
    selected_patient_id = st.selectbox("Select Patient ID", patient_ids)
    
    if selected_patient_id:
        patient = get_patient(selected_patient_id)
        matches_resp = requests.get(f"{API_BASE}/matches/{selected_patient_id}").json()
        
        # Patient Profile
        st.subheader(f"Patient Profile: {selected_patient_id}")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Age", f"{patient['age']} years")
        col2.metric("Medical Conditions", len(patient['conditions']))
        col3.metric("Current Medications", len(patient['medications']))
        
        st.markdown("**Conditions:**")
        st.write(", ".join(patient['conditions']))
        
        st.markdown("**Medications:**")
        st.write(", ".join(patient['medications']))
        
        st.divider()
        
        # Eligible Trials
        st.subheader(f"Eligible Trials ({matches_resp['eligible_trial_count']})")
        
        if matches_resp['eligible_trial_count'] > 0:
            for idx, trial_info in enumerate(matches_resp['eligible_trials'], 1):
                trial = get_trial(trial_info['trial_id'])
                preds = get_ml_predictions(patient, trial)
                
                with st.expander(f"{idx}. {trial_info['trial_id']} - {trial_info['title']}"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Compatibility Score", f"{preds['compatibility_score']}%")
                    col2.metric("Trial Success Probability", f"{preds['trial_success_score']}%")
                    col3.metric("Completion Likelihood", f"{100 - preds['completion_risk']}%")
                    
                    st.markdown(f"**Condition:** {trial_info['condition']}")
                    st.markdown(f"**Status:** {trial_info['reason']}")
        else:
            st.info("No eligible trials found for this patient")

# ===== CLINICAL TRIALS =====
elif page == "Clinical Trials":
    st.header("Clinical Trials Database")
    
    trials = get_all_trials()
    st.metric("Total Trials", len(trials))
    
    if trials:
        trials_df = pd.DataFrame([
            {
                'Trial ID': t['trial_id'],
                'Title': t['title'],
                'Condition': t['condition']
            }
            for t in trials
        ])
        
        st.dataframe(trials_df, use_container_width=True, hide_index=True)
        
        # Download option
        csv = trials_df.to_csv(index=False)
        st.download_button(
            label="Download Trials (CSV)",
            data=csv,
            file_name="clinical_trials.csv",
            mime="text/csv"
        )

# ===== ML MODELS =====
elif page == "ML Models":
    st.header("Machine Learning Models")
    
    st.markdown("""
    ### Model Architecture
    
    TrialMatch uses 3 Random Forest classifiers to optimize trial matching:
    
    **1. Trial Success Predictor**
    - Predicts likelihood of trial success (0-100%)
    - Input Features: Trial restrictiveness, lab requirements, conditions
    - Use Case: Identify trials with highest success rates
    
    **2. Patient Completion Risk Predictor**
    - Predicts patient dropout risk (0-100%)
    - Input Features: Age, comorbidities, medications, pregnancy status
    - Use Case: Identify stable candidates likely to complete trials
    
    **3. Compatibility Scorer**
    - Scores patient-trial compatibility (0-100%)
    - Input Features: Age match, condition overlap, demographic alignment
    - Use Case: Rank trials by compatibility for each patient
    
    ### Training Data
    - **500** synthetic patients with realistic profiles
    - **20** clinical trials with real eligibility criteria
    - **10,000** patient-trial combinations for evaluation
    
    ### Performance Metrics
    - All models trained on Random Forest (n_estimators=10, max_depth=3)
    - Stratified train-test split (80/20)
    - Cross-validation used for hyperparameter tuning
    """)
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Model 1", "Random Forest", "Trained")
    col2.metric("Model 2", "Random Forest", "Trained")
    col3.metric("Model 3", "Random Forest", "Trained")

st.divider()
st.markdown("---")
st.markdown("**TrialMatch v1.0** | Powered by Claude API, FastAPI, and Machine Learning | [GitHub](https://github.com/yourusername/trialmatch)")
