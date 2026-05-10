"""
BharatCare AI Pro · NLP Engine v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Symptom extraction, disease prediction, and severity classification.
Author: Deol Allwyn Samuel J B · VLSI · CIT · Afynix Digital
"""

import re
import string
from typing import Dict, List, Optional, Tuple
import numpy as np

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# ── Synonym map ──────────────────────────────────────────────────────────────
SYMPTOM_SYNONYMS: Dict[str, str] = {
    "running nose": "runny_nose", "runny nose": "runny_nose", "nasal discharge": "runny_nose",
    "body pain": "body_ache", "body ache": "body_ache", "muscle pain": "muscle_pain",
    "fits": "seizures", "convulsions": "seizures", "epilepsy fit": "seizures",
    "sugar": "diabetes_symptom", "high sugar": "diabetes_symptom", "blood sugar": "diabetes_symptom",
    "bp": "high_blood_pressure", "blood pressure": "high_blood_pressure", "high bp": "high_blood_pressure",
    "tight chest": "chest_tightness", "chest tightness": "chest_tightness",
    "chest pain": "chest_pain", "heart pain": "chest_pain",
    "kaichal": "fever", "high temperature": "fever", "pyrexia": "fever",
    "thalai vali": "headache", "head pain": "headache", "migraine": "headache",
    "bukhaar": "fever", "sar dard": "headache", "pet dard": "abdominal_pain",
    "ulti": "vomiting", "vomit": "vomiting", "nausea and vomiting": "vomiting",
    "dast": "diarrhea", "loose motion": "diarrhea", "loose stools": "diarrhea",
    "khansi": "cough", "persistent cough": "cough", "dry cough": "dry_cough",
    "saans lena mushkil": "shortness_of_breath", "breathlessness": "shortness_of_breath",
    "peeli skin": "jaundice", "yellow eyes": "jaundice", "yellow skin": "jaundice",
    "aankhon mein dard": "eye_pain", "eye pain": "eye_pain",
    "joint pain": "joint_pain", "jodo mein dard": "joint_pain",
    "weakness": "fatigue", "tired": "fatigue", "kamzori": "fatigue",
    "weight loss": "unexplained_weight_loss", "sudden weight loss": "unexplained_weight_loss",
    "frequent urination": "frequent_urination", "baar baar peshab": "frequent_urination",
    "excessive thirst": "excessive_thirst", "pyaas": "excessive_thirst",
    "rash": "skin_rash", "skin rash": "skin_rash", "daane": "skin_rash",
    "chills": "chills", "thand lagna": "chills", "rigors": "chills",
    "sweating": "sweating", "night sweats": "night_sweats",
    "loss of taste": "loss_of_taste", "swad nahi aata": "loss_of_taste",
    "loss of smell": "loss_of_smell", "khushbu nahi aati": "loss_of_smell",
    "eye redness": "red_eyes", "laal aankhein": "red_eyes",
    "pale skin": "pale_skin", "white skin": "pale_skin",
    "pus": "discharge", "discharge from eye": "eye_discharge",
    "blisters": "blisters", "chotan": "blisters",
    "itching": "itching", "khujli": "itching",
    "swelling": "swelling", "sujan": "swelling",
    "dizziness": "dizziness", "chakkar": "dizziness",
    "palpitations": "palpitations", "dil ki dhadkan": "palpitations",
    "dark urine": "dark_urine", "gehra peshab": "dark_urine",
    "constipation": "constipation", "kabz": "constipation",
    "back pain": "back_pain", "kamar dard": "back_pain",
    "blurred vision": "blurred_vision", "dhundli nazar": "blurred_vision",
    "nosebleed": "nosebleed", "naak se khoon": "nosebleed",
    "bleeding gums": "bleeding_gums", "madi se khoon": "bleeding_gums",
    "sore throat": "sore_throat", "gale mein dard": "sore_throat",
    "ear pain": "ear_pain", "kan mein dard": "ear_pain",
    "appetite loss": "loss_of_appetite", "bhookh nahi lagti": "loss_of_appetite",
    "no appetite": "loss_of_appetite", "not eating": "loss_of_appetite",
    "muscle weakness": "weakness", "numbness": "tingling_numbness",
    "tingling": "tingling_numbness", "jhunjhunahat": "tingling_numbness",
    "difficulty walking": "mobility_issue", "cannot walk": "mobility_issue",
    "confusion": "confusion", "disorientation": "confusion",
    "abdominal pain": "abdominal_pain", "stomach pain": "abdominal_pain",
    "stomach ache": "abdominal_pain", "pait dard": "abdominal_pain",
}

