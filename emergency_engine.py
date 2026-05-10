"""
BharatCare AI Pro · Emergency Engine v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
First aid protocols, ambulance directory, golden hour calculator.
Author: Deol Allwyn Samuel J B · VLSI · CIT · Afynix Digital
"""

from datetime import datetime, timedelta
import re
from typing import Dict, List, Optional

EMERGENCY_TYPES = [
    "Heart Attack", "Stroke", "Severe Accident/Trauma", "Snake Bite",
    "Poisoning", "Drowning", "Burns", "Choking", "Fracture/Dislocation",
    "Diabetic Emergency", "Epileptic Seizure", "Anaphylaxis/Allergic Shock",
    "Eye Injury", "Heat Stroke", "Electrocution",
]

FIRST_AID_PROTOCOLS: Dict[str, Dict] = {
    "Heart Attack": {
        "golden_hour_minutes": 60,
        "call_first": True,
        "steps": [
            "1. CALL 108 IMMEDIATELY — do not wait.",
            "2. Help the person sit down in a comfortable position — half-sitting with knees bent.",
            "3. Loosen any tight clothing around neck, chest, and waist.",
            "4. If conscious and not allergic, give 300 mg Aspirin (dissolve under tongue or chew).",
            "5. Keep the person calm — reassure them help is coming.",
            "6. If person becomes unconscious and stops breathing — start CPR.",
            "7. CPR: 30 chest compressions (hard, fast, 2 inches deep) then 2 rescue breaths. Repeat.",
            "8. Use AED (defibrillator) if available — follow its voice instructions.",
            "9. Do NOT give water or food.",
            "10. Stay with person until ambulance arrives.",
        ],
        "do_not": ["Do NOT leave the person alone", "Do NOT give food or water", "Do NOT allow them to walk to car",
                    "Do NOT ignore symptoms thinking it is just indigestion"],
    },
    "Stroke": {
        "golden_hour_minutes": 180,
        "call_first": True,
        "steps": [
            "1. Use FAST test — Face drooping? Arm weakness? Speech difficulty? Time to call 108.",
            "2. CALL 108 IMMEDIATELY — every minute of delay = 1.9 million brain cells lost.",
            "3. Note the exact time symptoms started — doctors NEED this information.",
            "4. Keep person lying down — head and shoulders slightly elevated (about 30 degrees).",
            "5. If unconscious, turn person on their side (recovery position) to prevent choking.",
            "6. Do NOT give any food, water, or medicines by mouth.",
            "7. Loosen tight clothing around neck and chest.",
            "8. Keep person warm with a blanket.",
            "9. Reassure person calmly — they may be confused and frightened.",
            "10. Be ready to tell ambulance: exact time symptoms started, medications patient takes.",
        ],
        "do_not": ["Do NOT give aspirin for stroke (different from heart attack)", "Do NOT give food or water",
                    "Do NOT allow person to fall asleep before paramedics check them",
                    "Do NOT delay — stroke treatment must start within 4.5 hours"],
    },
    "Severe Accident/Trauma": {
        "golden_hour_minutes": 60,
        "call_first": True,
        "steps": [
            "1. Ensure your own safety — check for traffic, fire, electrical hazards.",
            "2. CALL 108 and describe location precisely.",
            "3. Do NOT move the person unless there is immediate danger (fire, flood).",
            "4. Control severe bleeding: apply firm pressure with clean cloth — do NOT remove.",
            "5. If bleeding from limb is severe and cloth soaks through, tie tourniquet 2 inches above wound.",
            "6. If person is unconscious and breathing: turn to recovery position (on side).",
            "7. If not breathing and unconscious: start CPR — 30 compressions, 2 breaths.",
            "8. Do NOT remove objects impaled in the body — stabilise them in place.",
            "9. Keep the person warm — shock kills. Cover with blanket.",
            "10. Talk to person — reassure them even if unconscious (hearing is last sense to go).",
        ],
        "do_not": ["Do NOT move a person with suspected spinal injury", "Do NOT remove an impaled object",
                    "Do NOT give anything by mouth", "Do NOT apply tourniquet on neck, armpit, or groin"],
    },
    "Snake Bite": {
        "golden_hour_minutes": 240,
        "call_first": True,
        "steps": [
            "1. CALL 108 and go to nearest hospital with anti-venom stock IMMEDIATELY.",
            "2. Keep victim calm and still — movement spreads venom faster through lymph system.",
            "3. Immobilise the bitten limb — keep it at or BELOW heart level.",
            "4. Remove rings, bracelets, watches near the bite before swelling starts.",
            "5. Mark the edge of swelling with pen and note the time.",
            "6. Do NOT attempt to suck out venom — this does NOT work.",
            "7. Gently clean bite with soap and water if available.",
            "8. Cover with clean, loose bandage — do NOT apply tight pressure bandage (most Indian snakes).",
            "9. Try to photograph or remember appearance of snake (safely) — helps identify anti-venom.",
            "10. Monitor breathing, pulse, and consciousness every 5 minutes.",
        ],
        "do_not": ["NEVER cut the wound", "NEVER suck venom", "NEVER apply tourniquet (for Indian snakes)",
                    "NEVER apply ice or electric shock", "NEVER give alcohol or stimulants",
                    "NEVER apply traditional herbs or cow dung to bite"],
    },
    "Poisoning": {
        "golden_hour_minutes": 60,
        "call_first": True,
        "steps": [
            "1. CALL 108 or Poison Control: 1800-116-117 IMMEDIATELY.",
            "2. Identify the poison if possible — keep the container for paramedics.",
            "3. If conscious and poison was swallowed: DO NOT induce vomiting (unless instructed by doctor).",
            "4. If poison is on skin: remove contaminated clothing, wash skin with large amounts of water for 20 minutes.",
            "5. If poison is in eyes: flush with clean water continuously for 15-20 minutes.",
            "6. If inhaled poison: move person to fresh air immediately — do not enter enclosed space without protection.",
            "7. Keep person warm and calm.",
            "8. If unconscious: recovery position. If not breathing: CPR.",
            "9. Save any vomit for analysis by doctors.",
            "10. Note exact time of exposure.",
        ],
        "do_not": ["Do NOT induce vomiting unless specifically instructed by medical professional",
                    "Do NOT give milk, eggs, or charcoal without medical instruction",
                    "Do NOT leave person alone", "Do NOT enter gas-filled room without mask"],
    },
    "Drowning": {
        "golden_hour_minutes": 5,
        "call_first": False,
        "steps": [
            "1. DO NOT jump in water unless you are trained lifesaver — throw rope, branch, or ring buoy.",
            "2. Call 108 while helping — shout for others to help.",
            "3. Pull person out of water as quickly as safely possible.",
            "4. Check for breathing — tilt head, lift chin, look/listen/feel for 10 seconds.",
            "5. If not breathing: START CPR IMMEDIATELY — 30 compressions, 2 rescue breaths.",
            "6. Give 5 initial rescue breaths before compressions if possible.",
            "7. Do NOT waste time tilting to drain water — start CPR immediately.",
            "8. Once breathing, turn to recovery position on their side.",
            "9. Remove wet clothing, keep warm — hypothermia is a serious risk.",
            "10. All drowning victims need hospital evaluation even if they appear recovered.",
        ],
        "do_not": ["Do NOT jump in water without flotation unless trained", "Do NOT waste time draining water",
                    "Do NOT assume person is fine if they recover — secondary drowning can occur hours later"],
    },
    "Burns": {
        "golden_hour_minutes": 120,
        "call_first": False,
        "steps": [
            "1. Remove person from source of burn — ensure your own safety.",
            "2. Call 108 for burns larger than palm size, or burns on face/hands/genitals.",
            "3. COOL the burn: run cool (not ice cold) water over the burn for minimum 20 minutes.",
            "4. Do NOT use ice, butter, toothpaste, or coconut oil — these make burns worse.",
            "5. Remove jewellery, watches, tight clothing NEAR the burn (before swelling).",
            "6. Cover loosely with clean, non-fluffy material (cling film ideal, or clean plastic bag).",
            "7. Do NOT burst blisters — they protect against infection.",
            "8. Keep person warm — major burns cause dangerous heat loss.",
            "9. Give paracetamol or ibuprofen for pain if conscious.",
            "10. For chemical burns: brush off dry chemical first, then 20 min water flush.",
        ],
        "do_not": ["NEVER use ice — causes frostbite in already damaged tissue", "NEVER apply butter, oil, or toothpaste",
                    "NEVER burst blisters", "NEVER remove clothing stuck to burnt skin"],
    },
    "Choking": {
        "golden_hour_minutes": 5,
        "call_first": False,
        "steps": [
            "1. Ask 'Are you choking?' — if person can cough, speak or breathe, encourage coughing.",
            "2. If severe choking (cannot breathe, speak, or cough): CALL 108 and act immediately.",
            "3. Give 5 firm back blows between shoulder blades with heel of hand.",
            "4. If back blows do not work: give 5 abdominal thrusts (Heimlich manoeuvre).",
            "5. Heimlich: Stand behind person, make fist, place above navel, grasp fist with other hand, pull sharply inward and upward.",
            "6. Alternate 5 back blows and 5 abdominal thrusts until object expelled or person loses consciousness.",
            "7. If person becomes unconscious: lay down, call 108, start CPR.",
            "8. During CPR chest compressions may expel object — look in mouth before giving breaths.",
            "9. For infant choking (under 1 year): 5 back slaps + 5 chest thrusts (NOT abdominal).",
            "10. For pregnant woman: chest thrusts only, NOT abdominal thrusts.",
        ],
        "do_not": ["Do NOT do blind finger sweeps in mouth", "Do NOT do abdominal thrusts on infant under 1 year",
                    "Do NOT give abdominal thrusts to pregnant women — use chest thrusts"],
    },
    "Fracture/Dislocation": {
        "golden_hour_minutes": 180,
        "call_first": True,
        "steps": [
            "1. Do NOT attempt to straighten the bone or push dislocation back in place.",
            "2. Call 108 for suspected spine, pelvis, or femur (thigh bone) fractures.",
            "3. Immobilise the injured area in the position found — use splints, rolled newspaper, or rigid supports.",
            "4. Extend splint beyond joint above and below the fracture.",
            "5. Pad the splint with soft material for comfort.",
            "6. Apply ice pack (wrapped in cloth) to reduce swelling — 20 minutes on, 20 off.",
            "7. Elevate the injured limb above heart level if possible.",
            "8. Control any bleeding with gentle pressure.",
            "9. Monitor circulation: check pulse, sensation, and warmth beyond fracture site.",
            "10. Keep person calm and warm while waiting for help.",
        ],
        "do_not": ["NEVER straighten a bent fracture", "NEVER push a dislocated joint back in",
                    "Do NOT move person with suspected spine injury", "Do NOT apply heat to acute fracture"],
    },
    "Diabetic Emergency": {
        "golden_hour_minutes": 30,
        "call_first": False,
        "steps": [
            "1. Determine: Is it LOW blood sugar (hypoglycaemia) or HIGH (hyperglycaemia)?",
            "2. Low sugar signs: sweating, shaking, confusion, pale, hunger — 'cold and clammy needs candy'.",
            "3. HIGH sugar signs: frequent urination, fruity breath, extreme thirst, gradual onset — 'hot and dry needs insulin'.",
            "4. For LOW sugar (if conscious): give 15g fast sugar immediately — 3-4 glucose tablets, 100mL fruit juice, or 3 spoons sugar dissolved in water.",
            "5. Recheck after 15 minutes — give another 15g if still symptomatic.",
            "6. Once better, give a small snack with complex carbs (biscuit, roti).",
            "7. For HIGH sugar: give water to drink. Go to hospital for insulin — do NOT attempt home insulin adjustment without guidance.",
            "8. If unconscious: CALL 108. Place in recovery position. Do NOT give food/drink.",
            "9. If glucagon available and trained: inject for severe hypoglycaemia.",
            "10. Document blood glucose readings to show paramedics.",
        ],
        "do_not": ["Do NOT give sugar to unconscious person — aspiration risk",
                    "Do NOT assume all diabetic emergencies are low sugar",
                    "Do NOT leave unconscious diabetic person alone"],
    },
    "Epileptic Seizure": {
        "golden_hour_minutes": 10,
        "call_first": False,
        "steps": [
            "1. Stay calm. Most seizures end in 1-3 minutes on their own.",
            "2. Check the time — if seizure lasts more than 5 minutes, CALL 108 (status epilepticus).",
            "3. PROTECT from injury: clear hard objects away, cushion head with folded jacket.",
            "4. Do NOT restrain the person — let the seizure run its course.",
            "5. Turn person gently onto their side (recovery position) to prevent choking on saliva.",
            "6. Stay with them throughout.",
            "7. After seizure ends: keep person on side, talk calmly, they will be confused (post-ictal).",
            "8. Do NOT put anything in mouth during seizure — cannot swallow tongue.",
            "9. Check for injury after seizure ends.",
            "10. Call 108 if: first-ever seizure, pregnant, diabetic, or person does not regain consciousness within 5 minutes.",
        ],
        "do_not": ["NEVER put fingers, spoon, or any object in mouth during seizure",
                    "NEVER restrain seizure movements", "Do NOT give water until fully alert"],
    },
    "Anaphylaxis/Allergic Shock": {
        "golden_hour_minutes": 15,
        "call_first": True,
        "steps": [
            "1. CALL 108 IMMEDIATELY — anaphylaxis can be fatal within minutes.",
            "2. If EpiPen (adrenaline auto-injector) available: inject in outer thigh immediately — through clothing if needed.",
            "3. Position: Lie person flat with legs raised. If breathing difficulty, let them sit up.",
            "4. Give second EpiPen dose if available and no improvement after 5 minutes.",
            "5. If conscious, give antihistamine (Cetirizine) and steroid tablet if available.",
            "6. Loosen tight clothing around neck and waist.",
            "7. If person stops breathing: start CPR.",
            "8. Note trigger (food, insect sting, medicine) for paramedics.",
            "9. Even if person improves: hospital evaluation is mandatory — biphasic reaction can occur.",
            "10. Keep person warm and calm while waiting.",
        ],
        "do_not": ["Do NOT make person stand or walk — this can be fatal in anaphylaxis",
                    "Do NOT give oral antihistamine alone — it is not fast enough for anaphylaxis",
                    "Do NOT assume symptoms are just mild allergy — err on side of caution"],
    },
    "Eye Injury": {
        "golden_hour_minutes": 60,
        "call_first": False,
        "steps": [
            "1. For CHEMICAL in eye: flush with large amounts of clean water immediately for 15-20 minutes.",
            "2. Hold eyelid open under running water, let water wash across eyeball.",
            "3. For OBJECT in eye: do NOT rub or attempt to remove. Cover loosely with clean cloth.",
            "4. Go to eye casualty immediately for any object penetration.",
            "5. For BLOW to eye: apply cold compress (ice in cloth) for 15 min. Check vision.",
            "6. If vision blurred, doubled, or lost after injury: Emergency — go to hospital immediately.",
            "7. For cut/laceration to eye: cover loosely, do NOT press, go to hospital.",
            "8. Do NOT patch both eyes for chemical burns.",
            "9. Remove contact lenses before flushing if easily accessible.",
            "10. Even if eye feels better after flush — all chemical exposures require hospital evaluation.",
        ],
        "do_not": ["NEVER rub an injured eye", "NEVER try to remove embedded object",
                    "NEVER apply pressure to eye with suspected perforation"],
    },
    "Heat Stroke": {
        "golden_hour_minutes": 30,
        "call_first": True,
        "steps": [
            "1. Call 108 — heat stroke is life-threatening. Body temp can exceed 104°F (40°C).",
            "2. Move person to cool, shaded area immediately.",
            "3. Cool the person rapidly by any means available:",
            "   - Pour cool water over them and fan vigorously",
            "   - Apply ice packs to armpits, neck, and groin",
            "   - Immerse in cool (not ice cold) water if possible",
            "4. Remove excess clothing.",
            "5. If conscious and not vomiting: give cool water to drink slowly.",
            "6. Continue cooling until temperature drops below 38.5°C or emergency services arrive.",
            "7. Place in recovery position if unconscious.",
            "8. Do NOT give aspirin or paracetamol — these do not help heat stroke.",
            "9. Elevate feet slightly if not unconscious.",
            "10. Monitor breathing and consciousness until help arrives.",
        ],
        "do_not": ["Do NOT give aspirin or paracetamol", "Do NOT give alcohol to drink",
                    "Do NOT use ice-cold water (may cause shivering which generates more heat)"],
    },
    "Electrocution": {
        "golden_hour_minutes": 60,
        "call_first": True,
        "steps": [
            "1. DO NOT TOUCH THE PERSON — ensure power source is OFF first.",
            "2. Switch off main power supply or use dry non-conductive material (wooden plank, dry rope) to separate person from source.",
            "3. CALL 108 IMMEDIATELY.",
            "4. Only when safe: check for breathing and pulse.",
            "5. If not breathing: start CPR immediately.",
            "6. Lay person flat — elevate legs if no spinal injury suspected.",
            "7. Cover burns with clean, dry dressings. Do NOT break blisters.",
            "8. Keep person warm and calm.",
            "9. All electrocution victims must go to hospital — internal injuries may not be visible.",
            "10. Watch for cardiac arrhythmias — these can occur hours after electrocution.",
        ],
        "do_not": ["NEVER touch person while still in contact with electrical source",
                    "Do NOT assume person is safe because low voltage source",
                    "Do NOT use wet materials to separate person from current"],
    },
}

