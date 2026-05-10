"""
BharatCare AI Pro · Health Calculators v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Medical calculators collection using Indian-adjusted norms.
Author: Deol Allwyn Samuel J B · VLSI · CIT · Afynix Digital
"""

import math
from typing import Dict, List, Tuple


class BMICalculator:
    # India-adjusted WHO thresholds (lower than Western)
    CATEGORIES = [
        (0,    18.5, "Underweight",    "#3b82f6"),
        (18.5, 23.0, "Normal Weight",  "#22c55e"),
        (23.0, 27.5, "Overweight",     "#f59e0b"),
        (27.5, 32.5, "Obese Class I",  "#f97316"),
        (32.5, 999,  "Obese Class II+","#ef4444"),
    ]

    def calculate(self, weight_kg: float, height_cm: float) -> Dict:
        h_m  = height_cm / 100
        bmi  = round(weight_kg / (h_m ** 2), 1)
        cat, color = "Unknown", "#6b7280"
        for lo, hi, label, clr in self.CATEGORIES:
            if lo <= bmi < hi:
                cat, color = label, clr
                break
        low_w  = round(18.5 * h_m ** 2, 1)
        high_w = round(22.9 * h_m ** 2, 1)
        return {
            "bmi": bmi, "category": cat, "color": color,
            "healthy_weight_range": (low_w, high_w),
            "india_adjusted": True,
            "note": "India uses BMI ≥23 as overweight (vs ≥25 globally)",
        }

    def category_color(self, bmi: float) -> str:
        for lo, hi, _, clr in self.CATEGORIES:
            if lo <= bmi < hi:
                return clr
        return "#6b7280"


class BMRCalculator:
    def mifflin_st_jeor(self, weight: float, height: float, age: int, gender: str) -> float:
        bmr = 10 * weight + 6.25 * height - 5 * age
        return round(bmr + 5 if gender.lower() == "male" else bmr - 161, 1)

    def harris_benedict(self, weight: float, height: float, age: int, gender: str) -> float:
        if gender.lower() == "male":
            return round(88.362 + 13.397 * weight + 4.799 * height - 5.677 * age, 1)
        return round(447.593 + 9.247 * weight + 3.098 * height - 4.330 * age, 1)

    def tdee(self, bmr: float, activity: str) -> float:
        factors = {
            "sedentary":   1.2,
            "light":       1.375,
            "moderate":    1.55,
            "active":      1.725,
            "very_active": 1.9,
        }
        return round(bmr * factors.get(activity, 1.2), 0)


class BloodPressureAnalyzer:
    CATEGORIES = [
        (0,   120, 0,  80, "Normal",              "#22c55e", "Maintain healthy lifestyle"),
        (120, 130, 0,  80, "Elevated",             "#84cc16", "Lifestyle changes recommended — reduce salt, exercise"),
        (130, 140, 80, 90, "Stage 1 Hypertension", "#f59e0b", "See doctor — consider medication"),
        (140, 180, 90,120, "Stage 2 Hypertension", "#f97316", "Medication required — see doctor soon"),
        (180, 999,120,999, "Hypertensive Crisis",  "#ef4444", "EMERGENCY — go to hospital immediately"),
    ]

    def classify(self, systolic: int, diastolic: int) -> Dict:
        cat, color, rec = "Unknown", "#6b7280", "See a doctor"
        for s_lo, s_hi, d_lo, d_hi, label, clr, r in self.CATEGORIES:
            if s_lo <= systolic < s_hi or d_lo <= diastolic < d_hi:
                if systolic >= s_lo and diastolic >= d_lo:
                    cat, color, rec = label, clr, r
                    break
        # Simplified: use whichever category the systolic falls in
        for s_lo, s_hi, d_lo, d_hi, label, clr, r in self.CATEGORIES:
            if s_lo <= systolic < s_hi:
                cat, color, rec = label, clr, r
                break
        return {"category": cat, "color": color, "recommendation": rec,
                "systolic": systolic, "diastolic": diastolic}

    def pulse_pressure(self, systolic: int, diastolic: int) -> Dict:
        pp = systolic - diastolic
        status = "Normal (30-40)" if 30 <= pp <= 40 else ("Wide — cardiovascular risk" if pp > 60 else "Narrow")
        return {"pulse_pressure_mmhg": pp, "status": status}

    def map_pressure(self, systolic: int, diastolic: int) -> float:
        return round(diastolic + (systolic - diastolic) / 3, 1)


