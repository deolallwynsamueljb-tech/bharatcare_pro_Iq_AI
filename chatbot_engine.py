"""
BharatCare AI Pro · Health Chatbot Engine v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pure Python NLP chatbot — no external API needed.
Author: Deol Allwyn Samuel J B · VLSI · CIT · Afynix Digital
"""

import re
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

MEDICAL_FAQ: Dict[str, str] = {
    "What is dengue fever?": "Dengue is a viral infection spread by Aedes mosquitoes. Symptoms include high fever, severe headache, eye pain, joint and muscle pain, rash, and fatigue. There is no specific antiviral — treatment is supportive (fluids, paracetamol, rest). Avoid NSAIDs like ibuprofen. See a doctor immediately.",
    "How do I know if I have dengue?": "Classic signs: fever above 104°F, severe headache, pain behind the eyes, joint pain, and a rash. Get a CBC (blood count) test and Dengue NS1 antigen test within the first 5 days. Falling platelet count is a warning sign.",
    "What are symptoms of malaria?": "Malaria causes cyclical fever with chills and sweating (every 48-72 hours), headache, nausea, muscle pain, and fatigue. In severe cases: jaundice, anaemia, confusion. Do a Rapid Diagnostic Test (RDT) or blood smear at nearest PHC.",
    "How is TB spread?": "Tuberculosis spreads through airborne droplets when an infected person coughs, sneezes, or talks. It is NOT spread by sharing utensils or touching. TB is treatable — free DOTS treatment is available at all government hospitals. Nikshay helpline: 1800-11-6666.",
    "What is the normal blood sugar level?": "Normal fasting blood glucose: 70-100 mg/dL. Pre-diabetes: 100-125 mg/dL. Diabetes: ≥126 mg/dL (on two occasions). Post-meal (2 hours): normal is <140 mg/dL. HbA1c: Normal <5.7%, Pre-diabetes 5.7-6.4%, Diabetes ≥6.5%.",
    "What causes high blood pressure?": "Common causes include high salt diet, obesity, stress, sedentary lifestyle, genetics, smoking, alcohol, and kidney disease. Most hypertension has no single cause (primary/essential). Lifestyle changes + medications control it. Target BP <130/80 mmHg.",
    "Can diabetes be cured?": "Type 1 diabetes cannot be cured (yet). Type 2 diabetes can go into remission with significant weight loss, dietary change, and exercise — but it requires lifelong management. HbA1c < 6.5% without medication is considered remission. Consult your endocrinologist.",
    "What should I eat for diabetes?": "Focus on low glycemic index foods: brown rice, bajra roti, oats, lentils, vegetables. Avoid white rice, bread, sweets, sugary drinks. Eat bitter gourd (karela) and fenugreek (methi). Eat every 3-4 hours. 30 min walk daily helps significantly.",
    "How do I lower blood pressure naturally?": "Reduce salt to <5g/day. Eat more potassium (banana, spinach). Exercise 30 min/day. Manage stress with yoga or meditation. Garlic and hibiscus tea have evidence-based antihypertensive effects. Reduce alcohol. Quit smoking. Lose weight if overweight.",
    "What is anaemia?": "Anaemia means your blood has insufficient haemoglobin to carry oxygen. Symptoms: fatigue, pale skin, breathlessness, dizziness. Most common cause in India: iron deficiency (53% of women affected). Treatment: iron supplements + Vitamin C + iron-rich diet. Test: CBC + serum ferritin.",
    "What foods increase haemoglobin?": "Best iron-rich Indian foods: spinach, drumstick leaves (moringa), jaggery, dates, lentils, sesame seeds, pomegranate, eggs, chicken. Always eat Vitamin C with iron (amla, lemon, tomato) — it doubles absorption. Avoid tea/coffee with meals.",
    "How many calories in a chapati?": "One plain chapati (35g) has approximately 95 calories: 3g protein, 18.5g carbohydrate, 1.5g fat, 1.8g fibre. Whole wheat is healthier than maida. Two rotis = 190 kcal approximately.",
    "Is rice healthy?": "White rice has a high glycemic index (72) and lower fibre. For diabetes or weight management, choose brown rice (GI 55) or millets. Regular rice is fine for healthy individuals in moderate portions. Pair with plenty of dal, vegetables for a balanced meal.",
    "What are the symptoms of depression?": "Persistent sadness, loss of interest in activities, fatigue, sleep changes (too much or too little), appetite changes, concentration problems, feelings of worthlessness, and in severe cases, thoughts of death. PHQ-9 score ≥10 indicates moderate depression. See a doctor or therapist.",
    "How do I manage anxiety?": "Proven strategies: daily exercise (30 min), diaphragmatic breathing (4-7-8 technique), mindfulness meditation, CBT therapy, limiting caffeine and alcohol, regular sleep, journalling. Medication (SSRIs) if anxiety is severe or interfering with daily life. iCall helpline: 9152987821.",
    "Is paracetamol safe?": "Yes, paracetamol (acetaminophen) is generally safe at recommended doses. Adult dose: 500mg-1g every 6-8 hours, maximum 4g/day. Do NOT exceed — liver damage can occur with overdose. Avoid alcohol when taking paracetamol. Safe in pregnancy and for children (dose by weight).",
    "What is the dose of paracetamol for children?": "Children's paracetamol dose: 10-15 mg per kg body weight, every 6-8 hours. Example: 10kg child = 100-150mg per dose. Do not exceed 5 doses in 24 hours. Use weight-based dosing, not age. Infant drops are more concentrated than syrup — check concentration carefully.",
    "What is the difference between viral and bacterial infection?": "Viral infections (cold, flu, dengue, COVID): caused by viruses, usually self-limiting, antibiotics do NOT help. Bacterial infections (typhoid, UTI, TB, pneumonia): caused by bacteria, require specific antibiotics. Signs of bacterial: high fever, localised pain, pus/discharge. Always consult doctor before taking antibiotics.",
    "Should I take antibiotics for cold?": "No. Common cold is caused by viruses. Antibiotics ONLY work against bacteria — they do nothing for viral infections and can cause antibiotic resistance. Treatment for cold: rest, fluids, steam, paracetamol for fever, honey + ginger tea. See doctor only if symptoms worsen or last >10 days.",
    "What is the treatment for typhoid?": "Antibiotics: Ciprofloxacin (first line) or Azithromycin for uncomplicated cases; Ceftriaxone for severe cases. Complete the full course. Rest, plenty of fluids, soft easily digestible food. Widal test has poor accuracy — blood culture is gold standard for diagnosis.",
    "How does dengue affect platelet count?": "Dengue virus attacks platelets (thrombocytes), causing counts to fall. Normal: 150,000-400,000 per microlitre. In dengue: can fall to below 20,000 (dangerous). Below 10,000 or active bleeding requires platelet transfusion. Daily CBC monitoring is essential during dengue.",
    "What vaccines are mandatory for children in India?": "Under Universal Immunisation Programme (UIP): BCG, OPV, IPV, Pentavalent (DPT+HepB+Hib), Rotavirus, PCV, MR/MMR, JE (endemic areas), Vitamin A. These are FREE at government health centres. Private schedule additionally includes Varicella, HPV, Typhoid, Hepatitis A.",
    "When should I take a pregnant woman to hospital immediately?": "Emergency signs in pregnancy: heavy bleeding, severe headache + visual changes, swollen face/hands + high BP, reduced or absent fetal movement after 28 weeks, severe abdominal pain, fits/convulsions, high fever, leaking fluid before 37 weeks, signs of labour before 37 weeks.",
    "What is PCOS?": "Polycystic Ovary Syndrome is a hormonal disorder in women with excess androgen production. Symptoms: irregular periods, facial hair, acne, weight gain (especially abdomen), hair thinning, difficulty conceiving. Diagnosis: ultrasound + hormone panel. Treatment: lifestyle changes, Metformin, hormonal therapy. Very common in India — affects 1 in 5 women.",
    "How do I get Ayushman Bharat card?": "Check eligibility at pmjay.gov.in or call 14555. Coverage: ₹5 lakh per family per year for hospitalisation. If eligible (SECC data), visit nearest empanelled hospital or Common Service Centre with Aadhaar. Benefits include cashless treatment for 1,949 medical procedures.",
    "What is Jan Aushadhi?": "Jan Aushadhi Kendras are government pharmacies selling branded-quality generic medicines at 50-90% lower prices. Find nearest centre at janaushadhi.gov.in or call 1800-180-8080. Over 9,000 medicine SKUs available including cancer, cardiac, diabetes, and TB medicines.",
    "How do I know if chest pain is serious?": "CALL 108 immediately for: chest pain + sweating, chest pain radiating to left arm/jaw, chest pain + breathlessness, crushing/squeezing chest sensation (heart attack signs). Less urgent: sharp localised chest pain worsened by touch or breathing (likely musculoskeletal). When in doubt — go to emergency.",
    "What is the golden hour in heart attack?": "The first 60 minutes after heart attack symptoms begin is called the 'Golden Hour.' Starting treatment (opening blocked artery via angioplasty) within this time dramatically improves survival and limits heart damage. Every minute matters — call 108 immediately, do not drive yourself.",
    "How do I do CPR?": "Adult CPR: 1) Check breathing — no breathing = start CPR. 2) Call 108. 3) Place heel of hand on centre of chest. 4) Push hard and fast — 30 compressions, 2 inches deep, 100-120 per minute. 5) Give 2 rescue breaths. 6) Repeat until ambulance arrives or person recovers.",
    "What is dehydration and how to treat it?": "Dehydration: loss of fluids + electrolytes. Signs: dark urine, dry mouth, dizziness, fatigue. Treatment: ORS (Oral Rehydration Solution) is the gold standard. Home ORS: 1 litre boiled water + 6 teaspoons sugar + ½ teaspoon salt. Severe: IV fluids in hospital. Children dehydrate faster — act quickly.",
    "What causes jaundice?": "Jaundice (yellow skin/eyes) means excess bilirubin. Causes: Hepatitis A/B/E (liver infection), bile duct blockage, haemolytic anaemia, severe malaria, leptospirosis. Tests: LFT (liver function tests), bilirubin levels, USG abdomen. Always see doctor — some causes are serious emergencies.",
    "Is coconut water good for health?": "Yes. Tender coconut water is an excellent natural electrolyte drink with potassium (600mg/250ml), low calories (46 kcal), and good hydration. Beneficial for fever, vomiting, diarrhoea, dehydration, post-exercise. However, avoid in CKD patients (high potassium). Not a substitute for medicines.",
    "How much water should I drink per day?": "General guideline: 8-10 glasses (2-2.5 litres) per day for adults. Adjust for: hot weather (+500ml), exercise (+500-1000ml), fever (+300ml), pregnancy (+300ml). Best indicator: pale yellow urine = adequate hydration. Dark yellow = drink more. Water is the best drink.",
    "What is the DASH diet?": "DASH (Dietary Approaches to Stop Hypertension): emphasises fruits, vegetables, whole grains, low-fat dairy, lean protein. Limits salt (<2.3g sodium/day), red meat, added sugars, saturated fats. Lowers BP by 8-14 mmHg. Indian adaptation: brown rice, dal, sabzi, curd, fruits — less salt, no pickles.",
    "What causes kidney stones?": "Kidney stones form from concentrated minerals: calcium oxalate (most common), uric acid, struvite, cystine. Risk factors: insufficient water intake, high salt/protein diet, obesity, UTIs. Prevention: drink 2.5+ litres water daily, reduce salt and animal protein, lemon water (citrate prevents stones).",
    "How do I treat a minor burn at home?": "Cool running water for 20 minutes (NOT ice). Remove jewellery near burn. Cover loosely with clean cling film or plastic bag. Paracetamol/ibuprofen for pain. Do NOT: use butter, oil, toothpaste, or ice. See doctor for: burns >palm size, burns on face/hands/genitals, blisters, or chemical burns.",
    "What is the normal temperature of a child?": "Normal: 36.5-37.5°C (97.7-99.5°F). Low-grade fever: 37.5-38°C. Fever: >38°C. High fever: >39°C. Emergency: >40°C or any fever in baby under 3 months. Rectal thermometer is most accurate for infants. Use paracetamol 10-15mg/kg for fever. Seek help for fever + rash, stiff neck, or breathing difficulty.",
    "What are signs of stroke?": "Use FAST: Face drooping (ask to smile — uneven?), Arm weakness (one arm drifts down?), Speech difficulty (slurred or can't speak?), Time to call 108. Also watch for: sudden severe headache, vision loss, confusion, loss of balance. Note exact time symptoms started — critical for treatment decision.",
    "Is turmeric good for health?": "Yes — curcumin in turmeric has evidence-based anti-inflammatory, antioxidant, and some anti-cancer properties. Daily turmeric in cooking (½ tsp) is beneficial. Absorption improves with black pepper (piperine) and fat. Helpful for arthritis, inflammatory conditions, liver protection. NOT a medicine substitute for serious conditions.",
    "What is the benefit of eating moringa?": "Moringa (drumstick/Murungai) is a nutritional powerhouse: 7x more Vitamin C than oranges, 4x more calcium than milk, 3x more iron than spinach. Benefits: anaemia, bone health, blood sugar control, anti-inflammatory, lactation support. The leaves, pods, and flowers are all edible and nutritious.",
    "How do I check if medicine is expired?": "Check expiry date on strip or box — use format DD/MM/YYYY or MM/YYYY. Never use expired medicines — potency decreases and chemical breakdown can occur (tetracycline becomes toxic). Store medicines in cool, dry place away from sunlight. Dispose expired medicines safely at pharmacy or government facility.",
}