AMBULANCE_DIRECTORY: Dict[str, Dict] = {
    "All States": {"emergency": "108", "ambulance": "102", "police": "100", "fire": "101",
                   "disaster": "1078", "women_helpline": "1091", "child_helpline": "1098",
                   "senior_citizen": "14567", "poison_control": "1800-116-117",
                   "mental_health": "1800-599-0019", "covid": "1075"},
    "Tamil Nadu":      {"state_specific": "104 (Health Helpline)", "AIIMS_nearby": "AIIMS Madurai (planned)", "state_ambulance": "108"},
    "Maharashtra":     {"state_specific": "108", "AIIMS_nearby": "AIIMS Nagpur", "state_ambulance": "108"},
    "Delhi":           {"state_specific": "102", "AIIMS_nearby": "AIIMS Delhi", "state_ambulance": "102"},
    "Karnataka":       {"state_specific": "104", "AIIMS_nearby": "AIIMS Mangalore (planned)", "state_ambulance": "108"},
    "Andhra Pradesh":  {"state_specific": "108", "AIIMS_nearby": "AIIMS Mangalagiri", "state_ambulance": "108"},
    "Telangana":       {"state_specific": "108", "AIIMS_nearby": "AIIMS Bibinagar", "state_ambulance": "108"},
    "Kerala":          {"state_specific": "104", "AIIMS_nearby": "AIIMS Thiruvananthapuram", "state_ambulance": "108"},
    "Rajasthan":       {"state_specific": "108", "AIIMS_nearby": "AIIMS Jodhpur", "state_ambulance": "108"},
    "Uttar Pradesh":   {"state_specific": "108", "AIIMS_nearby": "AIIMS Gorakhpur", "state_ambulance": "108"},
    "West Bengal":     {"state_specific": "1800-345-5505", "AIIMS_nearby": "AIIMS Kalyani", "state_ambulance": "108"},
    "Gujarat":         {"state_specific": "108", "AIIMS_nearby": "AIIMS Rajkot", "state_ambulance": "108"},
    "Madhya Pradesh":  {"state_specific": "108", "AIIMS_nearby": "AIIMS Bhopal", "state_ambulance": "108"},
    "Punjab":          {"state_specific": "108", "AIIMS_nearby": "AIIMS Bathinda", "state_ambulance": "108"},
    "Haryana":         {"state_specific": "108", "AIIMS_nearby": "AIIMS Rewari", "state_ambulance": "108"},
    "Bihar":           {"state_specific": "102", "AIIMS_nearby": "AIIMS Patna", "state_ambulance": "102"},
    "Odisha":          {"state_specific": "108", "AIIMS_nearby": "AIIMS Bhubaneswar", "state_ambulance": "108"},
    "Assam":           {"state_specific": "108", "AIIMS_nearby": "AIIMS Guwahati", "state_ambulance": "108"},
    "Jharkhand":       {"state_specific": "108", "AIIMS_nearby": "AIIMS Deoghar", "state_ambulance": "108"},
    "Uttarakhand":     {"state_specific": "108", "AIIMS_nearby": "AIIMS Rishikesh", "state_ambulance": "108"},
    "Himachal Pradesh":{"state_specific": "108", "AIIMS_nearby": "AIIMS Bilaspur", "state_ambulance": "108"},
    "Chhattisgarh":    {"state_specific": "108", "AIIMS_nearby": "AIIMS Raipur", "state_ambulance": "108"},
    "Jammu & Kashmir": {"state_specific": "102", "AIIMS_nearby": "AIIMS Jammu / AIIMS Awantipora", "state_ambulance": "108"},
    "Goa":             {"state_specific": "108", "AIIMS_nearby": "Goa Medical College", "state_ambulance": "108"},
    "Tripura":         {"state_specific": "108", "AIIMS_nearby": "AIIMS Tripura (planned)", "state_ambulance": "108"},
    "Manipur":         {"state_specific": "108", "AIIMS_nearby": "AIIMS Imphal (planned)", "state_ambulance": "108"},
    "Meghalaya":       {"state_specific": "108", "AIIMS_nearby": "AIIMS Shillong", "state_ambulance": "108"},
    "Nagaland":        {"state_specific": "108", "AIIMS_nearby": "AIIMS Dimapur (planned)", "state_ambulance": "108"},
    "Arunachal Pradesh":{"state_specific":"108", "AIIMS_nearby": "AIIMS Itanagar", "state_ambulance": "108"},
    "Mizoram":         {"state_specific": "108", "AIIMS_nearby": "AIIMS Aizawl (planned)", "state_ambulance": "108"},
    "Sikkim":          {"state_specific": "108", "AIIMS_nearby": "AIIMS Gangtok (planned)", "state_ambulance": "108"},
    "Chandigarh":      {"state_specific": "108", "AIIMS_nearby": "PGIMER Chandigarh", "state_ambulance": "108"},
    "Puducherry":      {"state_specific": "104", "AIIMS_nearby": "JIPMER Puducherry", "state_ambulance": "108"},
    "Andaman & Nicobar":{"state_specific":"108", "AIIMS_nearby": "GB Pant Hospital", "state_ambulance": "108"},
    "Lakshadweep":     {"state_specific": "108", "AIIMS_nearby": "Lakshadweep Hospital Kavaratti", "state_ambulance": "108"},
    "Dadra & Nagar Haveli":{"state_specific":"108","AIIMS_nearby":"DNH Government Hospital","state_ambulance":"108"},
    "Daman & Diu":     {"state_specific": "108", "AIIMS_nearby": "Daman Hospital", "state_ambulance": "108"},
    "Ladakh":          {"state_specific": "108", "AIIMS_nearby": "SNM Hospital Leh", "state_ambulance": "108"},
}