class DiabetesRiskScorer:
    def score(self, age: int, bmi: float, family_history: bool,
              fasting_glucose: float = 0, hba1c: float = 0,
              physical_activity: str = "moderate", diet_type: str = "mixed") -> Dict:
        s = 0
        if age >= 45: s += 20
        elif age >= 35: s += 10
        if bmi >= 27.5: s += 20
        elif bmi >= 23: s += 10
        if family_history: s += 20
        if fasting_glucose >= 126: s += 30
        elif fasting_glucose >= 100: s += 15
        if hba1c >= 6.5: s += 30
        elif hba1c >= 5.7: s += 15
        if physical_activity == "sedentary": s += 10
        if diet_type in ["high_sugar", "processed"]: s += 10

        if s >= 70:
            level, prob = "High", round(min(s / 100, 0.95), 2)
        elif s >= 40:
            level, prob = "Moderate", round(s / 150, 2)
        else:
            level, prob = "Low", round(s / 200, 2)

        recs = ["Monitor blood sugar annually"]
        if s >= 40: recs.append("150 min/week exercise")
        if s >= 40: recs.append("Low GI diet — millets, brown rice")
        if bmi >= 23: recs.append("Lose 5-7% body weight")
        if fasting_glucose >= 100: recs.append("Repeat FBS in 3 months")

        return {"risk_score": s, "risk_level": level, "probability": prob, "recommendations": recs}


class HeartRiskCalculator:
    def framingham_score(self, age: int, gender: str, total_cholesterol: float,
                         hdl: float, systolic: int, smoker: bool,
                         diabetic: bool, on_bp_meds: bool) -> Dict:
        # Simplified Framingham 10-year CVD risk
        score = 0
        if gender.lower() == "male":
            score += max(0, (age - 30) * 1.5)
            score += max(0, (total_cholesterol - 160) * 0.1)
            score -= max(0, (hdl - 40) * 0.5)
            score += max(0, (systolic - 110) * 0.2)
        else:
            score += max(0, (age - 35) * 1.3)
            score += max(0, (total_cholesterol - 160) * 0.08)
            score -= max(0, (hdl - 35) * 0.4)
            score += max(0, (systolic - 110) * 0.18)
        if smoker:     score += 8
        if diabetic:   score += 6
        if on_bp_meds: score += 3

        risk_pct = round(min(max(score * 0.8, 1), 40), 1)
        if risk_pct >= 20:
            cat = "High (>20%) — Statin + lifestyle intervention"
        elif risk_pct >= 10:
            cat = "Moderate (10-20%) — Lifestyle changes + consider statin"
        else:
            cat = "Low (<10%) — Lifestyle maintenance"

        return {"10yr_risk_pct": risk_pct, "risk_category": cat}

    def qrisk_simplified(self, age: int, gender: str, bmi: float,
                         smoker: bool, diabetic: bool,
                         family_history: bool, systolic: int) -> float:
        score = (age - 25) * 0.5
        if bmi >= 30:      score += 5
        if smoker:         score += 7
        if diabetic:       score += 8
        if family_history: score += 5
        score += max(0, (systolic - 120) * 0.1)
        if gender.lower() == "female": score *= 0.85
        return round(min(max(score, 1), 45), 1)


