import click
import requests
import pandas as pd
from db import get_patient, get_trial, get_all_trials, get_all_patients
from ml_matcher import get_ml_predictions

API_BASE = "http://localhost:8000"

@click.group()
def cli():
    """TrialMatch CLI - AI-Powered Clinical Trial Eligibility Matching"""
    pass

@cli.command()
def stats():
    """Show system statistics"""
    try:
        stats_data = requests.get(f"{API_BASE}/stats").json()
        
        click.echo("\n" + "="*70)
        click.echo("📊 TRIALMATCH SYSTEM STATISTICS")
        click.echo("="*70)
        click.echo(f"Total Patients:              {stats_data['total_patients']}")
        click.echo(f"Total Trials:                {stats_data['total_trials']}")
        click.echo(f"Total Matches Found:         {stats_data['total_matches']}")
        click.echo(f"Patients with Matches:       {stats_data['patients_with_matches']}")
        click.echo(f"Match Success Rate:          {stats_data['percentage_matched']:.1f}%")
        click.echo(f"Avg Matches per Patient:     {stats_data['avg_matches_per_patient']:.2f}")
        click.echo("="*70 + "\n")
    except Exception as e:
        click.echo(f"❌ Error: {e}")

@cli.command()
@click.option('--patient-id', default=None, help='Patient ID (e.g., P0000)')
def patient(patient_id):
    """Search eligible trials for a patient"""
    try:
        if not patient_id:
            patient_id = click.prompt('Enter Patient ID')
        
        patient_data = get_patient(patient_id)
        if not patient_data:
            click.echo(f"❌ Patient {patient_id} not found")
            return
        
        matches_resp = requests.get(f"{API_BASE}/matches/{patient_id}").json()
        
        click.echo("\n" + "="*90)
        click.echo(f"👤 PATIENT PROFILE: {patient_id}")
        click.echo("="*90)
        click.echo(f"Age:                 {patient_data['age']} years")
        click.echo(f"Conditions:          {', '.join(patient_data['conditions'])}")
        click.echo(f"Medications:         {', '.join(patient_data['medications'])}")
        click.echo(f"Pregnancy Status:    {'Yes' if patient_data['pregnancy_status'] else 'No'}")
        click.echo("="*90 + "\n")
        
        if matches_resp['eligible_trial_count'] > 0:
            click.echo(f"✓ Found {matches_resp['eligible_trial_count']} eligible trial(s)\n")
            
            for idx, trial_info in enumerate(matches_resp['eligible_trials'], 1):
                trial = get_trial(trial_info['trial_id'])
                preds = get_ml_predictions(patient_data, trial)
                
                click.echo(f"{idx}. {trial_info['trial_id']} - {trial_info['title']}")
                click.echo(f"   Condition:             {trial_info['condition']}")
                click.echo(f"   Compatibility Score:   {preds['compatibility_score']}%")
                click.echo(f"   Trial Success Prob:    {preds['trial_success_score']}%")
                click.echo(f"   Completion Likelihood: {100 - preds['completion_risk']}%")
                click.echo()
        else:
            click.echo("⚠️  No eligible trials found for this patient\n")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")

@cli.command()
def trials():
    """List all clinical trials"""
    try:
        trials_data = get_all_trials()
        
        click.echo("\n" + "="*120)
        click.echo("📋 CLINICAL TRIALS DATABASE")
        click.echo("="*120)
        click.echo(f"{'Trial ID':<20} {'Title':<65} {'Condition':<35}")
        click.echo("-"*120)
        
        for trial in trials_data:
            title = trial.get('title', 'N/A')[:60] + "..." if len(str(trial.get('title', 'N/A'))) > 60 else trial.get('title', 'N/A')
            condition = trial.get('condition', 'N/A')
            click.echo(f"{trial.get('trial_id', 'N/A'):<20} {title:<65} {condition:<35}")
        
        click.echo("="*120 + f"\nTotal: {len(trials_data)} trials\n")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")

@cli.command()
def patients_list():
    """List all patients"""
    try:
        patients_data = get_all_patients()
        
        click.echo("\n" + "="*110)
        click.echo("👥 PATIENTS DATABASE")
        click.echo("="*110)
        click.echo(f"{'Patient ID':<15} {'Age':<8} {'Conditions':<40} {'Medications':<40}")
        click.echo("-"*110)
        
        for patient in patients_data[:100]:
            conditions = ', '.join(patient['conditions'][:2]) 
            if len(patient['conditions']) > 2:
                conditions += f" (+{len(patient['conditions'])-2})"
            
            medications = ', '.join(patient['medications'][:2])
            if len(patient['medications']) > 2:
                medications += f" (+{len(patient['medications'])-2})"
            
            click.echo(f"{patient['patient_id']:<15} {patient['age']:<8} {conditions:<40} {medications:<40}")
        
        click.echo("="*110 + f"\nTotal: {len(patients_data)} patients (showing first 100)\n")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")

@cli.command()
def models():
    """Show ML models information"""
    click.echo("\n" + "="*80)
    click.echo("🤖 MACHINE LEARNING MODELS")
    click.echo("="*80)
    
    click.echo("\n1. TRIAL SUCCESS PREDICTOR")
    click.echo("   Algorithm:      Gradient Boosting Classifier")
    click.echo("   Estimators:     50")
    click.echo("   Features:       Trial restrictiveness, lab requirements, conditions")
    click.echo("   Output:         0-100% success probability")
    
    click.echo("\n2. PATIENT COMPLETION RISK PREDICTOR")
    click.echo("   Algorithm:      Gradient Boosting Classifier + StandardScaler")
    click.echo("   Estimators:     50")
    click.echo("   Features:       Age, conditions, medications, pregnancy, lab values")
    click.echo("   Output:         0-100% completion risk")
    
    click.echo("\n3. COMPATIBILITY SCORER")
    click.echo("   Algorithm:      Gradient Boosting Classifier")
    click.echo("   Estimators:     50")
    click.echo("   Features:       Age match, condition overlap, lab values")
    click.echo("   Output:         0-100% compatibility score")
    
    click.echo("\nTRAINING DATA")
    click.echo("   Patients:       2000 synthetic profiles (realistic)")
    click.echo("   Trials:         41 clinical trials")
    click.echo("   Combinations:   82,000+ patient-trial pairs")
    
    click.echo("\nMODEL PERFORMANCE")
    click.echo("   Stratified train-test split (80/20)")
    click.echo("   Cross-validation for hyperparameter tuning")
    click.echo("   Metrics: Precision, Recall, F1-Score, ROC-AUC")
    
    click.echo("\n" + "="*80 + "\n")

@cli.command()
def help_guide():
    """Show usage guide"""
    click.echo("""
╔════════════════════════════════════════════════════════════════════════╗
║           TrialMatch CLI - Usage Guide                                ║
╚════════════════════════════════════════════════════════════════════════╝

COMMANDS:

  python cli.py stats
    → Show system statistics

  python cli.py patient [--patient-id P0000]
    → Search eligible trials for a patient

  python cli.py trials
    → List all clinical trials

  python cli.py patients-list
    → List all patients

  python cli.py models
    → Show ML model details

  python cli.py help-guide
    → Show this help guide

EXAMPLES:

  $ python cli.py stats
  $ python cli.py patient --patient-id P00123
  $ python cli.py trials
  $ python cli.py patients-list

═════════════════════════════════════════════════════════════════════════
    """)

if __name__ == '__main__':
    cli()