BLOOD_BANKS: Dict[str, List[Dict]] = {
    "Chennai":    [{"name": "Government Royapettah Hospital Blood Bank", "phone": "044-28194444", "address": "Royapettah, Chennai", "24h": True},
                   {"name": "SRMC Blood Bank", "phone": "044-45928888", "address": "Vadapalani, Chennai", "24h": True},
                   {"name": "Apollo Hospitals Blood Bank", "phone": "044-28290200", "address": "Greams Road, Chennai", "24h": True}],
    "Mumbai":     [{"name": "KEM Hospital Blood Bank", "phone": "022-24107000", "address": "Parel, Mumbai", "24h": True},
                   {"name": "Tata Memorial Blood Bank", "phone": "022-24177000", "address": "Parel, Mumbai", "24h": True}],
    "Delhi":      [{"name": "AIIMS Blood Bank", "phone": "011-26588500", "address": "Ansari Nagar, Delhi", "24h": True},
                   {"name": "Safdarjung Hospital Blood Bank", "phone": "011-26730000", "address": "Safdarjung, Delhi", "24h": True}],
    "Bangalore":  [{"name": "Victoria Hospital Blood Bank", "phone": "080-26700000", "address": "KR Market, Bangalore", "24h": True},
                   {"name": "Manipal Hospital Blood Bank", "phone": "080-25024444", "address": "HAL Airport Road, Bangalore", "24h": True}],
    "Hyderabad":  [{"name": "Osmania Hospital Blood Bank", "phone": "040-24600145", "address": "Afzalgunj, Hyderabad", "24h": True},
                   {"name": "Care Hospital Blood Bank", "phone": "040-67681681", "address": "Banjara Hills, Hyderabad", "24h": True}],
    "Kolkata":    [{"name": "IPGMER Blood Bank", "phone": "033-22041831", "address": "AJC Bose Road, Kolkata", "24h": True},
                   {"name": "RG Kar Blood Bank", "phone": "033-25565600", "address": "RG Kar, Kolkata", "24h": True}],
    "Pune":       [{"name": "Sassoon Hospital Blood Bank", "phone": "020-26128000", "address": "Sassoon Road, Pune", "24h": True},
                   {"name": "Ruby Hall Blood Bank", "phone": "020-66455100", "address": "Wanowrie, Pune", "24h": True}],
    "Ahmedabad":  [{"name": "SVP Hospital Blood Bank", "phone": "079-22680000", "address": "Ellisbridge, Ahmedabad", "24h": True}],
    "Jaipur":     [{"name": "SMS Hospital Blood Bank", "phone": "0141-2518888", "address": "Sawai Ram Singh Road, Jaipur", "24h": True}],
    "Lucknow":    [{"name": "KGMU Blood Bank", "phone": "0522-2257540", "address": "Shahmina Road, Lucknow", "24h": True}],
    "Coimbatore": [{"name": "GKNM Hospital Blood Bank", "phone": "0422-4305500", "address": "Race Course, Coimbatore", "24h": True},
                   {"name": "PSG Hospitals Blood Bank", "phone": "0422-4345789", "address": "Avinashi Road, Coimbatore", "24h": True}],
    "Madurai":    [{"name": "Government Rajaji Hospital", "phone": "0452-2532535", "address": "Pauper's Hospital Road, Madurai", "24h": True}],
}

