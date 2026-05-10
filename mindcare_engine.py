"""
BharatCare AI Pro · MindCare Engine v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mental health intelligence: PHQ-9, GAD-7, burnout, risk classification.
Author: Deol Allwyn Samuel J B · VLSI · CIT · Afynix Digital
"""

import re
import random
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer as VADER
    HAS_VADER = True
except ImportError:
    HAS_VADER = False

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False

# ── Official Questionnaires ───────────────────────────────────────────────────
PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things?",
    "Feeling down, depressed, or hopeless?",
    "Trouble falling or staying asleep, or sleeping too much?",
    "Feeling tired or having little energy?",
    "Poor appetite or overeating?",
    "Feeling bad about yourself — or that you are a failure or have let yourself or your family down?",
    "Trouble concentrating on things, such as reading the newspaper or watching television?",
    "Moving or speaking so slowly that other people could have noticed? Or being so fidgety or restless?",
    "Thoughts that you would be better off dead, or of hurting yourself in some way?",
]

GAD7_QUESTIONS = [
    "Feeling nervous, anxious, or on edge?",
    "Not being able to stop or control worrying?",
    "Worrying too much about different things?",
    "Trouble relaxing?",
    "Being so restless that it is hard to sit still?",
    "Becoming easily annoyed or irritable?",
    "Feeling afraid, as if something awful might happen?",
]

PHQ9_OPTIONS = ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]
GAD7_OPTIONS = ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]

STRESS_INDICATORS: Dict[str, int] = {
    "overwhelmed": 4, "burned out": 5, "exhausted": 4, "hopeless": 5, "worthless": 5,
    "cannot cope": 5, "falling apart": 5, "depressed": 4, "anxious": 3, "panicking": 4,
    "sleepless": 3, "insomnia": 3, "crying": 3, "irritable": 2, "stressed": 3,
    "worried": 2, "nervous": 2, "tense": 2, "angry": 2, "frustrated": 2,
    "sad": 3, "lonely": 3, "isolated": 3, "numb": 4, "empty": 4,
    "useless": 4, "failure": 4, "giving up": 5, "no hope": 5, "end it": 5,
    "not sleeping": 3, "no energy": 3, "no motivation": 3, "can't focus": 2,
    "panic attack": 5, "self harm": 5, "kill myself": 5, "want to die": 5,
    "pointless": 3, "burden": 4, "lost": 3, "confused": 2, "shaking": 3,
    "fear": 2, "dread": 3, "hyperventilating": 4, "dissociation": 4,
    "trauma": 4, "flashback": 4, "nightmares": 3,
}

POSITIVE_INDICATORS: Dict[str, int] = {
    "happy": 4, "grateful": 4, "hopeful": 4, "excited": 3, "calm": 3,
    "peaceful": 4, "content": 4, "motivated": 3, "energetic": 3,
    "positive": 3, "good day": 3, "feeling better": 4, "improving": 4,
    "supported": 3, "loved": 4, "confident": 3, "proud": 3,
    "accomplished": 3, "relaxed": 3, "optimistic": 4,
    "productive": 3, "focused": 3, "enjoying": 3, "laughed": 3,
    "grateful": 4, "thankful": 3, "blessed": 3, "connected": 3,
    "healing": 4, "growing": 3, "mindful": 3,
}

BREATHING_EXERCISES = [
    {"name": "4-7-8 Breathing", "technique": "Inhale 4 counts → Hold 7 counts → Exhale 8 counts",
     "duration_minutes": 5, "description": "Activates parasympathetic nervous system. Best for acute anxiety.",
     "benefit": "Reduces anxiety, lowers heart rate"},
    {"name": "Box Breathing", "technique": "Inhale 4 → Hold 4 → Exhale 4 → Hold 4",
     "duration_minutes": 4, "description": "Used by US Navy SEALs for stress management. Equal four-count pattern.",
     "benefit": "Focus, stress reduction, emotional regulation"},
    {"name": "Diaphragmatic Breathing", "technique": "Breathe deeply into belly (not chest). Feel stomach rise and fall.",
     "duration_minutes": 10, "description": "Foundation of all meditation. Reduces cortisol levels.",
     "benefit": "Reduces stress hormones, improves sleep"},
    {"name": "Alternate Nostril (Nadi Shodhana)", "technique": "Close right nostril, inhale left → Close left, exhale right → Repeat",
     "duration_minutes": 8, "description": "Classical pranayama. Balances left-right brain hemispheres.",
     "benefit": "Mental clarity, reduces anxiety, blood pressure"},
    {"name": "Humming Bee Breath (Bhramari)", "technique": "Plug ears, close eyes, inhale deeply, exhale with humming sound",
     "duration_minutes": 6, "description": "Vibration stimulates vagus nerve for deep calm.",
     "benefit": "Immediate calm, reduces anger and frustration"},
]

