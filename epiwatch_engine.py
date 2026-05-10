"""
BharatCare AI Pro · EpiWatch Engine v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Outbreak intelligence: risk scoring, forecasting, state heatmap.
Author: Deol Allwyn Samuel J B · VLSI · CIT · Afynix Digital
"""

import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

OUTBREAK_DISEASES = ["Dengue", "Malaria", "Cholera", "Typhoid", "COVID-19", "Influenza"]

INDIAN_STATES_POP: Dict[str, int] = {
    "Uttar Pradesh": 237882725, "Maharashtra": 123144223, "Bihar": 124799926,
    "West Bengal": 99609303, "Madhya Pradesh": 85358965, "Rajasthan": 81032689,
    "Tamil Nadu": 77841267, "Karnataka": 67562686, "Gujarat": 63872399,
    "Andhra Pradesh": 54374535, "Odisha": 46356334, "Telangana": 39362732,
    "Kerala": 35699443, "Jharkhand": 38593948, "Assam": 35607039,
    "Punjab": 30141373, "Chhattisgarh": 29436231, "Haryana": 28900667,
    "Delhi": 32941309, "Jammu & Kashmir": 13606320, "Uttarakhand": 11250858,
    "Himachal Pradesh": 7451955, "Tripura": 4169794, "Manipur": 3091545,
    "Meghalaya": 3366710, "Nagaland": 2249695, "Goa": 1586250,
    "Arunachal Pradesh": 1711947, "Mizoram": 1239244, "Sikkim": 690251,
    "Puducherry": 1413542, "Chandigarh": 1158473, "Andaman & Nicobar": 417035,
    "Ladakh": 289407, "Lakshadweep": 73183, "Dadra & Nagar Haveli": 586956,
    "Daman & Diu": 242911,
}

DISEASE_SEASONS: Dict[str, Dict] = {
    "Dengue":     {"peak_months": [7, 8, 9, 10, 11], "low_months": [1, 2, 3], "vector": "Aedes aegypti mosquito"},
    "Malaria":    {"peak_months": [7, 8, 9, 10], "low_months": [12, 1, 2, 3], "vector": "Anopheles mosquito"},
    "Cholera":    {"peak_months": [5, 6, 7, 8, 9], "low_months": [12, 1, 2], "vector": "Contaminated water"},
    "Typhoid":    {"peak_months": [4, 5, 6, 7, 8], "low_months": [11, 12, 1], "vector": "Contaminated food/water"},
    "COVID-19":   {"peak_months": [1, 2, 3, 11, 12], "low_months": [6, 7, 8], "vector": "Airborne respiratory droplets"},
    "Influenza":  {"peak_months": [1, 2, 11, 12], "low_months": [5, 6, 7], "vector": "Respiratory droplets"},
}

CLIMATE_ZONES: Dict[str, Dict] = {
    "Tropical Wet":           {"states": ["Kerala", "Goa", "Andaman & Nicobar", "Lakshadweep"], "disease_risk": {"Dengue": "High", "Malaria": "High", "Cholera": "Medium"}},
    "Tropical Wet-Dry":       {"states": ["Tamil Nadu", "Andhra Pradesh", "Telangana", "Karnataka", "Odisha"], "disease_risk": {"Dengue": "High", "Malaria": "Medium", "Typhoid": "Medium"}},
    "Arid":                   {"states": ["Rajasthan", "Gujarat"], "disease_risk": {"Typhoid": "Medium", "COVID-19": "Low"}},
    "Semi-Arid":              {"states": ["Madhya Pradesh", "Maharashtra", "Chhattisgarh"], "disease_risk": {"Malaria": "High", "Dengue": "Medium", "Typhoid": "High"}},
    "Humid Subtropical":      {"states": ["Delhi", "Uttar Pradesh", "Bihar", "West Bengal", "Punjab", "Haryana"], "disease_risk": {"Dengue": "High", "Typhoid": "High", "Cholera": "High", "Influenza": "Medium"}},
    "Highland":               {"states": ["Himachal Pradesh", "Uttarakhand", "Jammu & Kashmir", "Ladakh", "Sikkim"], "disease_risk": {"Influenza": "High", "Typhoid": "Low", "COVID-19": "Medium"}},
    "Northeastern Subtropical":{"states": ["Assam", "Meghalaya", "Manipur", "Nagaland", "Tripura", "Arunachal Pradesh", "Mizoram"], "disease_risk": {"Malaria": "High", "Dengue": "High", "Cholera": "Medium"}},
}

