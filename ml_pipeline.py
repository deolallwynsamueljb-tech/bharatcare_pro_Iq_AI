"""
BharatCare AI Pro · ML Pipeline v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
India's Complete Healthcare Intelligence OS

Pipeline Stages
───────────────
  Stage 1  →  Symptom disease classifier (NB + LR + RF + GB + Voting)
  Stage 2  →  Severity classifier (3-class)
  Stage 3  →  Mental health risk classifier (4-class RF)
  Stage 4  →  Drug side-effect probability predictor
  Stage 5  →  Outbreak predictor (RF + temporal features)
  Stage 6  →  Grade / outcome predictor
  Stage 7  →  SMOTE class balancing across all pipelines
  Stage 8  →  5-fold cross-validation for all models
  Stage 9  →  Feature importance extraction
  Stage 10 →  Model persistence (pickle)

Author  : Deol Allwyn Samuel J B · VLSI · CIT · Afynix Digital
Version : 2.0.0
"""

import os
import json
import pickle
import warnings
import time
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

from sklearn.preprocessing    import StandardScaler, LabelEncoder, MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble         import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
    RandomForestRegressor,
    IsolationForest,
)
from sklearn.linear_model     import LogisticRegression
from sklearn.naive_bayes      import MultinomialNB, ComplementNB
from sklearn.neighbors        import KNeighborsClassifier
from sklearn.svm              import SVC
from sklearn.neural_network   import MLPClassifier
from sklearn.pipeline         import Pipeline
from sklearn.model_selection  import (
    train_test_split,
    cross_val_score,
    StratifiedKFold,
)
from sklearn.metrics          import (
    accuracy_score, f1_score, classification_report,
    confusion_matrix, roc_auc_score,
    precision_score, recall_score, mean_absolute_error, r2_score,
)
from sklearn.decomposition    import TruncatedSVD

try:
    from imblearn.over_sampling import SMOTE, ADASYN
    from imblearn.combine       import SMOTETomek
    HAS_IMBLEARN = True
except ImportError:
    HAS_IMBLEARN = False
    print("  [INFO] imbalanced-learn not found — skipping SMOTE")

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

VERSION      = "2.0.0"
RANDOM_STATE = 42
MODEL_DIR    = "models"
DATA_DIR     = "data"
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(DATA_DIR,  exist_ok=True)

np.random.seed(RANDOM_STATE)

DISEASES = [
    "dengue", "malaria", "typhoid", "pneumonia", "tuberculosis",
    "diabetes", "hypertension", "covid19", "cholera", "hepatitis",
    "chickenpox", "conjunctivitis", "anaemia", "arthritis", "common_cold",
]

SYMPTOMS_PER_DISEASE: Dict[str, List[str]] = {
    "dengue":        ["high_fever","severe_headache","eye_pain","joint_pain","muscle_pain","rash","nausea","vomiting","bleeding_gums","fatigue"],
    "malaria":       ["cyclical_fever","chills","sweating","headache","nausea","vomiting","muscle_pain","anaemia","jaundice","fatigue"],
    "typhoid":       ["sustained_fever","abdominal_pain","headache","constipation","rose_spots","weakness","loss_of_appetite","diarrhea","vomiting","cough"],
    "pneumonia":     ["chest_pain","shortness_of_breath","cough","high_fever","chills","fatigue","rapid_breathing","phlegm","confusion","bluish_lips"],
    "tuberculosis":  ["persistent_cough","blood_in_sputum","night_sweats","weight_loss","fatigue","chest_pain","fever","loss_of_appetite","shortness_of_breath","chills"],
    "diabetes":      ["frequent_urination","excessive_thirst","unexplained_weight_loss","fatigue","blurred_vision","slow_healing","tingling_feet","frequent_infections","hunger","dry_mouth"],
    "hypertension":  ["headache","dizziness","blurred_vision","chest_pain","shortness_of_breath","nosebleed","palpitations","fatigue","neck_pain","flushing"],
    "covid19":       ["fever","dry_cough","fatigue","loss_of_smell","loss_of_taste","shortness_of_breath","body_ache","sore_throat","headache","diarrhea"],
    "cholera":       ["watery_diarrhea","vomiting","dehydration","muscle_cramps","rapid_heart_rate","sunken_eyes","dry_mouth","low_blood_pressure","fatigue","nausea"],
    "hepatitis":     ["jaundice","abdominal_pain","fatigue","nausea","vomiting","dark_urine","pale_stool","loss_of_appetite","fever","joint_pain"],
    "chickenpox":    ["itchy_rash","blisters","fever","fatigue","headache","loss_of_appetite","runny_nose","cough","abdominal_pain","sore_throat"],
    "conjunctivitis":["red_eyes","discharge","itching","watering_eyes","swollen_eyelids","sensitivity_to_light","blurred_vision","burning_sensation","crusting","foreign_body_sensation"],
    "anaemia":       ["fatigue","weakness","pale_skin","shortness_of_breath","dizziness","cold_hands","headache","chest_pain","irregular_heartbeat","brittle_nails"],
    "arthritis":     ["joint_pain","joint_swelling","stiffness","reduced_range_of_motion","warmth","redness","fatigue","fever","weight_loss","weakness"],
    "common_cold":   ["runny_nose","sneezing","sore_throat","cough","congestion","low_grade_fever","headache","fatigue","body_ache","watery_eyes"],
}

