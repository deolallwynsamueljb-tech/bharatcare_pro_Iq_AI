"""
BharatCare AI Pro · DrugIQ Engine v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Medicine intelligence: profiles, interactions, dosage, generics.
Author: Deol Allwyn Samuel J B · VLSI · CIT · Afynix Digital
"""

import difflib
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

DRUG_DATABASE: Dict[str, Dict] = {
    "Paracetamol": {"generic": "Paracetamol", "brands": ["Crocin", "Dolo 650", "Calpol"], "category": "Analgesic/Antipyretic", "class": "Para-aminophenol derivative",
        "indications": ["Fever", "Mild-moderate pain", "Headache", "Toothache", "Post-vaccination fever"],
        "contraindications": ["Severe liver disease", "Known hypersensitivity"],
        "side_effects": {"common": ["Nausea (rare at therapeutic doses)"], "rare": ["Liver enzyme elevation"], "serious": ["Hepatotoxicity in overdose (>4g/day)"]},
        "dosage": {"adult": "500-1000mg every 6-8 hours (max 4g/day)", "child": "10-15 mg/kg every 6 hours", "elderly": "500-750mg every 8 hours"},
        "max_dose_mg": 4000, "pregnancy_category": "B", "breastfeeding_safe": True, "kidney_adjust": False, "liver_adjust": True,
        "interactions": ["Warfarin (high doses)", "Alcohol (liver toxicity)", "Rifampicin"],
        "mechanism": "Inhibits prostaglandin synthesis in CNS; modulates pain threshold",
        "half_life_hours": 2.0, "price_brand_inr": 15, "price_generic_inr": 3, "otc": True, "schedule": "OTC"},
    "Ibuprofen": {"generic": "Ibuprofen", "brands": ["Brufen", "Combiflam (with paracetamol)", "Advil"], "category": "NSAID", "class": "Propionic acid derivative",
        "indications": ["Fever", "Pain", "Arthritis", "Menstrual pain", "Dental pain"],
        "contraindications": ["Peptic ulcer", "Renal impairment", "Third trimester pregnancy", "Asthma (some patients)", "Dengue (avoid — bleeding risk)"],
        "side_effects": {"common": ["GI upset", "Nausea", "Heartburn"], "rare": ["Peptic ulcer", "Renal dysfunction"], "serious": ["GI bleeding", "Cardiovascular events (long term)"]},
        "dosage": {"adult": "200-400mg every 6-8 hours with food (max 1200mg OTC, 3200mg Rx)", "child": "5-10 mg/kg every 6-8 hours (>6 months)", "elderly": "Start low 200mg — GI and renal risk"},
        "max_dose_mg": 3200, "pregnancy_category": "C (D in 3rd trimester)", "breastfeeding_safe": True, "kidney_adjust": True, "liver_adjust": True,
        "interactions": ["Aspirin", "Warfarin", "ACE inhibitors", "Diuretics", "Lithium"],
        "mechanism": "Non-selective COX-1/COX-2 inhibitor — reduces prostaglandin synthesis",
        "half_life_hours": 2.0, "price_brand_inr": 20, "price_generic_inr": 5, "otc": True, "schedule": "OTC"},
    "Aspirin": {"generic": "Aspirin (Acetylsalicylic acid)", "brands": ["Ecosprin", "Aspro", "Disprin"], "category": "NSAID/Antiplatelet", "class": "Salicylate",
        "indications": ["Antiplatelet (low dose 75-150mg)", "Pain", "Fever", "Kawasaki disease"],
        "contraindications": ["Children under 16 (Reye's syndrome)", "Active peptic ulcer", "Haemophilia", "Dengue (bleeding risk)"],
        "side_effects": {"common": ["GI upset", "Heartburn"], "rare": ["GI bleeding", "Tinnitus (high dose)"], "serious": ["Reye's syndrome in children", "Major GI bleed"]},
        "dosage": {"adult": "Antiplatelet: 75-150mg/day; Pain: 300-600mg every 4-6 hours", "child": "AVOID in children <16 years except Kawasaki (specialist)", "elderly": "75-150mg/day for antiplatelet"},
        "max_dose_mg": 4000, "pregnancy_category": "D (3rd trimester)", "breastfeeding_safe": False, "kidney_adjust": True, "liver_adjust": True,
        "interactions": ["Warfarin (major — bleeding)", "Ibuprofen (reduces antiplatelet effect)", "Methotrexate"],
        "mechanism": "Irreversibly inhibits COX-1 and COX-2; inhibits thromboxane A2 platelet aggregation",
        "half_life_hours": 3.0, "price_brand_inr": 10, "price_generic_inr": 2, "otc": True, "schedule": "OTC"},
    "Amoxicillin": {"generic": "Amoxicillin", "brands": ["Mox", "Amoxil", "Novamox"], "category": "Antibiotic", "class": "Aminopenicillin",
        "indications": ["Throat/ear/sinus infections", "Pneumonia", "UTI", "Typhoid (combined)", "H. pylori"],
        "contraindications": ["Penicillin allergy", "Infectious mononucleosis"],
        "side_effects": {"common": ["Diarrhoea", "Nausea", "Rash"], "rare": ["Antibiotic-associated colitis"], "serious": ["Anaphylaxis (penicillin allergy)", "Stevens-Johnson syndrome"]},
        "dosage": {"adult": "250-500mg every 8 hours (500-875mg every 12 hours for severe)", "child": "25-45 mg/kg/day in 2-3 divided doses", "elderly": "Same as adult; adjust for renal function"},
        "max_dose_mg": 3000, "pregnancy_category": "B", "breastfeeding_safe": True, "kidney_adjust": True, "liver_adjust": False,
        "interactions": ["Warfarin", "Methotrexate", "Oral contraceptives (may reduce efficacy)"],
        "mechanism": "Beta-lactam: inhibits bacterial cell wall synthesis by binding PBPs",
        "half_life_hours": 1.5, "price_brand_inr": 45, "price_generic_inr": 15, "otc": False, "schedule": "H"},
    "Azithromycin": {"generic": "Azithromycin", "brands": ["Zithromax", "Azee", "Azifast"], "category": "Antibiotic", "class": "Macrolide",
        "indications": ["Community-acquired pneumonia", "URTI", "STIs (chlamydia)", "Typhoid (uncomplicated)", "COVID-19 (limited evidence)"],
        "contraindications": ["Macrolide allergy", "Prolonged QT", "Liver disease"],
        "side_effects": {"common": ["Nausea", "Diarrhoea", "Abdominal pain"], "rare": ["Liver dysfunction", "QT prolongation"], "serious": ["Cardiovascular events in high-risk patients"]},
        "dosage": {"adult": "500mg day 1, then 250mg days 2-5 (Z-pack) or 500mg/day for 3 days", "child": "10 mg/kg day 1, then 5 mg/kg days 2-5", "elderly": "Same with caution for cardiac arrhythmia"},
        "max_dose_mg": 500, "pregnancy_category": "B", "breastfeeding_safe": True, "kidney_adjust": False, "liver_adjust": True,
        "interactions": ["Warfarin", "Digoxin", "Antacids reduce absorption", "QT-prolonging drugs"],
        "mechanism": "Binds 50S ribosomal subunit — inhibits bacterial protein synthesis",
        "half_life_hours": 68.0, "price_brand_inr": 80, "price_generic_inr": 25, "otc": False, "schedule": "H"},
    "Ciprofloxacin": {"generic": "Ciprofloxacin", "brands": ["Ciplox", "Cifran", "Quintor"], "category": "Antibiotic", "class": "Fluoroquinolone",
        "indications": ["UTI", "Typhoid", "GI infections", "Respiratory infections", "Skin infections"],
        "contraindications": ["Children/adolescents (risk of tendon damage)", "Pregnancy", "Myasthenia gravis", "Epilepsy"],
        "side_effects": {"common": ["Nausea", "Diarrhoea", "Dizziness"], "rare": ["Tendinitis/tendon rupture", "QT prolongation", "Photosensitivity"], "serious": ["CNS effects", "Aortic aneurysm (long-term)"]},
        "dosage": {"adult": "250-750mg every 12 hours (depends on indication)", "child": "Avoid in children; 10-15 mg/kg for serious infections only", "elderly": "Reduce dose for renal impairment"},
        "max_dose_mg": 1500, "pregnancy_category": "C", "breastfeeding_safe": False, "kidney_adjust": True, "liver_adjust": True,
        "interactions": ["Antacids/calcium (reduce absorption)", "Warfarin (increases effect)", "Theophylline", "NSAIDs (seizure risk)"],
        "mechanism": "Inhibits bacterial DNA gyrase and topoisomerase IV",
        "half_life_hours": 4.0, "price_brand_inr": 40, "price_generic_inr": 12, "otc": False, "schedule": "H"},
    "Metformin": {"generic": "Metformin", "brands": ["Glycomet", "Glucophage", "Metsmall"], "category": "Antidiabetic", "class": "Biguanide",
        "indications": ["Type 2 diabetes (first-line)", "PCOS", "Pre-diabetes (high risk)", "Metabolic syndrome"],
        "contraindications": ["eGFR <30 mL/min", "Acute MI", "Liver failure", "Contrast dye procedure (hold temporarily)"],
        "side_effects": {"common": ["Nausea", "Diarrhoea", "GI upset (take with food)"], "rare": ["Vitamin B12 deficiency", "Metallic taste"], "serious": ["Lactic acidosis (rare — usually in renal failure)"]},
        "dosage": {"adult": "Start 500mg with evening meal; increase to 500-850mg twice/thrice daily", "child": "10 years+: 500mg with food; max 2g/day", "elderly": "Monitor eGFR; hold if eGFR <45"},
        "max_dose_mg": 3000, "pregnancy_category": "B", "breastfeeding_safe": True, "kidney_adjust": True, "liver_adjust": True,
        "interactions": ["Alcohol (lactic acidosis risk)", "Iodinated contrast (hold 48h)", "Carbonic anhydrase inhibitors"],
        "mechanism": "Inhibits hepatic gluconeogenesis; increases insulin sensitivity; decreases GI glucose absorption",
        "half_life_hours": 5.0, "price_brand_inr": 35, "price_generic_inr": 8, "otc": False, "schedule": "H"},
    "Amlodipine": {"generic": "Amlodipine", "brands": ["Amlip", "Amlong", "Stamlo"], "category": "Antihypertensive", "class": "Dihydropyridine CCB",
        "indications": ["Hypertension", "Stable angina", "Vasospastic angina"],
        "contraindications": ["Severe hypotension", "Cardiogenic shock", "Severe aortic stenosis"],
        "side_effects": {"common": ["Ankle oedema", "Flushing", "Headache", "Dizziness"], "rare": ["Gingival hyperplasia"], "serious": ["Hypotension (rare at therapeutic doses)"]},
        "dosage": {"adult": "2.5-5mg once daily; may increase to 10mg/day", "child": "0.1-0.2 mg/kg/day (specialist)", "elderly": "Start 2.5mg — elderly more prone to ankle oedema"},
        "max_dose_mg": 10, "pregnancy_category": "C", "breastfeeding_safe": False, "kidney_adjust": False, "liver_adjust": True,
        "interactions": ["Simvastatin >20mg (myopathy risk)", "Cyclosporine", "CYP3A4 inhibitors (grapefruit juice)"],
        "mechanism": "Blocks L-type calcium channels in vascular smooth muscle → vasodilatation",
        "half_life_hours": 35.0, "price_brand_inr": 25, "price_generic_inr": 5, "otc": False, "schedule": "H"},
    "Atorvastatin": {"generic": "Atorvastatin", "brands": ["Lipitor", "Atorva", "Tonact"], "category": "Lipid-lowering", "class": "HMG-CoA reductase inhibitor (Statin)",
        "indications": ["High cholesterol", "Cardiovascular prevention", "Familial hypercholesterolaemia"],
        "contraindications": ["Active liver disease", "Pregnancy", "Breastfeeding", "Myopathy history"],
        "side_effects": {"common": ["Myalgia (muscle ache)", "GI upset"], "rare": ["Rhabdomyolysis", "Liver enzyme elevation"], "serious": ["Severe myopathy/rhabdomyolysis (rare)"]},
        "dosage": {"adult": "10-80mg once daily (evening)", "child": "10-20mg specialist supervised", "elderly": "Start 10-20mg; monitor CK and LFT"},
        "max_dose_mg": 80, "pregnancy_category": "X", "breastfeeding_safe": False, "kidney_adjust": False, "liver_adjust": True,
        "interactions": ["Amlodipine >10mg (myopathy)", "Clarithromycin", "Grapefruit juice", "Fibrates", "Niacin"],
        "mechanism": "Competitively inhibits HMG-CoA reductase — reduces hepatic cholesterol synthesis",
        "half_life_hours": 14.0, "price_brand_inr": 30, "price_generic_inr": 8, "otc": False, "schedule": "H"},
    "Omeprazole": {"generic": "Omeprazole", "brands": ["Omez", "Prilosec", "Ocid"], "category": "Antacid/PPI", "class": "Proton Pump Inhibitor",
        "indications": ["GERD", "Peptic ulcer", "H. pylori eradication", "NSAID-induced ulcer prevention", "Zollinger-Ellison"],
        "contraindications": ["Known hypersensitivity", "Caution: with clopidogrel"],
        "side_effects": {"common": ["Headache", "Diarrhoea", "Nausea"], "rare": ["Hypomagnesaemia (long term)", "C. diff infection"], "serious": ["Bone fracture risk (long-term use)", "Vitamin B12 deficiency"]},
        "dosage": {"adult": "20-40mg once daily before breakfast", "child": "0.7-3.5 mg/kg/day", "elderly": "Standard dose usually effective"},
        "max_dose_mg": 80, "pregnancy_category": "C", "breastfeeding_safe": True, "kidney_adjust": False, "liver_adjust": True,
        "interactions": ["Clopidogrel (reduces antiplatelet effect)", "Ketoconazole", "Methotrexate"],
        "mechanism": "Irreversibly inhibits gastric H+/K+ ATPase (proton pump)",
        "half_life_hours": 1.0, "price_brand_inr": 20, "price_generic_inr": 4, "otc": True, "schedule": "OTC"},
    "Cetirizine": {"generic": "Cetirizine", "brands": ["Zyrtec", "Cetzine", "Alerid"], "category": "Antihistamine", "class": "Second-generation H1 receptor antagonist",
        "indications": ["Allergic rhinitis", "Urticaria (hives)", "Seasonal allergy", "Allergic conjunctivitis"],
        "contraindications": ["Severe renal failure", "Hypersensitivity to hydroxyzine"],
        "side_effects": {"common": ["Drowsiness (less than first-gen)", "Dry mouth"], "rare": ["Agitation in children"], "serious": ["QT prolongation at high doses (rare)"]},
        "dosage": {"adult": "10mg once daily or 5mg twice daily", "child": "2-5 years: 2.5mg twice daily; 6+: 5-10mg/day", "elderly": "5mg once daily (renal dose adjust)"},
        "max_dose_mg": 20, "pregnancy_category": "B", "breastfeeding_safe": False, "kidney_adjust": True, "liver_adjust": False,
        "interactions": ["Alcohol (increased sedation)", "CNS depressants"],
        "mechanism": "Selective H1 histamine receptor antagonist; mast cell membrane stabiliser",
        "half_life_hours": 8.0, "price_brand_inr": 15, "price_generic_inr": 4, "otc": True, "schedule": "OTC"},
    "Hydroxychloroquine": {"generic": "Hydroxychloroquine", "brands": ["Plaquenil", "HCQS", "Dolquine"], "category": "Antimalarial/DMARD", "class": "4-aminoquinoline",
        "indications": ["Malaria prophylaxis/treatment", "Rheumatoid arthritis", "Lupus", "COVID-19 (off-label, limited evidence)"],
        "contraindications": ["Retinal disease", "G6PD deficiency", "Porphyria"],
        "side_effects": {"common": ["Nausea", "Headache", "Skin pigmentation"], "rare": ["Retinopathy (long term — annual eye check needed)"], "serious": ["Irreversible retinal damage", "QT prolongation", "Cardiomyopathy"]},
        "dosage": {"adult": "RA: 200-400mg/day; Malaria: 400mg weekly", "child": "5 mg/kg/day (specialist)", "elderly": "Lower dose; monitor renal function"},
        "max_dose_mg": 400, "pregnancy_category": "C", "breastfeeding_safe": True, "kidney_adjust": True, "liver_adjust": True,
        "interactions": ["Digoxin", "Cyclosporine", "QT-prolonging drugs", "Antacids reduce absorption"],
        "mechanism": "Concentrates in lysosomes; inhibits antigen presentation; anti-inflammatory",
        "half_life_hours": 540.0, "price_brand_inr": 50, "price_generic_inr": 15, "otc": False, "schedule": "H"},
    "Losartan": {"generic": "Losartan", "brands": ["Losar", "Cozaar", "Repace"], "category": "Antihypertensive", "class": "Angiotensin Receptor Blocker (ARB)",
        "indications": ["Hypertension", "Diabetic nephropathy", "Heart failure", "Stroke prevention"],
        "contraindications": ["Pregnancy", "Bilateral renal artery stenosis", "Hyperkalaemia"],
        "side_effects": {"common": ["Dizziness", "Hyperkalaemia"], "rare": ["Angioedema (less than ACEi)"], "serious": ["Foetal toxicity in pregnancy (absolutely contraindicated)"]},
        "dosage": {"adult": "50mg once daily; can increase to 100mg", "child": "0.7 mg/kg/day (specialist)", "elderly": "25mg starting dose"},
        "max_dose_mg": 150, "pregnancy_category": "D (absolutely contraindicated in 2nd/3rd trimester)", "breastfeeding_safe": False, "kidney_adjust": True, "liver_adjust": True,
        "interactions": ["NSAIDs (reduce effect; increase renal risk)", "K-sparing diuretics", "Lithium"],
        "mechanism": "Selectively blocks AT1 angiotensin II receptor → vasodilation + reduced aldosterone",
        "half_life_hours": 6.0, "price_brand_inr": 30, "price_generic_inr": 8, "otc": False, "schedule": "H"},
    "Sertraline": {"generic": "Sertraline", "brands": ["Zoloft", "Serta", "Daxid"], "category": "Antidepressant", "class": "Selective Serotonin Reuptake Inhibitor (SSRI)",
        "indications": ["Major depression", "OCD", "Panic disorder", "PTSD", "Social anxiety", "Premenstrual dysphoria"],
        "contraindications": ["MAOIs (within 14 days)", "Pimozide"],
        "side_effects": {"common": ["Nausea", "Diarrhoea", "Insomnia", "Sexual dysfunction"], "rare": ["Serotonin syndrome (with other serotonergic drugs)"], "serious": ["Suicidality in adolescents (monitor)", "Serotonin syndrome"]},
        "dosage": {"adult": "Start 50mg/day; may increase to 200mg/day", "child": "6-12 years OCD: start 25mg; adolescents 50mg (psychiatrist)", "elderly": "Start 25-50mg — slower titration"},
        "max_dose_mg": 200, "pregnancy_category": "C", "breastfeeding_safe": True, "kidney_adjust": False, "liver_adjust": True,
        "interactions": ["MAOIs (serotonin syndrome — fatal)", "Warfarin", "Tramadol", "Triptans", "St. John's Wort"],
        "mechanism": "Selectively inhibits serotonin reuptake → increases synaptic serotonin",
        "half_life_hours": 26.0, "price_brand_inr": 45, "price_generic_inr": 12, "otc": False, "schedule": "H1"},
    "ORS": {"generic": "Oral Rehydration Salts", "brands": ["Electral", "Enerzal ORS", "WHO-ORS"], "category": "Electrolyte replacement", "class": "Crystalloid solution",
        "indications": ["Diarrhoea dehydration", "Vomiting", "Fever fluid loss", "Heat exhaustion", "After exercise"],
        "contraindications": ["Severe dehydration needing IV", "Inability to drink", "Cholera with severe vomiting"],
        "side_effects": {"common": ["Nausea if taken too fast"], "rare": [], "serious": []},
        "dosage": {"adult": "200-400mL after each loose stool", "child": "Under 2 years: 50-100mL/kg over 4 hours; 2-10 years: 100-200mL after each stool", "elderly": "As per fluid loss"},
        "max_dose_mg": 0, "pregnancy_category": "A", "breastfeeding_safe": True, "kidney_adjust": False, "liver_adjust": False,
        "interactions": [],
        "mechanism": "Glucose-coupled sodium transport across intestinal mucosa restores fluid and electrolyte balance",
        "half_life_hours": 0, "price_brand_inr": 15, "price_generic_inr": 5, "otc": True, "schedule": "OTC"},
    "Vitamin D3": {"generic": "Cholecalciferol (Vitamin D3)", "brands": ["D-Rise", "Calcirol", "Uprise D3"], "category": "Vitamin/Supplement", "class": "Fat-soluble vitamin",
        "indications": ["Vitamin D deficiency", "Osteoporosis prevention", "Rickets", "Immune support"],
        "contraindications": ["Hypercalcaemia", "Vitamin D toxicity"],
        "side_effects": {"common": ["None at recommended doses"], "rare": ["Nausea, constipation (high dose)"], "serious": ["Hypercalcaemia in toxicity (>10,000 IU/day long term)"]},
        "dosage": {"adult": "1000-2000 IU/day maintenance; 60,000 IU weekly for 8 weeks if deficient", "child": "400-600 IU/day infant; 600-1000 IU/day older children", "elderly": "800-1000 IU/day"},
        "max_dose_mg": 4000, "pregnancy_category": "A (C at high doses)", "breastfeeding_safe": True, "kidney_adjust": True, "liver_adjust": False,
        "interactions": ["Thiazide diuretics (hypercalcaemia)", "Digoxin (hypercalcaemia increases toxicity)"],
        "mechanism": "Precursor converted to active 1,25-dihydroxyvitamin D; regulates calcium/phosphorus; immune modulation",
        "half_life_hours": 576.0, "price_brand_inr": 40, "price_generic_inr": 12, "otc": True, "schedule": "OTC"},
    "Metronidazole": {"generic": "Metronidazole", "brands": ["Flagyl", "Metrogyl", "Aristogyl"], "category": "Antibiotic/Antiprotozoal", "class": "Nitroimidazole",
        "indications": ["Anaerobic bacterial infections", "Amoebiasis", "Giardia", "H. pylori (with other drugs)", "Trichomonas"],
        "contraindications": ["First trimester pregnancy", "Alcohol use (disulfiram-like reaction)"],
        "side_effects": {"common": ["Nausea", "Metallic taste", "Dark urine"], "rare": ["Peripheral neuropathy (long term)"], "serious": ["Seizures (high dose or CNS disease)"]},
        "dosage": {"adult": "400-500mg three times daily for 7-10 days", "child": "35-50 mg/kg/day in 3 doses", "elderly": "Standard dose; avoid long-term"},
        "max_dose_mg": 2000, "pregnancy_category": "B (avoid 1st trimester)", "breastfeeding_safe": False, "kidney_adjust": False, "liver_adjust": True,
        "interactions": ["Alcohol (severe nausea/vomiting)", "Warfarin (increases INR)", "Lithium"],
        "mechanism": "Reduced to cytotoxic intermediates inside anaerobic organisms — disrupts DNA",
        "half_life_hours": 8.0, "price_brand_inr": 20, "price_generic_inr": 5, "otc": False, "schedule": "H"},
    "Folic Acid": {"generic": "Folic Acid (Vitamin B9)", "brands": ["Folvite", "Folitrax (high dose)", "Folate tablet"], "category": "Vitamin/Supplement", "class": "Water-soluble B vitamin",
        "indications": ["Neural tube defect prevention in pregnancy", "Folate deficiency anaemia", "Methotrexate supplement", "PCOS"],
        "contraindications": ["Undiagnosed megaloblastic anaemia (B12 deficiency may be masked)"],
        "side_effects": {"common": ["None at physiological doses"], "rare": ["Nausea, bloating"], "serious": []},
        "dosage": {"adult": "Preconception/pregnancy: 400-800 mcg/day; High risk: 5mg/day", "child": "Supplement: 100-400 mcg/day", "elderly": "400 mcg/day"},
        "max_dose_mg": 5, "pregnancy_category": "A", "breastfeeding_safe": True, "kidney_adjust": False, "liver_adjust": False,
        "interactions": ["Methotrexate (antagonism)", "Phenytoin (may reduce levels)"],
        "mechanism": "Essential cofactor for nucleotide synthesis and DNA methylation; critical for cell division",
        "half_life_hours": 3.5, "price_brand_inr": 10, "price_generic_inr": 2, "otc": True, "schedule": "OTC"},
    "Salbutamol": {"generic": "Salbutamol (Albuterol)", "brands": ["Asthalin", "Ventolin", "Levolin"], "category": "Bronchodilator", "class": "Short-acting beta2 agonist (SABA)",
        "indications": ["Acute asthma attack (rescue inhaler)", "COPD exacerbation", "Exercise-induced bronchoconstriction"],
        "contraindications": ["Hypokalaemia", "Tachyarrhythmias (use with caution)"],
        "side_effects": {"common": ["Tremor", "Tachycardia", "Headache", "Hypokalaemia (high dose)"], "rare": [], "serious": ["Severe hypokalaemia", "Paradoxical bronchospasm (rare)"]},
        "dosage": {"adult": "Inhaler: 2 puffs (200mcg) every 4-6 hours PRN; Nebuliser: 2.5mg in 3mL NS", "child": "1-2 puffs every 4-6 hours; Neb: 0.15 mg/kg", "elderly": "Standard inhaler dose"},
        "max_dose_mg": 32, "pregnancy_category": "C", "breastfeeding_safe": True, "kidney_adjust": False, "liver_adjust": False,
        "interactions": ["Beta-blockers (antagonism)", "Diuretics (hypokalaemia)", "MAOIs"],
        "mechanism": "Selective beta2 adrenergic agonist → bronchial smooth muscle relaxation",
        "half_life_hours": 4.0, "price_brand_inr": 60, "price_generic_inr": 20, "otc": False, "schedule": "H"},
    "Insulin Glargine": {"generic": "Insulin Glargine", "brands": ["Lantus", "Basalog", "Glaritus"], "category": "Antidiabetic/Insulin", "class": "Long-acting basal insulin",
        "indications": ["Type 1 diabetes", "Type 2 diabetes requiring insulin"],
        "contraindications": ["Hypoglycaemia episodes", "Hypersensitivity to insulin"],
        "side_effects": {"common": ["Hypoglycaemia", "Injection site reactions", "Weight gain"], "rare": ["Lipodystrophy at injection site"], "serious": ["Severe hypoglycaemia (especially if meal missed)"]},
        "dosage": {"adult": "0.2 units/kg/day subcutaneous, once daily (bedtime or same time daily)", "child": "0.2 units/kg/day specialist supervised", "elderly": "Start lower — hypoglycaemia risk"},
        "max_dose_mg": 0, "pregnancy_category": "C", "breastfeeding_safe": True, "kidney_adjust": True, "liver_adjust": True,
        "interactions": ["Sulphonylureas (hypoglycaemia risk)", "Alcohol", "Beta-blockers (mask hypoglycaemia symptoms)", "Corticosteroids"],
        "mechanism": "Basal insulin analogue — provides slow, steady insulin release over 24 hours",
        "half_life_hours": 24.0, "price_brand_inr": 850, "price_generic_inr": 350, "otc": False, "schedule": "H"},
    "Artemether-Lumefantrine": {"generic": "Artemether + Lumefantrine", "brands": ["Coartem", "Falcigo Kit", "Larinate"], "category": "Antimalarial", "class": "ACT (Artemisinin Combination Therapy)",
        "indications": ["Uncomplicated Plasmodium falciparum malaria", "First-line treatment"],
        "contraindications": ["First trimester pregnancy (use quinine+clindamycin instead)", "Severe malaria (use IV artesunate)", "QT prolongation"],
        "side_effects": {"common": ["Dizziness", "Headache", "Nausea", "Vomiting", "Fatigue"], "rare": ["QT prolongation"], "serious": ["Severe allergic reaction"]},
        "dosage": {"adult": "4 tablets at 0, 8, 24, 36, 48, 60 hours (weight >35kg)", "child": "Weight-based: 5-14kg: 1 tab; 15-24kg: 2 tabs; 25-34kg: 3 tabs; each dose at same intervals", "elderly": "Standard dose"},
        "max_dose_mg": 0, "pregnancy_category": "C (use after 1st trimester)", "breastfeeding_safe": True, "kidney_adjust": False, "liver_adjust": True,
        "interactions": ["QT-prolonging drugs", "CYP3A4 inhibitors/inducers", "Fatty food improves absorption"],
        "mechanism": "Artemether: rapidly kills ring and trophozoite stages; Lumefantrine: kills remaining parasites (longer acting)",
        "half_life_hours": 2.0, "price_brand_inr": 180, "price_generic_inr": 80, "otc": False, "schedule": "H"},
}