THERAPY_TYPES: Dict[str, Dict] = {
    "CBT": {"description": "Cognitive Behavioural Therapy — changes negative thought patterns",
            "suitable_for": "Depression, anxiety, OCD, PTSD", "duration": "12-20 sessions", "cost_range_inr": "800-2500/session"},
    "DBT": {"description": "Dialectical Behaviour Therapy — emotion regulation skills",
            "suitable_for": "Borderline personality, self-harm, suicidal ideation", "duration": "6-12 months", "cost_range_inr": "1000-3000/session"},
    "Mindfulness-Based Therapy": {"description": "MBSR/MBCT — present-moment awareness",
            "suitable_for": "Stress, relapse prevention in depression", "duration": "8-week programme", "cost_range_inr": "500-1500/session"},
    "Psychodynamic Therapy": {"description": "Explores unconscious patterns and past experiences",
            "suitable_for": "Long-standing emotional issues, personality", "duration": "Open-ended", "cost_range_inr": "1000-3000/session"},
    "Counselling": {"description": "Talk therapy for life challenges",
            "suitable_for": "Grief, relationship issues, adjustment problems", "duration": "6-12 sessions", "cost_range_inr": "400-1200/session"},
    "Group Therapy": {"description": "Therapy in group setting with peers",
            "suitable_for": "Social anxiety, addiction, grief", "duration": "Ongoing", "cost_range_inr": "200-600/session"},
    "Online Therapy": {"description": "Teleconsultation with licensed therapist",
            "suitable_for": "All conditions — accessible from home", "duration": "Flexible", "cost_range_inr": "500-1500/session"},
    "Psychiatric Consultation": {"description": "Medical doctor for medication management",
            "suitable_for": "Severe depression, schizophrenia, bipolar, ADHD", "duration": "Ongoing", "cost_range_inr": "600-2000/session"},
}

CRISIS_HELPLINES = [
    {"name": "iCall (TISS)", "number": "9152987821", "hours": "Mon-Sat 8am-10pm", "speciality": "Free psychological counselling"},
    {"name": "Vandrevala Foundation", "number": "1860-2662-345", "hours": "24/7", "speciality": "Crisis intervention, all mental health issues"},
    {"name": "NIMHANS", "number": "080-46110007", "hours": "Mon-Sat 8am-8pm", "speciality": "Expert psychiatric help"},
    {"name": "Snehi", "number": "044-24640050", "hours": "8am-10pm", "speciality": "Emotional support, suicide prevention"},
    {"name": "iCall WhatsApp", "number": "9152987821", "hours": "Mon-Sat", "speciality": "Chat-based counselling"},
    {"name": "Fortis Stress Helpline", "number": "8376804102", "hours": "24/7", "speciality": "Acute stress and anxiety"},
    {"name": "Mann Talks", "number": "8686139139", "hours": "Mon-Sun 8am-10pm", "speciality": "Young adults, students"},
    {"name": "National Mental Health Helpline", "number": "1800-599-0019", "hours": "24/7", "speciality": "Government free helpline"},
]

