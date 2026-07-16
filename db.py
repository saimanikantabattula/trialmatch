import sqlite3
import json
from pathlib import Path

DB_PATH = 'trialmatch.db'

def init_db():
    """Initialize SQLite database with tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Trials table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trials (
            trial_id TEXT PRIMARY KEY,
            title TEXT,
            condition TEXT,
            eligibility_rules TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Patients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            age INTEGER,
            conditions TEXT,
            lab_values TEXT,
            medications TEXT,
            pregnancy_status INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Matches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            match_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            trial_id TEXT,
            is_eligible INTEGER,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(patient_id, trial_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Database initialized")

def add_trial(trial_id, title, condition, eligibility_rules, status='recruiting'):
    """Add a trial to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO trials (trial_id, title, condition, eligibility_rules, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (trial_id, title, condition, json.dumps(eligibility_rules), status))
        conn.commit()
        print(f"✓ Added trial: {trial_id}")
    except sqlite3.IntegrityError:
        print(f"Trial {trial_id} already exists")
    finally:
        conn.close()

def add_patient(patient_id, age, conditions, lab_values, medications, pregnancy_status=False):
    """Add a patient to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO patients (patient_id, age, conditions, lab_values, medications, pregnancy_status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            patient_id, 
            age, 
            json.dumps(conditions),
            json.dumps(lab_values),
            json.dumps(medications),
            int(pregnancy_status)
        ))
        conn.commit()
        print(f"✓ Added patient: {patient_id}")
    except sqlite3.IntegrityError:
        print(f"Patient {patient_id} already exists")
    finally:
        conn.close()

def get_patient(patient_id):
    """Retrieve patient data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'patient_id': row[0],
            'age': row[1],
            'conditions': json.loads(row[2]),
            'lab_values': json.loads(row[3]),
            'medications': json.loads(row[4]),
            'pregnancy_status': bool(row[5])
        }
    return None

def get_trial(trial_id):
    """Retrieve trial data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM trials WHERE trial_id = ?', (trial_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'trial_id': row[0],
            'title': row[1],
            'condition': row[2],
            'eligibility_rules': json.loads(row[3]),
            'status': row[4]
        }
    return None

def get_all_trials():
    """Get all trials."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT trial_id, title, eligibility_rules FROM trials')
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {'trial_id': r[0], 'title': r[1], 'eligibility_rules': json.loads(r[2])}
        for r in rows
    ]

def get_all_patients():
    """Get all patients."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT patient_id, age, conditions, lab_values, medications, pregnancy_status FROM patients')
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            'patient_id': r[0],
            'age': r[1],
            'conditions': json.loads(r[2]),
            'lab_values': json.loads(r[3]),
            'medications': json.loads(r[4]),
            'pregnancy_status': bool(r[5])
        }
        for r in rows
    ]

if __name__ == '__main__':
    init_db()