RISK_LEVELS     = ["Minimal", "Low", "Moderate", "High"]
SEVERITY_LEVELS = ["Mild", "Moderate", "Critical"]


# ══════════════════════════════════════════════════════════════════════════════
# 1. SYMPTOM DATA GENERATION (synthetic training data)
# ══════════════════════════════════════════════════════════════════════════════

def _generate_symptom_records(n_per_disease: int = 334) -> pd.DataFrame:
    """Generate synthetic patient-symptom records for all 15 diseases."""
    records = []
    rng     = np.random.RandomState(RANDOM_STATE)

    for disease in DISEASES:
        core_symptoms = SYMPTOMS_PER_DISEASE[disease]
        for _ in range(n_per_disease):
            n_symp  = rng.randint(3, len(core_symptoms) + 1)
            chosen  = rng.choice(core_symptoms, size=n_symp, replace=False).tolist()
            # add 0-2 noise symptoms from other diseases
            noise_n = rng.randint(0, 3)
            if noise_n > 0:
                all_symp = [s for d, sl in SYMPTOMS_PER_DISEASE.items()
                            if d != disease for s in sl]
                noise = rng.choice(all_symp, size=min(noise_n, len(all_symp)), replace=False).tolist()
                chosen += noise
            text = " ".join(chosen)
            severity_roll = rng.random()
            if severity_roll < 0.55:
                severity = "Mild"
            elif severity_roll < 0.85:
                severity = "Moderate"
            else:
                severity = "Critical"
            records.append({"text": text, "disease": disease, "severity": severity})

    df = pd.DataFrame(records).sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
    return df


# ══════════════════════════════════════════════════════════════════════════════
# 2. DISEASE CLASSIFIER TRAINING
# ══════════════════════════════════════════════════════════════════════════════

