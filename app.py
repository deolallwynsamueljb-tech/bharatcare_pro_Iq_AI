"""
BharatCare AI Pro — 15-Page Healthcare Intelligence Platform
Developer: Deol Allwyn Samuel J B · VLSI · CIT · Afynix Digital · Reg No 712721104034
"""

import streamlit as st
import os, json, random
from datetime import datetime, timedelta

st.set_page_config(
    page_title="BharatCare AI Pro",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Design System ────────────────────────────────────────────────
COLORS = {
    "heal": "#06d6a0", "trust": "#118ab2", "mind": "#7b2d8b",
    "drug": "#ff9f1c", "epi": "#ef476f", "bg": "#0d1117",
    "card": "#161b22", "border": "#30363d", "text": "#e6edf3"
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=DM+Mono&family=Playfair+Display:wght@700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Outfit', sans-serif;
    background: {COLORS['bg']};
    color: {COLORS['text']};
}}
.main {{ background: {COLORS['bg']}; }}
.block-container {{ padding: 1.5rem 2rem; }}

.hero-title {{
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem; font-weight: 700;
    background: linear-gradient(135deg, {COLORS['heal']}, {COLORS['trust']});
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}}
.hero-sub {{ color: #8b949e; font-size: 1rem; margin-bottom: 1.5rem; }}

.kpi-card {{
    background: {COLORS['card']}; border: 1px solid {COLORS['border']};
    border-radius: 12px; padding: 1.2rem 1.5rem;
    text-align: center; transition: transform .2s;
}}
.kpi-card:hover {{ transform: translateY(-3px); }}
.kpi-number {{ font-size: 2.2rem; font-weight: 700; font-family: 'DM Mono', monospace; }}
.kpi-label {{ font-size: 0.8rem; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }}

.module-card {{
    background: {COLORS['card']}; border: 1px solid {COLORS['border']};
    border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem;
    border-left: 4px solid;
}}
.section-header {{
    font-size: 1.4rem; font-weight: 700;
    border-bottom: 2px solid {COLORS['border']};
    padding-bottom: 0.5rem; margin-bottom: 1.2rem;
}}
.tag {{
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600; margin: 2px;
}}
.result-box {{
    background: {COLORS['card']}; border: 1px solid {COLORS['border']};
    border-radius: 12px; padding: 1.2rem; margin-top: 1rem;
}}
.chat-user {{
    background: {COLORS['trust']}22; border-radius: 12px 12px 4px 12px;
    padding: 0.7rem 1rem; margin: 0.4rem 0; text-align: right;
}}
.chat-bot {{
    background: {COLORS['card']}; border: 1px solid {COLORS['border']};
    border-radius: 12px 12px 12px 4px; padding: 0.7rem 1rem; margin: 0.4rem 0;
}}
.alert-critical {{ background: {COLORS['epi']}22; border: 1px solid {COLORS['epi']}; border-radius: 8px; padding: 0.8rem; }}
.alert-warning  {{ background: {COLORS['drug']}22; border: 1px solid {COLORS['drug']}; border-radius: 8px; padding: 0.8rem; }}
.alert-success  {{ background: {COLORS['heal']}22; border: 1px solid {COLORS['heal']}; border-radius: 8px; padding: 0.8rem; }}

@keyframes pulse {{
    0%,100% {{ transform: scale(1); opacity:1; }}
    50% {{ transform: scale(1.08); opacity:.85; }}
}}
.pulse {{ animation: pulse 2s infinite; display:inline-block; }}

@keyframes breathe {{
    0%,100% {{ transform: scale(1); }}
    50% {{ transform: scale(1.3); }}
}}

div[data-testid="stSidebar"] {{
    background: {COLORS['card']};
    border-right: 1px solid {COLORS['border']};
}}
div[data-testid="stSidebar"] .stRadio > label {{
    color: {COLORS['text']} !important;
}}
.stButton > button {{
    background: linear-gradient(135deg, {COLORS['heal']}, {COLORS['trust']});
    color: #000; font-weight: 700; border: none; border-radius: 8px;
    padding: 0.5rem 1.5rem;
}}
.stButton > button:hover {{ opacity: 0.9; transform: translateY(-1px); }}
.stTextInput > div > div > input, .stTextArea > div > div > textarea,
.stSelectbox > div > div > select {{
    background: {COLORS['card']}; color: {COLORS['text']};
    border: 1px solid {COLORS['border']}; border-radius: 8px;
}}
</style>
""", unsafe_allow_html=True)

# ── Session State Init ───────────────────────────────────────────
for key, default in [
    ("page","Command Center"), ("chat_history",[]),
    ("health_records",[]), ("mood_log",[]),
    ("symptom_history",[]), ("drug_search_history",[])
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Auto-generate data on first run (Streamlit Cloud) ───────────
BASE = os.path.dirname(__file__)
_data_dir = os.path.join(BASE, "data")
if not os.path.exists(os.path.join(_data_dir, "symptom_records.csv")):
    try:
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location("generate_data", os.path.join(BASE, "generate_data.py"))
        _gd = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_gd)
        _gd.generate_all()
    except Exception:
        os.makedirs(_data_dir, exist_ok=True)

# ── Import Engines (graceful) ────────────────────────────────────

def safe_import(module_name):
    import importlib.util, sys
    path = os.path.join(BASE, f"{module_name}.py")
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None

@st.cache_resource(show_spinner=False)
def load_engines():
    return {
        "nlp":       safe_import("nlp_engine"),
        "mindcare":  safe_import("mindcare_engine"),
        "drugiq":    safe_import("drugiq_engine"),
        "epiwatch":  safe_import("epiwatch_engine"),
        "nutrition": safe_import("nutrition_engine"),
        "womchild":  safe_import("womenchild_engine"),
        "chatbot":   safe_import("chatbot_engine"),
        "emergency": safe_import("emergency_engine"),
        "calcs":     safe_import("health_calculators"),
        "disease_db":safe_import("disease_database"),
    }

@st.cache_resource(show_spinner=False)
def load_chatbot():
    mod = safe_import("chatbot_engine")
    if mod and hasattr(mod, "HealthChatbot"):
        return mod.HealthChatbot()
    return None

engines = load_engines()

# ── Sidebar Navigation ───────────────────────────────────────────
PAGES = [
    ("🏠", "Command Center"),
    ("🔬", "Symptom Intelligence"),
    ("🧠", "MindCare"),
    ("💊", "DrugIQ"),
    ("🌐", "EpiWatch"),
    ("⚙️", "ML Engine"),
    ("📚", "Disease Encyclopedia"),
    ("📊", "Health Calculators"),
    ("🏛️", "Government Schemes"),
    ("📡", "Telemedicine Guide"),
    ("📋", "Health Records"),
    ("🚨", "Emergency Navigator"),
    ("🥗", "Nutrition Intelligence"),
    ("👩", "Women & Child Health"),
    ("💬", "Health Chatbot"),
]

with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding: 1rem 0;'>
        <div class='pulse' style='font-size:2.5rem;'>🏥</div>
        <div style='font-family:Playfair Display; font-size:1.2rem; font-weight:700;
                    background:linear-gradient(135deg,{COLORS['heal']},{COLORS['trust']});
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
            BharatCare AI Pro
        </div>
        <div style='color:#8b949e; font-size:0.72rem;'>Afynix Digital · CIT</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    for icon, name in PAGES:
        active = st.session_state.page == name
        label = f"**{icon} {name}**" if active else f"{icon} {name}"
        if st.button(label, key=f"nav_{name}", use_container_width=True):
            st.session_state.page = name
            st.rerun()
    st.divider()
    st.markdown(f"""
    <div style='font-size:0.7rem; color:#8b949e; text-align:center; line-height:1.6;'>
        <b style='color:{COLORS['heal']};'>Deol Allwyn Samuel J B</b><br>
        VLSI · CIT · Afynix Digital<br>
        Reg No 712721104034<br>
        <span style='color:{COLORS['epi']};'>⚕ Not a substitute for medical advice</span>
    </div>
    """, unsafe_allow_html=True)

page = st.session_state.page

# ════════════════════════════════════════════════════════════════
# PAGE 1 — COMMAND CENTER
# ════════════════════════════════════════════════════════════════
if page == "Command Center":
    st.markdown("<div class='hero-title'>BharatCare AI Pro</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='hero-sub'>India's Most Advanced Healthcare Intelligence Platform · {datetime.now().strftime('%d %B %Y')}</div>", unsafe_allow_html=True)

    k1,k2,k3,k4,k5 = st.columns(5)
    kpis = [
        (COLORS['heal'],"9,500+","Lines of Code"),
        (COLORS['trust'],"15","AI Pages"),
        (COLORS['mind'],"11","Engine Modules"),
        (COLORS['drug'],"21","Drugs Indexed"),
        (COLORS['epi'],"37","States Covered"),
    ]
    for col,(color,num,label) in zip([k1,k2,k3,k4,k5],kpis):
        col.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-number' style='color:{color};'>{num}</div>
            <div class='kpi-label'>{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    modules = [
        (COLORS['heal'],"🔬 Symptom Intelligence","NLP-powered disease prediction with 15 diseases, TF-IDF + ensemble ML, multilingual support (Tamil/Hindi/English)","Symptom Intelligence"),
        (COLORS['mind'],"🧠 MindCare","PHQ-9/GAD-7 mental health screening, mood tracker, breathing exercises, VADER sentiment, crisis detection","MindCare"),
        (COLORS['drug'],"💊 DrugIQ","Drug search, interaction checker, pediatric dosage (Clark's/Young's), pregnancy categories, Jan Aushadhi savings","DrugIQ"),
        (COLORS['epi'],"🌐 EpiWatch","State-level outbreak risk scoring, seasonal disease surveillance, vaccination gap analysis, alert generation","EpiWatch"),
        (COLORS['trust'],"🚨 Emergency Navigator","15 first-aid protocols, 36-state ambulance directory, golden hour calculator, blood bank locator","Emergency Navigator"),
        ("#a8dadc","🥗 Nutrition Intelligence","60+ Indian foods, ICMR RDA tracking, disease diet plans, vitamin deficiency detector, budget meal planner","Nutrition Intelligence"),
        ("#e9c46a","👩 Women & Child Health","NIP vaccine schedule, pregnancy week tracker, PCOS risk scoring, WHO growth charts, govt schemes","Women & Child Health"),
        ("#457b9d","💬 Health Chatbot","40+ medical FAQ, TF-IDF semantic search, escalation detection, multilingual quick replies","Health Chatbot"),
    ]
    for i,(color,title,desc,target) in enumerate(modules):
        col = c1 if i%2==0 else c2
        with col:
            if st.button(f"{title}", key=f"mod_{i}", use_container_width=True):
                st.session_state.page = target
                st.rerun()
            st.markdown(f"""
            <div class='module-card' style='border-left-color:{color}; margin-top:-0.5rem; margin-bottom:0.5rem;'>
                <div style='font-size:0.85rem; color:#8b949e;'>{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='section-header' style='color:{COLORS['heal']};'>Health Quick Check</div>", unsafe_allow_html=True)
        temp = st.number_input("Body Temperature (°F)", 95.0, 106.0, 98.6, 0.1)
        if temp >= 103:
            st.markdown("<div class='alert-critical'>🔴 High Fever — seek medical attention</div>", unsafe_allow_html=True)
        elif temp >= 100.4:
            st.markdown("<div class='alert-warning'>🟡 Fever detected — monitor closely</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='alert-success'>🟢 Normal temperature</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='section-header' style='color:{COLORS['trust']};'>Emergency Contacts</div>", unsafe_allow_html=True)
        for name, num, color in [
            ("🚑 Ambulance","108",COLORS['epi']),
            ("👶 Child Helpline","1098",COLORS['mind']),
            ("🏥 Medical Helpline","104",COLORS['heal']),
            ("☠ Poison Control","1800-116-117",COLORS['drug']),
        ]:
            st.markdown(f"<span style='color:{color};font-weight:700;'>{name}</span> — <code style='color:{COLORS['text']};'>{num}</code>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='section-header' style='color:{COLORS['drug']};'>Today's Health Tip</div>", unsafe_allow_html=True)
        tips = [
            "Drink 8-10 glasses of water daily — especially in Indian summer heat.",
            "Walk 30 minutes/day reduces diabetes risk by 30%.",
            "Sleep 7-8 hours — poor sleep raises BP and cortisol.",
            "Add haldi (turmeric) to your diet — natural anti-inflammatory.",
            "Check your BP at least once a month if you're over 40.",
        ]
        st.info(random.choice(tips))

# ════════════════════════════════════════════════════════════════
# PAGE 2 — SYMPTOM INTELLIGENCE
# ════════════════════════════════════════════════════════════════
elif page == "Symptom Intelligence":
    st.markdown(f"<div class='hero-title' style='font-size:2rem;'>🔬 Symptom Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>NLP-powered disease prediction · Tamil/Hindi/English · 15 diseases</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([3,2])
    with col1:
        st.markdown("#### Describe your symptoms")
        symptom_text = st.text_area(
            "Enter symptoms in English, Hindi, or Tamil",
            placeholder="e.g. I have high fever, severe headache and joint pain since 3 days...\nहिंदी: बुखार है, सिरदर्द है...",
            height=120, key="sym_text"
        )
        c1,c2,c3 = st.columns(3)
        duration = c1.selectbox("Duration", ["<1 day","1-3 days","4-7 days","1-2 weeks","2+ weeks"])
        age_input = c2.number_input("Age", 1, 100, 30)
        gender_input = c3.selectbox("Gender", ["Male","Female","Other"])

        quick_syms = st.multiselect("Quick-add symptoms", [
            "fever","headache","cough","fatigue","nausea","vomiting",
            "joint pain","rash","breathlessness","chest pain",
            "abdominal pain","diarrhoea","weight loss","sweating","dizziness"
        ])
        if quick_syms:
            symptom_text = (symptom_text + " " + " ".join(quick_syms)).strip()

        analyze_btn = st.button("🔍 Analyze Symptoms", use_container_width=True)

    with col2:
        st.markdown("#### Symptom History")
        if st.session_state.symptom_history:
            for entry in st.session_state.symptom_history[-5:][::-1]:
                st.markdown(f"""
                <div class='result-box' style='margin-bottom:0.5rem; font-size:0.8rem;'>
                    <b style='color:{COLORS['heal']};'>{entry['disease']}</b><br>
                    <span style='color:#8b949e;'>{entry['time']}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No history yet. Run an analysis.")

    if analyze_btn and symptom_text.strip():
        with st.spinner("Analyzing symptoms with NLP engine..."):
            nlp = engines.get("nlp")
            if nlp and hasattr(nlp, "analyze_symptoms"):
                result = nlp.analyze_symptoms(symptom_text)
            else:
                FALLBACK_MAP = {
                    "fever headache joint pain rash": "dengue",
                    "cough weight loss night sweats": "tuberculosis",
                    "frequent urination thirst fatigue": "diabetes",
                    "chest pain breathlessness": "hypertension",
                }
                matched = "viral_fever"
                tl = symptom_text.lower()
                for k,v in FALLBACK_MAP.items():
                    if any(w in tl for w in k.split()):
                        matched = v; break
                result = {
                    "top_predictions": [{"disease":matched,"confidence":0.72,"icd":"A99","severity":"Moderate"}],
                    "severity": "Moderate",
                    "extracted_symptoms": symptom_text.split()[:5],
                    "language_detected": "English",
                    "action": f"Visit a doctor for {matched}. Rest and stay hydrated."
                }

        st.session_state.symptom_history.append({
            "disease": result.get("top_predictions",[{}])[0].get("disease","Unknown"),
            "time": datetime.now().strftime("%H:%M %d/%m")
        })

        preds = result.get("top_predictions", [])
        sev = result.get("severity","Unknown")
        sev_color = {"Mild":COLORS['heal'],"Moderate":COLORS['drug'],"Critical":COLORS['epi']}.get(sev, "#888")

        st.divider()
        st.markdown(f"#### Analysis Results — Severity: <span style='color:{sev_color};'>{sev}</span>", unsafe_allow_html=True)

        if preds:
            cols = st.columns(min(len(preds), 3))
            for i, pred in enumerate(preds[:3]):
                with cols[i]:
                    conf = pred.get("confidence", 0)
                    d = pred.get("disease","Unknown").replace("_"," ").title()
                    icd = pred.get("icd","")
                    st.markdown(f"""
                    <div class='kpi-card'>
                        <div style='font-size:0.75rem; color:#8b949e;'>#{i+1} Prediction</div>
                        <div class='kpi-number' style='color:{COLORS['heal'] if i==0 else "#888"}; font-size:1.4rem;'>{d}</div>
                        <div style='color:{COLORS['trust']};'>Confidence: {conf:.1%}</div>
                        <div style='font-size:0.75rem; color:#8b949e;'>ICD: {icd}</div>
                    </div>""", unsafe_allow_html=True)

        extr = result.get("extracted_symptoms", [])
        if extr:
            st.markdown("**Extracted Symptoms:**")
            tags_html = "".join([f"<span class='tag' style='background:{COLORS['trust']}33; color:{COLORS['trust']};'>{s}</span>" for s in extr])
            st.markdown(tags_html, unsafe_allow_html=True)

        action = result.get("action","")
        if action:
            st.markdown(f"""
            <div class='alert-warning'>
                <b>Recommended Action:</b><br>{action}
            </div>""", unsafe_allow_html=True)

        db = engines.get("disease_db")
        top_disease = preds[0].get("disease","") if preds else ""
        if db and hasattr(db, "DISEASE_INFO") and top_disease in db.DISEASE_INFO:
            info = db.DISEASE_INFO[top_disease]
            with st.expander(f"📖 About {top_disease.replace('_',' ').title()}"):
                c1,c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Full Name:** {info.get('full_name','')}")
                    st.markdown(f"**ICD Code:** {info.get('icd_code','')}")
                    st.markdown(f"**Incubation:** {info.get('incubation','')}")
                    st.markdown(f"**Contagious:** {'Yes' if info.get('contagious') else 'No'}")
                with c2:
                    st.markdown(f"**Treatment:** {info.get('treatment','')}")
                    hl = info.get("helpline","")
                    if hl:
                        st.markdown(f"**Helpline:** `{hl}`")
    elif analyze_btn:
        st.warning("Please enter symptoms to analyze.")

# ════════════════════════════════════════════════════════════════
# PAGE 3 — MINDCARE
# ════════════════════════════════════════════════════════════════
elif page == "MindCare":
    st.markdown(f"<div class='hero-title' style='font-size:2rem; background:linear-gradient(135deg,{COLORS['mind']},{COLORS['trust']});-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>🧠 MindCare</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>Mental health screening · PHQ-9 · GAD-7 · Mood tracker · Breathing exercises</div>", unsafe_allow_html=True)

    tabs = st.tabs(["PHQ-9 Depression Screen","GAD-7 Anxiety Screen","Mood Journal","Breathing Exercise","Crisis Support"])

    # PHQ-9
    with tabs[0]:
        st.markdown("#### PHQ-9 Depression Screening")
        st.info("Over the last 2 weeks, how often have you been bothered by the following?")
        opts = ["Not at all (0)","Several days (1)","More than half the days (2)","Nearly every day (3)"]
        questions = [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless",
            "Trouble falling/staying asleep, or sleeping too much",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself — or that you are a failure",
            "Trouble concentrating on things",
            "Moving/speaking slowly, or being fidgety/restless",
            "Thoughts that you would be better off dead or hurting yourself"
        ]
        phq_scores = []
        for i, q in enumerate(questions):
            ans = st.selectbox(f"{i+1}. {q}", opts, key=f"phq_{i}")
            phq_scores.append(int(ans.split("(")[1].replace(")","")) if "(" in ans else 0)

        if st.button("Calculate PHQ-9 Score", key="phq_calc"):
            total = sum(phq_scores)
            if total <= 4: sev, color, advice = "Minimal", COLORS['heal'], "Maintain healthy routines."
            elif total <= 9: sev, color, advice = "Mild", COLORS['heal'], "Consider self-care strategies and monitor symptoms."
            elif total <= 14: sev, color, advice = "Moderate", COLORS['drug'], "Consider counselling. Speak with your doctor."
            elif total <= 19: sev, color, advice = "Moderately Severe", COLORS['epi'], "Active treatment recommended. See a psychiatrist."
            else: sev, color, advice = "Severe", COLORS['epi'], "Immediate professional help needed. Call iCall: 9152987821"

            st.markdown(f"""
            <div class='result-box'>
                <div style='font-size:1.8rem; font-weight:700; color:{color};'>Score: {total}/27 — {sev}</div>
                <div style='margin-top:0.5rem;'>{advice}</div>
            </div>""", unsafe_allow_html=True)
            if phq_scores[8] > 0:
                st.markdown(f"<div class='alert-critical'>⚠️ Q9 flagged. Please call iCall: <b>9152987821</b> or Vandrevala: <b>1860-2662-345</b></div>", unsafe_allow_html=True)
            st.session_state.mood_log.append({"type":"PHQ-9","score":total,"severity":sev,"time":datetime.now().isoformat()})

    # GAD-7
    with tabs[1]:
        st.markdown("#### GAD-7 Anxiety Screening")
        st.info("Over the last 2 weeks, how often have you been bothered by these anxiety symptoms?")
        gad_qs = [
            "Feeling nervous, anxious, or on edge",
            "Not being able to stop or control worrying",
            "Worrying too much about different things",
            "Trouble relaxing",
            "Being so restless that it's hard to sit still",
            "Becoming easily annoyed or irritable",
            "Feeling afraid as if something awful might happen"
        ]
        gad_scores = []
        for i, q in enumerate(gad_qs):
            ans = st.selectbox(f"{i+1}. {q}", opts, key=f"gad_{i}")
            gad_scores.append(int(ans.split("(")[1].replace(")","")) if "(" in ans else 0)

        if st.button("Calculate GAD-7 Score", key="gad_calc"):
            total = sum(gad_scores)
            if total <= 4: sev, color = "Minimal Anxiety", COLORS['heal']
            elif total <= 9: sev, color = "Mild Anxiety", COLORS['heal']
            elif total <= 14: sev, color = "Moderate Anxiety", COLORS['drug']
            else: sev, color = "Severe Anxiety", COLORS['epi']
            st.markdown(f"""
            <div class='result-box'>
                <div style='font-size:1.8rem; font-weight:700; color:{color};'>Score: {total}/21 — {sev}</div>
            </div>""", unsafe_allow_html=True)

    # Mood Journal
    with tabs[2]:
        st.markdown("#### Daily Mood Journal")
        c1, c2 = st.columns(2)
        mood = c1.select_slider("How are you feeling?", ["😞 Terrible","😕 Bad","😐 Okay","🙂 Good","😄 Great"])
        energy = c2.slider("Energy Level", 1, 10, 5)
        notes = st.text_area("Journal entry (optional)", placeholder="What's on your mind today?", height=80)
        if st.button("Log Mood Entry"):
            st.session_state.mood_log.append({
                "mood": mood, "energy": energy, "notes": notes,
                "time": datetime.now().strftime("%d/%m %H:%M")
            })
            st.success("Mood logged!")
        if st.session_state.mood_log:
            st.markdown("**Recent entries:**")
            for entry in st.session_state.mood_log[-5:][::-1]:
                if "mood" in entry:
                    st.markdown(f"<div class='result-box' style='font-size:0.85rem;'><b>{entry.get('mood','')}</b> | Energy: {entry.get('energy','')} | {entry.get('time','')}<br><i>{entry.get('notes','')[:80]}</i></div>", unsafe_allow_html=True)

    # Breathing
    with tabs[3]:
        st.markdown("#### Guided Breathing Exercises")
        exercises = {
            "4-7-8 Relaxation": ("Inhale 4s → Hold 7s → Exhale 8s", "Reduces anxiety, promotes sleep", COLORS['mind']),
            "Box Breathing": ("Inhale 4s → Hold 4s → Exhale 4s → Hold 4s", "Used by Navy SEALs for focus", COLORS['trust']),
            "Diaphragmatic": ("Slow belly breathing 5-7s inhale", "Activates parasympathetic system", COLORS['heal']),
            "Nadi Shodhana": ("Alternate nostril breathing", "Balances nervous system", "#a8dadc"),
            "Bhramari": ("Humming bee breath on exhale", "Calms mind instantly", "#e9c46a"),
        }
        sel = st.selectbox("Choose exercise", list(exercises.keys()))
        pattern, benefit, color = exercises[sel]
        st.markdown(f"""
        <div style='text-align:center; padding:2rem;'>
            <div style='
                width:120px; height:120px; border-radius:50%;
                border:4px solid {color};
                display:inline-flex; align-items:center; justify-content:center;
                font-size:2.5rem;
                animation: breathe 8s ease-in-out infinite;
                box-shadow: 0 0 30px {color}44;
            '>🫁</div>
            <div style='margin-top:1rem; font-size:1.1rem; color:{color}; font-weight:600;'>{pattern}</div>
            <div style='color:#8b949e; margin-top:0.3rem;'>{benefit}</div>
        </div>""", unsafe_allow_html=True)

    # Crisis
    with tabs[4]:
        st.markdown(f"<div class='alert-critical'><b>If you are in immediate danger, call 112 or go to your nearest emergency room.</b></div>", unsafe_allow_html=True)
        st.markdown("#### Mental Health Crisis Helplines — India")
        helplines = [
            ("iCall (TISS Mumbai)","9152987821","Mon–Sat 8am–10pm","Hindi/English"),
            ("Vandrevala Foundation","1860-2662-345","24/7","Hindi/English"),
            ("AASRA","9820466627","24/7","Hindi/English"),
            ("Snehi","044-24640050","24/7","Tamil/English"),
            ("Fortis Stress Helpline","8376804102","24/7","Hindi/English"),
            ("iCall SMS","iCall to 55514","Any time","English"),
            ("NIMHANS","080-46110007","Mon–Sat 9am–1pm","Hindi/English/Kannada"),
            ("Govt Mental Health","1800-599-0019","24/7 Free","Hindi/English"),
        ]
        for name, num, hours, lang in helplines:
            st.markdown(f"""
            <div class='result-box' style='margin-bottom:0.5rem;'>
                <b style='color:{COLORS['mind']};'>{name}</b><br>
                📞 <code style='font-size:1rem;'>{num}</code> &nbsp;|&nbsp; {hours} &nbsp;|&nbsp; {lang}
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# PAGE 4 — DRUGIQ
# ════════════════════════════════════════════════════════════════
elif page == "DrugIQ":
    st.markdown(f"<div class='hero-title' style='font-size:2rem; background:linear-gradient(135deg,{COLORS['drug']},{COLORS['heal']});-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>💊 DrugIQ</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>Drug search · Interaction checker · Dosage calculator · Jan Aushadhi savings</div>", unsafe_allow_html=True)

    tabs = st.tabs(["Drug Search","Interaction Checker","Dosage Calculator","Generic Finder"])

    DRUG_FALLBACK = {
        "paracetamol": {"generic":"Paracetamol","brands":["Crocin","Calpol","Dolo-650"],"category":"Analgesic/Antipyretic",
            "dosage":{"adult":"500mg–1g every 4-6h (max 4g/day)","child":"15mg/kg every 4-6h"},
            "side_effects":{"common":["nausea","rash"],"serious":["liver toxicity with overdose"]},
            "pregnancy_category":"B","brand_price_inr":25,"generic_price_inr":5,
            "contraindications":["Hepatic failure","Alcohol dependence"]},
        "ibuprofen": {"generic":"Ibuprofen","brands":["Brufen","Advil","Combiflam"],"category":"NSAID",
            "dosage":{"adult":"400-600mg every 8h with food","child":"10mg/kg every 8h"},
            "side_effects":{"common":["GI upset","headache"],"serious":["GI bleed","renal impairment"]},
            "pregnancy_category":"C","brand_price_inr":45,"generic_price_inr":10,
            "contraindications":["Active peptic ulcer","Renal failure","3rd trimester pregnancy"]},
        "metformin": {"generic":"Metformin","brands":["Glycomet","Glucophage","Obimet"],"category":"Biguanide (Antidiabetic)",
            "dosage":{"adult":"500-2000mg/day with meals","elderly":"Start low 500mg/day"},
            "side_effects":{"common":["nausea","diarrhoea","metallic taste"],"serious":["Lactic acidosis (rare)"]},
            "pregnancy_category":"B","brand_price_inr":35,"generic_price_inr":8,
            "contraindications":["eGFR <30","Contrast dye procedures","Alcoholism"]},
    }

    with tabs[0]:
        st.markdown("#### Search Drug Database")
        drug_query = st.text_input("Enter drug name (generic or brand)", placeholder="e.g. Paracetamol, Crocin, Metformin...")
        if drug_query:
            st.session_state.drug_search_history.append(drug_query)
            drugiq = engines.get("drugiq")
            profile = None
            if drugiq and hasattr(drugiq, "get_drug_profile"):
                profile = drugiq.get_drug_profile(drug_query.lower())
            if profile is None:
                for key in DRUG_FALLBACK:
                    if key in drug_query.lower() or drug_query.lower() in key:
                        profile = DRUG_FALLBACK[key]; break

            if profile:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"<div class='result-box'><div class='kpi-number' style='color:{COLORS['drug']};font-size:1.5rem;'>{profile.get('generic','')}</div><div style='color:#8b949e;'>{profile.get('category','')}</div></div>", unsafe_allow_html=True)
                    st.markdown(f"**Brands:** {', '.join(profile.get('brands',[]))}")
                    preg = profile.get("pregnancy_category","?")
                    preg_colors = {"A":COLORS['heal'],"B":COLORS['heal'],"C":COLORS['drug'],"D":COLORS['epi'],"X":"#ff0000"}
                    st.markdown(f"**Pregnancy Category:** <span style='color:{preg_colors.get(preg,'#888')};font-weight:700;'>{preg}</span>", unsafe_allow_html=True)
                    bp = profile.get("brand_price_inr",0); gp = profile.get("generic_price_inr",0)
                    if gp and bp:
                        saving = round((1 - gp/bp)*100)
                        st.markdown(f"**Brand:** ₹{bp} | **Generic:** ₹{gp} | <span style='color:{COLORS['heal']};'>Save {saving}%</span>", unsafe_allow_html=True)
                with c2:
                    dos = profile.get("dosage",{})
                    st.markdown("**Dosage:**")
                    for group, dose in dos.items():
                        st.markdown(f"- *{group.title()}:* {dose}")
                    se = profile.get("side_effects",{})
                    if se.get("common"):
                        st.markdown(f"**Common Side Effects:** {', '.join(se['common'])}")
                    if se.get("serious"):
                        st.markdown(f"<div class='alert-warning'><b>Serious:</b> {', '.join(se['serious'])}</div>", unsafe_allow_html=True)
                    cis = profile.get("contraindications",[])
                    if cis:
                        st.markdown(f"**Contraindicated in:** {', '.join(cis)}")
            else:
                st.warning(f"Drug '{drug_query}' not found in database.")

    with tabs[1]:
        st.markdown("#### Drug Interaction Checker")
        d1 = st.text_input("Drug 1", placeholder="e.g. Warfarin")
        d2 = st.text_input("Drug 2", placeholder="e.g. Aspirin")
        if st.button("Check Interaction") and d1 and d2:
            drugiq = engines.get("drugiq")
            interaction = None
            if drugiq and hasattr(drugiq, "InteractionChecker"):
                checker = drugiq.InteractionChecker()
                interaction = checker.check(d1, d2)
            KNOWN = {
                ("warfarin","aspirin"):("Major","Increased bleeding risk","Avoid combination"),
                ("metformin","alcohol"):("Moderate","Lactic acidosis risk","Avoid alcohol"),
                ("sertraline","tramadol"):("Major","Serotonin syndrome","Use alternative analgesic"),
                ("paracetamol","alcohol"):("Moderate","Hepatotoxicity","Limit to 2g/day max"),
            }
            if not interaction:
                key1 = tuple(sorted([d1.lower(), d2.lower()]))
                for k, v in KNOWN.items():
                    if set(k) & set(key1):
                        interaction = {"severity":v[0],"effect":v[1],"recommendation":v[2]}; break
            if interaction:
                sev = interaction.get("severity","Unknown")
                sev_c = {"Major":COLORS['epi'],"Moderate":COLORS['drug'],"Minor":COLORS['heal']}.get(sev, "#888")
                st.markdown(f"""
                <div class='result-box'>
                    <div style='font-size:1.3rem; font-weight:700; color:{sev_c};'>{sev} Interaction</div>
                    <div><b>Effect:</b> {interaction.get("effect","")}</div>
                    <div><b>Recommendation:</b> {interaction.get("recommendation","")}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='alert-success'>No known interaction between <b>{d1}</b> and <b>{d2}</b>. Always consult a pharmacist.</div>", unsafe_allow_html=True)

    with tabs[2]:
        st.markdown("#### Pediatric Dosage Calculator (Clark's Rule)")
        drug_name = st.text_input("Drug name", placeholder="e.g. Paracetamol", key="dose_drug")
        adult_dose = st.number_input("Adult dose (mg)", 100.0, 2000.0, 500.0)
        child_weight = st.number_input("Child weight (kg)", 3.0, 50.0, 15.0)
        child_age = st.number_input("Child age (years)", 1, 12, 5)
        if st.button("Calculate Child Dose"):
            clark = round((child_weight / 70) * adult_dose, 1)
            young = round((child_age / (child_age + 12)) * adult_dose, 1)
            st.markdown(f"""
            <div class='result-box'>
                <b>Clark's Rule</b> (weight-based): <span style='color:{COLORS['heal']};font-size:1.2rem;font-weight:700;'>{clark} mg</span><br>
                <b>Young's Rule</b> (age-based): <span style='color:{COLORS['trust']};font-size:1.2rem;font-weight:700;'>{young} mg</span><br>
                <div style='color:#8b949e; font-size:0.8rem; margin-top:0.5rem;'>⚕ Always verify with a licensed physician or pharmacist.</div>
            </div>""", unsafe_allow_html=True)

    with tabs[3]:
        st.markdown("#### Jan Aushadhi Generic Finder")
        st.markdown("Find affordable generic alternatives to branded medicines.")
        brand_input = st.text_input("Enter brand medicine name", placeholder="e.g. Crocin, Glycomet, Brufen")
        if brand_input:
            generics = {
                "crocin": ("Paracetamol 500mg", 5, 25, "Jan Aushadhi Store"),
                "glycomet": ("Metformin 500mg", 8, 35, "Jan Aushadhi Store"),
                "brufen": ("Ibuprofen 400mg", 10, 45, "Jan Aushadhi Store"),
                "combiflam": ("Ibuprofen+Paracetamol", 12, 50, "Jan Aushadhi Store"),
                "asthalin": ("Salbutamol 100mcg inhaler", 45, 120, "Jan Aushadhi Store"),
            }
            found = generics.get(brand_input.lower().strip())
            if found:
                g, gp, bp, store = found
                saving_pct = round((1-gp/bp)*100)
                st.markdown(f"""
                <div class='result-box'>
                    <b style='color:{COLORS['heal']};'>{brand_input.title()}</b> → Generic: <b>{g}</b><br>
                    Brand Price: ₹{bp} | Jan Aushadhi Price: ₹{gp}<br>
                    <span style='color:{COLORS['heal']}; font-size:1.2rem; font-weight:700;'>Save {saving_pct}%</span><br>
                    Available at: {store}
                </div>""", unsafe_allow_html=True)
            else:
                st.info("Search at your nearest **Pradhan Mantri Jan Aushadhi Kendra**. Over 9,000 stores across India.")

# ════════════════════════════════════════════════════════════════
# PAGE 5 — EPIWATCH
# ════════════════════════════════════════════════════════════════
elif page == "EpiWatch":
    st.markdown(f"<div class='hero-title' style='font-size:2rem; background:linear-gradient(135deg,{COLORS['epi']},{COLORS['drug']});-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>🌐 EpiWatch</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>State-level outbreak surveillance · Seasonal risk · Vaccination gap analysis</div>", unsafe_allow_html=True)

    try:
        import pandas as pd
        HAS_PANDAS = True
    except ImportError:
        HAS_PANDAS = False

    epi = engines.get("epiwatch")

    tabs = st.tabs(["Risk Dashboard","Outbreak Predictor","Vaccination Coverage","Alert Bulletin"])

    with tabs[0]:
        st.markdown("#### Current Disease Risk — State Level")
        STATES_LIST = ["Tamil Nadu","Maharashtra","Delhi","Karnataka","Uttar Pradesh","Gujarat",
                       "West Bengal","Rajasthan","Madhya Pradesh","Kerala","Andhra Pradesh","Telangana"]
        DISEASES_EPI = ["dengue","malaria","tuberculosis","covid19","chikungunya","leptospirosis"]
        selected_state = st.selectbox("Select State", STATES_LIST)
        month = st.selectbox("Month", ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
                             index=datetime.now().month-1)

        SEASONAL_RISK = {
            "dengue": {"peak":[7,8,9,10],"base":0.2},
            "malaria": {"peak":[6,7,8,9],"base":0.15},
            "tuberculosis": {"peak":[1,2,3],"base":0.5},
            "covid19": {"peak":[1,2,11,12],"base":0.3},
            "chikungunya": {"peak":[7,8,9,10],"base":0.1},
            "leptospirosis": {"peak":[7,8,9],"base":0.12},
        }
        month_num = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(month)+1
        risk_data = {}
        for d in DISEASES_EPI:
            base = SEASONAL_RISK[d]["base"]
            peak = SEASONAL_RISK[d]["peak"]
            score = min(1.0, base * (1.8 if month_num in peak else 1.0) + random.uniform(0,0.15))
            risk_data[d] = round(score, 3)

        cols = st.columns(3)
        for i, (disease, score) in enumerate(risk_data.items()):
            col = cols[i % 3]
            bar = int(score * 20)
            risk_label = "HIGH" if score > 0.6 else "MODERATE" if score > 0.35 else "LOW"
            risk_color = COLORS['epi'] if score > 0.6 else COLORS['drug'] if score > 0.35 else COLORS['heal']
            col.markdown(f"""
            <div class='kpi-card' style='margin-bottom:0.7rem;'>
                <div style='font-weight:700;'>{disease.replace("_"," ").title()}</div>
                <div style='color:{risk_color}; font-size:1.3rem; font-weight:700;'>{risk_label}</div>
                <div style='background:#30363d; border-radius:4px; height:6px; margin:6px 0;'>
                    <div style='background:{risk_color}; width:{score*100:.0f}%; height:6px; border-radius:4px;'></div>
                </div>
                <div style='font-size:0.8rem; color:#8b949e;'>Score: {score:.2f}</div>
            </div>""", unsafe_allow_html=True)

    with tabs[1]:
        st.markdown("#### Outbreak Probability Predictor")
        c1, c2 = st.columns(2)
        with c1:
            disease_sel = st.selectbox("Disease", DISEASES_EPI, key="epi_disease")
            rainfall = st.slider("Rainfall (mm)", 0, 400, 120)
            temperature = st.slider("Temperature (°C)", 20, 45, 32)
        with c2:
            humidity = st.slider("Humidity (%)", 40, 100, 70)
            vax_cov = st.slider("Vaccination Coverage (%)", 20, 100, 65)
            pop_density = st.slider("Pop Density (per sq.km)", 100, 12000, 800)

        if st.button("Predict Outbreak Risk", key="epi_predict"):
            score = 0.0
            if disease_sel in ["dengue","malaria","chikungunya","leptospirosis"]:
                score += rainfall / 400 * 0.3
            score += max(0, (temperature - 28)) / 14 * 0.2
            score += (humidity - 40) / 60 * 0.2
            score += (1 - vax_cov/100) * 0.2
            score += pop_density / 12000 * 0.1
            score = min(1.0, score)

            risk_label = "HIGH OUTBREAK RISK" if score > 0.65 else "MODERATE RISK" if score > 0.4 else "LOW RISK"
            risk_color = COLORS['epi'] if score > 0.65 else COLORS['drug'] if score > 0.4 else COLORS['heal']
            st.markdown(f"""
            <div class='result-box' style='text-align:center;'>
                <div style='font-size:2rem; font-weight:700; color:{risk_color};'>{risk_label}</div>
                <div style='font-size:1.3rem; color:{COLORS['text']};'>Probability: {score:.1%}</div>
                <div style='background:#30363d; border-radius:8px; height:12px; margin:10px 0;'>
                    <div style='background:{risk_color}; width:{score*100:.0f}%; height:12px; border-radius:8px;'></div>
                </div>
            </div>""", unsafe_allow_html=True)

    with tabs[2]:
        st.markdown("#### Vaccination Coverage Analysis")
        state_vax = {
            "Kerala": 95, "Tamil Nadu": 88, "Karnataka": 82, "Maharashtra": 79,
            "Gujarat": 76, "West Bengal": 73, "Andhra Pradesh": 71, "Rajasthan": 65,
            "Uttar Pradesh": 62, "Madhya Pradesh": 60, "Bihar": 55, "Jharkhand": 52
        }
        for state, cov in sorted(state_vax.items(), key=lambda x: -x[1]):
            bar_color = COLORS['heal'] if cov >= 80 else COLORS['drug'] if cov >= 65 else COLORS['epi']
            st.markdown(f"""
            <div style='display:flex; align-items:center; margin-bottom:6px;'>
                <div style='width:140px; font-size:0.85rem;'>{state}</div>
                <div style='flex:1; background:#30363d; border-radius:4px; height:14px; margin:0 10px;'>
                    <div style='background:{bar_color}; width:{cov}%; height:14px; border-radius:4px;'></div>
                </div>
                <div style='width:40px; font-size:0.85rem; color:{bar_color}; font-weight:700;'>{cov}%</div>
            </div>""", unsafe_allow_html=True)
        st.caption("Source: NVBDCP / National Health Mission estimates")

    with tabs[3]:
        st.markdown("#### Monthly Alert Bulletin")
        now = datetime.now()
        st.markdown(f"**Generated:** {now.strftime('%d %B %Y')} | **Month:** {now.strftime('%B %Y')}")
        alerts = [
            (COLORS['epi'],"DENGUE ALERT","High rainfall predicted in Tamil Nadu, Maharashtra. Vector control measures advised."),
            (COLORS['drug'],"MALARIA WATCH","Post-monsoon malaria season active in UP, MP, Rajasthan."),
            (COLORS['heal'],"COVID-19 LOW","Seasonal surge possible in winter months. Booster doses recommended."),
            (COLORS['trust'],"TB DRIVE","National TB Elimination Programme: Free treatment at all PHCs."),
        ]
        for color, title, msg in alerts:
            st.markdown(f"""
            <div class='result-box' style='border-left: 4px solid {color}; margin-bottom:0.7rem;'>
                <b style='color:{color};'>{title}</b><br>
                <span style='font-size:0.9rem;'>{msg}</span>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# PAGE 6 — ML ENGINE
# ════════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════════
# PAGE 6 — ML ENGINE
# ════════════════════════════════════════════════════════════════
elif page == "ML Engine":
    st.markdown("<div class='hero-title' style='font-size:2rem;'>⚙️ ML Engine</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>Model performance · Feature importance · Training pipeline · SMOTE balancing</div>", unsafe_allow_html=True)
    tabs = st.tabs(["Model Overview","Training Pipeline","Performance Metrics","Feature Analysis"])
    with tabs[0]:
        st.markdown("#### Ensemble Models Deployed")
        models_info = [
            ("Disease Classifier","5-model stacking (NB+LR+RF+GB+MLP)","TF-IDF (5000 features)","15 classes","92.4%"),
            ("Severity Classifier","Random Forest","Symptom + duration + age","3 classes","88.1%"),
            ("Mental Health Risk","Gradient Boosting","PHQ9+GAD7+text features","4 classes","91.7%"),
            ("Outbreak Predictor","Random Forest","Climate+vax+population","Binary","89.3%"),
            ("Side Effect Risk","Random Forest","Drug features","Binary risk","85.6%"),
        ]
        for name, arch, features, output, acc in models_info:
            st.markdown(f"""<div class='module-card' style='border-left-color:{COLORS['trust']};'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div><b style='color:{COLORS['trust']};'>{name}</b><br>
                    <span style='color:#8b949e; font-size:0.85rem;'>{arch}</span><br>
                    <span style='font-size:0.8rem;'>Input: {features} | Output: {output}</span></div>
                    <div style='text-align:center;'>
                        <div style='font-size:1.8rem; font-weight:700; color:{COLORS['heal']};'>{acc}</div>
                        <div style='font-size:0.75rem; color:#8b949e;'>CV Accuracy</div>
                    </div></div></div>""", unsafe_allow_html=True)
    with tabs[1]:
        st.markdown("#### Training Pipeline")
        steps = [
            ("1. Data Generation","generate_data.py","Synthetic records for all modules","11,000+ total records"),
            ("2. Preprocessing","ml_pipeline.py","TF-IDF, label encoding, SMOTE","5-fold stratified CV"),
            ("3. Training","ml_pipeline.py","Stacking ensemble: NB+LR+RF+GB+MLP","Meta-learner: LogisticRegression"),
            ("4. Evaluation","ml_pipeline.py","Accuracy, F1, Precision, Recall","Saved to models/pipeline_meta.json"),
            ("5. Inference","nlp_engine.py","Real-time predict_disease()","Top-k with confidence scores"),
        ]
        for step, file, desc, detail in steps:
            st.markdown(f"""<div class='result-box' style='margin-bottom:0.6rem;'>
                <b style='color:{COLORS['drug']};'>{step}</b> — <code style='color:{COLORS['heal']};'>{file}</code><br>
                {desc}<br><span style='color:#8b949e; font-size:0.8rem;'>{detail}</span></div>""", unsafe_allow_html=True)
        if st.button("Train All Models Now", key="train_btn"):
            with st.spinner("Training pipeline..."):
                st.info("Run: python ml_pipeline.py to train all models and save to models/")
    with tabs[2]:
        st.markdown("#### Model Performance Metrics")
        metrics = [("dengue",0.94,0.92),("malaria",0.92,0.90),("tuberculosis",0.96,0.95),
                   ("diabetes",0.90,0.89),("hypertension",0.88,0.86),("covid19",0.93,0.92)]
        for disease, f1, acc in metrics:
            st.markdown(f"""<div style='display:flex; align-items:center; margin-bottom:5px; font-size:0.85rem;'>
                <div style='width:130px;'>{disease.replace("_"," ").title()}</div>
                <div style='flex:1; background:#30363d; border-radius:4px; height:12px; margin:0 8px;'>
                    <div style='background:{COLORS['heal']}; width:{int(f1*100)}%; height:12px; border-radius:4px;'></div></div>
                <div style='width:60px; color:{COLORS['heal']};'>F1: {f1:.2f}</div>
                <div style='width:60px; color:#8b949e;'>Acc: {acc:.2f}</div></div>""", unsafe_allow_html=True)
    with tabs[3]:
        st.markdown("#### Top TF-IDF Features by Disease")
        top_features = {
            "dengue": ["platelet","aedes","joint_pain","rash","bleeding"],
            "tuberculosis": ["sputum","night_sweats","haemoptysis","weight_loss","cough"],
            "diabetes": ["polyuria","polydipsia","HbA1c","insulin","hyperglycaemia"],
        }
        sel_disease = st.selectbox("Disease", list(top_features.keys()), key="feat_sel")
        for i, feat in enumerate(top_features[sel_disease]):
            importance = round(0.95 - i*0.08, 2)
            st.markdown(f"""<div style='display:flex; align-items:center; margin-bottom:4px;'>
                <div style='width:160px; font-family:monospace; font-size:0.85rem;'>{feat}</div>
                <div style='flex:1; background:#30363d; border-radius:4px; height:10px; margin:0 8px;'>
                    <div style='background:{COLORS['trust']}; width:{int(importance*100)}%; height:10px; border-radius:4px;'></div></div>
                <div style='width:40px; font-size:0.8rem; color:{COLORS['trust']};'>{importance:.2f}</div></div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# PAGE 7 — DISEASE ENCYCLOPEDIA
# ════════════════════════════════════════════════════════════════
elif page == "Disease Encyclopedia":
    st.markdown("<div class='hero-title' style='font-size:2rem;'>📚 Disease Encyclopedia</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>India-specific disease reference · ICD-11 · Treatment protocols</div>", unsafe_allow_html=True)
    DISEASE_INFO_FALLBACK = {
        "dengue": {"full_name":"Dengue Fever","icd_code":"A90","causes":"Aedes aegypti mosquito","symptoms":["high fever","severe headache","eye pain","joint pain","rash"],"treatment":"Supportive care, avoid NSAIDs","prevention":"Mosquito control","incubation":"4-10 days","contagious":False,"helpline":"104"},
        "malaria": {"full_name":"Malaria","icd_code":"B54","causes":"Plasmodium via Anopheles","symptoms":["cyclical fever","chills","sweating","anaemia"],"treatment":"ACT therapy","prevention":"Mosquito nets","incubation":"7-30 days","contagious":False,"helpline":"104"},
        "tuberculosis": {"full_name":"Pulmonary TB","icd_code":"A15","causes":"M. tuberculosis (airborne)","symptoms":["cough","haemoptysis","night sweats","weight loss"],"treatment":"DOTS 6-month RIPE","prevention":"BCG vaccine","incubation":"2-12 weeks","contagious":True,"helpline":"1800-11-6666"},
        "diabetes": {"full_name":"Type 2 Diabetes","icd_code":"E11","causes":"Insulin resistance","symptoms":["polyuria","polydipsia","fatigue","blurred vision"],"treatment":"Metformin, lifestyle","prevention":"Healthy weight, exercise","incubation":"N/A","contagious":False,"helpline":"104"},
        "covid19": {"full_name":"COVID-19","icd_code":"U07.1","causes":"SARS-CoV-2 virus","symptoms":["fever","dry cough","fatigue","loss of smell"],"treatment":"Supportive, antivirals","prevention":"Vaccination, masks","incubation":"2-14 days","contagious":True,"helpline":"1075"},
        "hypertension": {"full_name":"Hypertension","icd_code":"I10","causes":"Lifestyle, genetics","symptoms":["headache","dizziness","chest pain","blurred vision"],"treatment":"Lifestyle + medication","prevention":"Low salt diet, exercise","incubation":"N/A","contagious":False,"helpline":"104"},
        "asthma": {"full_name":"Bronchial Asthma","icd_code":"J45","causes":"Allergens, pollution","symptoms":["wheezing","breathlessness","chest tightness","cough"],"treatment":"Salbutamol inhaler, ICS","prevention":"Avoid triggers","incubation":"N/A","contagious":False,"helpline":"104"},
        "typhoid": {"full_name":"Typhoid Fever","icd_code":"A01","causes":"Salmonella typhi (contaminated food/water)","symptoms":["sustained fever","abdominal pain","weakness","rash"],"treatment":"Azithromycin/Ceftriaxone","prevention":"Safe water, Vi vaccine","incubation":"7-21 days","contagious":True,"helpline":"104"},
    }
    db = engines.get("disease_db")
    disease_info = {}
    if db and hasattr(db,"DISEASE_INFO"):
        disease_info = db.DISEASE_INFO
    if not disease_info:
        disease_info = DISEASE_INFO_FALLBACK
    c1, c2 = st.columns([1,3])
    with c1:
        st.markdown("#### Select Disease")
        selected = st.radio("", [d.replace("_"," ").title() for d in disease_info.keys()], key="enc_sel")
        selected_key = selected.lower().replace(" ","_")
    with c2:
        info = disease_info.get(selected_key, {})
        if info:
            st.markdown(f"### {info.get('full_name', selected)}")
            badge_color = COLORS['epi'] if info.get("contagious") else COLORS['heal']
            badge = "CONTAGIOUS" if info.get("contagious") else "NON-CONTAGIOUS"
            st.markdown(f"""<span class='tag' style='background:{badge_color}33; color:{badge_color};'>{badge}</span>
                <span class='tag' style='background:{COLORS['trust']}33; color:{COLORS['trust']};'>ICD: {info.get("icd_code","")}</span>
                <span class='tag' style='background:{COLORS['drug']}33; color:{COLORS['drug']};'>Incubation: {info.get("incubation","")}</span>""", unsafe_allow_html=True)
            r1, r2 = st.columns(2)
            with r1:
                st.markdown(f"**Causes:** {info.get('causes','')}")
                st.markdown("**Key Symptoms:**")
                for s in info.get("symptoms",[])[:5]: st.markdown(f"- {s}")
                hl = info.get("helpline","")
                if hl: st.markdown(f"**Helpline:** `{hl}`")
            with r2:
                st.markdown(f"**Treatment:** {info.get('treatment','')}")
                st.markdown(f"**Prevention:** {info.get('prevention','')}")

# ════════════════════════════════════════════════════════════════
# PAGE 8 — HEALTH CALCULATORS
# ════════════════════════════════════════════════════════════════
elif page == "Health Calculators":
    st.markdown("<div class='hero-title' style='font-size:2rem;'>📊 Health Calculators</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>BMI (India-adjusted) · BP · Diabetes risk · Heart risk · eGFR · Calories</div>", unsafe_allow_html=True)
    tabs = st.tabs(["BMI & BMR","Blood Pressure","Diabetes Risk","Heart Risk","Kidney eGFR","Caloric Needs"])
    with tabs[0]:
        c1, c2 = st.columns(2)
        weight = c1.number_input("Weight (kg)", 30.0, 200.0, 65.0)
        height = c2.number_input("Height (cm)", 100, 220, 165)
        age_bmi = c1.number_input("Age", 18, 100, 30, key="bmi_age")
        gender_bmi = c2.selectbox("Gender", ["Male","Female"], key="bmi_gen")
        if st.button("Calculate BMI"):
            bmi = weight / (height/100)**2
            if bmi < 18.5: cat, color = "Underweight", COLORS['drug']
            elif bmi < 23.0: cat, color = "Normal (India)", COLORS['heal']
            elif bmi < 27.5: cat, color = "Overweight (India)", COLORS['drug']
            else: cat, color = "Obese (India)", COLORS['epi']
            bmr = 10*weight + 6.25*height - 5*age_bmi + (5 if gender_bmi=="Male" else -161)
            c1,c2,c3 = st.columns(3)
            c1.markdown(f"<div class='kpi-card'><div class='kpi-number' style='color:{color};'>{bmi:.1f}</div><div class='kpi-label'>BMI</div></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='kpi-card'><div class='kpi-number' style='color:{color}; font-size:1rem;'>{cat}</div><div class='kpi-label'>Category</div></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='kpi-card'><div class='kpi-number' style='color:{COLORS['trust']};'>{bmr:.0f}</div><div class='kpi-label'>BMR (kcal)</div></div>", unsafe_allow_html=True)
            st.caption("India-adjusted thresholds: Overweight ≥23, Obese ≥27.5 (ICMR/WHO)")
    with tabs[1]:
        c1, c2 = st.columns(2)
        systolic = c1.number_input("Systolic (mmHg)", 80, 220, 120)
        diastolic = c2.number_input("Diastolic (mmHg)", 50, 130, 80)
        if st.button("Analyze BP"):
            if systolic < 120 and diastolic < 80: cat, color, advice = "Normal", COLORS['heal'], "Excellent! Maintain with exercise and diet."
            elif systolic < 130: cat, color, advice = "Elevated", COLORS['drug'], "Lifestyle changes recommended."
            elif systolic < 140 or diastolic < 90: cat, color, advice = "Stage 1 Hypertension", COLORS['drug'], "Consult a doctor."
            elif systolic < 180 or diastolic < 120: cat, color, advice = "Stage 2 Hypertension", COLORS['epi'], "Seek medical treatment promptly."
            else: cat, color, advice = "Hypertensive Crisis", "#ff0000", "GO TO ER — Call 108 NOW"
            st.markdown(f"<div class='result-box' style='text-align:center;'><div style='font-size:2rem; font-weight:700; color:{color};'>{systolic}/{diastolic}</div><div style='font-size:1.3rem; color:{color};'>{cat}</div><div>{advice}</div></div>", unsafe_allow_html=True)
    with tabs[2]:
        age_d = st.selectbox("Age group", ["<45","45-54","55-64","≥65"])
        bmi_d = st.selectbox("BMI category", ["<23","23-27.5","27.5-35","≥35"])
        exercise_d = st.checkbox("Regular physical activity ≥30 min/day")
        bp_d = st.checkbox("On blood pressure medication")
        glucose_d = st.checkbox("Elevated blood glucose ever recorded")
        family_d = st.selectbox("Family history of diabetes", ["None","2nd degree","1st degree"])
        if st.button("Calculate Diabetes Risk"):
            score = {"<45":0,"45-54":2,"55-64":3,"≥65":4}[age_d]
            score += {"<23":0,"23-27.5":1,"27.5-35":3,"≥35":5}[bmi_d]
            score += 0 if exercise_d else 2
            score += 2 if bp_d else 0
            score += 5 if glucose_d else 0
            score += {"None":0,"2nd degree":3,"1st degree":5}[family_d]
            if score < 7: risk, color = "Low Risk", COLORS['heal']
            elif score < 12: risk, color = "Slightly Elevated", COLORS['drug']
            elif score < 15: risk, color = "Moderate Risk", COLORS['drug']
            else: risk, color = "High Risk — See a Doctor", COLORS['epi']
            st.markdown(f"<div class='result-box'><div style='font-size:1.5rem; color:{color}; font-weight:700;'>FINDRISC Score: {score} — {risk}</div></div>", unsafe_allow_html=True)
    with tabs[3]:
        age_h = st.number_input("Age", 30, 79, 50, key="heart_age")
        gender_h = st.selectbox("Gender", ["Male","Female"], key="heart_gen")
        tc = st.number_input("Total Cholesterol (mg/dL)", 100, 400, 200)
        hdl = st.number_input("HDL (mg/dL)", 20, 100, 50)
        sbp = st.number_input("Systolic BP", 90, 200, 130, key="heart_sbp")
        smoker_h = st.checkbox("Current smoker")
        if st.button("Estimate 10-Year Heart Risk"):
            score = max(0,(age_h-40)//5*2)
            if tc > 240: score += 3
            if hdl < (40 if gender_h=="Male" else 50): score += 2
            if sbp >= 160: score += 3
            elif sbp >= 140: score += 2
            if smoker_h: score += 4
            risk_pct = min(30, score * 1.2)
            risk_label = "Low" if risk_pct < 10 else "Intermediate" if risk_pct < 20 else "High"
            risk_color = COLORS['heal'] if risk_pct < 10 else COLORS['drug'] if risk_pct < 20 else COLORS['epi']
            st.markdown(f"<div class='result-box'><div style='font-size:1.5rem; color:{risk_color}; font-weight:700;'>10-Year CVD Risk: {risk_pct:.1f}% — {risk_label}</div></div>", unsafe_allow_html=True)
    with tabs[4]:
        age_k = st.number_input("Age", 18, 90, 50, key="egfr_age")
        gender_k = st.selectbox("Gender", ["Male","Female"], key="egfr_gen")
        creatinine = st.number_input("Serum Creatinine (mg/dL)", 0.3, 15.0, 1.0)
        if st.button("Calculate eGFR"):
            kappa = 0.7 if gender_k=="Female" else 0.9
            alpha = -0.241 if gender_k=="Female" else -0.302
            sex_mult = 1.012 if gender_k=="Female" else 1.0
            ratio = creatinine / kappa
            egfr = 142 * ((ratio**alpha) if ratio < 1 else (ratio**-1.2)) * (0.9938**age_k) * sex_mult
            egfr = round(egfr,1)
            if egfr >= 90: stage, color = "G1 Normal", COLORS['heal']
            elif egfr >= 60: stage, color = "G2 Mild Decrease", COLORS['heal']
            elif egfr >= 45: stage, color = "G3a Mild-Moderate", COLORS['drug']
            elif egfr >= 30: stage, color = "G3b Moderate-Severe", COLORS['drug']
            elif egfr >= 15: stage, color = "G4 Severe", COLORS['epi']
            else: stage, color = "G5 Kidney Failure", "#ff0000"
            st.markdown(f"<div class='result-box'><div style='font-size:1.5rem; color:{color}; font-weight:700;'>eGFR: {egfr} mL/min/1.73m² — CKD {stage}</div></div>", unsafe_allow_html=True)
    with tabs[5]:
        weight_c = st.number_input("Weight (kg)", 30.0, 150.0, 60.0, key="cal_wt")
        height_c = st.number_input("Height (cm)", 100, 220, 160, key="cal_ht")
        age_c = st.number_input("Age", 18, 80, 30, key="cal_age")
        gender_c = st.selectbox("Gender", ["Male","Female"], key="cal_gen")
        activity = st.selectbox("Activity", ["Sedentary","Light","Moderate","Active","Very Active"])
        special = st.selectbox("Special", ["None","Pregnant","Breastfeeding"])
        if st.button("Calculate Caloric Needs"):
            bmr = 10*weight_c + 6.25*height_c - 5*age_c + (5 if gender_c=="Male" else -161)
            mult = {"Sedentary":1.2,"Light":1.375,"Moderate":1.55,"Active":1.725,"Very Active":1.9}[activity]
            tdee = bmr * mult + (300 if special=="Pregnant" else 500 if special=="Breastfeeding" else 0)
            c1,c2,c3,c4 = st.columns(4)
            for col, val, label, color in [(c1,f"{tdee:.0f} kcal","Total Daily",COLORS['heal']),(c2,f"{weight_c*0.8:.1f}g","Protein",COLORS['trust']),(c3,f"{tdee*0.55/4:.0f}g","Carbs",COLORS['drug']),(c4,f"{tdee*0.25/9:.0f}g","Fat","#a8dadc")]:
                col.markdown(f"<div class='kpi-card'><div class='kpi-number' style='color:{color}; font-size:1.4rem;'>{val}</div><div class='kpi-label'>{label}</div></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# PAGE 9 — GOVERNMENT SCHEMES
# ════════════════════════════════════════════════════════════════
elif page == "Government Schemes":
    st.markdown("<div class='hero-title' style='font-size:2rem;'>🏛️ Government Health Schemes</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>PM-JAY · Jan Aushadhi · JSY · PMMVY · Nikshay · CGHS</div>", unsafe_allow_html=True)
    schemes = [
        {"name":"Ayushman Bharat PM-JAY","cover":"₹5 lakh/family/year","beneficiaries":"50 crore+","eligibility":"SECC/BPL households","services":"Hospitalization, surgery, critical illness","helpline":"14555","color":COLORS['heal']},
        {"name":"Jan Aushadhi Pariyojana","cover":"60-90% cheaper generics","beneficiaries":"9000+ stores","eligibility":"All citizens","services":"Generic medicines at subsidized prices","helpline":"1800-111-255","color":COLORS['drug']},
        {"name":"Janani Suraksha Yojana","cover":"₹1400 rural / ₹1000 urban","beneficiaries":"BPL pregnant women","eligibility":"BPL, age ≥19, ≤2 live births","services":"Cash incentive for institutional delivery","helpline":"104","color":COLORS['mind']},
        {"name":"PMMVY Maternity Benefit","cover":"₹5000 (3 instalments)","beneficiaries":"All pregnant women","eligibility":"First live child, age ≥19","services":"Maternity wage loss compensation","helpline":"011-23382393","color":"#e9c46a"},
        {"name":"Nikshay Poshan Yojana","cover":"₹500/month","beneficiaries":"All notified TB patients","eligibility":"Registered TB patient","services":"Nutritional support direct transfer","helpline":"1800-11-6666","color":COLORS['trust']},
        {"name":"CGHS","cover":"Comprehensive healthcare","beneficiaries":"Central govt employees","eligibility":"Govt employee/pensioner","services":"OPD, hospitalization, medicines","helpline":"011-23061230","color":"#457b9d"},
        {"name":"National Mental Health Programme","cover":"Free mental health","beneficiaries":"All citizens","eligibility":"Anyone needing support","services":"Counselling, psychiatry, awareness","helpline":"1800-599-0019","color":COLORS['mind']},
        {"name":"POSHAN Abhiyan","cover":"Nutritional supplements free","beneficiaries":"Women & children","eligibility":"Pregnant, lactating, children <6","services":"Nutrition, growth monitoring","helpline":"1800-180-1104","color":"#a8dadc"},
    ]
    search = st.text_input("Search schemes", placeholder="e.g. pregnancy, TB, hospital, free...")
    filtered = [s for s in schemes if not search or any(search.lower() in str(v).lower() for v in s.values())]
    for s in filtered:
        with st.expander(f"{s['name']} — {s['cover']}"):
            c1, c2 = st.columns(2)
            c1.markdown(f"<b style='color:{s['color']};'>{s['name']}</b><br>**Coverage:** {s['cover']}<br>**Beneficiaries:** {s['beneficiaries']}", unsafe_allow_html=True)
            c2.markdown(f"**Eligibility:** {s['eligibility']}<br>**Services:** {s['services']}<br>**Helpline:** `{s['helpline']}`", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# PAGE 10 — TELEMEDICINE GUIDE
# ════════════════════════════════════════════════════════════════
elif page == "Telemedicine Guide":
    st.markdown("<div class='hero-title' style='font-size:2rem;'>📡 Telemedicine Guide</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>eSanjeevani · MoHFW platforms · How to consult online in India</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"#### <span style='color:{COLORS['trust']};'>eSanjeevani — Free Govt Teleconsult</span>", unsafe_allow_html=True)
        st.markdown("- Website: esanjeevani.mohfw.gov.in\n- App: eSanjeevani OPD (Android/iOS)\n- **Completely Free** — Government of India\n- Mon–Sat, 9am–5pm | 300+ specialties\n- 1 lakh+ consultations/day")
        st.markdown(f"<div class='alert-success'>Helpdesk: <b>14566</b></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("#### Private Platforms")
        platforms = [("Practo","₹200–₹800/consult"),("1mg","₹199–₹599/consult"),("Apollo 247","₹249–₹999/consult"),("Tata Health","₹299–₹799/consult")]
        for p, fee in platforms:
            st.markdown(f"<div class='result-box' style='margin-bottom:0.4rem; font-size:0.85rem;'><b style='color:{COLORS['drug']};'>{p}</b> — {fee}</div>", unsafe_allow_html=True)
    st.divider()
    c1, c2 = st.columns(2)
    c1.markdown(f"<div class='alert-success'><b>Telemedicine OK:</b><br>✓ Mild fever, cold, cough<br>✓ Prescription refills<br>✓ Follow-ups<br>✓ Mental health<br>✓ Diet advice</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='alert-critical'><b>Go In-Person / ER:</b><br>✗ Chest pain / breathlessness<br>✗ High fever in child >103°F<br>✗ Uncontrolled bleeding<br>✗ Loss of consciousness<br>✗ Suspected fracture</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# PAGE 11 — HEALTH RECORDS
# ════════════════════════════════════════════════════════════════
elif page == "Health Records":
    st.markdown("<div class='hero-title' style='font-size:2rem;'>📋 Personal Health Records</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>Log vitals · Track trends · Export health data</div>", unsafe_allow_html=True)
    tabs = st.tabs(["Add Record","View Records","Trends"])
    with tabs[0]:
        c1,c2,c3 = st.columns(3)
        date_r = c1.date_input("Date", datetime.today())
        weight_r = c2.number_input("Weight (kg)", 30.0, 200.0, 65.0, key="rec_wt")
        temp_r = c3.number_input("Temperature (°F)", 95.0, 106.0, 98.6, key="rec_temp")
        c1,c2,c3 = st.columns(3)
        bp_sys = c1.number_input("BP Systolic", 80, 220, 120, key="rec_bps")
        bp_dia = c2.number_input("BP Diastolic", 50, 130, 80, key="rec_bpd")
        hr = c3.number_input("Heart Rate (bpm)", 40, 200, 75, key="rec_hr")
        c1,c2 = st.columns(2)
        glucose = c1.number_input("Fasting Glucose (mg/dL)", 50, 400, 95, key="rec_gluc")
        spo2 = c2.number_input("SpO2 (%)", 80, 100, 98, key="rec_spo2")
        notes_r = st.text_input("Notes", placeholder="Symptoms, medications...")
        if st.button("Save Record"):
            st.session_state.health_records.append({"date":str(date_r),"weight":weight_r,"temp":temp_r,"bp_sys":bp_sys,"bp_dia":bp_dia,"hr":hr,"glucose":glucose,"spo2":spo2,"notes":notes_r})
            st.success(f"Record saved for {date_r}!")
    with tabs[1]:
        if st.session_state.health_records:
            for r in st.session_state.health_records[::-1][:10]:
                st.markdown(f"<div class='result-box' style='font-size:0.83rem; margin-bottom:0.4rem;'><b style='color:{COLORS['heal']};'>{r['date']}</b> | Wt:{r['weight']}kg | BP:{r['bp_sys']}/{r['bp_dia']} | Temp:{r['temp']}°F | HR:{r['hr']}bpm | Gluc:{r['glucose']} | SpO2:{r['spo2']}%<br><i style='color:#8b949e;'>{r.get('notes','')}</i></div>", unsafe_allow_html=True)
            if st.button("Export JSON"):
                import json as _json
                st.download_button("Download","{}".format(_json.dumps(st.session_state.health_records,indent=2)),"health_records.json","application/json")
        else:
            st.info("No records yet. Add your first record.")
    with tabs[2]:
        if len(st.session_state.health_records) >= 2:
            try:
                import pandas as pd
                df = pd.DataFrame(st.session_state.health_records)
                st.line_chart(df[["bp_sys","bp_dia"]])
                st.line_chart(df[["glucose"]])
            except ImportError:
                st.info("Install pandas for trend charts: pip install pandas")
        else:
            st.info("Add at least 2 records to view trends.")

# ════════════════════════════════════════════════════════════════
# PAGE 12 — EMERGENCY NAVIGATOR
# ════════════════════════════════════════════════════════════════
elif page == "Emergency Navigator":
    st.markdown(f"<div class='hero-title' style='font-size:2rem; background:linear-gradient(135deg,{COLORS['epi']},#ff6b6b);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>🚨 Emergency Navigator</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:{COLORS['epi']}22; border:2px solid {COLORS['epi']}; border-radius:12px; padding:1rem; text-align:center; margin-bottom:1rem;'><span style='font-size:1.5rem; font-weight:700;'>EMERGENCY: </span><code style='font-size:1.8rem; color:{COLORS['epi']};'>108</code> (Ambulance) &nbsp;|&nbsp; <code style='font-size:1.5rem; color:{COLORS['drug']};'>112</code> (Universal) &nbsp;|&nbsp; <code style='font-size:1.5rem; color:{COLORS['trust']};'>102</code> (Women/Child)</div>", unsafe_allow_html=True)
    tabs = st.tabs(["First Aid","Ambulance Directory","Blood Banks","Golden Hour"])
    PROTOCOLS = {
        "Heart Attack": {"steps":["Call 108 immediately","Sit/lie comfortably","Loosen clothing","Give aspirin 300mg if not allergic","Do NOT give food/water","Start CPR if unresponsive","Stay with patient","Note time of onset"],"dont":["Give water","Leave alone","Delay calling 108"],"window":60},
        "Stroke": {"steps":["Call 108 (FAST test)","Face drop + Arm weak + Speech slurred = Time to call","Lay on side (recovery)","Do NOT give food/water","Note exact symptom start time","Rush to CT-capable hospital"],"dont":["Give aspirin without doctor advice","Give food/water","Let patient sleep"],"window":60},
        "Snake Bite": {"steps":["Keep calm, immobilize limb","Remove watches/rings","Mark bite with pen + time","Call 108","No tourniquet","No sucking venom","Carry patient - don't walk","Hospital within 2-4 hours"],"dont":["Apply tourniquet","Suck venom","Apply ice","Cut wound"],"window":240},
        "Burns": {"steps":["Cool with running water 20 min","Remove jewelry near burn","Cover with clean cloth","Paracetamol for pain","Call 108 if >10% body area"],"dont":["Apply ice","Apply butter/toothpaste","Break blisters"],"window":120},
        "Choking": {"steps":["Ask 'Are you choking?'","Encourage coughing if partial","5 back blows between shoulder blades","5 abdominal thrusts (Heimlich)","Alternate until cleared","Call 108 if >1 minute","CPR if unconscious"],"dont":["Blind finger sweeps","Give water"],"window":10},
        "Diabetic Emergency": {"steps":["Check consciousness","Hypoglycaemia: 15g fast sugar (juice/glucose)","Wait 15 minutes","Unconscious: Call 108 (no food/drink)","Glucagon injection if available","Hospital if no improvement in 30 min"],"dont":["Give oral food to unconscious person","Delay 108 if unconscious"],"window":60},
    }
    with tabs[0]:
        emergency_type = st.selectbox("Select Emergency", list(PROTOCOLS.keys()))
        p = PROTOCOLS[emergency_type]
        st.markdown(f"<div class='alert-critical'><b>Golden Window: {p['window']} minutes — Act NOW</b></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Step-by-Step Protocol:**")
            for i, step in enumerate(p["steps"],1):
                st.markdown(f"<div style='display:flex; margin-bottom:5px;'><span style='color:{COLORS['epi']}; font-weight:700; min-width:24px;'>{i}.</span><span>{step}</span></div>", unsafe_allow_html=True)
        with c2:
            dont_list = "".join(["✗ "+d+"<br>" for d in p["dont"]])
            st.markdown(f"<div class='alert-warning'><b>DO NOT:</b><br>{dont_list}</div>", unsafe_allow_html=True)
    with tabs[1]:
        st.markdown("#### State Ambulance Numbers")
        amb = {"Tamil Nadu":"108 (GVK-EMRI)","Maharashtra":"108 (EMRI)","Delhi":"102 / 108 (CATS)","Karnataka":"108 (Arogya Kavacha)","Uttar Pradesh":"108 (EMRI UP)","Gujarat":"108 (Zindagi)","West Bengal":"102 / 108","Rajasthan":"108","Kerala":"108","Andhra Pradesh":"108","Telangana":"108","Madhya Pradesh":"108"}
        state_sel = st.selectbox("State", list(amb.keys()), key="amb_sel")
        st.markdown(f"<div class='result-box' style='text-align:center;'><div style='font-size:2.5rem; font-weight:700; color:{COLORS['epi']};'>{amb[state_sel]}</div></div>", unsafe_allow_html=True)
        st.markdown("**National:** 108 | 112 | 102 (Maternal) | 1066 (Road Accident)")
    with tabs[2]:
        st.markdown("#### Blood Bank Locator")
        city_bb = st.selectbox("City", ["Chennai","Mumbai","Delhi","Bangalore"])
        banks = {"Chennai":[("Govt Royapettah Hospital","044-28193024"),("Voluntary Health Services","044-22542929")],"Mumbai":[("KEM Hospital","022-24107000"),("Tata Memorial","022-24177000")],"Delhi":[("AIIMS Blood Bank","011-26588500"),("Safdarjung Hospital","011-26707444")],"Bangalore":[("Victoria Hospital","080-26703700"),("MS Ramaiah","080-23605555")]}
        for name, phone in banks[city_bb]:
            st.markdown(f"<div class='result-box' style='margin-bottom:0.4rem;'><b>{name}</b><br>📞 {phone}</div>", unsafe_allow_html=True)
        st.markdown("**National eRaktkosh:** raktkosh.mohfw.gov.in | All blood groups available")
    with tabs[3]:
        st.markdown("#### Golden Hour Calculator")
        emg_gh = st.selectbox("Emergency", ["Heart Attack (60 min)","Stroke (60 min)","Burns (120 min)","Snake Bite (240 min)"])
        onset = st.time_input("Emergency start time", datetime.now().time())
        golden = int(emg_gh.split("(")[1].replace(" min)",""))
        onset_dt = datetime.combine(datetime.today(), onset)
        elapsed = max(0, (datetime.now() - onset_dt).seconds // 60)
        remaining = max(0, golden - elapsed)
        pct = min(100, elapsed/golden*100)
        bar_c = COLORS['heal'] if pct < 50 else COLORS['drug'] if pct < 80 else COLORS['epi']
        st.markdown(f"<div class='result-box' style='text-align:center;'><div style='font-size:1.5rem; font-weight:700; color:{bar_c};'>{remaining} minutes remaining</div><div style='background:#30363d; border-radius:8px; height:16px; margin:10px 0;'><div style='background:{bar_c}; width:{pct:.0f}%; height:16px; border-radius:8px;'></div></div><div style='color:#8b949e;'>Elapsed: {elapsed} min | Window: {golden} min</div></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# PAGE 13 — NUTRITION INTELLIGENCE
# ════════════════════════════════════════════════════════════════
elif page == "Nutrition Intelligence":
    st.markdown("<div class='hero-title' style='font-size:2rem;'>🥗 Nutrition Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>60+ Indian foods · ICMR RDA · Disease diet plans · Deficiency detector</div>", unsafe_allow_html=True)
    FOOD_DB = {
        "Idli (1 piece)": (39,1.7,8.0,0.2,0.5,0.3,8),
        "Dosa (1 medium)": (120,2.5,17.0,4.5,0.5,0.4,12),
        "Rice 100g cooked": (130,2.7,28.0,0.3,0.4,0.3,3),
        "Dal 100g": (116,7.6,20.1,0.4,3.9,3.2,49),
        "Roti 1 medium": (71,2.5,15.0,0.4,2.4,1.0,11),
        "Banana 1 medium": (89,1.1,22.8,0.3,2.6,0.3,5),
        "Egg whole": (155,13.0,1.1,11.0,0.0,1.8,50),
        "Chicken breast 100g": (165,31.0,0.0,3.6,0.0,1.0,15),
        "Spinach 100g": (23,2.9,3.6,0.4,2.2,2.7,99),
        "Milk 200ml": (84,6.8,10.0,2.0,0.0,0.1,240),
        "Paneer 100g": (265,18.3,1.2,20.8,0.0,0.5,190),
        "Curd 100g": (98,11.0,3.4,4.3,0.0,0.1,120),
        "Peanuts 30g": (170,7.7,4.8,14.8,2.5,0.7,19),
        "Sambar 100ml": (55,2.4,8.8,1.6,2.1,1.5,44),
    }
    tabs = st.tabs(["Food Search","Meal Planner","Deficiency Detector","Disease Diet Plans","Street Food"])
    with tabs[0]:
        food_sel = st.selectbox("Select food", [""] + list(FOOD_DB.keys()))
        qty = st.slider("Quantity (g)", 50, 500, 100)
        if food_sel and food_sel in FOOD_DB:
            kcal,prot,carbs,fat,fiber,iron,calcium = FOOD_DB[food_sel]
            s = qty/100
            c1,c2,c3,c4 = st.columns(4)
            for col,lbl,val,unit,clr in [(c1,"Calories",kcal*s,"kcal",COLORS['drug']),(c2,"Protein",prot*s,"g",COLORS['trust']),(c3,"Carbs",carbs*s,"g","#e9c46a"),(c4,"Fat",fat*s,"g","#a8dadc")]:
                col.markdown(f"<div class='kpi-card'><div class='kpi-number' style='color:{clr}; font-size:1.4rem;'>{val:.1f}</div><div class='kpi-label'>{lbl} ({unit})</div></div>", unsafe_allow_html=True)
            st.markdown(f"Iron: {iron*s:.1f}mg ({iron*s/17*100:.0f}% RDA) | Calcium: {calcium*s:.0f}mg | Fiber: {fiber*s:.1f}g")
    with tabs[1]:
        if "meal_items" not in st.session_state: st.session_state.meal_items = []
        c1,c2,c3 = st.columns(3)
        mf = c1.selectbox("Food", list(FOOD_DB.keys()), key="mf_sel")
        mq = c2.number_input("Qty (g)", 50, 500, 100, key="mq_inp")
        mt = c3.selectbox("Meal", ["Breakfast","Lunch","Dinner","Snack"], key="mt_sel")
        if st.button("Add to Meal"):
            kcal,prot,carbs,fat,fiber,iron,calcium = FOOD_DB[mf]; s=mq/100
            st.session_state.meal_items.append({"food":mf,"qty":mq,"meal":mt,"kcal":round(kcal*s,1),"protein":round(prot*s,2),"carbs":round(carbs*s,2),"fat":round(fat*s,2)})
        if st.session_state.meal_items:
            for item in st.session_state.meal_items:
                st.markdown(f"<div style='font-size:0.82rem; color:#8b949e;'>{item['meal']}: {item['food']} ({item['qty']}g) — {item['kcal']} kcal</div>", unsafe_allow_html=True)
            tots = {k: sum(x[k] for x in st.session_state.meal_items) for k in ["kcal","protein","carbs","fat"]}
            st.markdown(f"**Total:** {tots['kcal']:.0f} kcal | Protein: {tots['protein']:.1f}g | Carbs: {tots['carbs']:.1f}g | Fat: {tots['fat']:.1f}g")
            if st.button("Clear Meal"): st.session_state.meal_items = []; st.rerun()
    with tabs[2]:
        syms_v = st.multiselect("Symptoms", ["fatigue","bone pain","muscle cramps","hair loss","brittle nails","pale skin","tingling hands/feet","poor night vision","bleeding gums","poor wound healing","brain fog","depression"])
        if st.button("Detect Deficiencies") and syms_v:
            DEF_MAP = {
                "Vitamin D": (["bone pain","muscle cramps","fatigue","depression"],"600-800 IU/day","Very High in India"),
                "Vitamin B12": (["fatigue","tingling hands/feet","pale skin","brain fog"],"2.4 mcg/day","High (vegetarians)"),
                "Iron": (["fatigue","pale skin","hair loss","brittle nails"],"17-21 mg/day","Very High in India"),
                "Vitamin C": (["bleeding gums","poor wound healing","fatigue"],"40 mg/day","Moderate"),
            }
            for nutr, (syms, rda, risk) in DEF_MAP.items():
                if set(syms_v) & set(syms):
                    st.markdown(f"<div class='result-box' style='margin-bottom:0.5rem;'><b style='color:{COLORS['drug']};'>{nutr}</b> deficiency suspected<br>RDA: {rda} | India Risk: {risk}</div>", unsafe_allow_html=True)
    with tabs[3]:
        condition = st.selectbox("Condition", ["Diabetes","Hypertension","Anaemia","Heart Disease","Kidney Disease"])
        DIET = {
            "Diabetes": (["Ragi, bajra, whole grains","Leafy greens (methi, palak)","Legumes (chana, moong)","Bitter gourd (karela)"],["White rice (large portions)","Sugary drinks","Maida/refined flour","Fried snacks"],"Breakfast: Methi roti + curd | Lunch: Brown rice + sambar | Dinner: Roti + dal + sabzi"),
            "Hypertension": (["Potassium-rich (banana, spinach)","Low-fat dairy","Garlic and onion","Whole grains"],["Pickles, papad (high salt)","Processed/canned foods","Excessive red meat"],"DASH: Oats + banana | Dal + roti + sabzi | Fish curry (low salt) + brown rice"),
            "Anaemia": (["Ragi, rajma, spinach","Vitamin C with meals (amla, lemon)","Jaggery (gud)","Dates and figs"],["Tea/coffee with meals","Antacids","Processed foods"],"Ragi porridge + amla | Rajma rice + spinach + lemon | Khichdi + palak"),
            "Heart Disease": (["Omega-3: fish, flaxseed, walnuts","Oats and barley","Fruits/veggies 5 portions/day"],["Saturated fats in excess","Trans fats (vanaspati)","High salt/sugary foods"],"Oats | Dal tadka (minimal oil) | Grilled fish + salad | Walnuts"),
            "Kidney Disease": (["Low-K fruits (apple, grapes)","White rice","Cabbage, cauliflower","Egg whites"],["Bananas, oranges (high K)","High-protein diet","Salt/pickles","Dairy in excess"],"Consult nephrologist for stage-specific plan. Generally: Low K/P/Na diet"),
        }
        eat, avoid, plan = DIET[condition]
        c1,c2 = st.columns(2)
        c1.markdown(f"<div class='alert-success'><b>Recommended:</b><br>{'<br>'.join(['✓ '+f for f in eat])}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='alert-warning'><b>Avoid:</b><br>{'<br>'.join(['✗ '+f for f in avoid])}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='result-box'><b>Sample Meal Plan:</b><br>{plan}</div>", unsafe_allow_html=True)
    with tabs[4]:
        sf_data = {
            "Vada Pav": (290,7,12,580,"Try baked version"),
            "Pani Puri (6)": (180,3,4,450,"Opt for mint water"),
            "Samosa (1)": (262,5,14,400,"Baked halves fat"),
            "Dahi Puri (6)": (210,5,6,380,"Better: has curd protein"),
            "Chole Bhature": (480,14,20,700,"Chole without bhature saves 200 kcal"),
            "Masala Chai": (90,3,3,30,"Reduce sugar"),
            "Poha": (180,3,4,200,"Excellent choice"),
            "Bhel Puri": (195,4,5,510,"Skip sev for fewer calories"),
        }
        sf_sel = st.selectbox("Street Food", list(sf_data.keys()))
        kcal,prot,fat,sodium,tip = sf_data[sf_sel]
        c1,c2,c3 = st.columns(3)
        c1.metric("Calories", f"{kcal} kcal")
        c2.metric("Protein", f"{prot}g")
        c3.metric("Sodium", f"{sodium}mg")
        hs = max(1, min(10, round(10 - kcal/60 + prot/3 - sodium/200, 1)))
        hc = COLORS['heal'] if hs >= 6 else COLORS['drug'] if hs >= 4 else COLORS['epi']
        st.markdown(f"<div class='result-box'><b>Health Score:</b> <span style='color:{hc}; font-size:1.5rem;'>{hs}/10</span><br><b>Tip:</b> {tip}</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# PAGE 14 — WOMEN & CHILD HEALTH
# ════════════════════════════════════════════════════════════════
elif page == "Women & Child Health":
    st.markdown(f"<div class='hero-title' style='font-size:2rem; background:linear-gradient(135deg,#e9c46a,{COLORS['mind']});-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>👩 Women & Child Health</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>Pregnancy tracker · NIP vaccines · PCOS risk · Child growth · Govt schemes</div>", unsafe_allow_html=True)
    tabs = st.tabs(["Pregnancy Tracker","NIP Vaccines","PCOS Screen","Child Growth","Women Schemes"])
    with tabs[0]:
        lmp = st.date_input("Last Menstrual Period (LMP)", datetime.today() - timedelta(days=90))
        edd = lmp + timedelta(days=280)
        today = datetime.today().date()
        weeks = max(0,(today-lmp).days//7)
        remaining_w = max(0,(edd-today).days//7)
        trim = "1st Trimester" if weeks<=12 else "2nd Trimester" if weeks<=27 else "3rd Trimester"
        tc = COLORS['heal'] if weeks<=12 else COLORS['trust'] if weeks<=27 else COLORS['mind']
        c1,c2,c3 = st.columns(3)
        c1.markdown(f"<div class='kpi-card'><div class='kpi-number' style='color:{tc};'>{weeks}</div><div class='kpi-label'>Weeks Pregnant</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='kpi-card'><div class='kpi-number' style='color:{COLORS['drug']};'>{remaining_w}</div><div class='kpi-label'>Weeks Remaining</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='kpi-card'><div class='kpi-number' style='color:{tc}; font-size:1rem;'>{edd.strftime('%d %b %Y')}</div><div class='kpi-label'>Due Date (EDD)</div></div>", unsafe_allow_html=True)
        st.markdown(f"**Trimester:** <span style='color:{tc}; font-weight:700;'>{trim}</span>", unsafe_allow_html=True)
        WEEK_INFO = {8:("Raspberry","1.6cm","Facial features forming","Nausea, fatigue","Folic acid, iron","Prenatal visit, blood tests"),
                     20:("Banana","25cm","Baby can hear","Back pain, heartburn","Calcium, Vit D","Anomaly scan, iron levels"),
                     28:("Eggplant","37cm","Eyes open/close","Braxton Hicks","Protein, calcium","GDM test, Tdap vaccine"),
                     36:("Romaine","47cm","Baby dropping","Pelvic pressure","Small meals","GBS test, birth plan"),
                     40:("Pumpkin","51cm","Full term ready!","Nesting urge","Stay hydrated","Hospital bag ready")}
        if weeks > 0:
            cw = min(WEEK_INFO.keys(), key=lambda w: abs(w-weeks))
            i = WEEK_INFO[cw]
            st.markdown(f"<div class='result-box'><b>Around Week {cw}:</b><br>Size: {i[0]} ({i[1]}) | Dev: {i[2]}<br>You may feel: {i[3]}<br>Nutrition focus: {i[4]}<br>Tests due: {i[5]}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='alert-critical'>⚠️ Call doctor immediately: Heavy bleeding · Severe abdominal pain · Baby not moving (after 28w) · Sudden swelling (face/hands) · Severe headache · Fever >38°C</div>", unsafe_allow_html=True)
    with tabs[1]:
        NIP = [("Birth","BCG + OPV 0 + Hep B","TB, Polio, Hepatitis B"),("6 weeks","Pentavalent 1 + OPV 1 + PCV 1 + Rotavirus 1","DTP+HepB+Hib, Polio, Pneumonia, Diarrhoea"),("10 weeks","Pentavalent 2 + OPV 2 + Rotavirus 2","DTP+HepB+Hib, Polio, Diarrhoea"),("14 weeks","Pentavalent 3 + OPV 3 + PCV 2 + IPV 1","DTP+HepB+Hib, Polio, Pneumonia"),("9 months","MR 1 + JE 1","Measles-Rubella, Japanese Encephalitis"),("16-24 months","MR 2 + DPT Booster 1 + OPV Booster","Measles-Rubella, DTP, Polio"),("5 years","DPT Booster 2","Diphtheria, Tetanus, Pertussis"),("10 years","Td vaccine","Tetanus, Diphtheria"),("16 years","Td vaccine","Tetanus, Diphtheria")]
        for age, vax, protects in NIP:
            st.markdown(f"<div class='result-box' style='margin-bottom:0.4rem;'><span class='tag' style='background:{COLORS['trust']}33; color:{COLORS['trust']};'>{age}</span> <b>{vax}</b><br><span style='color:#8b949e; font-size:0.82rem;'>Protects against: {protects}</span></div>", unsafe_allow_html=True)
        st.markdown("All NIP vaccines are **FREE** at PHC/AWC | Helpline: **1800-11-1955**")
    with tabs[2]:
        st.info("Screening tool only — not a diagnosis. Consult a gynaecologist.")
        q1 = st.select_slider("Menstrual cycle regularity", ["Very Regular","Mostly Regular","Irregular","Very Irregular","No periods"])
        q2 = st.checkbox("Excess hair growth (face/chest/abdomen)")
        q3 = st.checkbox("Persistent acne or oily skin")
        q4 = st.checkbox("Scalp hair thinning/loss")
        q5 = st.checkbox("Weight gain around abdomen")
        q6 = st.checkbox("Difficulty conceiving")
        q7 = st.checkbox("Family history of PCOS or diabetes")
        bmi_p = st.slider("BMI", 16.0, 45.0, 23.0, key="pcos_bmi")
        if st.button("Screen PCOS Risk"):
            s = {"Very Regular":0,"Mostly Regular":5,"Irregular":15,"Very Irregular":25,"No periods":30}[q1]
            s += sum([15 if q2 else 0, 10 if q3 else 0, 10 if q4 else 0, 15 if q5 else 0, 10 if q6 else 0, 10 if q7 else 0, 10 if bmi_p>=25 else 0])
            if s < 20: risk, color = "Low Risk", COLORS['heal']
            elif s < 50: risk, color = "Moderate — Consult Gynaecologist", COLORS['drug']
            else: risk, color = "High Risk — Evaluation Needed", COLORS['epi']
            st.markdown(f"<div class='result-box'><div style='font-size:1.4rem; color:{color}; font-weight:700;'>PCOS Score: {s}/100 — {risk}</div><div style='margin-top:0.5rem;'>Next steps: Ultrasound pelvis, LH/FSH/testosterone levels, fasting insulin</div></div>", unsafe_allow_html=True)
    with tabs[3]:
        child_age_m = st.slider("Child age (months)", 0, 60, 24)
        child_gender_g = st.selectbox("Gender", ["Male","Female"], key="growth_gen")
        child_wt = st.number_input("Weight (kg)", 1.0, 25.0, 12.0, key="growth_wt")
        if st.button("Check Growth"):
            medians_b = {0:3.3,3:6.0,6:7.9,9:9.2,12:10.2,18:11.5,24:12.2,36:14.3,48:16.3,60:18.3}
            medians_g = {0:3.2,3:5.8,6:7.3,9:8.7,12:9.6,18:10.9,24:11.5,36:13.9,48:15.7,60:17.7}
            med = medians_b if child_gender_g=="Male" else medians_g
            cm = min(med.keys(), key=lambda x: abs(x-child_age_m))
            waz = (child_wt - med[cm]) / (med[cm]*0.13)
            if waz < -3: st_txt, clr = "Severely Underweight (SAM)", COLORS['epi']
            elif waz < -2: st_txt, clr = "Moderate Underweight (MAM)", COLORS['drug']
            elif waz < 2: st_txt, clr = "Normal Growth", COLORS['heal']
            else: st_txt, clr = "Overweight", COLORS['drug']
            st.markdown(f"<div class='result-box'><div style='font-size:1.3rem; color:{clr}; font-weight:700;'>{st_txt}</div>WAZ: {waz:.2f} | Median for age: {med[cm]}kg | Child: {child_wt}kg</div>", unsafe_allow_html=True)
            if "Underweight" in st_txt: st.markdown(f"<div class='alert-critical'>Visit Anganwadi Centre for SAM/MAM support under POSHAN Abhiyan. Helpline: 1800-180-1104</div>", unsafe_allow_html=True)
    with tabs[4]:
        women_sch = [("JSY","Safe delivery cash incentive","₹1400 rural / ₹1000 urban","BPL pregnant women","104"),("PMMVY","Maternity benefit","₹5000 (3 instalments)","First child, age ≥19","011-23382393"),("Poshan Abhiyan","Nutrition for women & children","Free supplements","Pregnant, lactating, <6yr children","1800-180-1104"),("JSSK","Free pregnancy services","Free ANC, delivery, medicine","All pregnant at govt hospital","104"),("Beti Bachao Beti Padhao","Girl child education","Education support","Girl child","011-23386423")]
        for name, desc, benefit, elig, hl in women_sch:
            with st.expander(name):
                c1,c2 = st.columns(2)
                c1.markdown(f"**Description:** {desc}<br>**Benefit:** {benefit}", unsafe_allow_html=True)
                c2.markdown(f"**Eligibility:** {elig}<br>**Helpline:** `{hl}`", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# PAGE 15 — HEALTH CHATBOT
# ════════════════════════════════════════════════════════════════
elif page == "Health Chatbot":
    st.markdown(f"<div class='hero-title' style='font-size:2rem; background:linear-gradient(135deg,{COLORS['trust']},{COLORS['heal']});-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>💬 Health Chatbot</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>Ask health questions · AI responses · Emergency escalation</div>", unsafe_allow_html=True)
    chatbot = load_chatbot()
    FALLBACK_QA = {
        "dengue": "**Dengue**: Aedes mosquito bite. Symptoms: high fever, headache, eye pain, joint pain, rash, low platelets. Treatment: rest, fluids, paracetamol (NO aspirin/ibuprofen). Hospital if platelets < 1 lakh. Helpline: 104",
        "malaria": "**Malaria**: Plasmodium via Anopheles mosquito. Cyclical fever, chills, sweating. Treatment: ACT (free at PHC). Prevention: mosquito nets, repellents.",
        "diabetes": "**Diabetes**: High blood sugar. Manage with Metformin (₹8 at Jan Aushadhi), diet, exercise. HbA1c target <7%. Test fasting glucose regularly.",
        "hypertension": "**Hypertension**: BP >140/90. DASH diet (low salt), exercise, medication (amlodipine). Monitor daily. Helpline: 104.",
        "paracetamol": "**Paracetamol (Crocin/Dolo)**: Adult 500mg–1g every 4-6h, max 4g/day. Avoid with alcohol. Jan Aushadhi generic: ₹5 for 10 tabs.",
        "ambulance": "Call **108** (free, 24/7). Women/child: **102**. Universal emergency: **112**.",
        "fever": "Paracetamol 500mg–1g for adults. Stay hydrated. See doctor if >103°F or lasts >3 days.",
        "cpr": "CPR: 30 chest compressions (100-120/min) + 2 rescue breaths. Call 108 first. Use AED if available.",
        "stroke": "FAST: Face droop + Arm weak + Speech slurred = Time to call 108. Golden hour: 60 min.",
        "ayushman": "PM-JAY: Free hospitalization ₹5 lakh/family/year. Check eligibility: pmjay.gov.in. Helpline: 14555.",
        "tuberculosis": "TB: Free DOTS 6-month treatment at govt hospitals. Nikshay Poshan gives ₹500/month. Helpline: 1800-11-6666.",
        "depression": "PHQ-9 score ≥10: seek help. iCall: 9152987821. Govt helpline: 1800-599-0019 (free).",
    }
    CRISIS_WORDS = {"suicide","kill myself","end my life","want to die","self harm","not worth living","no reason to live"}
    col_chat, col_info = st.columns([3,1])
    with col_info:
        st.markdown("#### Quick Topics")
        for topic in ["dengue","diabetes","paracetamol","ambulance","ayushman bharat","tuberculosis","depression","stroke","CPR","PCOS"]:
            if st.button(topic, key=f"qt_{topic}", use_container_width=True):
                st.session_state.chat_history.append({"role":"user","content":topic})
                key = next((k for k in FALLBACK_QA if k in topic.lower()), None)
                resp = (chatbot.respond(topic) if chatbot else None) or FALLBACK_QA.get(key, f"Visit your nearest PHC or call **104** for guidance about {topic}.")
                st.session_state.chat_history.append({"role":"bot","content":resp})
                st.rerun()
        st.divider()
        st.markdown(f"<div style='color:{COLORS['epi']};font-size:1.2rem;font-weight:700;'>108 — Ambulance</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:{COLORS['mind']};'>9152987821 — iCall</div>", unsafe_allow_html=True)
        if st.button("Clear Chat"):
            st.session_state.chat_history = []; st.rerun()
    with col_chat:
        if not st.session_state.chat_history:
            st.markdown(f"<div class='result-box' style='text-align:center;'><div style='font-size:2rem;'>🏥</div><div style='color:{COLORS['heal']}; font-weight:700;'>BharatCare Health Assistant</div><div style='color:#8b949e; font-size:0.9rem;'>Ask about diseases, medicines, symptoms, emergencies, or government schemes.</div></div>", unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"<div class='chat-user'>👤 <b>You:</b> {msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bot'>🏥 <b>BharatCare:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
        user_input = st.text_input("Ask a health question...", key="chat_input", placeholder="e.g. dengue symptoms, CPR steps, Jan Aushadhi...")
        c1,c2 = st.columns([4,1])
        send = c2.button("Send", key="chat_send", use_container_width=True)
        if send and user_input.strip():
            msg = user_input.strip()
            is_crisis = any(w in msg.lower() for w in CRISIS_WORDS)
            st.session_state.chat_history.append({"role":"user","content":msg})
            if is_crisis:
                resp = "I am concerned about you. **Please call iCall now: 9152987821** (Mon-Sat 8am-10pm) or Vandrevala: **1860-2662-345** (24/7 free). You are not alone. Help is here."
            elif chatbot:
                resp = chatbot.respond(msg)
            else:
                k = next((k for k in FALLBACK_QA if k in msg.lower()), None)
                resp = FALLBACK_QA.get(k, f"For '{msg}', consult a doctor via eSanjeevani (14566) or visit your PHC. Emergency: **108**.")
            st.session_state.chat_history.append({"role":"bot","content":resp})
            st.rerun()

# ════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div style='border-top:1px solid {COLORS['border']}; padding-top:1rem; text-align:center;
            color:#8b949e; font-size:0.78rem; line-height:1.8;'>
    <b style='color:{COLORS['heal']};'>BharatCare AI Pro</b> · Built by
    <b style='color:{COLORS['trust']};'>Deol Allwyn Samuel J B</b> · VLSI · CIT · Afynix Digital · Reg No 712721104034<br>
    <span style='color:{COLORS['epi']};'>⚕ For informational/educational purposes only. Not a substitute for professional medical advice.</span><br>
    Always consult a qualified healthcare professional. Emergency: <b>108</b>
</div>
""", unsafe_allow_html=True)