# ── Disease → symptoms ───────────────────────────────────────────────────────
DISEASE_SYMPTOM_MAP: Dict[str, List[str]] = {
    "dengue":         ["high_fever", "severe_headache", "eye_pain", "joint_pain", "muscle_pain", "skin_rash", "nausea", "vomiting", "bleeding_gums", "fatigue"],
    "malaria":        ["cyclical_fever", "chills", "sweating", "headache", "nausea", "vomiting", "muscle_pain", "anaemia_symptom", "jaundice", "fatigue"],
    "typhoid":        ["sustained_fever", "abdominal_pain", "headache", "constipation", "weakness", "loss_of_appetite", "diarrhea", "vomiting", "cough"],
    "pneumonia":      ["chest_pain", "shortness_of_breath", "cough", "high_fever", "chills", "fatigue", "phlegm", "confusion"],
    "tuberculosis":   ["persistent_cough", "blood_in_sputum", "night_sweats", "unexplained_weight_loss", "fatigue", "chest_pain", "fever", "loss_of_appetite"],
    "diabetes":       ["frequent_urination", "excessive_thirst", "unexplained_weight_loss", "fatigue", "blurred_vision", "tingling_numbness", "loss_of_appetite"],
    "hypertension":   ["headache", "dizziness", "blurred_vision", "chest_pain", "shortness_of_breath", "nosebleed", "palpitations", "fatigue"],
    "covid19":        ["fever", "dry_cough", "fatigue", "loss_of_smell", "loss_of_taste", "shortness_of_breath", "body_ache", "sore_throat", "headache"],
    "cholera":        ["watery_diarrhea", "vomiting", "dehydration", "muscle_cramps", "fatigue", "dark_urine", "dizziness"],
    "hepatitis":      ["jaundice", "abdominal_pain", "fatigue", "nausea", "vomiting", "dark_urine", "loss_of_appetite", "fever"],
    "chickenpox":     ["itching", "blisters", "skin_rash", "fever", "fatigue", "headache", "loss_of_appetite"],
    "conjunctivitis": ["red_eyes", "eye_discharge", "itching", "swelling", "eye_pain", "blurred_vision"],
    "anaemia":        ["fatigue", "weakness", "pale_skin", "shortness_of_breath", "dizziness", "headache", "palpitations"],
    "arthritis":      ["joint_pain", "swelling", "stiffness", "mobility_issue", "fatigue", "fever"],
    "common_cold":    ["runny_nose", "sneezing", "sore_throat", "cough", "fever", "headache", "fatigue", "body_ache"],
}

# ── Severity keywords ────────────────────────────────────────────────────────
SEVERITY_KEYWORDS: Dict[str, List[str]] = {
    "critical": [
        "unconscious", "unable to breathe", "chest pain severe", "blood vomiting",
        "seizure", "coughing blood", "stroke", "heart attack", "paralysis",
        "severe bleeding", "cannot wake", "blue lips", "severe shortness of breath",
        "very high fever", "confusion", "no urine", "collapsed",
    ],
    "moderate": [
        "moderate fever", "persistent vomiting", "dizziness", "shortness of breath",
        "weakness", "loss of appetite", "abdominal pain", "yellow eyes",
        "dark urine", "swelling", "palpitations", "not improving", "worsening",
    ],
    "mild": [
        "mild fever", "slight headache", "runny nose", "mild cough", "sneezing",
        "little tired", "slight body ache", "minor itching", "dry throat",
        "low energy", "slight nausea", "mild sore throat",
    ],
}