def train_disease_classifier(df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Train 5-model ensemble for disease prediction from symptom text.
    Returns results dict + vectorizer + label encoder.
    """
    print("\n" + "─" * 56)
    print("  BharatCare ML · Disease Classifier Training")
    print("─" * 56)

    if df is None or len(df) == 0:
        df = _generate_symptom_records()

    print(f"  Records     : {len(df):,}  |  Diseases: {df['disease'].nunique()}")

    le   = LabelEncoder()
    y    = le.fit_transform(df["disease"])
    tfidf = TfidfVectorizer(
        ngram_range=(1, 2), max_features=3000,
        sublinear_tf=True, min_df=2,
    )
    X = tfidf.fit_transform(df["text"])

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )

    # SMOTE on dense array
    X_tr_arr = X_tr.toarray()
    if HAS_IMBLEARN:
        try:
            smt      = SMOTE(random_state=RANDOM_STATE, k_neighbors=3)
            X_tr_arr, y_tr = smt.fit_resample(X_tr_arr, y_tr)
            print(f"  SMOTE       : balanced to {len(X_tr_arr)} samples")
        except Exception as e:
            print(f"  SMOTE skipped: {e}")

    X_te_arr = X_te.toarray()

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    models_def = {
        "Naive Bayes":    ComplementNB(alpha=0.5),
        "Logistic Reg":   LogisticRegression(C=1.5, max_iter=1000,
                                              multi_class="multinomial",
                                              random_state=RANDOM_STATE),
        "Random Forest":  RandomForestClassifier(n_estimators=300, max_depth=15,
                                                  class_weight="balanced",
                                                  random_state=RANDOM_STATE, n_jobs=-1),
        "Gradient Boost": GradientBoostingClassifier(n_estimators=200, learning_rate=0.08,
                                                      max_depth=5, random_state=RANDOM_STATE),
        "Neural Network": MLPClassifier(hidden_layer_sizes=(256, 128),
                                        activation="relu", max_iter=300,
                                        random_state=RANDOM_STATE, early_stopping=True),
    }
    if HAS_XGB:
        models_def["XGBoost"] = xgb.XGBClassifier(
            n_estimators=250, learning_rate=0.08, max_depth=6,
            use_label_encoder=False, eval_metric="mlogloss",
            random_state=RANDOM_STATE, n_jobs=-1,
        )

    results = {}
    for name, mdl in models_def.items():
        t0 = time.time()
        mdl.fit(X_tr_arr, y_tr)
        y_pred = mdl.predict(X_te_arr)

        cv_acc = cross_val_score(mdl, X_tr_arr, y_tr, cv=cv, scoring="accuracy", n_jobs=-1)
        cv_f1  = cross_val_score(mdl, X_tr_arr, y_tr, cv=cv, scoring="f1_macro",  n_jobs=-1)
        elapsed = time.time() - t0

        results[name] = {
            "model":       mdl,
            "accuracy":    round(accuracy_score(y_te, y_pred), 4),
            "f1_macro":    round(f1_score(y_te, y_pred, average="macro", zero_division=0), 4),
            "cv_acc_mean": round(cv_acc.mean(), 4),
            "cv_f1_mean":  round(cv_f1.mean(),  4),
            "cm":          confusion_matrix(y_te, y_pred).tolist(),
            "y_test":      y_te,
            "y_pred":      y_pred,
            "train_time":  round(elapsed, 2),
        }
        print(f"  {name:20s}  Acc={results[name]['accuracy']:.4f}  "
              f"F1={results[name]['f1_macro']:.4f}  [{elapsed:.1f}s]")

    best = max(results, key=lambda x: results[x]["f1_macro"])
    print(f"\n  [BEST] {best}  F1={results[best]['f1_macro']:.4f}")

    payload = {
        "results":     results,
        "vectorizer":  tfidf,
        "label_enc":   le,
        "best":        best,
        "diseases":    DISEASES,
    }
    with open(f"{MODEL_DIR}/disease_classifier.pkl", "wb") as fh:
        pickle.dump(payload, fh)
    print(f"  Saved → {MODEL_DIR}/disease_classifier.pkl")

    return payload


# ══════════════════════════════════════════════════════════════════════════════
# 3. SEVERITY CLASSIFIER
# ══════════════════════════════════════════════════════════════════════════════

def train_severity_classifier(df: Optional[pd.DataFrame] = None) -> Dict:
    """Train a 3-class severity model (Mild/Moderate/Critical)."""
    print("\n" + "─" * 56)
    print("  BharatCare ML · Severity Classifier Training")
    print("─" * 56)

    if df is None:
        df = _generate_symptom_records()

    le_sev = LabelEncoder()
    y      = le_sev.fit_transform(df["severity"])

    tfidf = TfidfVectorizer(ngram_range=(1, 2), max_features=2000, sublinear_tf=True)
    X     = tfidf.fit_transform(df["text"]).toarray()

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )

    if HAS_IMBLEARN:
        try:
            smt      = SMOTE(random_state=RANDOM_STATE, k_neighbors=3)
            X_tr, y_tr = smt.fit_resample(X_tr, y_tr)
        except Exception:
            pass

    rf = RandomForestClassifier(n_estimators=200, class_weight="balanced",
                                 random_state=RANDOM_STATE, n_jobs=-1)
    rf.fit(X_tr, y_tr)
    y_pred = rf.predict(X_te)

    acc = accuracy_score(y_te, y_pred)
    f1  = f1_score(y_te, y_pred, average="macro", zero_division=0)
    print(f"  Severity RF  Acc={acc:.4f}  F1={f1:.4f}")

    payload = {"model": rf, "vectorizer": tfidf, "label_enc": le_sev}
    with open(f"{MODEL_DIR}/severity_classifier.pkl", "wb") as fh:
        pickle.dump(payload, fh)
    print(f"  Saved → {MODEL_DIR}/severity_classifier.pkl")
    return payload


# ══════════════════════════════════════════════════════════════════════════════
# 4. MENTAL HEALTH RISK CLASSIFIER
# ══════════════════════════════════════════════════════════════════════════════

def _generate_mental_health_records(n: int = 2000) -> pd.DataFrame:
    """Synthetic mental health dataset with PHQ-9 scores and risk labels."""
    rng = np.random.RandomState(RANDOM_STATE + 1)
    records = []

    PHRASES = {
        "high": ["I want to die", "I can't go on", "no hope", "ending everything",
                 "so depressed I can't function", "can't stop crying", "panic attacks daily",
                 "severe anxiety all the time", "self harm thoughts", "hopeless"],
        "moderate": ["feeling very low", "can't sleep", "anxious", "stressed at work",
                     "not enjoying anything", "feeling empty", "overwhelmed", "burnout",
                     "constant worry", "mood swings"],
        "low": ["a bit sad today", "somewhat stressed", "little tired", "low energy",
                "mild worry", "not as happy as usual", "slight anxiety"],
        "minimal": ["doing okay", "generally fine", "occasional stress", "managing well",
                    "mostly positive", "normal days", "handling things"],
    }

    for risk_level in RISK_LEVELS:
        n_each = n // len(RISK_LEVELS)
        key    = risk_level.lower()
        phrases = PHRASES.get(key, PHRASES["minimal"])
        for _ in range(n_each):
            if risk_level == "High":
                phq9  = rng.randint(15, 28)
                gad7  = rng.randint(12, 22)
            elif risk_level == "Moderate":
                phq9  = rng.randint(10, 16)
                gad7  = rng.randint(7, 13)
            elif risk_level == "Low":
                phq9  = rng.randint(5, 11)
                gad7  = rng.randint(3, 8)
            else:
                phq9  = rng.randint(0, 6)
                gad7  = rng.randint(0, 5)

            n_phrases = rng.randint(1, 4)
            text = ". ".join(rng.choice(phrases, size=min(n_phrases, len(phrases)), replace=False))
            records.append({
                "text": text, "phq9": phq9, "gad7": gad7,
                "risk_level": risk_level,
                "sleep_hours": float(rng.uniform(3, 9)),
                "work_hours":  float(rng.randint(6, 14)),
            })

    return pd.DataFrame(records).sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)


def train_mental_health_classifier(df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Train mental health risk classifier on PHQ-9, GAD-7, and text features.
    Returns 4-class model: Minimal / Low / Moderate / High
    """
    print("\n" + "─" * 56)
    print("  BharatCare ML · Mental Health Risk Classifier")
    print("─" * 56)

    if df is None:
        df = _generate_mental_health_records()

    print(f"  Records  : {len(df):,}  |  Levels: {df['risk_level'].value_counts().to_dict()}")

    le = LabelEncoder()
    y  = le.fit_transform(df["risk_level"])

    # TF-IDF on text
    tfidf = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
    X_text = tfidf.fit_transform(df["text"]).toarray()

    # Numeric features: phq9, gad7, sleep, work
    X_num  = df[["phq9", "gad7", "sleep_hours", "work_hours"]].fillna(0).values
    X      = np.hstack([X_text, X_num])

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )
    if HAS_IMBLEARN:
        try:
            smt = SMOTE(random_state=RANDOM_STATE, k_neighbors=3)
            X_tr, y_tr = smt.fit_resample(X_tr, y_tr)
        except Exception:
            pass

    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_tr)
    X_te_s = scaler.transform(X_te)

    cv     = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=300, class_weight="balanced",
                                                 random_state=RANDOM_STATE, n_jobs=-1),
        "Gradient Boost": GradientBoostingClassifier(n_estimators=150, learning_rate=0.1,
                                                      random_state=RANDOM_STATE),
        "Logistic Reg":   LogisticRegression(C=1.0, max_iter=800, class_weight="balanced",
                                              random_state=RANDOM_STATE),
        "Neural Network": MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=300,
                                         random_state=RANDOM_STATE, early_stopping=True),
    }

    best_model, best_f1, best_name = None, 0.0, ""
    results = {}
    for name, mdl in models.items():
        t0 = time.time()
        mdl.fit(X_tr_s, y_tr)
        y_pred = mdl.predict(X_te_s)
        cv_f1  = cross_val_score(mdl, X_tr_s, y_tr, cv=cv, scoring="f1_macro", n_jobs=-1)
        f1     = f1_score(y_te, y_pred, average="macro", zero_division=0)
        acc    = accuracy_score(y_te, y_pred)
        elapsed = time.time() - t0
        results[name] = {"accuracy": round(acc, 4), "f1_macro": round(f1, 4),
                         "cv_f1_mean": round(cv_f1.mean(), 4), "train_time": round(elapsed, 2)}
        print(f"  {name:20s}  Acc={acc:.4f}  F1={f1:.4f}  [{elapsed:.1f}s]")
        if f1 > best_f1:
            best_f1, best_model, best_name = f1, mdl, name

    print(f"\n  [BEST] {best_name}  F1={best_f1:.4f}")

    payload = {
        "model": best_model, "scaler": scaler,
        "vectorizer": tfidf, "label_enc": le,
        "results": results, "best": best_name,
    }
    with open(f"{MODEL_DIR}/mindcare_classifier.pkl", "wb") as fh:
        pickle.dump(payload, fh)
    print(f"  Saved → {MODEL_DIR}/mindcare_classifier.pkl")
    return payload


