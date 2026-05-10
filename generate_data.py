"""
BharatCare AI Pro — Synthetic Data Generator
Generates training and demo data for all 4 modules
Developer: Deol Allwyn Samuel J B · VLSI · CIT · Afynix Digital
"""

import os
import json
import random
import numpy as np
from datetime import datetime, timedelta
import csv

random.seed(42)
np.random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

DISEASES = [
    "dengue","malaria","tuberculosis","typhoid","covid19",
    "diabetes","hypertension","asthma","pneumonia","viral_fever",
    "gastroenteritis","jaundice","chikungunya","leptospirosis","anaemia"
]

SYMPTOM_POOL = {
    "dengue": ["high fever","severe headache","eye pain","joint pain","muscle pain","rash","nausea","vomiting","fatigue","bleeding gums","low platelet"],
    "malaria": ["cyclical fever","chills","sweating","headache","nausea","vomiting","muscle pain","fatigue","anaemia","spleen enlargement","jaundice"],
    "tuberculosis": ["persistent cough","blood in sputum","night sweats","weight loss","fatigue","chest pain","fever","loss of appetite","swollen lymph nodes","breathlessness"],
    "typhoid": ["sustained fever","abdominal pain","headache","weakness","loss of appetite","rash","diarrhoea","constipation","nausea","spleen enlargement"],
    "covid19": ["fever","dry cough","fatigue","loss of smell","loss of taste","sore throat","breathlessness","body ache","headache","diarrhoea"],
    "diabetes": ["frequent urination","excessive thirst","weight loss","fatigue","blurred vision","slow healing","frequent infections","tingling hands","hunger","dark skin patches"],
    "hypertension": ["headache","dizziness","blurred vision","chest pain","shortness of breath","nosebleed","flushing","palpitations","fatigue","anxiety"],
    "asthma": ["wheezing","shortness of breath","chest tightness","cough","breathlessness","nighttime cough","exercise difficulty","mucus production","rapid breathing","anxiety"],
    "pneumonia": ["high fever","cough with mucus","chest pain","breathlessness","fatigue","chills","sweating","nausea","vomiting","confusion"],
    "viral_fever": ["fever","headache","body ache","fatigue","sore throat","runny nose","cough","loss of appetite","weakness","chills"],
    "gastroenteritis": ["diarrhoea","vomiting","abdominal cramps","nausea","fever","dehydration","loss of appetite","weakness","bloating","blood in stool"],
    "jaundice": ["yellow skin","yellow eyes","dark urine","pale stool","abdominal pain","fatigue","nausea","vomiting","itching","fever"],
    "chikungunya": ["sudden fever","severe joint pain","joint swelling","muscle pain","headache","rash","fatigue","nausea","eye pain","back pain"],
    "leptospirosis": ["high fever","severe headache","muscle pain","chills","red eyes","jaundice","abdominal pain","diarrhoea","rash","vomiting"],
    "anaemia": ["fatigue","weakness","pale skin","shortness of breath","dizziness","cold hands","chest pain","headache","brittle nails","poor concentration"]
}

STATES = ["Tamil Nadu","Maharashtra","Delhi","Karnataka","Uttar Pradesh","Gujarat","West Bengal","Rajasthan","Madhya Pradesh","Kerala"]
GENDERS = ["Male","Female","Other"]
AGE_GROUPS = ["child","adolescent","adult","middle_aged","elderly"]

def random_age(group):
    ranges = {"child":(2,12),"adolescent":(13,19),"adult":(20,35),"middle_aged":(36,55),"elderly":(56,85)}
    lo,hi = ranges[group]
    return random.randint(lo,hi)

def generate_patient_symptoms(n=5000):
    records = []
    per_disease = n // len(DISEASES)
    for disease in DISEASES:
        syms = SYMPTOM_POOL[disease]
        for _ in range(per_disease):
            age_group = random.choice(AGE_GROUPS)
            age = random_age(age_group)
            gender = random.choice(GENDERS)
            num_syms = random.randint(3, min(8, len(syms)))
            chosen = random.sample(syms, num_syms)
            duration_days = random.randint(1, 14)
            severity_score = random.randint(1, 10)
            if severity_score <= 3:
                severity = "Mild"
            elif severity_score <= 7:
                severity = "Moderate"
            else:
                severity = "Critical"
            symptom_text = ", ".join(chosen)
            records.append({
                "symptom_text": symptom_text,
                "disease": disease,
                "severity": severity,
                "age": age,
                "age_group": age_group,
                "gender": gender,
                "duration_days": duration_days,
                "state": random.choice(STATES),
                "severity_score": severity_score
            })
    random.shuffle(records)
    return records

