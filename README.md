# TrialMatch: AI-Powered Clinical Trial Eligibility Matching

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

TrialMatch is an enterprise-grade machine learning system that automatically matches patients to eligible clinical trials using artificial intelligence. The system addresses a critical gap in clinical research: 90% of clinical trials fail to recruit sufficient participants, while patients struggle to identify trials for which they are eligible.

## Problem Statement

Clinical trial recruitment remains a significant challenge in medical research. Patients who could benefit from experimental treatments lack efficient mechanisms to discover eligible trials, while trial administrators face substantial costs in patient recruitment. Complex eligibility criteria, often specified in unstructured text, make manual matching error-prone and time-consuming.

## Solution Architecture

TrialMatch solves this problem through an integrated system combining natural language processing, machine learning, and database technology:

1. Claude API processes unstructured trial eligibility criteria into structured rules
2. Three Gradient Boosting classifiers evaluate patient-trial compatibility
3. FastAPI backend provides scalable REST endpoints
4. Command-line interface enables interactive queries

## System Statistics

| Metric | Value |
|--------|-------|
| Total Patients | 2000 |
| Total Clinical Trials | 41 |
| Patient-Trial Matches | 731 |
| Match Success Rate | 32.8% |
| Combinations Evaluated | 82,000+ |

## Machine Learning Models

### Model 1: Trial Success Predictor
- Algorithm: Gradient Boosting Classifier (50 estimators)
- Accuracy: 100.0%
- ROC-AUC: 1.0
- Purpose: Predict likelihood of trial success based on structural characteristics
- Features: Trial restrictiveness, lab requirements, condition count, age range

### Model 2: Patient Completion Risk Predictor
- Algorithm: Gradient Boosting Classifier with StandardScaler (50 estimators)
- Accuracy: 100.0%
- ROC-AUC: 1.0
- Purpose: Assess probability of patient trial completion
- Features: Patient age, condition count, medication count, pregnancy status, severe conditions, severe kidney disease

### Model 3: Compatibility Scorer
- Algorithm: Gradient Boosting Classifier (50 estimators)
- Accuracy: 100.0%
- ROC-AUC: 1.0
- Purpose: Score patient-trial compatibility on 0-100 scale
- Features: Age match, condition overlap, lab value compatibility, feature count differential, age distance from trial requirement

## Installation

### Prerequisites
- Python 3.9 or higher
- Anthropic API key
- 2GB available disk space

### Setup Instructions

```bash
# Clone repository
git clone https://github.com/saimanikantabattula/trialmatch.git
cd trialmatch

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env
```

### System Initialization

```bash
# Initialize database
python db.py

# Generate dataset (2000 patients, 41 trials)
python generate_enhanced_dataset.py

# Train machine learning models
python train_enhanced_models.py

# Evaluate model performance (optional)
python evaluate_models.py

# Verify dataset integrity (optional)
python verify_dataset.py
python verify_trials.py
```

## Usage

### Starting the System

Terminal 1 - Start FastAPI Server:
```bash
python main.py
```

Terminal 2 - Command Line Interface:
```bash
# Display system statistics
python cli.py stats

# Search eligible trials for patient
python cli.py patient --patient-id P00050

# List all clinical trials
python cli.py trials

# List all patients
python cli.py patients-list

# Display ML model information
python cli.py models

# Display help documentation
python cli.py help-guide
```

## Command-Line Interface

### stats
Display comprehensive system statistics including patient count, trial count, matches found, and match rates.

Example:
```bash
$ python cli.py stats
================================================================================
TRIALMATCH SYSTEM STATISTICS
================================================================================
Total Patients:              2000
Total Trials:                41
Total Matches Found:         731
Patients with Matches:       655
Match Success Rate:          32.8%
Avg Matches per Patient:     0.37
================================================================================
```

### patient
Search for eligible trials matching a specific patient's medical profile. Returns trials with ML prediction scores.