# ── Tamil keywords ───────────────────────────────────────────────────────────
TAMIL_KEYWORDS: Dict[str, str] = {
    "kaichal": "fever", "kaichalay": "fever", "thalai vali": "headache",
    "vayiru vali": "abdominal_pain", "irumAl": "cough", "irumal": "cough",
    "mookal oduthal": "runny_nose", "mookkil ner": "runny_nose",
    "vanthi": "vomiting", "வாந்தி": "vomiting", "pEdi": "diarrhea",
    "jaundice": "jaundice", "manja noi": "jaundice", "kannu semappu": "red_eyes",
    "mூttiram அதிகam": "frequent_urination", "mூttiram athikam": "frequent_urination",
    "thuvaaham": "excessive_thirst", "urakkam": "fatigue", "pallam": "weakness",
    "சொறி": "itching", "sorri": "itching", "தடிப்பு": "skin_rash", "thadippu": "skin_rash",
    "manam": "nausea", "மயக்கம்": "dizziness", "mayakkam": "dizziness",
    "maarbil vali": "chest_pain", "maarbu vali": "chest_pain",
    "mutu vali": "joint_pain", "தசை வலி": "muscle_pain", "tasai vali": "muscle_pain",
    "ratha voanthi": "blood_in_vomit", "irumallil rAdam": "blood_in_sputum",
    "kulir nodukal": "chills", "viyarvai": "sweating",
    "ethu thoondal": "loss_of_appetite", "payam": "fear", "thooku varamal": "insomnia",
    "nalla thengala": "night_sweats", "ullaga": "weight_loss",
    "paar parthal": "blurred_vision", "mudiyavilai": "fatigue",
}

# ── Hindi keywords ───────────────────────────────────────────────────────────
HINDI_KEYWORDS: Dict[str, str] = {
    "bukhaar": "fever", "bukhar": "fever", "tez bukhaar": "high_fever",
    "sar dard": "headache", "sir dard": "headache",
    "pet dard": "abdominal_pain", "paet mein dard": "abdominal_pain",
    "khansi": "cough", "sookhi khansi": "dry_cough", "balgam": "phlegm",
    "ulti": "vomiting", "mataali": "nausea", "qaai": "vomiting",
    "dast": "diarrhea", "loose motion": "diarrhea", "p얼teela": "diarrhea",
    "kamzori": "fatigue", "thakaan": "fatigue", "kamezona": "weakness",
    "chakkar aana": "dizziness", "chakkar": "dizziness",
    "saans lena mushkil": "shortness_of_breath", "saans ki takleef": "shortness_of_breath",
    "peeli skin": "jaundice", "aankhon ka peela": "jaundice",
    "khoon": "bleeding", "naak se khoon": "nosebleed",
    "meetha khaane ki ichha": "diabetes_symptom", "baar baar peshab": "frequent_urination",
    "pyaas": "excessive_thirst", "bahut pyaas": "excessive_thirst",
    "vajan kam hona": "weight_loss", "bhookh nahi": "loss_of_appetite",
    "joint dard": "joint_pain", "jodon mein dard": "joint_pain",
    "sardard": "headache", "gardan akadna": "neck_stiffness",
    "skin par daane": "skin_rash", "khujli": "itching",
    "aankhein laal": "red_eyes", "aankhon se paani": "eye_discharge",
    "thand lagna": "chills", "kaanpna": "chills",
    "raat ko paseena": "night_sweats", "paseena aana": "sweating",
    "seene mein dard": "chest_pain", "dil ki dhadkan": "palpitations",
    "gaala kharaab": "sore_throat", "gale mein kharaash": "sore_throat",
    "dhundli nazar": "blurred_vision", "nazar kamzor": "blurred_vision",
}