WELLNESS_TIPS = [
    "Start each morning with 5 minutes of deep breathing before checking your phone.",
    "Write 3 things you are grateful for tonight — gratitude rewires the brain for positivity.",
    "Take a 10-minute walk outside today. Sunlight boosts serotonin naturally.",
    "Eat one balanced meal today — your gut produces 95% of your serotonin.",
    "Call someone you care about. Human connection is the strongest antidepressant.",
    "Screen time limit: put your phone down 1 hour before bed for better sleep.",
    "Drink a glass of water before each meal — dehydration causes mood drops.",
    "Name your emotion right now: naming feelings reduces their intensity by 50%.",
    "Set one small achievable goal today. Completing it builds confidence.",
    "Spend 5 minutes journaling your thoughts — it reduces anxiety significantly.",
    "Listen to music you love for 10 minutes — it releases dopamine immediately.",
    "Progressive muscle relaxation: tense and release each muscle group from feet up.",
    "Eat foods rich in omega-3: walnuts, flaxseeds, fish. They reduce inflammation in the brain.",
    "The 5-4-3-2-1 grounding technique: name 5 things you see, 4 you touch, 3 you hear.",
    "Social media detox for one evening this week — compare less, live more.",
    "Reduce caffeine after 2pm for better sleep quality.",
    "Add turmeric to your diet — curcumin has proven antidepressant properties.",
    "Exercise for 30 minutes — as effective as antidepressants for mild-moderate depression.",
    "Accept that you cannot control everything. Write down your worries and let them go.",
    "Cold water splash on face activates the dive reflex — instant calm.",
    "Spend time in nature. Even 20 minutes in a park reduces cortisol by 21%.",
    "Say 'no' to one obligation this week. Boundaries are self-care.",
    "Volunteer or help someone — acts of kindness elevate your own mood.",
    "Laugh intentionally — watch something funny. Laughter genuinely heals.",
    "Try Yoga Nidra (body scan meditation) for sleep — 20 min equals 4 hours rest.",
    "Celebrate small wins. Progress, not perfection.",
    "Practise self-compassion: speak to yourself as you would a dear friend.",
    "Limit news consumption to 15 min/day. Constant news triggers anxiety.",
    "Make your bed every morning. One completed task sets a positive tone.",
    "Sit in silence for 5 minutes. Stillness is medicine for the overstimulated mind.",
]

AFFIRMATIONS = [
    "I am enough exactly as I am right now.",
    "I choose peace over anxiety in this moment.",
    "Every storm runs out of rain. This too shall pass.",
    "I am stronger than my struggles.",
    "My mental health is worth protecting.",
    "I am healing, even when I cannot see it.",
    "I deserve rest, care, and compassion.",
    "Small steps forward are still forward.",
    "I am not my thoughts. I am the observer of my thoughts.",
    "I am worthy of love and belonging.",
    "Today I will be gentle with myself.",
    "I have survived every difficult day so far.",
    "My feelings are valid and temporary.",
    "I am capable of handling what comes my way.",
    "Asking for help is a sign of strength, not weakness.",
    "I am allowed to take up space in this world.",
    "My best is good enough.",
    "I release what I cannot control.",
    "I am building the life I deserve, one day at a time.",
    "Breathe. You are exactly where you need to be.",
]


class PHQ9Scorer:
    SEVERITY_MAP = [
        (0,  4,  "Minimal",           "No significant depression. Continue healthy habits."),
        (5,  9,  "Mild",              "Mild depression. Monitor symptoms. Lifestyle changes recommended."),
        (10, 14, "Moderate",          "Moderate depression. Professional consultation recommended."),
        (15, 19, "Moderately Severe", "Significant depression. Psychiatrist/therapist needed soon."),
        (20, 27, "Severe",            "Severe depression. Urgent professional help required."),
    ]

    def score(self, answers: List[int]) -> Dict:
        total = sum(answers)
        sev, interp = "Unknown", "Consult a professional"
        for lo, hi, label, interpretation in self.SEVERITY_MAP:
            if lo <= total <= hi:
                sev, interp = label, interpretation
                break
        q9 = answers[8] if len(answers) == 9 else 0
        suicidal_flag = q9 >= 1
        recs = [interp]
        if suicidal_flag:
            recs.insert(0, "⚠️ Question 9 flagged — seek immediate professional support")
        if total >= 10:
            recs.append("Consider scheduling appointment with psychiatrist or therapist")
        return {
            "total": total,
            "severity": sev,
            "interpretation": interp,
            "recommendation": " | ".join(recs),
            "suicidal_ideation_flag": suicidal_flag,
            "max_score": 27,
        }


class GAD7Scorer:
    SEVERITY_MAP = [
        (0,  4,  "Minimal",  "Minimal anxiety. Self-care and monitoring sufficient."),
        (5,  9,  "Mild",     "Mild anxiety. Try breathing exercises and lifestyle changes."),
        (10, 14, "Moderate", "Moderate anxiety. Professional help recommended."),
        (15, 21, "Severe",   "Severe anxiety. Urgent mental health support needed."),
    ]

    def score(self, answers: List[int]) -> Dict:
        total = sum(answers)
        sev, interp = "Unknown", "Consult a professional"
        for lo, hi, label, interpretation in self.SEVERITY_MAP:
            if lo <= total <= hi:
                sev, interp = label, interpretation
                break
        return {"total": total, "severity": sev, "interpretation": interp, "max_score": 21}