POISON_CONTROL: Dict[str, Dict] = {
    "Pesticide/Organophosphate": {
        "antidote": "Atropine + Pralidoxime (hospital)",
        "first_aid": ["Remove from exposure area immediately", "Remove contaminated clothing (wear gloves)", "Wash skin with soap and water for 15-20 min", "If ingested and conscious, give activated charcoal only if instructed by doctor", "Do NOT induce vomiting"],
        "do_not": ["Do NOT induce vomiting", "Do NOT give any food or water", "Do NOT touch contaminated skin with bare hands"],
        "call": "108 or Poison Control 1800-116-117",
    },
    "Kerosene/Petroleum": {
        "antidote": "Supportive treatment in hospital",
        "first_aid": ["Remove person to fresh air", "If swallowed: DO NOT INDUCE VOMITING (aspiration risk is fatal)", "Give small amount of water if conscious", "Rush to hospital immediately"],
        "do_not": ["NEVER induce vomiting — kerosene in lungs is fatal", "Do NOT give milk"],
        "call": "108 immediately",
    },
    "Medicine Overdose": {
        "antidote": "Depends on drug — hospital will administer NAC for paracetamol, naloxone for opioids",
        "first_aid": ["Keep medication packet/bottle — show to paramedics", "If conscious: activated charcoal within 1 hour if instructed", "Do NOT induce vomiting", "If unconscious: recovery position, call 108"],
        "do_not": ["Do NOT induce vomiting", "Do NOT leave person alone", "Do NOT give coffee or other stimulants"],
        "call": "108 or Poison Control 1800-116-117",
    },
    "Acid/Alkali": {
        "antidote": "No specific antidote — dilution and hospital care",
        "first_aid": ["If on skin: flush with large amounts of water for 20+ minutes", "If in eyes: flush with clean water for 20+ minutes", "If swallowed: give small amounts of water only — do NOT give milk or try neutralisation", "Rush to hospital immediately"],
        "do_not": ["NEVER try to neutralise acid with alkali or vice versa", "Do NOT induce vomiting", "Do NOT give large amounts of water — just 1-2 glasses"],
        "call": "108 immediately",
    },
    "Food Poisoning": {
        "antidote": "Supportive: ORS, electrolytes",
        "first_aid": ["Let person vomit naturally if body wants to", "Give ORS to replace lost fluids", "Avoid solid food for 6-12 hours", "Seek medical help if bloody diarrhea, high fever, or dehydration signs"],
        "do_not": ["Do NOT stop natural vomiting", "Do NOT give anti-diarrhoeals for bloody diarrhoea"],
        "call": "Doctor if not improving in 24 hours. 108 for severe cases.",
    },
    "Alcohol Poisoning": {
        "antidote": "Supportive treatment — hospital for severe cases",
        "first_aid": ["If unconscious: recovery position (never on back — aspiration risk)", "Monitor breathing every 5 minutes", "Keep warm", "Do NOT give coffee or make them walk"],
        "do_not": ["NEVER leave unconscious person on their back", "Do NOT give coffee", "Do NOT put in cold shower"],
        "call": "108 if unconscious or breathing difficulty",
    },
}