class ChildGrowthCalculator:
    # Simplified WHO median and SD values (weight-for-age, kg)
    WHO_WFA_BOYS  = {0: (3.3, 0.45), 3: (6.0, 0.7), 6: (7.9, 0.8), 12: (10.2, 1.0), 24: (12.5, 1.2), 36: (14.5, 1.4)}
    WHO_WFA_GIRLS = {0: (3.2, 0.44), 3: (5.6, 0.65), 6: (7.3, 0.75), 12: (9.6, 0.95), 24: (12.0, 1.15), 36: (14.0, 1.35)}

    def _nearest_age(self, age_months: int, gender: str) -> Tuple[float, float]:
        table = self.WHO_WFA_BOYS if gender.lower() == "male" else self.WHO_WFA_GIRLS
        ages  = sorted(table.keys())
        nearest = min(ages, key=lambda a: abs(a - age_months))
        return table[nearest]

    def wfa_zscore(self, weight_kg: float, age_months: int, gender: str) -> float:
        median, sd = self._nearest_age(age_months, gender)
        return round((weight_kg - median) / sd, 2)

    def hfa_zscore(self, height_cm: float, age_months: int, gender: str) -> float:
        # Simplified median heights
        med = 50 + age_months * 1.8 if gender.lower() == "male" else 49 + age_months * 1.75
        sd  = 2.5
        return round((height_cm - med) / sd, 2)

    def classify_nutrition(self, wfa_z: float, hfa_z: float) -> str:
        if wfa_z < -3 or hfa_z < -3:
            return "Severely Malnourished"
        if wfa_z < -2:
            return "Underweight"
        if hfa_z < -2:
            return "Stunted"
        if wfa_z > 2:
            return "Overweight"
        return "Normal"


class CaloricNeedsCalculator:
    def pregnancy(self, trimester: int, pre_pregnancy_bmi: float) -> Dict:
        extras = {1: 0, 2: 340, 3: 450}
        base   = 1800 if pre_pregnancy_bmi < 18.5 else 1600 if pre_pregnancy_bmi < 25 else 1500
        total  = base + extras.get(trimester, 0)
        return {
            "extra_calories": extras.get(trimester, 0),
            "total_calories": total,
            "protein_g": 71,
            "folate_mcg": 600,
            "iron_mg": 27,
            "calcium_mg": 1000,
        }

    def breastfeeding(self, age_infant_months: int) -> Dict:
        extra = 500 if age_infant_months <= 6 else 400
        return {"extra_calories": extra, "total_calories": 1800 + extra, "protein_g": 71}

    def elderly(self, age: int, gender: str, activity: str) -> Dict:
        base = 2000 if gender.lower() == "male" else 1600
        if age >= 70: base -= 200
        mult = {"sedentary": 1.0, "light": 1.1, "moderate": 1.2}.get(activity, 1.0)
        return {
            "calories": round(base * mult),
            "protein_g": round(0.8 * 65),  # 0.8g/kg average
            "calcium_mg": 1200,
            "vitamin_d_iu": 800,
        }


class KidneyFunctionEstimator:
    def egfr_ckd_epi(self, creatinine: float, age: int, gender: str) -> Dict:
        k     = 0.7 if gender.lower() == "female" else 0.9
        alpha = -0.329 if gender.lower() == "female" else -0.411
        gender_factor = 1.018 if gender.lower() == "female" else 1.0
        ratio = creatinine / k
        if ratio < 1:
            egfr = 141 * (ratio ** alpha) * (0.993 ** age) * gender_factor
        else:
            egfr = 141 * (ratio ** -1.209) * (0.993 ** age) * gender_factor
        egfr = round(egfr, 1)

        if egfr >= 90:
            stage, desc = "G1 (Normal/High)", "Kidney function normal"
        elif egfr >= 60:
            stage, desc = "G2 (Mildly decreased)", "Mild reduction — monitor annually"
        elif egfr >= 45:
            stage, desc = "G3a (Mild-Moderate)", "See nephrologist — restrict NSAIDs"
        elif egfr >= 30:
            stage, desc = "G3b (Moderate-Severe)", "Specialist care — dose-adjust medications"
        elif egfr >= 15:
            stage, desc = "G4 (Severe)", "Prepare for dialysis planning"
        else:
            stage, desc = "G5 (Kidney Failure)", "Dialysis or transplant required"

        return {"egfr": egfr, "ckd_stage": stage, "description": desc}

    def dose_adjustment_needed(self, egfr: float) -> bool:
        return egfr < 60