class BurnoutDetector:
    BURNOUT_QUESTIONS = [
        "I feel emotionally drained from my work.",
        "I feel used up at the end of the workday.",
        "I feel fatigued when I face another day at work.",
        "I feel burned out from my work.",
        "I feel frustrated by my job.",
        "I feel I am working too hard in my job.",
        "I feel like I am at the end of my rope.",
        "Working with people all day is a strain for me.",
        "I feel like I do not care about what happens to people at work.",
        "I have accomplished many worthwhile things in this job. (Reverse scored)",
    ]

    def detect(self, answers: List[int], work_hours: int = 8, sleep_hours: float = 7.0) -> Dict:
        raw_score = sum(answers[:9]) - answers[9] if len(answers) == 10 else sum(answers)
        if work_hours > 10: raw_score += 10
        if sleep_hours < 6: raw_score += 10

        if raw_score >= 40:
            level = "Severe"
        elif raw_score >= 25:
            level = "High"
        elif raw_score >= 15:
            level = "Moderate"
        else:
            level = "Low"

        factors = []
        if work_hours > 10:   factors.append(f"Long work hours ({work_hours}h/day)")
        if sleep_hours < 6:   factors.append(f"Sleep deprivation ({sleep_hours}h/night)")
        if answers[4] >= 3:   factors.append("Job frustration")
        if answers[6] >= 3:   factors.append("Emotional exhaustion")

        recs = ["Take short breaks every 90 minutes", "Set clear work-life boundaries",
                "Delegate tasks where possible", "Exercise 3x per week"]
        if level in ["High", "Severe"]:
            recs.insert(0, "Seek professional mental health support urgently")

        return {"burnout_level": level, "score": raw_score, "factors": factors, "recommendations": recs}


class SentimentAnalyzer:
    def analyze(self, text: str) -> Dict:
        if HAS_VADER:
            analyzer = VADER()
            vs = analyzer.polarity_scores(text)
            subj = 0.5
            if HAS_TEXTBLOB:
                blob = TextBlob(text)
                subj = blob.sentiment.subjectivity
            return {"compound": vs["compound"], "positive": vs["pos"],
                    "negative": vs["neg"], "neutral": vs["neu"], "subjectivity": subj}
        return self.fallback_analyze(text)

    def fallback_analyze(self, text: str) -> Dict:
        text_low = text.lower()
        pos_score = sum(v for k, v in POSITIVE_INDICATORS.items() if k in text_low)
        neg_score = sum(v for k, v in STRESS_INDICATORS.items() if k in text_low)
        total     = pos_score + neg_score + 1
        compound  = round((pos_score - neg_score) / total, 3)
        return {
            "compound": compound,
            "positive": round(pos_score / total, 3),
            "negative": round(neg_score / total, 3),
            "neutral":  round(1 - abs(compound), 3),
            "subjectivity": 0.6,
        }


class MoodTracker:
    def __init__(self):
        self.history: List[Dict] = []

    def add_entry(self, date: str, mood_score: int, notes: str = ""):
        self.history.append({"date": date, "score": mood_score, "notes": notes})

    def get_trend(self) -> Dict:
        if not self.history:
            return {"avg": 5.0, "trend": "No data", "best_day": "N/A", "worst_day": "N/A"}
        scores = [e["score"] for e in self.history]
        avg    = round(sum(scores) / len(scores), 1)
        best   = max(self.history, key=lambda x: x["score"])["date"]
        worst  = min(self.history, key=lambda x: x["score"])["date"]
        if len(scores) > 1:
            trend = "Improving" if scores[-1] > scores[0] else ("Declining" if scores[-1] < scores[0] else "Stable")
        else:
            trend = "Stable"
        return {"avg": avg, "trend": trend, "best_day": best, "worst_day": worst}

    def get_chart_data(self):
        try:
            import pandas as pd
            return pd.DataFrame(self.history) if self.history else pd.DataFrame(columns=["date", "score", "notes"])
        except ImportError:
            return self.history