def save_csv(records, filename, fieldnames):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"  Saved {len(records)} records -> {filename}")
    return path

def generate_mental_health_data(n=2000):
    MOODS = ["happy","anxious","depressed","stressed","calm","overwhelmed","hopeful","irritable","lonely","content"]
    PROFESSIONS = ["student","software_engineer","teacher","healthcare_worker","homemaker","factory_worker","farmer","self_employed","unemployed","retired"]
    records = []
    for _ in range(n):
        age = random.randint(16, 65)
        gender = random.choice(GENDERS)
        profession = random.choice(PROFESSIONS)
        phq9 = [random.randint(0,3) for _ in range(9)]
        gad7 = [random.randint(0,3) for _ in range(7)]
        phq9_total = sum(phq9)
        gad7_total = sum(gad7)
        if phq9_total <= 4:
            depression_level = "Minimal"
        elif phq9_total <= 9:
            depression_level = "Mild"
        elif phq9_total <= 14:
            depression_level = "Moderate"
        elif phq9_total <= 19:
            depression_level = "Moderately Severe"
        else:
            depression_level = "Severe"
        if gad7_total <= 4:
            anxiety_level = "Minimal"
        elif gad7_total <= 9:
            anxiety_level = "Mild"
        elif gad7_total <= 14:
            anxiety_level = "Moderate"
        else:
            anxiety_level = "Severe"
        sleep_hours = round(random.uniform(3, 10), 1)
        exercise_days = random.randint(0, 7)
        stress_events = random.randint(0, 5)
        social_support = random.randint(1, 10)
        mood_today = random.choice(MOODS)
        overall_risk = "High" if (phq9_total > 14 or gad7_total > 14 or stress_events >= 4) else \
                       "Moderate" if (phq9_total > 9 or gad7_total > 9) else "Low"
        records.append({
            "age": age, "gender": gender, "profession": profession,
            "phq9_total": phq9_total, "gad7_total": gad7_total,
            "depression_level": depression_level, "anxiety_level": anxiety_level,
            "sleep_hours": sleep_hours, "exercise_days": exercise_days,
            "stress_events": stress_events, "social_support": social_support,
            "mood_today": mood_today, "overall_risk": overall_risk,
            "state": random.choice(STATES)
        })
    return records

def generate_drug_interaction_data(n=1000):
    DRUG_PAIRS = [
        ("Warfarin","Aspirin","Major","Increased bleeding risk"),
        ("Metformin","Alcohol","Moderate","Lactic acidosis risk"),
        ("Ciprofloxacin","Antacids","Moderate","Reduced absorption"),
        ("Sertraline","Tramadol","Major","Serotonin syndrome"),
        ("Amlodipine","Simvastatin","Moderate","Increased statin levels"),
        ("Paracetamol","Alcohol","Moderate","Hepatotoxicity"),
        ("Ibuprofen","Lisinopril","Moderate","Reduced antihypertensive effect"),
        ("Azithromycin","Digoxin","Moderate","Increased digoxin levels"),
        ("Hydroxychloroquine","Metformin","Minor","Monitor blood glucose"),
        ("ORS","None","None","Safe combination"),
    ]
    records = []
    for _ in range(n):
        pair = random.choice(DRUG_PAIRS)
        drug1, drug2, severity, effect = pair
        age = random.randint(18, 75)
        outcome = "ADR_reported" if severity == "Major" and random.random() > 0.5 else "No_ADR"
        records.append({
            "drug1": drug1, "drug2": drug2,
            "interaction_severity": severity,
            "effect_description": effect,
            "patient_age": age,
            "patient_gender": random.choice(["Male","Female"]),
            "outcome": outcome,
            "state": random.choice(STATES)
        })
    return records