QUICK_REPLIES: Dict[str, List[str]] = {
    "symptoms":       ["What causes this?", "How serious is this?", "What should I do?", "When to see doctor?"],
    "medicines":      ["Is this safe in pregnancy?", "What is the dosage?", "Any side effects?", "Generic alternative?"],
    "diet":           ["What should I avoid?", "Best foods for this condition?", "Budget meal plan?", "Calorie count?"],
    "emergency":      ["Call 108", "First aid steps", "Nearest hospital type", "Golden hour timer"],
    "mental_health":  ["PHQ-9 depression test", "GAD-7 anxiety test", "Breathing exercises", "Talk to helpline"],
    "children":       ["Vaccine schedule", "Normal milestones", "Fever in children", "Growth chart"],
    "women":          ["Pregnancy tracker", "PCOS risk check", "Anaemia test", "Government schemes"],
    "government":     ["Ayushman Bharat card", "Jan Aushadhi finder", "Free vaccination", "ASHA worker contact"],
    "general":        ["What is BMI?", "Daily water intake", "Healthy eating tips", "Exercise recommendations"],
    "prevention":     ["How to prevent dengue?", "Cancer prevention tips", "Heart health tips", "Diabetes prevention"],
}

HEALTH_TIPS = [
    "Drink a glass of water when you wake up — it jumpstarts metabolism.",
    "10 minutes of sunlight daily gives you free Vitamin D.",
    "Amla (Indian gooseberry) has 20x more Vitamin C than orange juice.",
    "Walking 10,000 steps/day reduces diabetes risk by 60%.",
    "Add turmeric and black pepper to your cooking for anti-inflammatory benefits.",
    "Sleep 7-8 hours: it reduces heart disease risk by 34%.",
    "Eat a rainbow: different coloured vegetables provide different nutrients.",
    "Ragi (finger millet) is the highest calcium grain — 344mg per 100g.",
    "Curd/yogurt with live cultures boosts gut health and immunity.",
    "Deep breathing for 5 minutes lowers cortisol (stress hormone) significantly.",
    "Drinking green tea (2 cups/day) is associated with reduced cancer risk.",
    "Screen time before bed delays sleep — put phone down 1 hour before sleeping.",
    "Drumstick (Murungai) leaves: more iron than spinach, more calcium than milk.",
    "Garlic daily (raw or cooked) helps lower blood pressure naturally.",
    "Avoid sitting for more than 45 minutes continuously — get up and walk.",
    "Flaxseeds are the best plant source of omega-3 fatty acids.",
    "A handful of nuts daily (almonds, walnuts) protects the heart.",
    "Cooking in iron kadai adds up to 80% more iron to your food.",
    "Sprouting lentils increases their nutrient content by 30-50%.",
    "Warm lemon water in the morning aids digestion and Vitamin C intake.",
    "Jaggery + sesame (til) is a traditional winter health snack — iron + calcium.",
    "Fenugreek (methi) seeds soaked overnight help control blood sugar.",
    "Eat slowly and chew well — it takes 20 minutes for fullness to register.",
    "One banana after exercise replenishes potassium and carbohydrates.",
    "Regular handwashing prevents 20% of respiratory infections.",
    "Coconut water after fever replaces lost electrolytes naturally.",
    "Moringa leaf powder: add to dal or idli batter for a nutrition boost.",
    "Cold compress on temples + neck helps tension headaches without medicine.",
    "Pomegranate juice boosts iron absorption and heart health.",
    "Avoid plastic water bottles in sunlight — BPA leaches into water.",
    "Tulsi (Holy Basil) tea helps with cold, stress, and immunity.",
    "Brown rice has 3x more fibre than white rice — switch gradually.",
    "Massaging with warm sesame oil (Abhyanga) improves circulation and sleep.",
    "Ripe banana + curd = natural probiotic snack for gut health.",
    "Exercise during pregnancy (with doctor's approval) reduces delivery complications.",
    "High heels >5cm worn daily cause chronic back pain and foot problems.",
    "Salt in teaspoon: only ½ tsp (2.3g sodium) is the daily safe limit.",
    "Air pollution days: wear N95 mask, avoid outdoor exercise during peak hours.",
    "Reading to children even from 6 months builds language development pathways.",
    "Massaging baby with oil daily improves weight gain in low birth weight infants.",
    "Fermented foods (idli, dosa batter, curd) feed good gut bacteria.",
    "Dark leafy greens like methi, spinach, and curry leaves are natural multivitamins.",
    "Laughing reduces cortisol, boosts immunity — watch something funny daily!",
    "Social connection is the strongest predictor of long-term health and happiness.",
    "Plant-based diets are associated with 23% lower risk of type 2 diabetes.",
    "Fasting (16:8) has metabolic benefits but should be supervised in diabetics.",
    "Intermittent walking breaks are as effective as continuous exercise for BP.",
    "Cooking with mustard oil provides ALA omega-3 fatty acids.",
    "Keep medicine away from children — 300+ child deaths annually from accidental ingestion.",
    "Breast milk for first 6 months exclusively reduces infant mortality by 13x.",
]

