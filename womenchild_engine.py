"""
BharatCare AI Pro · Women & Child Health Engine v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pregnancy tracker, vaccine schedule, child growth, PCOS, anaemia.
Author: Deol Allwyn Samuel J B · VLSI · CIT · Afynix Digital
"""

from datetime import datetime, timedelta
import math
from typing import Dict, List, Optional
import re

# ── India NIP Vaccine Schedule ─────────────────────────────────────────────────
VACCINE_SCHEDULE: Dict[str, List[Dict]] = {
    "At Birth":         [{"vaccine": "BCG", "doses": 1, "route": "Intradermal", "disease": "Tuberculosis"},
                          {"vaccine": "OPV-0", "doses": 1, "route": "Oral", "disease": "Polio"},
                          {"vaccine": "Hep B-1", "doses": 1, "route": "Intramuscular", "disease": "Hepatitis B"}],
    "6 Weeks":          [{"vaccine": "OPV-1", "doses": 1, "route": "Oral", "disease": "Polio"},
                          {"vaccine": "Pentavalent-1 (DPT+HepB+Hib)", "doses": 1, "route": "IM", "disease": "Diphtheria/Pertussis/Tetanus/Hepatitis B/Hib"},
                          {"vaccine": "Rotavirus-1", "doses": 1, "route": "Oral", "disease": "Rotavirus Diarrhoea"},
                          {"vaccine": "PCV-1", "doses": 1, "route": "IM", "disease": "Pneumococcal Disease"},
                          {"vaccine": "IPV-1", "doses": 1, "route": "IM", "disease": "Polio (inactivated)"},
                          {"vaccine": "fIPV-1", "doses": 1, "route": "Intradermal", "disease": "Polio"}],
    "10 Weeks":         [{"vaccine": "OPV-2", "doses": 1, "route": "Oral", "disease": "Polio"},
                          {"vaccine": "Pentavalent-2", "doses": 1, "route": "IM", "disease": "DPT+HepB+Hib"},
                          {"vaccine": "Rotavirus-2", "doses": 1, "route": "Oral", "disease": "Rotavirus"}],
    "14 Weeks":         [{"vaccine": "OPV-3", "doses": 1, "route": "Oral", "disease": "Polio"},
                          {"vaccine": "Pentavalent-3", "doses": 1, "route": "IM", "disease": "DPT+HepB+Hib"},
                          {"vaccine": "Rotavirus-3", "doses": 1, "route": "Oral", "disease": "Rotavirus"},
                          {"vaccine": "PCV-2", "doses": 1, "route": "IM", "disease": "Pneumococcal"},
                          {"vaccine": "IPV-2", "doses": 1, "route": "IM", "disease": "Polio"}],
    "9 Months":         [{"vaccine": "Measles-Rubella (MR-1)", "doses": 1, "route": "Subcutaneous", "disease": "Measles+Rubella"},
                          {"vaccine": "OPV Booster", "doses": 1, "route": "Oral", "disease": "Polio"},
                          {"vaccine": "Vitamin A (1st dose)", "doses": 1, "route": "Oral", "disease": "Vitamin A deficiency"},
                          {"vaccine": "JE-1 (endemic areas)", "doses": 1, "route": "IM", "disease": "Japanese Encephalitis"}],
    "12 Months":        [{"vaccine": "PCV Booster", "doses": 1, "route": "IM", "disease": "Pneumococcal"}],
    "15 Months":        [{"vaccine": "MMR (alternate) or MR-2", "doses": 1, "route": "SC", "disease": "Measles+Mumps+Rubella"},
                          {"vaccine": "Varicella (private)", "doses": 1, "route": "SC", "disease": "Chickenpox"}],
    "16-18 Months":     [{"vaccine": "DPT Booster-1", "doses": 1, "route": "IM", "disease": "Diphtheria/Pertussis/Tetanus"},
                          {"vaccine": "OPV Booster-2", "doses": 1, "route": "Oral", "disease": "Polio"},
                          {"vaccine": "Vitamin A (2nd dose)", "doses": 1, "route": "Oral", "disease": "Vitamin A deficiency"},
                          {"vaccine": "JE-2 (endemic areas)", "doses": 1, "route": "IM", "disease": "Japanese Encephalitis"}],
    "2 Years":          [{"vaccine": "Typhoid Vi-PS (private)", "doses": 1, "route": "IM", "disease": "Typhoid"}],
    "4-6 Years":        [{"vaccine": "DPT Booster-2", "doses": 1, "route": "IM", "disease": "DPT"},
                          {"vaccine": "OPV Booster-3", "doses": 1, "route": "Oral", "disease": "Polio"},
                          {"vaccine": "Varicella 2nd dose (private)", "doses": 1, "route": "SC", "disease": "Chickenpox"}],
    "10 Years":         [{"vaccine": "Td (Tetanus + diphtheria)", "doses": 1, "route": "IM", "disease": "Tetanus+Diphtheria"},
                          {"vaccine": "HPV (girls only, school programme)", "doses": 1, "route": "IM", "disease": "Cervical Cancer"}],
    "16 Years":         [{"vaccine": "Td Booster", "doses": 1, "route": "IM", "disease": "Tetanus+Diphtheria"},
                          {"vaccine": "HPV 2nd dose (girls)", "doses": 1, "route": "IM", "disease": "Cervical Cancer"}],
}