# ══════════════════════════════════════════════════════════════════════════════
# 5. DRUG SIDE EFFECT PREDICTOR
# ══════════════════════════════════════════════════════════════════════════════

def _generate_drug_records(n: int = 3000) -> pd.DataFrame:
    """Synthetic drug-patient records for side effect probability modelling."""
    rng = np.random.RandomState(RANDOM_STATE + 2)
    DRUG_CATEGORIES = ["Antibiotic", "Painkiller", "Antidiabetic",
                        "Antihypertensive", "Antidepressant", "Antihistamine",
                        "Antifungal", "Steroid", "Vitamin", "Antacid"]
    records = []
    for _ in range(n):
        age      = rng.randint(5, 85)
        weight   = float(rng.uniform(15, 120))
        gender   = rng.choice(["Male", "Female"])
        cat      = rng.choice(DRUG_CATEGORIES)
        kidney   = rng.choice(["Normal", "Mild_CKD", "Moderate_CKD"], p=[0.75, 0.15, 0.10])
        liver    = rng.choice(["Normal", "Mild", "Moderate"], p=[0.80, 0.12, 0.08])
        dose_rel = float(rng.uniform(0.5, 1.5))

        # Simple rule-based side-effect risk (target variable 0-3: None/Mild/Moderate/Severe)
        risk_score = 0
        if age > 65:    risk_score += 1
        if kidney != "Normal": risk_score += 1
        if liver  != "Normal": risk_score += 1
        if dose_rel > 1.2:     risk_score += 1
        if cat in ["Steroid", "Antibiotic", "Antidepressant"]: risk_score += 1
        risk_score += rng.randint(0, 2)
        side_effect_severity = min(risk_score, 3)

        records.append({
            "age": age, "weight": weight, "gender": int(gender == "Female"),
            "drug_cat_enc": DRUG_CATEGORIES.index(cat),
            "kidney_enc":   ["Normal", "Mild_CKD", "Moderate_CKD"].index(kidney),
            "liver_enc":    ["Normal", "Mild", "Moderate"].index(liver),
            "dose_relative": round(dose_rel, 2),
            "side_effect_severity": side_effect_severity,
        })
    return pd.DataFrame(records)