# ── Action map ───────────────────────────────────────────────────────────────
ACTION_MAP: Dict[str, Dict] = {
    "dengue":        {"action": "See doctor immediately for blood test (CBC, Dengue NS1/IgM)", "specialist": "General Physician / Infectious Disease", "home_remedy": "Papaya leaf juice, ORS, rest", "emergency_signs": ["Bleeding from gums/nose", "Severe abdominal pain", "Very low platelet count"]},
    "malaria":       {"action": "Rapid Diagnostic Test (RDT) immediately. Start ACT if positive", "specialist": "General Physician / Infectious Disease", "home_remedy": "Neem decoction, ORS, complete bed rest", "emergency_signs": ["Confusion/unconsciousness", "Seizures", "Severe anaemia"]},
    "typhoid":       {"action": "Widal test + blood culture. Start antibiotics as prescribed", "specialist": "General Physician / Gastroenterologist", "home_remedy": "Boiled water only, soft diet, bed rest", "emergency_signs": ["Severe abdominal pain", "High fever with confusion", "Blood in stools"]},
    "pneumonia":     {"action": "Chest X-ray + CBC immediately. Antibiotics required", "specialist": "Pulmonologist / General Physician", "home_remedy": "Steam inhalation, turmeric milk, stay warm", "emergency_signs": ["SpO2 <92%", "Breathing >30 breaths/min", "Blue lips"]},
    "tuberculosis":  {"action": "Sputum test + chest X-ray. Register on Nikshay portal. Free DOTS treatment", "specialist": "Pulmonologist / Chest Physician", "home_remedy": "High protein diet, sunlight, no alcohol", "emergency_signs": ["Coughing large amounts of blood", "Severe breathing difficulty"]},
    "diabetes":      {"action": "Fasting blood glucose + HbA1c test. Lifestyle changes + medication", "specialist": "Endocrinologist / Diabetologist", "home_remedy": "Karela juice, methi seeds, daily walk", "emergency_signs": ["Blood sugar <70 mg/dL (sweating, confusion)", "Blood sugar >300", "Fruity breath"]},
    "hypertension":  {"action": "BP monitoring twice daily. Low-salt diet. Start medication if >140/90", "specialist": "Cardiologist / General Physician", "home_remedy": "Garlic daily, hibiscus tea, reduce salt", "emergency_signs": ["BP >180/120 with headache", "Chest pain", "Vision changes", "Slurred speech"]},
    "covid19":       {"action": "Isolate immediately. Monitor SpO2 with oximeter. RTPCR test if needed", "specialist": "General Physician / Pulmonologist", "home_remedy": "Kadha, steam inhalation, rest, Vitamin C", "emergency_signs": ["SpO2 <94%", "Difficulty breathing at rest", "Confusion", "Persistent chest pain"]},
    "cholera":       {"action": "Start ORS immediately. IV fluids if severe vomiting. Antibiotics", "specialist": "General Physician / Gastroenterologist", "home_remedy": "ORS every 5 minutes, coconut water, rice water", "emergency_signs": ["No urine for 6 hours", "Unconsciousness", "Rapid weak pulse"]},
    "hepatitis":     {"action": "Liver function tests (LFT) + Hepatitis panel. Complete rest", "specialist": "Gastroenterologist / Hepatologist", "home_remedy": "No alcohol, papaya, turmeric milk, rest", "emergency_signs": ["Deep jaundice with confusion", "Vomiting blood", "Severe abdominal swelling"]},
    "chickenpox":    {"action": "Isolate for 7 days. Calamine lotion + antihistamines. Acyclovir if severe", "specialist": "General Physician / Dermatologist", "home_remedy": "Neem paste on blisters, oatmeal bath, trim nails", "emergency_signs": ["Breathing difficulty", "Rash on eyes", "High fever >104°F"]},
    "conjunctivitis":{"action": "Antibiotic eye drops (bacterial) or antihistamine (allergic). Avoid sharing items", "specialist": "Ophthalmologist", "home_remedy": "Rose water wash, cold compress, avoid touching eyes", "emergency_signs": ["Severe eye pain", "Vision loss", "Redness extending beyond eye"]},
    "anaemia":       {"action": "CBC + iron studies test. Iron supplements + dietary changes", "specialist": "Haematologist / General Physician", "home_remedy": "Spinach, dates, jaggery, drumstick leaves", "emergency_signs": ["Severe breathlessness", "Chest pain", "Fainting", "Hb <7 g/dL"]},
    "arthritis":     {"action": "X-ray of joints. NSAIDs for pain. Physiotherapy. Rheumatoid factor test if needed", "specialist": "Orthopaedician / Rheumatologist", "home_remedy": "Turmeric ginger tea, warm oil massage, gentle yoga", "emergency_signs": ["Sudden severe joint pain with fever", "Complete inability to move limb"]},
    "common_cold":   {"action": "Rest, fluids, paracetamol. No antibiotics. Steam inhalation", "specialist": "General Physician (if >7 days or worsening)", "home_remedy": "Tulsi ginger tea, steam, honey and lemon, turmeric milk", "emergency_signs": ["Fever >103°F for >3 days", "Difficulty breathing", "Stiff neck", "Ear pain"]},
}