# ── Pregnancy weeks data ───────────────────────────────────────────────────────
PREGNANCY_WEEKS: Dict[int, Dict] = {}
_WEEKS_DATA = [
    (1,  "Poppy seed",    0,    0.0,  ["Conception occurs", "Cell division begins"], ["May not know yet", "Possible implantation spotting"], "Folic acid 400-800 mcg immediately", []),
    (4,  "Pea",           1,    0.4,  ["Heart begins beating", "Neural tube forming"], ["Missed period", "Breast tenderness", "Fatigue"], "Folic acid critical — prevents neural tube defects", ["Confirm pregnancy with hCG blood test", "Start prenatal vitamins"]),
    (6,  "Lentil",        2,    0.6,  ["Brain forming", "Limb buds appear", "Facial features starting"], ["Nausea", "Fatigue", "Frequent urination", "Mood swings"], "Folic acid, B6 for nausea", ["Book first OB appointment", "Blood group + Rh factor"]),
    (8,  "Raspberry",     3,    1.6,  ["All major organs forming", "Fingers and toes", "Heartbeat detectable by ultrasound"], ["Morning sickness peak", "Bloating", "Heightened smell"], "Iron + Folic acid", ["First ultrasound (dating scan)", "CBC, Blood type, Rubella immunity"]),
    (10, "Strawberry",    4,    3.5,  ["Vital organs functional", "Eyelids formed", "Fingernails starting"], ["Nausea often peaks then reduces", "Round ligament pain begins"], "Iron, Calcium, Vitamin D", []),
    (12, "Lime",          14,   5.4,  ["Reflexes forming", "Can suck thumb", "Kidneys produce urine"], ["Nausea may ease", "Energy returns", "Visible bump beginning"], "Continue prenatal vitamins", ["NT scan (11-13 weeks)", "Double marker test"]),
    (16, "Avocado",       100,  11.6, ["Skeleton hardening", "Can hear sounds", "Hair growing"], ["Round ligament pain", "Back pain beginning", "Appetite increases"], "Calcium 1000mg/day + Vitamin D", ["Quadruple marker/AFP test", "Anatomy scan booking"]),
    (20, "Banana",        300,  16.5, ["Halfway point!", "Vernix forming", "Swallowing amniotic fluid", "Can feel kicks"], ["Kicks felt (quickening)", "Back pain", "Heartburn"], "Iron especially important — blood volume doubles", ["Anomaly scan (18-22 weeks)", "Gestational diabetes screen booking"]),
    (24, "Corn",          600,  21.3, ["Lungs developing surfactant", "Hearing well-developed", "Responds to light"], ["Braxton Hicks contractions", "Stretch marks", "Constipation"], "Iron 27mg/day, Omega-3", ["Glucose Tolerance Test (24-28 weeks)", "Check Hb"]),
    (28, "Eggplant",      1000, 25.4, ["Rapid brain development", "Eyes open", "Breathing practice", "Fat deposits"], ["Frequent urination returns", "Sleep difficulty", "Carpal tunnel"], "Calcium 1200mg, Iron, DHA", ["28-week check: BP, urine, fundal height", "TIFFA if not done"]),
    (32, "Squash",        1700, 28.0, ["Skin smoothing", "Practising breathing", "Head may engage"], ["Shortness of breath", "Heartburn severe", "Pelvic pressure"], "Iron, Vitamin K, Calcium", ["Growth scan", "Check fetal position"]),
    (36, "Honeydew melon",2600, 32.0, ["Full term approaching", "Lungs nearly mature", "Shedding vernix"], ["Dropping sensation", "Nesting urge", "Cervix changes"], "Iron, maintain Omega-3", ["Weekly NST possible", "GBS screening (35-37 weeks)"]),
    (38, "Pumpkin",       3000, 35.6, ["Fully developed", "Skull plates not fully fused", "Ready for birth"], ["Braxton Hicks frequent", "Cervix effacing", "Vaginal discharge increase"], "Iron, stay hydrated", ["Weekly BP and urine check"]),
    (40, "Watermelon",    3400, 51.2, ["Full term: 37-40 weeks", "Ready for birth", "Brain still developing postnatally"], ["Due date", "Cervix dilation", "Labour signs: contractions, water breaking"], "Stay nourished, rest", ["NST, biophysical profile if overdue"]),
]
for week, size, weight_g, length_cm, dev, syms, nutr, tests in _WEEKS_DATA:
    PREGNANCY_WEEKS[week] = {"size_comparison": size, "baby_weight_g": weight_g,
                              "baby_length_cm": length_cm, "developments": dev,
                              "mother_symptoms": syms, "nutrition_focus": nutr, "tests_due": tests,
                              "warnings": ["Seek help if heavy bleeding", "Seek help if severe headache + visual changes", "Seek help if no fetal movement felt after 28 weeks"]}