Example:
```bash
$ python cli.py patient --patient-id P00123

==========================================================================================
PATIENT PROFILE: P00123
==========================================================================================
Age:                 58 years
Conditions:          type 2 diabetes, hypertension
Medications:         metformin, lisinopril
Pregnancy Status:    No
==========================================================================================

Found 3 eligible trial(s)

1. NCT04623697 - Efficacy of Dapagliflozin in Type 2 Diabetes
   Condition:             Type 2 Diabetes
   Compatibility Score:   85%
   Trial Success Prob:    72%
   Completion Likelihood: 81%
```

### trials
Display complete list of all clinical trials in the database with associated metadata.

### patients-list
Display all patients in the database (first 100 shown). Includes age, conditions, and medications.

### models
Display detailed information about machine learning models including architecture, training methodology, and performance metrics.

### help-guide
Display comprehensive usage documentation.

## REST API Endpoints

All endpoints accessible at http://localhost:8000

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /stats | System statistics |
| GET | /matches/{patient_id} | Eligible trials for specified patient |
| GET | /patients | List all patients |
| GET | /trials | List all clinical trials |
| GET | /docs | Interactive API documentation (Swagger UI) |

### Example API Requests

```bash
# Retrieve system statistics
curl http://localhost:8000/stats

# Get trials for specific patient
curl http://localhost:8000/matches/P00050

# List all trials
curl http://localhost:8000/trials

# Access interactive API documentation
open http://localhost:8000/docs
```

## Project Structure
## Dataset Description

### Patient Data (2000 profiles)
- Age Range: 18-85 years
- Conditions: Up to 5 per patient from medical database
- Lab Values: HbA1c, eGFR, glucose, creatinine, blood pressure, cholesterol, triglycerides, LDL
- Medications: Up to 6 per patient based on conditions
- Pregnancy Status: Tracked for women 18-50 years old

### Clinical Trial Data (41 trials)
- Condition Coverage: 20+ medical conditions
- Average Age Range: 50.8 years
- Average Lab Requirements: 0.5 per trial
- Average Condition Requirements: 1.2 per trial
- Average Exclusion Criteria: 1.2 per trial

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend Framework | FastAPI | 0.115+ |
| Machine Learning | scikit-learn | 1.3+ |
| Algorithm | Gradient Boosting | Ensemble |
| Database | SQLite3 | 3.0+ |
| Natural Language Processing | Claude API | Anthropic |
| Command-Line Interface | Click | Latest |
| Data Processing | Pandas | 2.0+ |
| Numerical Computing | NumPy | 1.20+ |
| Programming Language | Python | 3.9+ |

## Model Performance Metrics

All models trained using stratified 80/20 train-test split with cross-validation.

### Performance Summary

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|-------|----------|-----------|--------|----------|---------|
| Trial Success Predictor | 100.0% | 100.0% | 100.0% | 100.0% | 1.0 |
| Completion Risk Predictor | 100.0% | 100.0% | 100.0% | 100.0% | 1.0 |
| Compatibility Scorer | 100.0% | 100.0% | 100.0% | 100.0% | 1.0 |

## System Performance Characteristics

- Database Size: Approximately 50 MB
- API Response Time: Less than 500ms per request
- Matching Computation: Less than 100ms per patient-trial pair
- Total Patient-Trial Combinations Evaluated: 82,000+
- Repository Size (cleaned): Approximately 2 MB

## Capabilities and Features

This system demonstrates:
- End-to-end machine learning pipeline implementation
- Advanced ensemble methods (Gradient Boosting)
- Natural language processing integration with Claude API
- RESTful API design with FastAPI
- Comprehensive data engineering practices
- Feature engineering and scaling techniques
- Model evaluation and validation methodologies
- Professional code organization and documentation

## Future Enhancement Opportunities

- Integration with real patient data (HIPAA-compliant)
- Advanced trial recommendation ranking algorithms
- Trial cost and geographic proximity filtering
- Patient outcome tracking and analysis
- Web-based dashboard interface
- Mobile application development
- Real-time trial updates via ClinicalTrials.gov API integration
- Explainable AI implementation (SHAP values)

## License

MIT License - This project may be used for personal or commercial applications.

## Author

Developed as a comprehensive portfolio project for data science positions.

---

## Support

For questions or issues, refer to the command-line help documentation:

```bash
python cli.py help-guide
```

Consult code comments for detailed implementation information.

---

**Built with Python, Machine Learning, and Artificial Intelligence**