STATE_HEALTHCARE: Dict[str, Dict] = {
    "Kerala":            {"hospitals_per_lakh": 5.2, "doctors_per_lakh": 21, "vaccination_coverage": 0.92},
    "Tamil Nadu":        {"hospitals_per_lakh": 4.8, "doctors_per_lakh": 18, "vaccination_coverage": 0.90},
    "Delhi":             {"hospitals_per_lakh": 6.5, "doctors_per_lakh": 35, "vaccination_coverage": 0.88},
    "Goa":               {"hospitals_per_lakh": 5.0, "doctors_per_lakh": 22, "vaccination_coverage": 0.91},
    "Karnataka":         {"hospitals_per_lakh": 4.2, "doctors_per_lakh": 16, "vaccination_coverage": 0.85},
    "Maharashtra":       {"hospitals_per_lakh": 3.8, "doctors_per_lakh": 15, "vaccination_coverage": 0.84},
    "Andhra Pradesh":    {"hospitals_per_lakh": 3.5, "doctors_per_lakh": 13, "vaccination_coverage": 0.86},
    "Telangana":         {"hospitals_per_lakh": 3.6, "doctors_per_lakh": 14, "vaccination_coverage": 0.85},
    "Gujarat":           {"hospitals_per_lakh": 3.2, "doctors_per_lakh": 12, "vaccination_coverage": 0.83},
    "West Bengal":       {"hospitals_per_lakh": 3.0, "doctors_per_lakh": 11, "vaccination_coverage": 0.80},
    "Punjab":            {"hospitals_per_lakh": 3.5, "doctors_per_lakh": 14, "vaccination_coverage": 0.82},
    "Rajasthan":         {"hospitals_per_lakh": 2.8, "doctors_per_lakh": 9,  "vaccination_coverage": 0.78},
    "Madhya Pradesh":    {"hospitals_per_lakh": 2.4, "doctors_per_lakh": 7,  "vaccination_coverage": 0.72},
    "Uttar Pradesh":     {"hospitals_per_lakh": 1.8, "doctors_per_lakh": 6,  "vaccination_coverage": 0.68},
    "Bihar":             {"hospitals_per_lakh": 1.5, "doctors_per_lakh": 5,  "vaccination_coverage": 0.65},
    "Assam":             {"hospitals_per_lakh": 2.2, "doctors_per_lakh": 8,  "vaccination_coverage": 0.70},
    "Odisha":            {"hospitals_per_lakh": 2.5, "doctors_per_lakh": 8,  "vaccination_coverage": 0.73},
    "Jharkhand":         {"hospitals_per_lakh": 2.0, "doctors_per_lakh": 6,  "vaccination_coverage": 0.68},
    "Chhattisgarh":      {"hospitals_per_lakh": 2.1, "doctors_per_lakh": 6,  "vaccination_coverage": 0.70},
}

rng_epi = np.random.RandomState(42)


def generate_outbreak_history() -> "pd.DataFrame":
    records = []
    diseases = list(DISEASE_SEASONS.keys())
    states   = list(INDIAN_STATES_POP.keys())[:20]
    for year in [2022, 2023, 2024]:
        for month in range(1, 13):
            for disease in diseases[:6]:
                for state in states[:12]:
                    seasonal = 1.4 if month in DISEASE_SEASONS[disease]["peak_months"] else (
                               0.6 if month in DISEASE_SEASONS[disease]["low_months"] else 1.0)
                    pop_m = INDIAN_STATES_POP.get(state, 5000000) / 1_000_000
                    base_cases = int(pop_m * 10 * seasonal * rng_epi.uniform(0.5, 2.0))
                    deaths = int(base_cases * rng_epi.uniform(0.001, 0.03))
                    records.append({
                        "state": state, "disease": disease, "year": year, "month": month,
                        "cases": base_cases, "deaths": deaths,
                        "case_fatality_rate": round(deaths / max(base_cases, 1) * 100, 2),
                        "response_time_days": rng_epi.randint(2, 14),
                        "containment_status": rng_epi.choice(["Contained", "Active", "Monitoring"]),
                        "climate_factor": round(seasonal, 2),
                        "vaccination_coverage": round(rng_epi.uniform(0.55, 0.92), 2),
                    })
    if HAS_PANDAS:
        return pd.DataFrame(records)
    return records