ESCALATION_KEYWORDS = [
    "suicide", "kill myself", "want to die", "end my life", "self harm", "cut myself",
    "no reason to live", "better off dead", "give up on life", "can't go on",
    "ending everything", "hopeless", "worthless to everyone", "jump",
    "overdose", "poison myself", "hang myself", "hurt myself intentionally",
    "my heart stopped", "can't breathe", "unconscious", "not responding",
    "bleeding severely", "heart attack", "stroke", "fit not stopping",
    "eaten poison", "swallowed bleach", "swallowed pesticide",
    "baby not breathing", "child not waking up",
]

GREETING_RESPONSES = [
    "Hello! I'm BharatCare Assistant 🏥 — your health companion. How can I help you today?",
    "Namaste! I'm here to answer your health questions in English, Hindi, or Tamil. What's on your mind?",
    "Hi there! Ask me anything about symptoms, medicines, diet, or emergency first aid.",
    "Welcome to BharatCare AI! I can help with disease information, drug queries, nutrition, and more.",
    "Hello! For medical emergencies, please call 108 immediately. For health questions, I'm here to help!",
    "Vanakkam! How are you feeling today? I can help with health information, symptoms, or wellness tips.",
    "Hi! I'm your BharatCare health assistant. Ask me about symptoms, diet, medicines, or mental wellness.",
    "Hello! Remember — I provide health information, not medical diagnosis. Always consult a doctor for treatment.",
]