# Fill intermediate weeks by interpolation
for w in range(1, 41):
    if w not in PREGNANCY_WEEKS:
        prev = max([k for k in PREGNANCY_WEEKS if k <= w], default=1)
        PREGNANCY_WEEKS[w] = dict(PREGNANCY_WEEKS[prev])

# ── Child Milestones ───────────────────────────────────────────────────────────
CHILD_MILESTONES: Dict[str, Dict] = {
    "1":  {"motor": ["Lifts head briefly when on tummy", "Moves arms/legs symmetrically"], "language": ["Startles to sounds", "Makes small sounds"], "social": ["Brief eye contact", "Responds to voice"], "cognitive": ["Follows objects with eyes briefly"]},
    "2":  {"motor": ["Holds head steady", "Pushes up on arms when on tummy"], "language": ["Coos", "Responds to sounds"], "social": ["Social smile", "Recognises parent's face"], "cognitive": ["Tracks moving objects"]},
    "4":  {"motor": ["Rolls front to back", "Holds head steady", "Bears weight on legs"], "language": ["Babbles", "Laughs", "Squeals"], "social": ["Smiles spontaneously", "Enjoys playing with people"], "cognitive": ["Recognises familiar faces", "Reaches for objects"]},
    "6":  {"motor": ["Sits with support", "Rolls both ways", "Bears weight when standing"], "language": ["Babbles chains (babababa)", "Responds to name"], "social": ["Knows familiar faces", "Likes mirror"], "cognitive": ["Curious, tries to reach things", "Transfers objects between hands"]},
    "9":  {"motor": ["Sits without support", "Crawls", "Pulls to stand"], "language": ["Says mama/dada (non-specifically)", "Understands 'no'"], "social": ["Stranger anxiety", "Waves bye"], "cognitive": ["Object permanence beginning", "Bangs objects together"]},
    "12": {"motor": ["Walks with support or alone", "Picks up with pincer grasp"], "language": ["1-2 meaningful words", "Understands simple commands"], "social": ["Shy with strangers", "Shows preferences"], "cognitive": ["Points to objects", "Follows simple one-step commands"]},
    "18": {"motor": ["Walks well alone", "Climbs stairs with help", "Throws ball overhand"], "language": ["10-20 words", "Points to body parts", "Names familiar objects"], "social": ["Parallel play", "Temper tantrums begin"], "cognitive": ["Simple pretend play", "Identifies objects by function"]},
    "24": {"motor": ["Runs", "Kicks ball", "Jumps with both feet"], "language": ["50+ words", "2-word phrases", "Strangers understand ~50%"], "social": ["Plays alongside others", "Shows ownership (mine!)"], "cognitive": ["Simple problem solving", "Matches shapes and colours"]},
    "36": {"motor": ["Climbs well", "Pedals tricycle", "Draws a circle"], "language": ["3-word sentences", "Asks questions (what, why)", "Understood by strangers most of the time"], "social": ["Cooperative play", "Takes turns sometimes"], "cognitive": ["Understands same/different", "Counts 2-3 objects"]},
}