class FeverAnalyzer:
    def classify(self, temp_celsius: float, age_years: float = 25) -> Dict:
        if temp_celsius < 37.2:
            sev, action, color = "Normal", "No fever", "#22c55e"
        elif temp_celsius < 38.0:
            sev, action, color = "Low-grade Fever", "Rest and fluids", "#84cc16"
        elif temp_celsius < 39.0:
            sev, action, color = "Moderate Fever", "Paracetamol + fluids + doctor if >2 days", "#f59e0b"
        elif temp_celsius < 40.0:
            sev, action, color = "High Fever", "Paracetamol, doctor visit needed", "#f97316"
        else:
            sev, action, color = "Very High Fever (Hyperpyrexia)", "EMERGENCY — go to hospital", "#ef4444"
        return {"severity": sev, "action": action, "color": color, "temp_c": temp_celsius,
                "temp_f": round(temp_celsius * 9/5 + 32, 1)}

    def child_fever_protocol(self, temp: float, age_months: int) -> Dict:
        urgent = (age_months < 3 and temp >= 38.0) or (age_months < 12 and temp >= 39.0) or temp >= 40.5
        steps  = ["Take temperature rectally for infants under 3 months",
                  "Give paracetamol as per weight (10-15 mg/kg)",
                  "Offer fluids frequently (breastmilk, ORS, water)",
                  "Sponge with lukewarm water",
                  "Remove excess clothing",
                  "Monitor every 30 minutes"]
        if urgent:
            steps.insert(0, "⚠️ SEEK EMERGENCY CARE IMMEDIATELY")
        return {"urgent": urgent, "steps": steps, "temp_c": temp, "age_months": age_months}


class WaterIntakeCalculator:
    def calculate(self, weight_kg: float, activity: str, climate: str,
                  health_conditions: List[str] = None) -> Dict:
        base = weight_kg * 35  # mL per day base
        if activity == "active":      base += 600
        elif activity == "very_active": base += 1000
        if climate == "hot":          base += 500
        elif climate == "very_hot":   base += 1000
        adjustments = []
        if health_conditions:
            if "kidney_stones" in health_conditions:
                base += 500
                adjustments.append("Increased for kidney stone prevention")
            if "heart_failure" in health_conditions:
                base = min(base, 1500)
                adjustments.append("Restricted to 1.5L for heart failure")
            if "fever" in health_conditions:
                base += 300
                adjustments.append("Extra 300mL for fever")
        liters = round(base / 1000, 1)
        glasses = round(liters / 0.25)
        return {"liters_per_day": liters, "ml_per_day": int(base),
                "glasses_250ml": glasses, "adjustments": adjustments}


def run_all_calculators_demo():
    print("=== BharatCare Health Calculators Demo ===")
    bmi = BMICalculator()
    print("BMI (70kg, 170cm):", bmi.calculate(70, 170))
    bmr = BMRCalculator()
    b   = bmr.mifflin_st_jeor(70, 170, 30, "male")
    print(f"BMR: {b} kcal | TDEE (moderate): {bmr.tdee(b, 'moderate')} kcal")
    bp  = BloodPressureAnalyzer()
    print("BP 135/85:", bp.classify(135, 85))
    fever = FeverAnalyzer()
    print("Fever 39.2°C:", fever.classify(39.2))
    water = WaterIntakeCalculator()
    print("Water (70kg, active, hot):", water.calculate(70, "active", "hot"))


if __name__ == "__main__":
    run_all_calculators_demo()