FALLBACK_RESPONSES = [
    "I'm not sure about that specific query. Could you rephrase? Or try asking about symptoms, medicines, diet, or first aid.",
    "I don't have detailed information on that. For medical concerns, please consult your doctor or call the health helpline at 104.",
    "That's outside my knowledge. For the best advice, please speak to a qualified healthcare professional.",
    "I couldn't find a match for that. Try questions like 'What is dengue?' or 'What to eat for diabetes?'",
    "Hmm, I'm not confident about that. For accurate medical information, please visit your nearest government health centre.",
    "I don't want to guess on medical matters. Please consult a doctor for personalised advice. I can help with general health information.",
]


class MedicalFAQDatabase:
    def __init__(self):
        self.questions = list(MEDICAL_FAQ.keys())
        self.answers   = list(MEDICAL_FAQ.values())
        if HAS_SKLEARN:
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=1000)
            self.tfidf      = self.vectorizer.fit_transform(self.questions)

    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, str, float]]:
        if not HAS_SKLEARN:
            return self._keyword_search(query, top_k)
        q_vec  = self.vectorizer.transform([query])
        scores = cosine_similarity(q_vec, self.tfidf)[0]
        top    = np.argsort(scores)[::-1][:top_k]
        return [(self.questions[i], self.answers[i], round(float(scores[i]), 3)) for i in top if scores[i] > 0.05]

    def _keyword_search(self, query: str, top_k: int) -> List[Tuple[str, str, float]]:
        query_low = query.lower()
        results   = []
        for q, a in MEDICAL_FAQ.items():
            words   = set(query_low.split())
            q_words = set(q.lower().split())
            score   = len(words & q_words) / max(len(words), 1)
            if score > 0:
                results.append((q, a, round(score, 3)))
        return sorted(results, key=lambda x: x[2], reverse=True)[:top_k]

    def exact_match(self, query: str) -> Optional[str]:
        query_low = query.lower()
        for q, a in MEDICAL_FAQ.items():
            if query_low in q.lower() or q.lower() in query_low:
                return a
        return None