PCOS_RISK_FACTORS = [
    {"question": "Do you have irregular periods (>35 days apart or fewer than 9 periods/year)?", "weight": 20},
    {"question": "Do you have excess facial or body hair (hirsutism)?", "weight": 15},
    {"question": "Do you have severe acne that doesn't respond to treatment?", "weight": 10},
    {"question": "Are you overweight or have you gained weight primarily around your abdomen?", "weight": 15},
    {"question": "Do you have thinning hair or hair loss on the scalp?", "weight": 10},
    {"question": "Has a close female relative (mother/sister) been diagnosed with PCOS?", "weight": 15},
    {"question": "Have you been told you have high testosterone or androgen levels?", "weight": 20},
    {"question": "Do you have dark skin patches on neck, armpits, or groin (acanthosis nigricans)?", "weight": 10},
    {"question": "Do you have difficulty getting pregnant (if trying)?", "weight": 15},
    {"question": "Do you frequently experience mood swings or depression?", "weight": 5},
    {"question": "Do you have pelvic pain or pain during periods?", "weight": 5},
    {"question": "Have you had ultrasound showing multiple cysts on ovaries?", "weight": 30},
]

GOVT_SCHEMES_WOMEN = [
    {"name": "Janani Suraksha Yojana (JSY)", "benefit": "Cash incentive ₹600-1400 for institutional delivery", "eligibility": "Pregnant women in low-income families", "helpline": "104"},
    {"name": "Pradhan Mantri Matru Vandana Yojana (PMMVY)", "benefit": "₹5000 maternity benefit for first live birth", "eligibility": "Pregnant and lactating women (first child only)", "helpline": "011-23381611"},
    {"name": "Poshan Abhiyan (National Nutrition Mission)", "benefit": "Free iron-folic acid, counselling, nutrition tracking", "eligibility": "Pregnant, lactating women, children 0-6 years", "helpline": "1800-180-1104"},
    {"name": "Janani Shishu Suraksha Karyakram (JSSK)", "benefit": "Free delivery, C-section, medicines, diagnostics, referral transport", "eligibility": "All pregnant women at government health facilities", "helpline": "104"},
    {"name": "National Programme for Family Planning", "benefit": "Free contraceptives, sterilisation services", "eligibility": "All married couples", "helpline": "1800-11-6555"},
    {"name": "Beti Bachao Beti Padhao", "benefit": "Girl child welfare — education support, awareness", "eligibility": "Girl children — especially in low sex ratio districts", "helpline": "1800-180-1104"},
    {"name": "Kishori Shakti Yojana", "benefit": "Health, nutrition, and life skills for adolescent girls 11-18 years", "eligibility": "Adolescent girls enrolled in Anganwadi programme", "helpline": "011-23381611"},
    {"name": "PM Surakshit Matritva Abhiyan", "benefit": "Free ANC on 9th of every month at government facilities", "eligibility": "All pregnant women in second/third trimester", "helpline": "104"},
]