# ── Interaction database ───────────────────────────────────────────────────────
INTERACTION_DB: Dict[Tuple, Dict] = {
    ("Warfarin", "Aspirin"):         {"severity": "Major", "effect": "Significantly increased bleeding risk", "recommendation": "Avoid combination unless specifically indicated (e.g., mechanical valve). Monitor INR closely."},
    ("Warfarin", "Ibuprofen"):       {"severity": "Major", "effect": "Increased anticoagulant effect + GI bleeding risk", "recommendation": "Use paracetamol instead. If NSAID needed, monitor INR."},
    ("Warfarin", "Amoxicillin"):     {"severity": "Moderate", "effect": "May increase INR — gut flora alteration reduces Vitamin K", "recommendation": "Monitor INR during and 1 week after antibiotic course."},
    ("Metformin", "Alcohol"):        {"severity": "Major", "effect": "Increased risk of lactic acidosis", "recommendation": "Avoid alcohol. Educate patient about risks."},
    ("Sertraline", "Tramadol"):      {"severity": "Major", "effect": "Serotonin syndrome risk — potentially fatal", "recommendation": "Avoid combination. Use alternative analgesic."},
    ("Ciprofloxacin", "Antacids"):   {"severity": "Moderate", "effect": "Antacids reduce ciprofloxacin absorption by up to 90%", "recommendation": "Take ciprofloxacin 2 hours before or 6 hours after antacids."},
    ("Atorvastatin", "Clarithromycin"):{"severity": "Major", "effect": "CYP3A4 inhibition increases statin levels → rhabdomyolysis", "recommendation": "Hold atorvastatin during clarithromycin course. Use azithromycin if possible."},
    ("Metronidazole", "Alcohol"):    {"severity": "Major", "effect": "Disulfiram-like reaction: severe nausea, vomiting, flushing, hypotension", "recommendation": "Avoid all alcohol during treatment and 48h after last dose."},
    ("Aspirin", "Ibuprofen"):        {"severity": "Moderate", "effect": "Ibuprofen may reduce antiplatelet effect of low-dose aspirin", "recommendation": "If both needed, take aspirin 30min before ibuprofen or use paracetamol for pain."},
    ("Losartan", "Ibuprofen"):       {"severity": "Moderate", "effect": "NSAIDs reduce antihypertensive effect; increase kidney injury risk", "recommendation": "Avoid regular NSAIDs in patients on ARBs. Use paracetamol."},
    ("Paracetamol", "Alcohol"):      {"severity": "Major", "effect": "Hepatotoxicity risk significantly increased with chronic alcohol use", "recommendation": "Avoid paracetamol in chronic alcoholics. Use maximum 2g/day if unavoidable."},
    ("Metformin", "Iodinated Contrast"):{"severity": "Major", "effect": "Risk of contrast-induced nephropathy → metformin accumulation → lactic acidosis", "recommendation": "Hold metformin 48h before and after contrast procedure."},
    ("Insulin Glargine", "Alcohol"): {"severity": "Major", "effect": "Alcohol causes unpredictable glucose changes + masks hypoglycaemia symptoms", "recommendation": "Avoid alcohol. If drinking, eat with alcohol and monitor glucose closely."},
    ("Cetirizine", "Alcohol"):       {"severity": "Moderate", "effect": "Enhanced CNS depression — sedation, impaired driving", "recommendation": "Avoid alcohol with cetirizine. Warn patient about impaired driving."},
    ("Salbutamol", "Beta-blockers"): {"severity": "Major", "effect": "Beta-blockers antagonise bronchodilator effect — can cause bronchoconstriction", "recommendation": "Avoid non-selective beta-blockers in asthma. Use cardioselective (bisoprolol) if needed."},
}