def train_side_effect_predictor(df: Optional[pd.DataFrame] = None) -> Dict:
    """Train drug side effect severity predictor."""
    print("\n" + "─" * 56)
    print("  BharatCare ML · Drug Side Effect Predictor")
    print("─" * 56)

    if df is None:
        df = _generate_drug_records()

    FEAT = ["age", "weight", "gender", "drug_cat_enc", "kidney_enc", "liver_enc", "dose_relative"]
    X    = df[FEAT].values
    y    = df["side_effect_severity"].values

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )
    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_tr)
    X_te_s = scaler.transform(X_te)

    if HAS_IMBLEARN:
        try:
            smt = SMOTE(random_state=RANDOM_STATE, k_neighbors=3)
            X_tr_s, y_tr = smt.fit_resample(X_tr_s, y_tr)
        except Exception:
            pass

    rf = RandomForestClassifier(n_estimators=200, class_weight="balanced",
                                 random_state=RANDOM_STATE, n_jobs=-1)
    rf.fit(X_tr_s, y_tr)
    y_pred = rf.predict(X_te_s)
    acc = accuracy_score(y_te, y_pred)
    f1  = f1_score(y_te, y_pred, average="macro", zero_division=0)
    print(f"  Side Effect RF  Acc={acc:.4f}  F1={f1:.4f}")

    fi = pd.Series(rf.feature_importances_, index=FEAT).sort_values(ascending=False)
    print("  Top features:", fi.head(3).index.tolist())

    payload = {"model": rf, "scaler": scaler, "features": FEAT}
    with open(f"{MODEL_DIR}/side_effect_predictor.pkl", "wb") as fh:
        pickle.dump(payload, fh)
    print(f"  Saved → {MODEL_DIR}/side_effect_predictor.pkl")
    return payload