class PregnancyTracker:
    def edd(self, lmp_date: str) -> str:
        """Expected delivery date using Naegele's rule."""
        try:
            lmp = datetime.strptime(lmp_date, "%Y-%m-%d")
            edd = lmp + timedelta(days=280)
            return edd.strftime("%d %B %Y")
        except Exception:
            return "Invalid date format. Use YYYY-MM-DD"

    def get_week_info(self, lmp_date: str) -> Dict:
        try:
            lmp     = datetime.strptime(lmp_date, "%Y-%m-%d")
            today   = datetime.now()
            days    = (today - lmp).days
            week    = max(1, min(days // 7, 40))
            trimester = "First (1-12)" if week <= 12 else ("Second (13-27)" if week <= 27 else "Third (28-40)")
            info    = PREGNANCY_WEEKS.get(week, PREGNANCY_WEEKS[40])
            return {"current_week": week, "days_pregnant": days, "trimester": trimester,
                    "edd": self.edd(lmp_date), **info}
        except Exception:
            return {"error": "Invalid date. Use YYYY-MM-DD format."}

    def nutrition_plan(self, week: int) -> Dict:
        if week <= 12:
            return {"trimester": "First", "extra_calories": 0,
                    "priority_nutrients": ["Folic acid 600mcg", "Iron 27mg", "Vitamin B12"],
                    "foods_to_focus": ["Spinach", "Dal", "Eggs", "Milk", "Citrus fruits"],
                    "supplements": ["Folic Acid 5mg", "Iron 100mg + Folic 500mcg", "Calcium 500mg"],
                    "avoid": ["Alcohol", "Raw meat/fish", "Unpasteurised dairy", "Excess caffeine"]}
        elif week <= 27:
            return {"trimester": "Second", "extra_calories": 340,
                    "priority_nutrients": ["Calcium 1200mg", "Iron 27mg", "DHA 200mg", "Vitamin D"],
                    "foods_to_focus": ["Milk", "Curd", "Fish (cooked)", "Drumstick", "Banana", "Dates"],
                    "supplements": ["Calcium 1g", "Iron 100mg", "DHA supplement", "Vitamin D 1000 IU"],
                    "avoid": ["Raw papaya (excess)", "Alcohol", "High mercury fish"]}
        else:
            return {"trimester": "Third", "extra_calories": 450,
                    "priority_nutrients": ["Calcium 1200mg", "Iron 27mg", "Protein 78g/day", "DHA"],
                    "foods_to_focus": ["High protein: eggs, dal, paneer", "Calcium: milk, sesame", "Oats", "Walnuts"],
                    "supplements": ["Continue all prenatal supplements", "Vitamin K (for delivery)", "Magnesium for cramps"],
                    "avoid": ["Excess salt (pre-eclampsia risk)", "Processed foods"]}

    def test_schedule(self, lmp_date: str) -> List[Dict]:
        try:
            lmp = datetime.strptime(lmp_date, "%Y-%m-%d")
            tests = [
                {"week": 8,  "test": "First ANC: BP, weight, CBC, Blood group/Rh, FBS, TSH, Rubella/VDRL, Hep B, HIV", "date": (lmp + timedelta(weeks=8)).strftime("%d %b %Y")},
                {"week": 11, "test": "NT Scan + Double Marker (Downs screening)", "date": (lmp + timedelta(weeks=11)).strftime("%d %b %Y")},
                {"week": 16, "test": "Quadruple marker / AFP + anomaly scan booking", "date": (lmp + timedelta(weeks=16)).strftime("%d %b %Y")},
                {"week": 20, "test": "Anomaly Scan (TIFFA) — checks all organs", "date": (lmp + timedelta(weeks=20)).strftime("%d %b %Y")},
                {"week": 24, "test": "Glucose Tolerance Test (GDM screen) + CBC", "date": (lmp + timedelta(weeks=24)).strftime("%d %b %Y")},
                {"week": 28, "test": "28-week ANC: BP, urine, fundal height, fetal movement", "date": (lmp + timedelta(weeks=28)).strftime("%d %b %Y")},
                {"week": 32, "test": "Growth scan — fetal weight and position", "date": (lmp + timedelta(weeks=32)).strftime("%d %b %Y")},
                {"week": 36, "test": "GBS swab + check fetal position + NST begins", "date": (lmp + timedelta(weeks=36)).strftime("%d %b %Y")},
                {"week": 38, "test": "Weekly check: BP, urine, cervical assessment", "date": (lmp + timedelta(weeks=38)).strftime("%d %b %Y")},
            ]
            return tests
        except Exception:
            return []


class VaccineScheduleTracker:
    def get_due_vaccines(self, birth_date: str) -> List[Dict]:
        try:
            bd     = datetime.strptime(birth_date, "%Y-%m-%d")
            today  = datetime.now()
            age_days = (today - bd).days
            age_weeks = age_days // 7
            due = []
            schedule_weeks = {"At Birth": 0, "6 Weeks": 6, "10 Weeks": 10, "14 Weeks": 14,
                              "9 Months": 39, "12 Months": 52, "15 Months": 65, "16-18 Months": 70,
                              "2 Years": 104, "4-6 Years": 260, "10 Years": 520, "16 Years": 832}
            for label, week in schedule_weeks.items():
                if age_weeks >= week:
                    vaccines = VACCINE_SCHEDULE.get(label, [])
                    if vaccines:
                        due.append({"age": label, "vaccines": [v["vaccine"] for v in vaccines],
                                   "status": "Due" if age_weeks == week else "Past due" if age_weeks > week + 4 else "Recent"})
            return due
        except Exception:
            return []

    def full_schedule(self, birth_date: str):
        rows = []
        for age_label, vaccines in VACCINE_SCHEDULE.items():
            for v in vaccines:
                rows.append({"age": age_label, "vaccine": v["vaccine"],
                             "disease_prevented": v["disease"], "route": v["route"]})
        try:
            import pandas as pd
            return pd.DataFrame(rows)
        except ImportError:
            return rows


class ChildGrowthChart:
    WHO_MEDIAN = {
        "boy":  {0:3.3,3:6.0,6:7.9,9:9.2,12:10.2,18:11.5,24:12.5,36:14.5},
        "girl": {0:3.2,3:5.6,6:7.3,9:8.6,12:9.6,18:10.9,24:12.0,36:14.0},
    }

    def _nearest(self, age_m: int, gender: str) -> float:
        table = self.WHO_MEDIAN.get(gender.lower()[:3], self.WHO_MEDIAN["boy"])
        ages  = sorted(table.keys())
        n     = min(ages, key=lambda a: abs(a - age_m))
        return table[n]

    def assess(self, age_months: int, weight_kg: float, height_cm: float, gender: str) -> Dict:
        median_w = self._nearest(age_months, gender)
        z_weight = round((weight_kg - median_w) / (median_w * 0.12), 2)
        median_h = 50 + age_months * 1.75
        z_height = round((height_cm - median_h) / 3.0, 2)
        bmi_val  = round(weight_kg / (height_cm / 100) ** 2, 1)

        w_status = "Normal" if -2 <= z_weight <= 2 else ("Underweight" if z_weight < -2 else "Overweight")
        h_status = "Normal" if z_height >= -2 else "Stunted"
        bmi_st   = "Normal" if 14 <= bmi_val <= 18 else ("Low" if bmi_val < 14 else "High")

        return {"weight_status": w_status, "height_status": h_status, "bmi_status": bmi_st,
                "z_score_weight": z_weight, "z_score_height": z_height, "bmi": bmi_val,
                "recommendation": "Regular growth monitoring at anganwadi/PHC" if w_status == "Normal" else
                                   "Consult doctor and increase calorie-protein intake"}


class PCOSRiskScorer:
    def score(self, answers: List[int]) -> Dict:
        total = sum(a * PCOS_RISK_FACTORS[i]["weight"] for i, a in enumerate(answers) if i < len(PCOS_RISK_FACTORS))
        max_score = sum(f["weight"] for f in PCOS_RISK_FACTORS)
        pct = round(total / max_score * 100, 1)
        if pct >= 60:
            level = "High"
        elif pct >= 35:
            level = "Moderate"
        else:
            level = "Low"
        flags = [PCOS_RISK_FACTORS[i]["question"] for i, a in enumerate(answers) if a == 1 and i < len(PCOS_RISK_FACTORS)]
        recs  = ["Consult gynaecologist" if level == "High" else "Monitor symptoms"]
        if level == "High":
            recs += ["Hormone panel: FSH, LH, Testosterone, AMH", "Pelvic ultrasound",
                     "Fasting glucose + insulin", "Exercise 150 min/week", "Reduce refined carbohydrates"]
        return {"risk_level": level, "score": pct, "flags": flags[:5], "recommendations": recs, "see_doctor": level != "Low"}


class AnaemiaDetector:
    RISK_SYMPTOMS = ["fatigue", "weakness", "pale skin", "breathlessness", "dizziness", "cold hands",
                     "palpitations", "headache", "brittle nails", "craving non-food items (pica)", "yellow skin"]

    def assess(self, symptoms: List[str], gender: str, age: int, diet_type: str = "vegetarian") -> Dict:
        sym_low = [s.lower() for s in symptoms]
        matched = [s for s in self.RISK_SYMPTOMS if any(s in x for x in sym_low)]
        prob_score = len(matched) * 10
        if gender.lower() == "female":       prob_score += 20
        if age < 18 or age > 65:             prob_score += 10
        if diet_type in ["vegetarian","vegan"]: prob_score += 15

        prob = "High" if prob_score >= 40 else ("Moderate" if prob_score >= 20 else "Low")
        factors = []
        if gender.lower() == "female":       factors.append("Female (higher iron loss)")
        if diet_type == "vegetarian":        factors.append("Vegetarian diet (lower iron bioavailability)")
        if len(matched) >= 4:                factors.append(f"{len(matched)} anaemia symptoms present")

        return {
            "probability": prob,
            "symptoms_matched": matched,
            "risk_factors": factors,
            "recommended_tests": ["Complete Blood Count (CBC)", "Serum Ferritin", "Serum Iron + TIBC",
                                   "Peripheral Blood Smear", "Vitamin B12 and Folate levels"],
            "diet_changes": ["Increase iron: drumstick leaves, spinach, dates, jaggery",
                             "Eat Vitamin C with iron-rich foods",
                             "Avoid tea/coffee 1 hour before/after meals",
                             "Cook in iron vessels"],
        }