PREGNANCY_CATEGORY_INFO = {
    "A": "Adequate studies show no risk to fetus in first trimester. Safest.",
    "B": "Animal studies show no risk; no adequate human studies. Generally considered safe.",
    "C": "Animal studies show adverse effects; no adequate human studies. Use only if benefits outweigh risks.",
    "D": "Evidence of human foetal risk; benefits may outweigh risks in serious situations.",
    "X": "Studies show foetal abnormalities. Contraindicated in pregnancy.",
}


class DrugSearcher:
    def search(self, query: str) -> List[Dict]:
        query_low = query.lower()
        results   = []
        for name, drug in DRUG_DATABASE.items():
            score = 0
            if query_low in name.lower(): score = 10
            elif any(query_low in b.lower() for b in drug.get("brands", [])): score = 9
            elif any(query_low in ind.lower() for ind in drug.get("indications", [])): score = 5
            if score > 0:
                results.append({"name": name, "score": score, **drug})
        if not results:
            matches = difflib.get_close_matches(query, DRUG_DATABASE.keys(), n=5, cutoff=0.4)
            results = [{"name": m, "score": 3, **DRUG_DATABASE[m]} for m in matches]
        return sorted(results, key=lambda x: x["score"], reverse=True)[:5]

    def get_drug(self, name: str) -> Optional[Dict]:
        if name in DRUG_DATABASE:
            return {"name": name, **DRUG_DATABASE[name]}
        matches = difflib.get_close_matches(name, DRUG_DATABASE.keys(), n=1, cutoff=0.5)
        if matches:
            return {"name": matches[0], **DRUG_DATABASE[matches[0]]}
        # Search in brand names
        for drug_name, drug in DRUG_DATABASE.items():
            if any(name.lower() in b.lower() for b in drug.get("brands", [])):
                return {"name": drug_name, **drug}
        return None