class RiskScorer:
    WEIGHTS = {"seasonal": 0.30, "vaccination_gap": 0.25, "healthcare_capacity": 0.20,
                "population_density": 0.15, "sanitation": 0.10}

    def seasonal_multiplier(self, disease: str, month: int) -> float:
        info = DISEASE_SEASONS.get(disease, {})
        if month in info.get("peak_months", []):    return 1.5
        if month in info.get("low_months", []):     return 0.5
        return 1.0

    def score_state(self, state: str, disease: str, month: int = None) -> Dict:
        month = month or datetime.now().month
        sm    = self.seasonal_multiplier(disease, month)
        hc    = STATE_HEALTHCARE.get(state, {"hospitals_per_lakh": 2.5, "vaccination_coverage": 0.75})
        vax   = hc["vaccination_coverage"]
        hosp  = hc["hospitals_per_lakh"]
        pop   = INDIAN_STATES_POP.get(state, 5000000)

        # Normalise
        vax_gap  = (1 - vax) * 40       # 0-40 pts
        hc_gap   = max(0, (4 - hosp)) * 8  # 0-32 pts
        pop_risk = min(pop / 50_000_000 * 20, 20)  # 0-20 pts
        seasonal_pts = (sm - 0.5) * 20  # 0-20 pts
        risk_score = round(vax_gap + hc_gap + pop_risk + seasonal_pts, 1)
        risk_score = max(0, min(100, risk_score))

        if risk_score >= 65: risk_level, alert = "High", "RED ALERT"
        elif risk_score >= 40: risk_level, alert = "Moderate", "ORANGE"
        else: risk_level, alert = "Low", "GREEN"

        factors = [f"Seasonal multiplier: {sm}x",
                   f"Vaccination coverage: {round(vax*100,0)}%",
                   f"Hospitals per lakh: {hosp}"]
        return {"state": state, "disease": disease, "month": month,
                "risk_score": risk_score, "risk_level": risk_level, "alert_level": alert,
                "contributing_factors": factors}

    def score_all_states(self, disease: str, month: int = None):
        month = month or datetime.now().month
        rows  = [self.score_state(state, disease, month) for state in INDIAN_STATES_POP]
        if HAS_PANDAS:
            return pd.DataFrame(rows).sort_values("risk_score", ascending=False)
        return sorted(rows, key=lambda x: x["risk_score"], reverse=True)


class OutbreakPredictor:
    def __init__(self):
        self.model  = None
        self.scaler = None
        if HAS_SKLEARN:
            self._train()

    def _train(self):
        rng = np.random.RandomState(42)
        n   = 2000
        X   = np.column_stack([
            rng.randint(1, 13, n),                   # month
            rng.uniform(0.5, 0.95, n),               # vax
            rng.uniform(50, 5000, n),                # pop density
            rng.uniform(15, 42, n),                  # temp
            rng.uniform(0, 400, n),                  # rainfall
            rng.uniform(0.2, 0.95, n),               # sanitation
            rng.uniform(0.5, 8, n),                  # hosp beds
        ])
        risk = (1 - X[:, 1]) * 0.3 + (X[:, 2] / 5000) * 0.15 + \
               (1 - X[:, 6] / 8) * 0.2 + rng.uniform(0, 0.2, n)
        y = (risk > 0.4).astype(int)
        self.scaler = StandardScaler()
        X_s = self.scaler.fit_transform(X)
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_s, y)

    def predict(self, state: str, disease: str, month: int = None) -> Dict:
        month = month or datetime.now().month
        hc = STATE_HEALTHCARE.get(state, {"hospitals_per_lakh": 2.5, "vaccination_coverage": 0.75})
        sm = RiskScorer().seasonal_multiplier(disease, month)
        pop = INDIAN_STATES_POP.get(state, 5_000_000)

        if HAS_SKLEARN and self.model:
            X = np.array([[month, hc["vaccination_coverage"], pop / 1000,
                            28.0, 100 * sm, 0.65, hc["hospitals_per_lakh"]]])
            X_s  = self.scaler.transform(X)
            prob = float(self.model.predict_proba(X_s)[0][1])
        else:
            prob = float(RiskScorer().score_state(state, disease, month)["risk_score"]) / 100

        cases = int(pop / 100000 * prob * 15 * sm)
        sev   = "High" if prob > 0.65 else ("Moderate" if prob > 0.35 else "Low")
        return {"state": state, "disease": disease, "month": month,
                "outbreak_probability": round(prob, 3), "cases_estimate": cases,
                "severity": sev, "confidence": 0.82}

    def forecast_14day(self, state: str, disease: str):
        rows = []
        today = datetime.now()
        base  = self.predict(state, disease, today.month)["cases_estimate"]
        for i in range(14):
            d   = today + timedelta(days=i + 1)
            if d.weekday() >= 5: continue
            variation = rng_epi.uniform(0.85, 1.15)
            rows.append({"date": d.strftime("%Y-%m-%d"), "cases_forecast": max(0, int(base * variation)),
                          "lower": max(0, int(base * 0.7)), "upper": int(base * 1.3)})
            if len(rows) >= 10: break
        if HAS_PANDAS:
            return pd.DataFrame(rows)
        return rows