class ResponseMatcher:
    def __init__(self, faq_db: MedicalFAQDatabase):
        self.faq = faq_db
        self._build_keyword_map()

    def _build_keyword_map(self):
        self.keyword_map = {
            r"\bdengue\b":           "dengue",
            r"\bmalaria\b":          "malaria",
            r"\btyphoid\b":          "typhoid",
            r"\btb\b|\btuberculosis\b": "tuberculosis",
            r"\bdiabetes\b|\bsugar\b": "diabetes",
            r"\bbp\b|\bhypertension\b|\bblood pressure\b": "hypertension",
            r"\bcovid\b|\bcorona\b": "covid",
            r"\banaemia\b|\banaemia\b": "anaemia",
            r"\bheart attack\b|\bchest pain\b": "heart attack",
            r"\bstroke\b":           "stroke",
            r"\bdepression\b|\bsad\b|\bdepressed\b": "depression",
            r"\banxiety\b|\banxious\b": "anxiety",
            r"\bparacetamol\b|\bcrocin\b": "paracetamol",
            r"\bpregnant\b|\bpregnancy\b": "pregnancy",
            r"\bvaccin\b":           "vaccine",
            r"\bpcos\b":             "pcos",
            r"\bburn\b":             "burn",
            r"\bchok\b":             "choking",
            r"\bsnake\b":            "snake bite",
            r"\bvitamin\b|\bdeficien\b": "vitamin deficiency",
            r"\bweight loss\b|\bdie\b": "weight loss",
            r"\bjank aushadhi\b|\bgeneric\b": "jan aushadhi",
            r"\bayushman\b|\bpmjay\b": "ayushman",
        }

    def keyword_match(self, text: str) -> Optional[str]:
        text_low = text.lower()
        for pattern, topic in self.keyword_map.items():
            if re.search(pattern, text_low):
                results = self.faq.search(topic, top_k=1)
                if results:
                    return results[0][1]
        return None

    def match(self, user_input: str) -> Dict:
        exact = self.faq.exact_match(user_input)
        if exact:
            return {"response": exact, "confidence": 0.95, "source": "exact_match",
                    "quick_replies": random.choice(list(QUICK_REPLIES.values()))}

        kw_match = self.keyword_match(user_input)
        if kw_match:
            return {"response": kw_match, "confidence": 0.80, "source": "keyword_match",
                    "quick_replies": random.choice(list(QUICK_REPLIES.values()))}

        results = self.faq.search(user_input, top_k=1)
        if results and results[0][2] > 0.15:
            return {"response": results[0][1], "confidence": results[0][2], "source": "tfidf",
                    "quick_replies": random.choice(list(QUICK_REPLIES.values()))}

        return {"response": random.choice(FALLBACK_RESPONSES), "confidence": 0.0, "source": "fallback",
                "quick_replies": QUICK_REPLIES["general"]}