class InteractionChecker:
    def _normalize(self, name: str) -> str:
        d = DrugSearcher().get_drug(name)
        return d["name"] if d else name

    def check(self, drug1: str, drug2: str) -> Dict:
        d1 = self._normalize(drug1)
        d2 = self._normalize(drug2)
        for (a, b), info in INTERACTION_DB.items():
            if (a == d1 and b == d2) or (a == d2 and b == d1):
                return {"interaction_found": True, "drug1": d1, "drug2": d2, **info}
        return {"interaction_found": False, "drug1": d1, "drug2": d2, "severity": "None",
                "effect": "No known major interaction found", "recommendation": "Continue as prescribed. Consult pharmacist for complete interaction check."}

    def check_multiple(self, drugs: List[str]) -> List[Dict]:
        results = []
        for i in range(len(drugs)):
            for j in range(i + 1, len(drugs)):
                r = self.check(drugs[i], drugs[j])
                if r["interaction_found"]:
                    results.append(r)
        return results


class DosageCalculator:
    def child_dose_clark(self, adult_dose_mg: float, weight_kg: float) -> float:
        return round(adult_dose_mg * weight_kg / 70, 1)

    def child_dose_young(self, adult_dose_mg: float, age_years: int) -> float:
        return round(adult_dose_mg * age_years / (age_years + 12), 1)

    def adult_dose(self, drug: str, weight_kg: float, age: int, kidney_function: str = "Normal") -> Dict:
        d = DrugSearcher().get_drug(drug)
        if not d:
            return {"error": f"Drug '{drug}' not found"}
        dose_info = d.get("dosage", {}).get("adult", "Consult pharmacist")
        adjustments = []
        if d.get("kidney_adjust") and kidney_function in ["Mild_CKD", "Moderate_CKD"]:
            adjustments.append(f"Dose adjustment needed for {kidney_function}")
        if age >= 65:
            adjustments.append("Elderly: start with lower dose, monitor closely")
        return {"drug": drug, "dose": dose_info, "adjustments": adjustments,
                "max_dose_mg": d.get("max_dose_mg"), "schedule": d.get("schedule")}