HOSPITAL_TYPES: Dict[str, Dict] = {
    "Heart Attack":    {"specialist_needed": "Cardiologist/Cath Lab", "hospital_type": "Cardiac Centre or Multi-specialty Hospital", "what_to_tell_them": "Chest pain + sweating, time of onset, last meal"},
    "Stroke":          {"specialist_needed": "Neurologist/Stroke team", "hospital_type": "Hospital with CT Scan and Stroke unit", "what_to_tell_them": "FAST signs, exact time symptoms started"},
    "Snake Bite":      {"specialist_needed": "Emergency physician with anti-venom", "hospital_type": "Government hospital (anti-venom available) or District Hospital", "what_to_tell_them": "Snake description, bite location, time of bite"},
    "Burns":           {"specialist_needed": "Plastic Surgeon / Burns Unit", "hospital_type": "Hospital with Burns Unit", "what_to_tell_them": "Burn cause (flame/chemical/electrical), body area affected"},
    "Epileptic Seizure":{"specialist_needed":"Neurologist", "hospital_type": "Any hospital with emergency", "what_to_tell_them": "Duration of seizure, known epileptic, medications"},
    "Anaphylaxis/Allergic Shock":{"specialist_needed":"Emergency physician", "hospital_type": "Nearest emergency room", "what_to_tell_them": "Trigger (food/insect/medicine), time of exposure"},
}