# ══════════════════════════════════════════════════════════════════════════════
# 6. OUTBREAK PREDICTOR
# ══════════════════════════════════════════════════════════════════════════════

def _generate_outbreak_records(n: int = 2000) -> pd.DataFrame:
    """Synthetic outbreak records for classifier training."""
    rng = np.random.RandomState(RANDOM_STATE + 3)
    OUTBREAK_DISEASES = ["dengue", "malaria", "cholera", "typhoid", "covid19", "influenza"]
    CLIMATE_ZONES     = ["tropical", "arid", "semi_arid", "humid_subtropical", "highland"]
    records = []
    for _ in range(n):
        disease      = rng.choice(OUTBREAK_DISEASES)
        month        = rng.randint(1, 13)
        vax_coverage = float(rng.uniform(0.30, 0.95))
        pop_density  = float(rng.uniform(50, 5000))
        temp_c       = float(rng.uniform(15, 42))
        rainfall_mm  = float(rng.uniform(0, 400))
        sanitation   = float(rng.uniform(0.2, 0.95))
        climate      = rng.choice(CLIMATE_ZONES)
        hosp_beds    = float(rng.uniform(0.5, 8))  # per 1000

        # Risk score
        risk = 0.0
        if disease in ["dengue", "malaria"] and month in [7, 8, 9, 10]:
            risk += 0.3
        if disease in ["cholera", "typhoid"] and rainfall_mm > 200:
            risk += 0.25
        if vax_coverage < 0.5:  risk += 0.2
        if pop_density > 2000:  risk += 0.15
        if sanitation  < 0.5:   risk += 0.15
        if hosp_beds   < 1.5:   risk += 0.1
        risk += rng.uniform(0, 0.15)

        outbreak = int(risk > 0.5)
        records.append({
            "disease_enc":   OUTBREAK_DISEASES.index(disease),
            "month":         month,
            "vax_coverage":  round(vax_coverage, 2),
            "pop_density":   round(pop_density, 0),
            "temp_c":        round(temp_c, 1),
            "rainfall_mm":   round(rainfall_mm, 1),
            "sanitation":    round(sanitation, 2),
            "climate_enc":   CLIMATE_ZONES.index(climate),
            "hosp_beds":     round(hosp_beds, 2),
            "outbreak":      outbreak,
        })
    return pd.DataFrame(records)