def generate_outbreak_data(n=1500):
    OUTBREAK_DISEASES = ["dengue","malaria","cholera","influenza","leptospirosis","chikungunya"]
    MONTHS = list(range(1, 13))
    records = []
    base_date = datetime(2022, 1, 1)
    for i in range(n):
        disease = random.choice(OUTBREAK_DISEASES)
        state = random.choice(STATES)
        month = random.choice(MONTHS)
        year = random.randint(2022, 2025)
        date = datetime(year, month, 1)
        peak_months = {
            "dengue": [7,8,9,10], "malaria": [6,7,8,9],
            "cholera": [5,6,7,8], "influenza": [1,2,11,12],
            "leptospirosis": [7,8,9], "chikungunya": [7,8,9,10]
        }
        is_peak = 1 if month in peak_months.get(disease,[]) else 0
        rainfall_mm = random.uniform(0, 400) if is_peak else random.uniform(0, 100)
        temp_c = random.uniform(20, 42)
        humidity_pct = random.uniform(40, 95)
        vax_coverage = random.uniform(0.3, 0.95)
        population_density = random.uniform(100, 12000)
        cases = random.randint(5, 2000) if is_peak else random.randint(0, 100)
        outbreak = 1 if cases > 200 else 0
        records.append({
            "date": date.strftime("%Y-%m"),
            "state": state,
            "disease": disease,
            "month": month,
            "year": year,
            "is_peak_season": is_peak,
            "rainfall_mm": round(rainfall_mm, 1),
            "temperature_c": round(temp_c, 1),
            "humidity_pct": round(humidity_pct, 1),
            "vaccination_coverage": round(vax_coverage, 3),
            "population_density_per_sqkm": round(population_density, 1),
            "reported_cases": cases,
            "outbreak_flag": outbreak
        })
    return records

def generate_nutrition_logs(n=1000):
    MEAL_TYPES = ["breakfast","lunch","dinner","snack"]
    FOOD_ITEMS = [
        ("Idli","South Indian",39,1.7,8.0,0.2,0.5),
        ("Dosa","South Indian",120,2.5,17.0,4.5,0.5),
        ("Rice","Grains",130,2.7,28.0,0.3,0.4),
        ("Dal","Lentils",116,7.6,20.1,0.4,3.9),
        ("Roti","Grains",71,2.5,15.0,0.4,2.4),
        ("Sambar","South Indian",55,2.4,8.8,1.6,2.1),
        ("Banana","Fruits",89,1.1,22.8,0.3,2.6),
        ("Milk","Dairy",42,3.4,5.0,1.0,0.0),
        ("Egg","Proteins",155,13.0,1.1,11.0,0.0),
        ("Chicken","Proteins",165,31.0,0.0,3.6,0.0),
        ("Spinach","Vegetables",23,2.9,3.6,0.4,2.2),
        ("Apple","Fruits",52,0.3,14.0,0.2,2.4),
        ("Peanuts","Nuts",567,25.8,16.1,49.2,8.5),
        ("Curd","Dairy",98,11.0,3.4,4.3,0.0),
    ]
    records = []
    start = datetime(2024, 1, 1)
    for i in range(n):
        user_id = f"USER{random.randint(1,200):04d}"
        date = start + timedelta(days=random.randint(0,365))
        meal = random.choice(MEAL_TYPES)
        food_name, category, kcal, protein, carbs, fat, fiber = random.choice(FOOD_ITEMS)
        qty_grams = random.randint(50, 300)
        scale = qty_grams / 100.0
        age = random.randint(18, 70)
        gender = random.choice(["Male","Female"])
        target_kcal = 2000 if gender == "Male" else 1700
        records.append({
            "user_id": user_id,
            "date": date.strftime("%Y-%m-%d"),
            "meal_type": meal,
            "food_item": food_name,
            "category": category,
            "quantity_grams": qty_grams,
            "calories": round(kcal * scale, 1),
            "protein_g": round(protein * scale, 2),
            "carbs_g": round(carbs * scale, 2),
            "fat_g": round(fat * scale, 2),
            "fiber_g": round(fiber * scale, 2),
            "age": age,
            "gender": gender,
            "target_kcal": target_kcal,
            "state": random.choice(STATES)
        })
    return records