class EmergencyProtocol:
    def get_protocol(self, emergency_type: str) -> Dict:
        return FIRST_AID_PROTOCOLS.get(emergency_type, {
            "steps": ["1. Ensure safety of yourself and victim.", "2. Call 108 immediately.", "3. Stay with person until help arrives."],
            "do_not": ["Do not panic"], "golden_hour_minutes": 60, "call_first": True,
        })

    def get_do_not(self, emergency_type: str) -> List[str]:
        return self.get_protocol(emergency_type).get("do_not", [])

    def get_golden_hour(self, emergency_type: str) -> int:
        return self.get_protocol(emergency_type).get("golden_hour_minutes", 60)


class FirstAidGuide:
    def get_steps(self, emergency_type: str) -> List[str]:
        return EmergencyProtocol().get_protocol(emergency_type).get("steps", [])

    def get_critical_warning(self, emergency_type: str) -> str:
        warnings = {
            "Heart Attack":    "Every minute without CPR = 10% less chance of survival. Start CPR if unconscious.",
            "Stroke":          "Time is brain. Every minute = 1.9 million neurons lost. CALL NOW.",
            "Snake Bite":      "NEVER cut, suck, or apply tourniquet. Immobilise and go to hospital IMMEDIATELY.",
            "Burns":           "20 minutes of cool running water. NOT ice. NOT butter. ONLY cool water.",
            "Choking":         "Act within 4 minutes. Alternate 5 back blows and 5 abdominal thrusts NOW.",
            "Drowning":        "Start CPR immediately. Do NOT waste time draining water.",
            "Electrocution":   "DO NOT TOUCH. Turn power off first. Only then check for breathing.",
            "Anaphylaxis/Allergic Shock": "EpiPen first. Then call 108. Antihistamine alone is NOT enough.",
        }
        return warnings.get(emergency_type, "Call 108 immediately and stay calm.")