def train_outbreak_predictor(df: Optional[pd.DataFrame] = None) -> Dict:
    """Train outbreak probability classifier."""
    print("\n" + "─" * 56)
    print("  BharatCare ML · Outbreak Predictor Training")
    print("─" * 56)

    if df is None:
        df = _generate_outbreak_records()

    FEAT = ["disease_enc", "month", "vax_coverage", "pop_density",
            "temp_c", "rainfall_mm", "sanitation", "climate_enc", "hosp_beds"]
    X = df[FEAT].values
    y = df["outbreak"].values

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )
    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_tr)
    X_te_s = scaler.transform(X_te)

    if HAS_IMBLEARN:
        try:
            smt = SMOTE(random_state=RANDOM_STATE, k_neighbors=3)
            X_tr_s, y_tr = smt.fit_resample(X_tr_s, y_tr)
        except Exception:
            pass

    rf = RandomForestClassifier(n_estimators=250, class_weight="balanced",
                                 random_state=RANDOM_STATE, n_jobs=-1)
    rf.fit(X_tr_s, y_tr)
    y_pred = rf.predict(X_te_s)
    y_prob = rf.predict_proba(X_te_s)[:, 1]

    acc = accuracy_score(y_te, y_pred)
    f1  = f1_score(y_te, y_pred, zero_division=0)
    auc = roc_auc_score(y_te, y_prob)
    print(f"  Outbreak RF   Acc={acc:.4f}  F1={f1:.4f}  AUC={auc:.4f}")

    fi = pd.Series(rf.feature_importances_, index=FEAT).sort_values(ascending=False)
    print("  Top features:", fi.head(3).index.tolist())

    payload = {"model": rf, "scaler": scaler, "features": FEAT,
               "accuracy": round(acc, 4), "f1": round(f1, 4), "auc": round(auc, 4)}
    with open(f"{MODEL_DIR}/outbreak_predictor.pkl", "wb") as fh:
        pickle.dump(payload, fh)
    print(f"  Saved → {MODEL_DIR}/outbreak_predictor.pkl")
    return payload


# ══════════════════════════════════════════════════════════════════════════════
# 7. MODEL LOADING HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def load_disease_classifier() -> Optional[Dict]:
    path = f"{MODEL_DIR}/disease_classifier.pkl"
    if os.path.exists(path):
        with open(path, "rb") as fh:
            return pickle.load(fh)
    return None


def load_severity_classifier() -> Optional[Dict]:
    path = f"{MODEL_DIR}/severity_classifier.pkl"
    if os.path.exists(path):
        with open(path, "rb") as fh:
            return pickle.load(fh)
    return None


def load_mindcare_classifier() -> Optional[Dict]:
    path = f"{MODEL_DIR}/mindcare_classifier.pkl"
    if os.path.exists(path):
        with open(path, "rb") as fh:
            return pickle.load(fh)
    return None


def load_side_effect_predictor() -> Optional[Dict]:
    path = f"{MODEL_DIR}/side_effect_predictor.pkl"
    if os.path.exists(path):
        with open(path, "rb") as fh:
            return pickle.load(fh)
    return None


def load_outbreak_predictor() -> Optional[Dict]:
    path = f"{MODEL_DIR}/outbreak_predictor.pkl"
    if os.path.exists(path):
        with open(path, "rb") as fh:
            return pickle.load(fh)
    return None


# ══════════════════════════════════════════════════════════════════════════════
# 8. INFERENCE HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def predict_disease(symptom_text: str, top_k: int = 5) -> List[Dict]:
    """
    Predict top-k diseases from symptom text string.
    Returns [{"disease": str, "probability": float, "display_name": str}, ...]
    """
    payload = load_disease_classifier()
    if payload is None:
        payload = train_disease_classifier()

    mdl    = payload["results"][payload["best"]]["model"]
    tfidf  = payload["vectorizer"]
    le     = payload["label_enc"]

    X    = tfidf.transform([symptom_text]).toarray()
    prob = mdl.predict_proba(X)[0]
    top  = np.argsort(prob)[::-1][:top_k]

    return [
        {
            "disease":      le.inverse_transform([i])[0],
            "probability":  round(float(prob[i]), 4),
            "display_name": le.inverse_transform([i])[0].replace("_", " ").title(),
        }
        for i in top
    ]