class VaccinationGapAnalyzer:
    VACCINE_TARGETS = {"Dengue": 0.5, "Malaria": 0.7, "COVID-19": 0.85, "Influenza": 0.60,
                        "Typhoid": 0.75, "Cholera": 0.65}

    def analyze(self, state: str) -> Dict:
        hc  = STATE_HEALTHCARE.get(state, {"vaccination_coverage": 0.70})
        cov = hc["vaccination_coverage"]
        pop = INDIAN_STATES_POP.get(state, 5000000)
        avg_target = 0.80
        gap = round(max(avg_target - cov, 0), 2)
        at_risk = int(pop * gap)
        return {"state": state, "coverage": round(cov * 100, 1), "gap_pct": round(gap * 100, 1),
                "at_risk_population": at_risk,
                "priority_action": "Mobile vaccination campaigns" if gap > 0.2 else "Routine immunisation strengthening"}

    def national_coverage_report(self):
        rows = [self.analyze(s) for s in list(INDIAN_STATES_POP.keys())[:20]]
        if HAS_PANDAS:
            return pd.DataFrame(rows).sort_values("coverage")
        return rows


class HospitalCapacityPredictor:
    def predict_demand(self, state: str, disease: str, cases: int) -> Dict:
        hc        = STATE_HEALTHCARE.get(state, {"hospitals_per_lakh": 2.5})
        pop       = INDIAN_STATES_POP.get(state, 5_000_000)
        beds_avail = int(pop / 100_000 * hc["hospitals_per_lakh"] * 10)
        beds_needed = int(cases * 0.15)  # ~15% need hospitalisation
        icu_needed  = int(cases * 0.02)
        overflow    = beds_needed > beds_avail * 0.8
        return {"state": state, "disease": disease, "cases": cases,
                "beds_needed": beds_needed, "beds_available": beds_avail,
                "icu_beds_needed": icu_needed, "overflow_risk": overflow,
                "recommendation": "Activate surge capacity" if overflow else "Current capacity adequate"}


class AlertGenerator:
    def generate_bulletin(self, month: int = None) -> Dict:
        month = month or datetime.now().month
        scorer = RiskScorer()
        predictor = OutbreakPredictor()
        high_risk = []
        disease_alerts = []
        for disease in OUTBREAK_DISEASES:
            scores_df = scorer.score_all_states(disease, month)
            if HAS_PANDAS:
                hr_states = scores_df[scores_df["risk_level"] == "High"]["state"].tolist()[:3]
            else:
                hr_states = [r["state"] for r in scores_df if r["risk_level"] == "High"][:3]
            if hr_states:
                high_risk.extend(hr_states)
                disease_alerts.append({"disease": disease, "high_risk_states": hr_states,
                                        "season": "Peak" if month in DISEASE_SEASONS[disease]["peak_months"] else "Normal"})
        prev_actions = ["Eliminate stagnant water in homes and surroundings",
                        "Ensure all children are up to date with immunisations",
                        "Use only boiled or purified water",
                        "Seek healthcare early at first signs of fever",
                        "Report cluster cases to nearest PHC immediately"]
        return {"month": month, "high_risk_states": list(set(high_risk))[:5],
                "disease_alerts": disease_alerts, "preventive_actions": prev_actions,
                "date": datetime.now().strftime("%d %B %Y")}

    def format_report(self, state: str) -> str:
        lines = [f"## EpiWatch Risk Report — {state}", f"Generated: {datetime.now().strftime('%d %B %Y')}", ""]
        for disease in OUTBREAK_DISEASES:
            r = RiskScorer().score_state(state, disease)
            lines.append(f"**{disease}**: {r['risk_level']} (Score: {r['risk_score']}/100) — {r['alert_level']}")
        return "\n".join(lines)


def get_current_risk_map():
    scorer = RiskScorer()
    month  = datetime.now().month
    rows   = []
    for state in INDIAN_STATES_POP:
        row = {"state": state}
        for disease in OUTBREAK_DISEASES[:4]:
            r = scorer.score_state(state, disease, month)
            row[f"{disease}_risk"] = r["risk_score"]
            row[f"{disease}_level"] = r["risk_level"]
        row["population"] = INDIAN_STATES_POP[state]
        rows.append(row)
    if HAS_PANDAS:
        return pd.DataFrame(rows)
    return rows