class GenericFinder:
    def find_generic(self, brand_name: str) -> Dict:
        for drug_name, drug in DRUG_DATABASE.items():
            if any(brand_name.lower() in b.lower() for b in drug.get("brands", [])):
                brand_p   = drug["price_brand_inr"]
                generic_p = drug["price_generic_inr"]
                savings   = round((brand_p - generic_p) / brand_p * 100, 0)
                return {"brand": brand_name, "generic": drug["generic"],
                        "brand_price_inr": brand_p, "generic_price_inr": generic_p,
                        "savings_pct": savings, "savings_inr": brand_p - generic_p,
                        "available_at": "Jan Aushadhi Kendra — call 1800-180-8080"}
        return {"error": f"Brand '{brand_name}' not found in database"}


class PregnancyChecker:
    def check(self, drug: str, trimester: int = 1) -> Dict:
        d = DrugSearcher().get_drug(drug)
        if not d:
            return {"error": f"Drug '{drug}' not found"}
        cat  = d.get("pregnancy_category", "Unknown")
        safe = cat in ["A", "B"]
        risk_map = {"A": "Safe", "B": "Probably safe", "C": "Use with caution", "D": "Avoid if possible", "X": "ABSOLUTELY CONTRAINDICATED"}
        return {"drug": drug, "safe": safe, "category": cat,
                "risk": risk_map.get(cat, "Unknown"),
                "category_meaning": PREGNANCY_CATEGORY_INFO.get(cat, "Unknown"),
                "recommendation": "Consult your OB/GYN before taking any medicine during pregnancy."}


class ExpiryAnalyzer:
    def analyze(self, manufacture_date: str, expiry_date: str) -> Dict:
        try:
            exp = datetime.strptime(expiry_date, "%m/%Y")
            exp = exp.replace(day=28)
            now = datetime.now()
            remaining = (exp - now).days
            if remaining < 0:
                return {"days_remaining": remaining, "status": "EXPIRED", "safe_to_use": False, "risk_level": "High"}
            elif remaining <= 30:
                return {"days_remaining": remaining, "status": "Expiring Soon", "safe_to_use": False, "risk_level": "Medium"}
            return {"days_remaining": remaining, "status": "Valid", "safe_to_use": True, "risk_level": "None"}
        except Exception:
            return {"error": "Invalid date format. Use MM/YYYY"}


def get_drug_profile(drug_name: str) -> Dict:
    return DrugSearcher().get_drug(drug_name) or {"error": f"'{drug_name}' not found. Check spelling or use generic name."}