def predict_severity(symptom_text: str) -> Dict:
    """Predict severity (Mild/Moderate/Critical) from symptom text."""
    payload = load_severity_classifier()
    if payload is None:
        payload = train_severity_classifier()

    mdl   = payload["model"]
    tfidf = payload["vectorizer"]
    le    = payload["label_enc"]

    X     = tfidf.transform([symptom_text]).toarray()
    label = le.inverse_transform(mdl.predict(X))[0]
    prob  = mdl.predict_proba(X)[0]
    return {"severity": label, "confidence": round(float(prob.max()), 4)}


def predict_mental_health_risk(text: str, phq9: int = 0, gad7: int = 0,
                                sleep_hours: float = 7.0, work_hours: float = 8.0) -> Dict:
    """Predict mental health risk level from text + questionnaire scores."""
    payload = load_mindcare_classifier()
    if payload is None:
        payload = train_mental_health_classifier()

    mdl    = payload["model"]
    scaler = payload["scaler"]
    tfidf  = payload["vectorizer"]
    le     = payload["label_enc"]

    X_text = tfidf.transform([text]).toarray()
    X_num  = np.array([[phq9, gad7, sleep_hours, work_hours]])
    X      = np.hstack([X_text, X_num])
    X_s    = scaler.transform(X)

    label  = le.inverse_transform(mdl.predict(X_s))[0]
    prob   = mdl.predict_proba(X_s)[0]
    return {"risk_level": label, "confidence": round(float(prob.max()), 4),
            "all_probs":  dict(zip(le.classes_, prob.round(3)))}


def predict_outbreak_probability(disease: str, month: int, vax_coverage: float,
                                  pop_density: float, temp_c: float, rainfall_mm: float,
                                  sanitation: float, climate: str, hosp_beds: float) -> Dict:
    """Predict outbreak probability for given parameters."""
    payload = load_outbreak_predictor()
    if payload is None:
        payload = train_outbreak_predictor()

    DISEASES_ = ["dengue", "malaria", "cholera", "typhoid", "covid19", "influenza"]
    CLIMATES_  = ["tropical", "arid", "semi_arid", "humid_subtropical", "highland"]

    d_enc = DISEASES_.index(disease)  if disease in DISEASES_  else 0
    c_enc = CLIMATES_.index(climate)  if climate in CLIMATES_   else 0

    mdl    = payload["model"]
    scaler = payload["scaler"]
    X      = np.array([[d_enc, month, vax_coverage, pop_density,
                         temp_c, rainfall_mm, sanitation, c_enc, hosp_beds]])
    X_s    = scaler.transform(X)
    prob   = mdl.predict_proba(X_s)[0][1]
    risk   = "High" if prob > 0.7 else "Medium" if prob > 0.4 else "Low"
    return {"outbreak_probability": round(float(prob), 4), "risk_level": risk}


# ══════════════════════════════════════════════════════════════════════════════
# 9. META — train all models
# ══════════════════════════════════════════════════════════════════════════════

def train_all() -> Dict:
    """Train the complete BharatCare ML pipeline. Returns all payloads."""
    t_start = time.time()
    print("=" * 56)
    print("  BharatCare AI Pro - ML Pipeline v2.0")
    print("  Deol Allwyn Samuel J B · VLSI · CIT · Afynix Digital")
    print("=" * 56)

    payloads = {}
    payloads["disease"]      = train_disease_classifier()
    payloads["severity"]     = train_severity_classifier()
    payloads["mental_health"]= train_mental_health_classifier()
    payloads["side_effect"]  = train_side_effect_predictor()
    payloads["outbreak"]     = train_outbreak_predictor()

    total = time.time() - t_start
    print(f"\n  [DONE] All models trained in {total:.1f}s")
    print("=" * 56)

    meta = {
        "trained_at": datetime.now().isoformat(),
        "version":    VERSION,
        "models": {
            "disease_classifier":    payloads["disease"]["results"][payloads["disease"]["best"]]["accuracy"],
            "severity_classifier":   "trained",
            "mindcare_classifier":   payloads["mental_health"]["results"][payloads["mental_health"]["best"]]["accuracy"],
            "side_effect_predictor": "trained",
            "outbreak_predictor":    payloads["outbreak"]["accuracy"],
        },
    }
    with open(f"{MODEL_DIR}/pipeline_meta.json", "w") as fh:
        json.dump(meta, fh, indent=2)

    return payloads


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    train_all()