class AmbulanceDirectory:
    def get_numbers(self, state: str) -> Dict:
        national = AMBULANCE_DIRECTORY.get("All States", {})
        state_info = AMBULANCE_DIRECTORY.get(state, {})
        return {**national, **state_info}

    def get_national_numbers(self) -> Dict:
        return AMBULANCE_DIRECTORY.get("All States", {})


class GoldenHourCalculator:
    def calculate(self, emergency_type: str, incident_time: str) -> Dict:
        golden = EmergencyProtocol().get_golden_hour(emergency_type)
        try:
            now   = datetime.now()
            inc_t = datetime.strptime(incident_time, "%H:%M")
            inc_dt = now.replace(hour=inc_t.hour, minute=inc_t.minute, second=0)
            if inc_dt > now:
                inc_dt -= timedelta(days=1)
            elapsed   = int((now - inc_dt).total_seconds() / 60)
            remaining = max(golden - elapsed, 0)
            pct_used  = min(elapsed / golden * 100, 100)

            if pct_used >= 100:
                urgency, color = "CRITICAL — Past Golden Hour", "#ef4444"
            elif pct_used >= 70:
                urgency, color = "URGENT — Running Out of Time", "#f97316"
            elif pct_used >= 40:
                urgency, color = "HIGH — Act Quickly", "#f59e0b"
            else:
                urgency, color = "ACTIVE — Within Golden Hour", "#22c55e"

            return {"elapsed_minutes": elapsed, "remaining_minutes": remaining,
                    "golden_hour_minutes": golden, "urgency": urgency, "color": color,
                    "pct_elapsed": round(pct_used, 1)}
        except Exception:
            return {"elapsed_minutes": 0, "remaining_minutes": golden,
                    "golden_hour_minutes": golden, "urgency": "ACTIVE", "color": "#22c55e",
                    "pct_elapsed": 0}


class HospitalFinder:
    def find_type(self, emergency_type: str) -> Dict:
        return HOSPITAL_TYPES.get(emergency_type, {
            "specialist_needed": "Emergency Physician",
            "hospital_type": "Nearest multi-specialty hospital with emergency",
            "what_to_tell_them": "Nature of emergency, time of onset, patient age",
        })