def generate_health_records(n=500):
    records = []
    start = datetime(2024, 1, 1)
    for i in range(n):
        user_id = f"BCP{random.randint(1,100):04d}"
        date = start + timedelta(days=random.randint(0,480))
        age = random.randint(18, 75)
        gender = random.choice(GENDERS)
        weight = round(random.uniform(40, 110), 1)
        height = random.randint(145, 190)
        bmi = round(weight / (height/100)**2, 1)
        bp_sys = random.randint(100, 180)
        bp_dia = random.randint(60, 110)
        fasting_glucose = random.randint(70, 280)
        hb_level = round(random.uniform(7.0, 17.0), 1)
        spo2 = random.randint(88, 100)
        heart_rate = random.randint(55, 110)
        temp_f = round(random.uniform(97.0, 104.0), 1)
        smoker = random.choice([0,1])
        diabetic = 1 if fasting_glucose > 126 else 0
        hypertensive = 1 if bp_sys > 140 else 0
        records.append({
            "user_id": user_id,
            "date": date.strftime("%Y-%m-%d"),
            "age": age,
            "gender": gender,
            "weight_kg": weight,
            "height_cm": height,
            "bmi": bmi,
            "bp_systolic": bp_sys,
            "bp_diastolic": bp_dia,
            "fasting_glucose_mgdl": fasting_glucose,
            "haemoglobin_gdl": hb_level,
            "spo2_pct": spo2,
            "heart_rate_bpm": heart_rate,
            "temperature_f": temp_f,
            "smoker": smoker,
            "diabetic_flag": diabetic,
            "hypertensive_flag": hypertensive,
            "state": random.choice(STATES)
        })
    return records

def generate_vaccine_tracker(n=400):
    VACCINES = ["BCG","OPV0","Hepatitis B birth","Pentavalent1","OPV1","PCV1","Pentavalent2","OPV2",
                "Rotavirus1","Pentavalent3","OPV3","PCV2","IPV","Rotavirus2","MR1","JE1","DPT Booster1","MR2","JE2","DPT Booster2"]
    records = []
    for _ in range(n):
        child_id = f"CHILD{random.randint(1,200):04d}"
        dob = datetime(2020,1,1) + timedelta(days=random.randint(0,1460))
        gender = random.choice(["Male","Female"])
        state = random.choice(STATES)
        for vaccine in random.sample(VACCINES, random.randint(3, len(VACCINES))):
            due_offset = random.randint(0, 730)
            administered = random.choice([1,1,1,0])
            records.append({
                "child_id": child_id,
                "date_of_birth": dob.strftime("%Y-%m-%d"),
                "gender": gender,
                "state": state,
                "vaccine": vaccine,
                "due_date": (dob + timedelta(days=due_offset)).strftime("%Y-%m-%d"),
                "administered": administered
            })
    return records

def generate_all():
    print("\n BharatCare AI Pro — Generating Synthetic Data")
    print("=" * 55)

    print("\n[1/6] Patient Symptom Records (5000)...")
    symptom_records = generate_patient_symptoms(5000)
    save_csv(symptom_records, "symptom_records.csv", list(symptom_records[0].keys()))

    print("\n[2/6] Mental Health Assessments (2000)...")
    mh_records = generate_mental_health_data(2000)
    save_csv(mh_records, "mental_health_data.csv", list(mh_records[0].keys()))

    print("\n[3/6] Drug Interaction Cases (1000)...")
    drug_records = generate_drug_interaction_data(1000)
    save_csv(drug_records, "drug_interactions.csv", list(drug_records[0].keys()))

    print("\n[4/6] Outbreak Surveillance Data (1500)...")
    outbreak_records = generate_outbreak_data(1500)
    save_csv(outbreak_records, "outbreak_data.csv", list(outbreak_records[0].keys()))

    print("\n[5/6] Nutrition Logs (1000)...")
    nutrition_records = generate_nutrition_logs(1000)
    save_csv(nutrition_records, "nutrition_logs.csv", list(nutrition_records[0].keys()))

    print("\n[6/6] Health Records + Vaccine Tracker...")
    health_records = generate_health_records(500)
    save_csv(health_records, "health_records.csv", list(health_records[0].keys()))
    vaccine_records = generate_vaccine_tracker(400)
    save_csv(vaccine_records, "vaccine_tracker.csv", list(vaccine_records[0].keys()))

    meta = {
        "generated_at": datetime.now().isoformat(),
        "total_records": 5000 + 2000 + 1000 + 1500 + 1000 + 500 + 400,
        "files": [
            "symptom_records.csv","mental_health_data.csv","drug_interactions.csv",
            "outbreak_data.csv","nutrition_logs.csv","health_records.csv","vaccine_tracker.csv"
        ],
        "diseases": DISEASES,
        "states": STATES
    }
    with open(os.path.join(DATA_DIR, "data_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    total = meta["total_records"]
    print(f"\n{'='*55}")
    print(f" Data Generation Complete!")
    print(f" Total Records: {total:,}")
    print(f" Output Directory: {DATA_DIR}")
    print(f"{'='*55}\n")

if __name__ == "__main__":
    generate_all()