GOVT_SCHEMES_BY_DISEASE = {
    "tuberculosis":  ["Nikshay Poshan Yojana — ₹500/month support", "Free DOTS treatment at government hospitals", "Nikshay helpline: 1800-11-6666"],
    "diabetes":      ["NPCDCS — free screening at PHCs", "Ayushman Bharat PM-JAY — ₹5 lakh cover", "Jan Aushadhi Kendras — 50-90% cheaper generics"],
    "hypertension":  ["NPCDCS — free BP check at Health Wellness Centres", "Ayushman Bharat PM-JAY", "Jan Aushadhi for affordable medicines"],
    "malaria":       ["NVBDCP — free diagnosis and treatment", "Free LLIN mosquito nets in endemic areas"],
    "dengue":        ["Free dengue testing at government hospitals", "NVBDCP vector control programme"],
    "anaemia":       ["Anaemia Mukt Bharat — free iron-folic acid", "PM POSHAN — fortified midday meals for children"],
    "common_cold":   ["JSSK — free medicines for children under 5", "Ayushman Arogya Mandir — free primary care"],
    "pneumonia":     ["PCV vaccine under Universal Immunisation Programme", "Free treatment at government hospitals"],
    "cholera":       ["Free OCV during outbreaks (IDSP programme)", "ORS free at all government health centres"],
    "chickenpox":    ["Varicella vaccine — private (not yet in NIP)", "Free treatment at government hospitals"],
    "hepatitis":     ["NVHCP — free Hep B vaccination", "Free Hep C treatment at AIIMS/government hospitals"],
    "arthritis":     ["Ayushman Bharat for joint replacement surgeries", "NPCDCS for NCD management"],
    "conjunctivitis":["Free eye care at NPCB camps", "Ayushman Bharat for surgery if needed"],
    "typhoid":       ["Free typhoid treatment at government hospitals", "Typhoid Vi-PS vaccine under SII/Bharat Biotech"],
    "covid19":       ["Free COVID vaccines under Universal Vaccination", "PM-JAY for hospitalisation"],
}