class ConversationManager:
    def __init__(self):
        self.history: List[Dict] = []

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content,
                              "timestamp": datetime.now().strftime("%H:%M")})

    def get_context(self, last_n: int = 5) -> List[Dict]:
        return self.history[-last_n:]

    def export_chat(self) -> str:
        lines = ["BharatCare AI — Chat Export", "=" * 40]
        for msg in self.history:
            lines.append(f"[{msg['timestamp']}] {msg['role'].upper()}: {msg['content']}")
        return "\n".join(lines)

    def clear(self):
        self.history = []


class EscalationDetector:
    def check(self, text: str) -> Dict:
        text_low = text.lower()
        triggered = [kw for kw in ESCALATION_KEYWORDS if kw in text_low]
        if triggered:
            mental_crisis = any(kw in text_low for kw in ["suicide", "kill myself", "want to die",
                                 "end my life", "self harm", "no reason to live", "better off dead"])
            return {
                "escalate": True,
                "reason": "Mental health crisis detected" if mental_crisis else "Medical emergency detected",
                "helpline": "iCall: 9152987821 | Vandrevala: 1860-2662-345 | Emergency: 108",
            }
        return {"escalate": False, "reason": "", "helpline": ""}


class HealthChatbot:
    def __init__(self):
        self.faq     = MedicalFAQDatabase()
        self.matcher = ResponseMatcher(self.faq)
        self.convo   = ConversationManager()
        self.escl    = EscalationDetector()

    def respond(self, user_input: str) -> Dict:
        self.convo.add_message("user", user_input)
        # Escalation check first
        esc = self.escl.check(user_input)
        if esc["escalate"]:
            response = (f"⚠️ I'm concerned about what you've shared. Please reach out immediately:\n"
                        f"📞 {esc['helpline']}\nYou are not alone. Help is available 24/7.")
            self.convo.add_message("bot", response)
            return {"message": response, "quick_replies": [], "escalate": True,
                    "health_tip": random.choice(HEALTH_TIPS)}

        # Check greeting
        greet_words = ["hi", "hello", "hey", "namaste", "vanakkam", "good morning", "good evening"]
        if any(w in user_input.lower() for w in greet_words) and len(user_input.split()) <= 4:
            response = random.choice(GREETING_RESPONSES)
        else:
            result   = self.matcher.match(user_input)
            response = result["response"]

        self.convo.add_message("bot", response)
        return {"message": response, "quick_replies": random.choice(list(QUICK_REPLIES.values())),
                "escalate": False, "health_tip": random.choice(HEALTH_TIPS)}

    def get_daily_tip(self) -> str:
        return random.choice(HEALTH_TIPS)

    def reset(self):
        self.convo.clear()