class RiskClassifier:
    CRISIS_KEYWORDS = [
        "want to die", "kill myself", "suicide", "end my life", "self harm",
        "cut myself", "no reason to live", "better off dead", "give up on life",
        "end it all", "can't go on", "worthless to everyone", "jump",
    ]

    def classify(self, text: str, phq9_score: int = 0, gad7_score: int = 0) -> Dict:
        text_low = text.lower()
        flags    = [kw for kw in self.CRISIS_KEYWORDS if kw in text_low]

        neg_score = sum(v for k, v in STRESS_INDICATORS.items() if k in text_low)
        pos_score = sum(v for k, v in POSITIVE_INDICATORS.items() if k in text_low)
        net_score = neg_score - pos_score + phq9_score + gad7_score // 2

        immediate = bool(flags)
        if flags or net_score >= 50:
            risk_level, risk_score = "High", min(100, 60 + net_score)
        elif net_score >= 25 or phq9_score >= 10:
            risk_level, risk_score = "Moderate", min(59, 30 + net_score)
        elif net_score >= 10 or phq9_score >= 5:
            risk_level, risk_score = "Low", min(29, 15 + net_score)
        else:
            risk_level, risk_score = "Minimal", max(0, net_score)

        return {
            "risk_level":      risk_level,
            "risk_score":      risk_score,
            "flags":           flags,
            "immediate_action":immediate,
        }

    def suicide_risk_check(self, text: str) -> bool:
        text_low = text.lower()
        return any(kw in text_low for kw in self.CRISIS_KEYWORDS)


class TherapyRecommender:
    def recommend(self, phq9: int, gad7: int, burnout: str, risk: str) -> Dict:
        if risk == "High" or phq9 >= 15:
            primary   = "Psychiatric Consultation"
            secondary = "DBT"
            helplines = CRISIS_HELPLINES[:3]
            self_help = ["Call crisis helpline now", "Talk to a trusted person immediately"]
        elif phq9 >= 10 or gad7 >= 10:
            primary   = "CBT"
            secondary = "Mindfulness-Based Therapy"
            helplines = CRISIS_HELPLINES[:2]
            self_help = ["Daily breathing exercises", "Mood journaling", "Reduce alcohol/caffeine"]
        elif burnout in ["High", "Severe"]:
            primary   = "Counselling"
            secondary = "Mindfulness-Based Therapy"
            helplines = [CRISIS_HELPLINES[0]]
            self_help = ["Set work-life boundaries", "Take planned breaks", "Talk to manager about workload"]
        else:
            primary   = "Self-help (guided resources)"
            secondary = "Online Therapy (preventive)"
            helplines = []
            self_help = ["Daily wellness tips", "Breathing exercises", "Regular exercise", "Social connection"]

        return {
            "primary":    primary,
            "secondary":  secondary,
            "self_help":  self_help,
            "helplines":  helplines,
            "therapy_info": THERAPY_TYPES.get(primary, {}),
        }


def analyze_mental_health(text: str, phq9_answers: List[int],
                           gad7_answers: List[int]) -> Dict:
    """Main entry point for mental health analysis."""
    phq9_result = PHQ9Scorer().score(phq9_answers) if phq9_answers else {"total": 0, "severity": "Not assessed"}
    gad7_result = GAD7Scorer().score(gad7_answers) if gad7_answers else {"total": 0, "severity": "Not assessed"}
    sentiment   = SentimentAnalyzer().analyze(text)
    risk_result = RiskClassifier().classify(text, phq9_result.get("total", 0), gad7_result.get("total", 0))
    burnout_det = BurnoutDetector()
    therapy_rec = TherapyRecommender().recommend(
        phq9_result.get("total", 0), gad7_result.get("total", 0),
        "Low", risk_result["risk_level"]
    )
    tip  = random.choice(WELLNESS_TIPS)
    affm = random.choice(AFFIRMATIONS)

    return {
        "text":            text,
        "phq9":            phq9_result,
        "gad7":            gad7_result,
        "sentiment":       sentiment,
        "risk":            risk_result,
        "therapy":         therapy_rec,
        "daily_tip":       tip,
        "affirmation":     affm,
        "breathing_ex":    random.choice(BREATHING_EXERCISES),
        "crisis_helplines":CRISIS_HELPLINES[:3] if risk_result["risk_level"] in ["Moderate","High"] else [],
        "immediate_help":  risk_result["immediate_action"],
    }