class SymptomExtractor:
    def __init__(self):
        self._build_patterns()

    def _build_patterns(self):
        self.synonym_patterns = {
            re.compile(r'\b' + re.escape(k) + r'\b', re.IGNORECASE): v
            for k, v in {**SYMPTOM_SYNONYMS, **TAMIL_KEYWORDS, **HINDI_KEYWORDS}.items()
        }

    def normalize_text(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text

    def detect_language_hints(self, text: str) -> str:
        tamil_count = sum(1 for k in TAMIL_KEYWORDS if k in text.lower())
        hindi_count = sum(1 for k in HINDI_KEYWORDS if k in text.lower())
        if tamil_count > hindi_count and tamil_count > 0:
            return "tamil"
        if hindi_count > 0:
            return "hindi"
        return "english"

    def extract_symptoms(self, text: str) -> List[str]:
        text_norm = self.normalize_text(text)
        found: List[str] = []
        for pattern, canonical in self.synonym_patterns.items():
            if pattern.search(text_norm):
                found.append(canonical)

        # Direct match against disease symptom lists
        all_known = set(s for syms in DISEASE_SYMPTOM_MAP.values() for s in syms)
        for sym in all_known:
            sym_readable = sym.replace("_", " ")
            if sym_readable in text_norm and sym not in found:
                found.append(sym)

        return list(dict.fromkeys(found))  # deduplicate

    def tokenize(self, text: str) -> List[str]:
        return self.normalize_text(text).split()


class DiseasePredictor:
    def __init__(self):
        self.corpus = self._build_corpus()
        self.disease_names = list(DISEASE_SYMPTOM_MAP.keys())
        if HAS_SKLEARN:
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
            self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)

    def _build_corpus(self) -> List[str]:
        return [" ".join(symptoms) for symptoms in DISEASE_SYMPTOM_MAP.values()]

    def predict(self, symptoms: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        if not symptoms:
            return []
        query = " ".join(symptoms)
        if HAS_SKLEARN:
            q_vec   = self.vectorizer.transform([query])
            scores  = cosine_similarity(q_vec, self.tfidf_matrix)[0]
        else:
            scores = self._fallback_score(symptoms)

        ranked = sorted(zip(self.disease_names, scores), key=lambda x: x[1], reverse=True)
        return [(name, round(float(score), 4)) for name, score in ranked[:top_k] if score > 0]

    def _fallback_score(self, symptoms: List[str]) -> np.ndarray:
        scores = []
        for disease, dis_syms in DISEASE_SYMPTOM_MAP.items():
            overlap = len(set(symptoms) & set(dis_syms))
            scores.append(overlap / max(len(dis_syms), 1))
        return np.array(scores)

    def get_symptom_overlap(self, symptoms: List[str], disease: str) -> Dict:
        dis_syms = DISEASE_SYMPTOM_MAP.get(disease, [])
        matched  = [s for s in symptoms if s in dis_syms]
        missing  = [s for s in dis_syms if s not in symptoms]
        return {
            "matched":     matched,
            "missing":     missing[:5],
            "overlap_pct": round(len(matched) / max(len(dis_syms), 1) * 100, 1),
        }


class SeverityClassifier:
    WEIGHTS = {"critical": 3, "moderate": 2, "mild": 1}

    def classify(self, symptoms: List[str], text: str) -> str:
        score = self.get_severity_score(symptoms, text)
        if score >= 60:
            return "Critical"
        elif score >= 30:
            return "Moderate"
        return "Mild"

    def get_severity_score(self, symptoms: List[str], text: str = "") -> int:
        text_lower = text.lower()
        score = 0
        for level, keywords in SEVERITY_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    score += self.WEIGHTS[level] * 10
        score += len(symptoms) * 3
        return min(score, 100)


class ActionRecommender:
    def recommend(self, disease: str, severity: str) -> Dict:
        base = ACTION_MAP.get(disease, {
            "action": "Consult a doctor for proper diagnosis",
            "specialist": "General Physician",
            "home_remedy": "Rest, fluids, paracetamol for fever",
            "emergency_signs": ["High fever", "Difficulty breathing"],
        })
        result = dict(base)
        if severity == "Critical":
            result["action"] = "⚠️ EMERGENCY: Go to nearest hospital immediately. " + result["action"]
        return result

    def get_govt_schemes(self, disease: str) -> List[str]:
        return GOVT_SCHEMES_BY_DISEASE.get(disease, [
            "Ayushman Bharat PM-JAY — ₹5 lakh annual cover",
            "Ayushman Arogya Mandir — Free primary care at HWCs",
            "Jan Aushadhi Kendras — 50-90% cheaper generic medicines",
        ])


def analyze_symptoms(text: str) -> Dict:
    """
    Main entry point. Accepts free text in English/Hindi/Tamil.
    Returns complete clinical analysis dict.
    """
    extractor   = SymptomExtractor()
    predictor   = DiseasePredictor()
    severity_cl = SeverityClassifier()
    recommender = ActionRecommender()

    lang     = extractor.detect_language_hints(text)
    symptoms = extractor.extract_symptoms(text)

    if not symptoms:
        # Fallback: use all words as symptoms
        symptoms = extractor.tokenize(text)

    top_diseases = predictor.predict(symptoms, top_k=5)
    top_disease  = top_diseases[0][0] if top_diseases else "common_cold"
    severity     = severity_cl.classify(symptoms, text)
    action_info  = recommender.recommend(top_disease, severity)
    schemes      = recommender.get_govt_schemes(top_disease)

    overlaps = {}
    for dis, _ in top_diseases[:3]:
        overlaps[dis] = predictor.get_symptom_overlap(symptoms, dis)

    return {
        "input_text":        text,
        "language_detected": lang,
        "symptoms_extracted":symptoms,
        "symptom_count":     len(symptoms),
        "top_diseases":      top_diseases,
        "primary_disease":   top_disease,
        "severity":          severity,
        "severity_score":    severity_cl.get_severity_score(symptoms, text),
        "action":            action_info["action"],
        "specialist":        action_info["specialist"],
        "home_remedy":       action_info["home_remedy"],
        "emergency_signs":   action_info["emergency_signs"],
        "govt_schemes":      schemes,
        "symptom_overlap":   overlaps,
        "emergency_flag":    severity == "Critical",
    }
