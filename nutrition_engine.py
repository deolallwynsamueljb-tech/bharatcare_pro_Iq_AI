"""
BharatCare AI Pro · Nutrition Engine v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Indian food database, nutrition calculator, diet planner.
Author: Deol Allwyn Samuel J B · VLSI · CIT · Afynix Digital
"""

import math
from typing import Dict, List, Optional, Tuple
import difflib

# ── Food Database ─────────────────────────────────────────────────────────────
# Fields: name, cat, serving_g, kcal, prot, carb, fat, fiber, fe(iron), ca(calcium),
#         vitC, vitA, b12, folate, na(sodium), k(potassium), gi, price, region
INDIAN_FOOD_DB: Dict[str, Dict] = {
    # South Indian
    "Idli":              {"cat":"South Indian","g":80, "kcal":78,"prot":2.5,"carb":15.5,"fat":0.5,"fiber":0.5,"fe":0.5,"ca":10,"vitC":0,"vitA":0,"b12":0,"folate":12,"na":180,"k":50,"gi":70,"price":5,"region":"Tamil Nadu"},
    "Dosa (Plain)":      {"cat":"South Indian","g":100,"kcal":165,"prot":3.6,"carb":27.0,"fat":5.5,"fiber":1.0,"fe":0.8,"ca":14,"vitC":0,"vitA":0,"b12":0,"folate":18,"na":250,"k":80,"gi":67,"price":8,"region":"Tamil Nadu"},
    "Sambar":            {"cat":"South Indian","g":150,"kcal":65,"prot":3.5,"carb":9.0,"fat":1.8,"fiber":2.5,"fe":1.5,"ca":35,"vitC":5,"vitA":120,"b12":0,"folate":25,"na":300,"k":220,"gi":30,"price":6,"region":"Tamil Nadu"},
    "Rasam":             {"cat":"South Indian","g":150,"kcal":35,"prot":1.5,"carb":5.5,"fat":1.0,"fiber":0.8,"fe":0.8,"ca":20,"vitC":8,"vitA":50,"b12":0,"folate":10,"na":280,"k":180,"gi":25,"price":4,"region":"Tamil Nadu"},
    "Pongal":            {"cat":"South Indian","g":150,"kcal":200,"prot":5.5,"carb":34.0,"fat":7.0,"fiber":1.5,"fe":1.2,"ca":30,"vitC":0,"vitA":0,"b12":0,"folate":15,"na":200,"k":90,"gi":65,"price":10,"region":"Tamil Nadu"},
    "Avial":             {"cat":"South Indian","g":120,"kcal":150,"prot":2.8,"carb":12.0,"fat":9.5,"fiber":3.0,"fe":1.0,"ca":50,"vitC":15,"vitA":200,"b12":0,"folate":30,"na":150,"k":300,"gi":35,"price":12,"region":"Kerala"},
    "Upma":              {"cat":"Breakfast","g":150,"kcal":175,"prot":4.5,"carb":30.0,"fat":5.0,"fiber":2.0,"fe":1.0,"ca":25,"vitC":2,"vitA":30,"b12":0,"folate":15,"na":220,"k":100,"gi":55,"price":8,"region":"South India"},
    "Poha":              {"cat":"Breakfast","g":100,"kcal":130,"prot":2.5,"carb":26.0,"fat":1.5,"fiber":1.2,"fe":0.9,"ca":12,"vitC":3,"vitA":15,"b12":0,"folate":10,"na":180,"k":75,"gi":60,"price":7,"region":"Central India"},
    # Rice and Grains
    "White Rice (cooked)":{"cat":"Grains","g":150,"kcal":195,"prot":3.8,"carb":43.0,"fat":0.3,"fiber":0.5,"fe":0.6,"ca":10,"vitC":0,"vitA":0,"b12":0,"folate":8,"na":5,"k":55,"gi":72,"price":4,"region":"All India"},
    "Brown Rice (cooked)":{"cat":"Grains","g":150,"kcal":185,"prot":4.2,"carb":38.5,"fat":1.5,"fiber":2.5,"fe":1.0,"ca":15,"vitC":0,"vitA":0,"b12":0,"folate":15,"na":5,"k":80,"gi":55,"price":8,"region":"All India"},
    "Chapati/Roti":       {"cat":"Grains","g":35,"kcal":95,"prot":3.0,"carb":18.5,"fat":1.5,"fiber":1.8,"fe":1.2,"ca":20,"vitC":0,"vitA":0,"b12":0,"folate":12,"na":90,"k":65,"gi":62,"price":2,"region":"North India"},
    "Paratha (plain)":    {"cat":"Grains","g":70,"kcal":200,"prot":4.5,"carb":28.0,"fat":8.0,"fiber":2.0,"fe":1.5,"ca":25,"vitC":0,"vitA":0,"b12":0,"folate":18,"na":200,"k":80,"gi":65,"price":8,"region":"North India"},
    "Khichdi":            {"cat":"Grains","g":200,"kcal":220,"prot":8.5,"carb":40.0,"fat":3.5,"fiber":3.0,"fe":2.0,"ca":45,"vitC":2,"vitA":20,"b12":0,"folate":35,"na":280,"k":200,"gi":50,"price":8,"region":"All India"},
    "Bajra Roti":         {"cat":"Grains","g":40,"kcal":110,"prot":3.5,"carb":20.5,"fat":2.0,"fiber":3.5,"fe":3.0,"ca":35,"vitC":0,"vitA":0,"b12":0,"folate":20,"na":10,"k":85,"gi":55,"price":3,"region":"Rajasthan"},
    # Lentils / Dal
    "Dal Toor":           {"cat":"Lentils","g":150,"kcal":120,"prot":8.5,"carb":18.0,"fat":1.5,"fiber":4.5,"fe":2.8,"ca":55,"vitC":1,"vitA":5,"b12":0,"folate":90,"na":250,"k":320,"gi":25,"price":10,"region":"All India"},
    "Dal Moong":          {"cat":"Lentils","g":150,"kcal":105,"prot":7.5,"carb":17.0,"fat":0.5,"fiber":4.0,"fe":2.5,"ca":45,"vitC":2,"vitA":5,"b12":0,"folate":80,"na":200,"k":290,"gi":25,"price":10,"region":"All India"},
    "Dal Makhani":        {"cat":"Lentils","g":200,"kcal":280,"prot":12.0,"carb":30.0,"fat":12.0,"fiber":5.5,"fe":4.0,"ca":85,"vitC":2,"vitA":30,"b12":0.2,"folate":95,"na":450,"k":420,"gi":28,"price":18,"region":"North India"},
    "Rajma":              {"cat":"Lentils","g":200,"kcal":240,"prot":13.0,"carb":38.0,"fat":2.0,"fiber":7.5,"fe":4.5,"ca":70,"vitC":3,"vitA":5,"b12":0,"folate":115,"na":350,"k":480,"gi":28,"price":15,"region":"North India"},
    "Chole":              {"cat":"Lentils","g":200,"kcal":250,"prot":11.5,"carb":40.0,"fat":5.0,"fiber":8.0,"fe":3.5,"ca":60,"vitC":5,"vitA":10,"b12":0,"folate":105,"na":350,"k":450,"gi":30,"price":15,"region":"North India"},
    "Sprouted Moong":     {"cat":"Lentils","g":50,"kcal":30,"prot":3.2,"carb":3.8,"fat":0.2,"fiber":1.5,"fe":1.0,"ca":15,"vitC":8,"vitA":5,"b12":0,"folate":60,"na":5,"k":120,"gi":25,"price":5,"region":"All India"},
    # Vegetables
    "Spinach (Palak)":    {"cat":"Vegetables","g":100,"kcal":23,"prot":2.9,"carb":3.6,"fat":0.4,"fiber":2.2,"fe":2.7,"ca":99,"vitC":28,"vitA":469,"b12":0,"folate":194,"na":79,"k":558,"gi":15,"price":8,"region":"All India"},
    "Drumstick (Moringa)":{"cat":"Vegetables","g":100,"kcal":37,"prot":2.1,"carb":8.5,"fat":0.2,"fiber":3.2,"fe":0.4,"ca":30,"vitC":141,"vitA":74,"b12":0,"folate":44,"na":42,"k":461,"gi":20,"price":10,"region":"South India"},
    "Tomato":             {"cat":"Vegetables","g":100,"kcal":18,"prot":0.9,"carb":3.9,"fat":0.2,"fiber":1.2,"fe":0.3,"ca":10,"vitC":14,"vitA":42,"b12":0,"folate":15,"na":5,"k":237,"gi":15,"price":5,"region":"All India"},
    "Onion":              {"cat":"Vegetables","g":100,"kcal":40,"prot":1.1,"carb":9.3,"fat":0.1,"fiber":1.7,"fe":0.2,"ca":23,"vitC":7,"vitA":1,"b12":0,"folate":19,"na":4,"k":146,"gi":10,"price":4,"region":"All India"},
    "Potato (boiled)":    {"cat":"Vegetables","g":150,"kcal":117,"prot":2.7,"carb":26.5,"fat":0.1,"fiber":2.0,"fe":0.4,"ca":9,"vitC":13,"vitA":0,"b12":0,"folate":18,"na":6,"k":379,"gi":65,"price":5,"region":"All India"},
    "Carrot":             {"cat":"Vegetables","g":100,"kcal":41,"prot":0.9,"carb":9.6,"fat":0.2,"fiber":2.8,"fe":0.3,"ca":33,"vitC":6,"vitA":835,"b12":0,"folate":19,"na":69,"k":320,"gi":16,"price":6,"region":"All India"},
    "Brinjal/Eggplant":   {"cat":"Vegetables","g":100,"kcal":25,"prot":1.0,"carb":5.9,"fat":0.2,"fiber":3.0,"fe":0.2,"ca":9,"vitC":2,"vitA":1,"b12":0,"folate":22,"na":2,"k":229,"gi":15,"price":6,"region":"All India"},
    "Bitter Gourd (Karela)":{"cat":"Vegetables","g":100,"kcal":17,"prot":1.0,"carb":3.7,"fat":0.2,"fiber":2.6,"fe":0.4,"ca":19,"vitC":84,"vitA":6,"b12":0,"folate":72,"na":5,"k":296,"gi":20,"price":8,"region":"All India"},
    "Okra (Bhindi)":      {"cat":"Vegetables","g":100,"kcal":31,"prot":2.0,"carb":7.0,"fat":0.2,"fiber":3.2,"fe":0.6,"ca":77,"vitC":21,"vitA":14,"b12":0,"folate":60,"na":7,"k":303,"gi":20,"price":8,"region":"All India"},
    "Cabbage":            {"cat":"Vegetables","g":100,"kcal":25,"prot":1.3,"carb":5.8,"fat":0.1,"fiber":2.5,"fe":0.5,"ca":40,"vitC":37,"vitA":5,"b12":0,"folate":43,"na":18,"k":170,"gi":10,"price":5,"region":"All India"},
    # Fruits
    "Banana":             {"cat":"Fruits","g":120,"kcal":107,"prot":1.3,"carb":27.0,"fat":0.4,"fiber":3.1,"fe":0.3,"ca":6,"vitC":10,"vitA":4,"b12":0,"folate":24,"na":1,"k":422,"gi":51,"price":5,"region":"All India"},
    "Mango":              {"cat":"Fruits","g":150,"kcal":100,"prot":1.4,"carb":25.0,"fat":0.4,"fiber":2.6,"fe":0.3,"ca":17,"vitC":46,"vitA":54,"b12":0,"folate":43,"na":2,"k":277,"gi":51,"price":10,"region":"All India"},
    "Guava":              {"cat":"Fruits","g":100,"kcal":68,"prot":2.6,"carb":14.3,"fat":0.9,"fiber":5.4,"fe":0.3,"ca":18,"vitC":228,"vitA":31,"b12":0,"folate":49,"na":2,"k":417,"gi":12,"price":5,"region":"All India"},
    "Amla (Indian Gooseberry)":{"cat":"Fruits","g":50,"kcal":28,"prot":0.5,"carb":6.8,"fat":0.1,"fiber":3.4,"fe":0.7,"ca":25,"vitC":330,"vitA":9,"b12":0,"folate":5,"na":1,"k":154,"gi":15,"price":3,"region":"All India"},
    "Orange":             {"cat":"Fruits","g":150,"kcal":71,"prot":1.3,"carb":17.8,"fat":0.2,"fiber":3.6,"fe":0.2,"ca":60,"vitC":82,"vitA":14,"b12":0,"folate":30,"na":0,"k":237,"gi":40,"price":8,"region":"All India"},
    "Papaya":             {"cat":"Fruits","g":150,"kcal":65,"prot":0.7,"carb":15.7,"fat":0.3,"fiber":2.5,"fe":0.3,"ca":31,"vitC":89,"vitA":47,"b12":0,"folate":53,"na":11,"k":264,"gi":38,"price":8,"region":"All India"},
    "Pomegranate":        {"cat":"Fruits","g":100,"kcal":83,"prot":1.7,"carb":18.7,"fat":1.2,"fiber":4.0,"fe":0.3,"ca":10,"vitC":10,"vitA":0,"b12":0,"folate":38,"na":3,"k":236,"gi":53,"price":15,"region":"All India"},
    "Jackfruit":          {"cat":"Fruits","g":100,"kcal":95,"prot":1.7,"carb":23.2,"fat":0.6,"fiber":1.5,"fe":0.2,"ca":24,"vitC":14,"vitA":5,"b12":0,"folate":24,"na":2,"k":303,"gi":50,"price":5,"region":"South India"},
    # Proteins
    "Egg (boiled)":       {"cat":"Protein","g":50,"kcal":78,"prot":6.3,"carb":0.6,"fat":5.3,"fiber":0,"fe":0.9,"ca":25,"vitC":0,"vitA":75,"b12":0.6,"folate":22,"na":62,"k":63,"gi":0,"price":7,"region":"All India"},
    "Chicken (boiled)":   {"cat":"Protein","g":100,"kcal":165,"prot":31.0,"carb":0,"fat":3.6,"fiber":0,"fe":1.0,"ca":14,"vitC":0,"vitA":0,"b12":0.3,"folate":7,"na":74,"k":256,"gi":0,"price":30,"region":"All India"},
    "Fish (Rohu, cooked)":{"cat":"Protein","g":100,"kcal":120,"prot":20.0,"carb":0,"fat":3.8,"fiber":0,"fe":1.0,"ca":50,"vitC":0,"vitA":10,"b12":1.5,"folate":8,"na":50,"k":320,"gi":0,"price":35,"region":"East India"},
    "Sardines (canned)":  {"cat":"Protein","g":60,"kcal":130,"prot":17.0,"carb":0,"fat":7.0,"fiber":0,"fe":1.4,"ca":250,"vitC":0,"vitA":25,"b12":3.5,"folate":10,"na":200,"k":230,"gi":0,"price":20,"region":"Coastal India"},
    "Paneer (100g)":      {"cat":"Dairy","g":100,"kcal":265,"prot":18.3,"carb":3.4,"fat":20.8,"fiber":0,"fe":0.2,"ca":208,"vitC":0,"vitA":30,"b12":0.5,"folate":7,"na":30,"k":77,"gi":0,"price":40,"region":"North India"},
    "Curd/Yogurt":        {"cat":"Dairy","g":150,"kcal":90,"prot":5.0,"carb":9.0,"fat":3.5,"fiber":0,"fe":0.1,"ca":145,"vitC":0,"vitA":25,"b12":0.4,"folate":10,"na":80,"k":200,"gi":36,"price":10,"region":"All India"},
    "Milk (full fat)":    {"cat":"Dairy","g":250,"kcal":150,"prot":8.0,"carb":12.0,"fat":8.0,"fiber":0,"fe":0.1,"ca":280,"vitC":0,"vitA":68,"b12":1.0,"folate":12,"na":105,"k":330,"gi":27,"price":15,"region":"All India"},
    # Nuts and Seeds
    "Groundnuts (roasted)":{"cat":"Nuts","g":30,"kcal":175,"prot":7.0,"carb":5.5,"fat":14.5,"fiber":2.5,"fe":0.7,"ca":20,"vitC":0,"vitA":0,"b12":0,"folate":27,"na":2,"k":187,"gi":14,"price":5,"region":"All India"},
    "Almonds":            {"cat":"Nuts","g":30,"kcal":173,"prot":6.3,"carb":6.1,"fat":14.9,"fiber":3.5,"fe":1.0,"ca":76,"vitC":0,"vitA":0,"b12":0,"folate":15,"na":0,"k":208,"gi":0,"price":25,"region":"All India"},
    "Sesame Seeds (til)": {"cat":"Nuts","g":15,"kcal":89,"prot":2.7,"carb":3.5,"fat":7.7,"fiber":1.6,"fe":2.1,"ca":135,"vitC":0,"vitA":0,"b12":0,"folate":14,"na":3,"k":65,"gi":35,"price":5,"region":"All India"},
    "Flaxseeds":          {"cat":"Nuts","g":15,"kcal":82,"prot":2.8,"carb":4.4,"fat":6.5,"fiber":4.0,"fe":0.9,"ca":36,"vitC":0,"vitA":0,"b12":0,"folate":18,"na":4,"k":115,"gi":35,"price":5,"region":"All India"},
    "Cashews":            {"cat":"Nuts","g":30,"kcal":163,"prot":4.4,"carb":9.5,"fat":13.0,"fiber":0.9,"fe":1.7,"ca":10,"vitC":0,"vitA":0,"b12":0,"folate":7,"na":3,"k":160,"gi":25,"price":20,"region":"South India"},
    "Dates":              {"cat":"Fruits","g":40,"kcal":112,"prot":0.8,"carb":30.0,"fat":0.1,"fiber":2.9,"fe":0.8,"ca":16,"vitC":0,"vitA":3,"b12":0,"folate":7,"na":1,"k":234,"gi":42,"price":10,"region":"All India"},
    # Beverages
    "Tender Coconut Water":{"cat":"Beverage","g":250,"kcal":46,"prot":1.8,"carb":9.0,"fat":0.5,"fiber":1.1,"fe":0.3,"ca":58,"vitC":6,"vitA":0,"b12":0,"folate":16,"na":252,"k":600,"gi":54,"price":25,"region":"South India"},
    "Buttermilk (Chaas)": {"cat":"Beverage","g":200,"kcal":40,"prot":3.2,"carb":4.8,"fat":1.0,"fiber":0,"fe":0.1,"ca":120,"vitC":0,"vitA":10,"b12":0.3,"folate":6,"na":55,"k":160,"gi":32,"price":5,"region":"All India"},
    "Sugarcane Juice":    {"cat":"Beverage","g":250,"kcal":180,"prot":0,"carb":45.0,"fat":0,"fiber":0,"fe":0.4,"ca":40,"vitC":5,"vitA":0,"b12":0,"folate":5,"na":18,"k":270,"gi":43,"price":10,"region":"All India"},
    # Street Food
    "Pav Bhaji":          {"cat":"Street Food","g":250,"kcal":380,"prot":9.0,"carb":55.0,"fat":14.0,"fiber":5.5,"fe":2.5,"ca":80,"vitC":25,"vitA":150,"b12":0.1,"folate":45,"na":700,"k":450,"gi":55,"price":60,"region":"Mumbai"},
    "Masala Dosa":        {"cat":"Street Food","g":200,"kcal":350,"prot":7.5,"carb":52.0,"fat":12.5,"fiber":3.5,"fe":2.0,"ca":55,"vitC":10,"vitA":20,"b12":0,"folate":40,"na":450,"k":320,"gi":60,"price":50,"region":"South India"},
    "Bhel Puri":          {"cat":"Street Food","g":150,"kcal":180,"prot":4.5,"carb":32.0,"fat":4.5,"fiber":3.0,"fe":2.0,"ca":40,"vitC":12,"vitA":15,"b12":0,"folate":25,"na":380,"k":200,"gi":55,"price":30,"region":"Mumbai"},
    "Vada":               {"cat":"Street Food","g":60,"kcal":160,"prot":4.0,"carb":18.5,"fat":8.5,"fiber":2.5,"fe":1.5,"ca":25,"vitC":0,"vitA":0,"b12":0,"folate":20,"na":220,"k":150,"gi":50,"price":15,"region":"South India"},
    "Pakora":             {"cat":"Street Food","g":60,"kcal":180,"prot":3.5,"carb":18.0,"fat":10.5,"fiber":2.0,"fe":1.0,"ca":20,"vitC":2,"vitA":10,"b12":0,"folate":15,"na":200,"k":120,"gi":55,"price":20,"region":"North India"},
    # Breakfast
    "Oats (cooked)":      {"cat":"Breakfast","g":150,"kcal":147,"prot":5.4,"carb":25.0,"fat":2.5,"fiber":4.2,"fe":2.1,"ca":85,"vitC":0,"vitA":0,"b12":0,"folate":11,"na":8,"k":164,"gi":55,"price":15,"region":"All India"},
    "Bread (whole wheat)":{"cat":"Breakfast","g":60,"kcal":140,"prot":5.6,"carb":28.0,"fat":1.5,"fiber":3.8,"fe":2.0,"ca":50,"vitC":0,"vitA":0,"b12":0,"folate":20,"na":200,"k":100,"gi":55,"price":8,"region":"All India"},
    "Biryani (veg)":      {"cat":"Rice","g":250,"kcal":380,"prot":8.0,"carb":62.0,"fat":10.0,"fiber":4.0,"fe":2.0,"ca":60,"vitC":8,"vitA":30,"b12":0,"folate":35,"na":550,"k":280,"gi":65,"price":80,"region":"South India"},
}

DISEASE_DIET_PLANS: Dict[str, Dict] = {
    "diabetes": {
        "allowed":    ["Brown rice", "Oats", "Bajra roti", "Dal moong", "Bitter gourd", "Spinach", "Drumstick", "Guava", "Amla", "Fenugreek (methi)", "Fish", "Eggs"],
        "avoid":      ["White rice", "White bread", "Sugary drinks", "Sweets", "Potato chips", "Maida products", "Fruit juices"],
        "key_nutrients": ["Low GI carbohydrates", "High fibre", "Chromium", "Magnesium", "Omega-3"],
        "meal_plan":  {
            "breakfast": "Oats porridge + 1 egg + Amla juice",
            "mid_morning": "Sprouted moong salad or 1 small guava",
            "lunch": "2 bajra rotis + palak dal + bitter gourd sabzi + curd",
            "evening_snack": "Roasted groundnuts (30g) + green tea",
            "dinner": "Khichdi (brown rice + moong) + sambar + raw salad",
        },
        "notes": "Target HbA1c <7. Eat every 3-4 hours. Avoid skipping meals.",
    },
    "hypertension": {
        "allowed":    ["Banana", "Spinach", "Oats", "Garlic", "Flaxseeds", "Beetroot", "Dal", "Fish", "Curd", "Amla", "Hibiscus tea"],
        "avoid":      ["Table salt", "Pickles", "Papad", "Processed meats", "Canned food", "Alcohol", "Excess caffeine"],
        "key_nutrients": ["Potassium", "Magnesium", "Calcium", "Omega-3", "Low sodium (<2g/day)"],
        "meal_plan":  {
            "breakfast": "Oats with banana + low-fat milk + garlic chutney",
            "lunch": "Brown rice + dal + spinach curry + curd (no added salt in curd)",
            "evening_snack": "Roasted flaxseeds + hibiscus tea",
            "dinner": "2 rotis + fish curry (low salt) + salad",
        },
        "notes": "DASH diet. Target Na <2000mg/day. Increase K, Mg, Ca.",
    },
    "anaemia": {
        "allowed":    ["Spinach", "Drumstick leaves", "Dates", "Pomegranate", "Jaggery", "Lentils", "Sesame seeds", "Eggs", "Chicken liver", "Fish", "Amla", "Guava"],
        "avoid":      ["Tea with meals", "Coffee with meals", "High calcium with iron (separate by 2h)", "Whole wheat with iron-rich meal (phytates)"],
        "key_nutrients": ["Iron", "Vitamin C (enhances iron absorption)", "Folate", "Vitamin B12", "Protein"],
        "meal_plan":  {
            "breakfast": "Poha + sprouted moong + amla juice (vitamin C boosts iron absorption)",
            "lunch": "Rice + drumstick sambar + palak curry + lemon squeeze",
            "evening_snack": "Dates (3) + sesame balls (til ladoo)",
            "dinner": "Roti + rajma curry + salad with tomato and lemon",
        },
        "notes": "Always eat Vitamin C with iron-rich foods. Avoid tea 1 hour before and after meals.",
    },
    "heart_disease": {
        "allowed":    ["Fish (sardines, mackerel)", "Walnuts", "Flaxseeds", "Oats", "Garlic", "Amla", "Spinach", "Tomato", "Brinjal", "Rajma", "Curd (low fat)"],
        "avoid":      ["Vanaspati/trans fats", "Full fat dairy (excess)", "Red meat (excess)", "Processed foods", "Alcohol", "Excess salt", "Coconut oil (excess)"],
        "key_nutrients": ["Omega-3", "Soluble fibre", "Potassium", "Antioxidants", "Coenzyme Q10"],
        "meal_plan":  {
            "breakfast": "Oats with flaxseeds + amla juice + walnuts (4-5)",
            "lunch": "Brown rice + rajma + salad + low fat curd",
            "evening_snack": "Roasted groundnuts + green tea",
            "dinner": "2 rotis + fish curry (grilled, not fried) + steamed vegetables",
        },
        "notes": "Mediterranean-style diet. Limit saturated fats. Target LDL <100 mg/dL.",
    },
    "kidney_disease": {
        "allowed":    ["White rice", "Cabbage", "Cauliflower", "Apple", "Egg white", "Low-potassium fruits"],
        "avoid":      ["High potassium: banana, orange, coconut water", "High phosphorus: dal, nuts, dairy excess", "High protein: excess meat, eggs", "Salt (sodium)", "Tomato (excess)", "Dark leafy greens"],
        "key_nutrients": ["Controlled protein", "Low potassium", "Low phosphorus", "Low sodium"],
        "meal_plan":  {
            "breakfast": "Bread + egg white omelette (1-2 whites only) + apple",
            "lunch": "White rice + cauliflower sabzi + small portion curd",
            "dinner": "2 rotis + cabbage curry + very small dal serving",
        },
        "notes": "Kidney diet MUST be personalised by nephrologist. eGFR determines restrictions.",
    },
    "cancer_supportive": {
        "allowed":    ["Turmeric", "Garlic", "Green tea", "Cruciferous vegetables", "Berries", "Tomato (lycopene)", "Flaxseeds", "Whole grains", "Fish"],
        "avoid":      ["Processed meats", "Alcohol", "Sugary foods", "Aflatoxin foods (old peanuts)", "Smoked/charred foods"],
        "key_nutrients": ["Antioxidants", "Anti-inflammatory compounds", "Protein (for muscle)", "Fibre"],
        "meal_plan":  {
            "breakfast": "Turmeric milk + oats + fruit salad",
            "lunch": "Brown rice + dal + mixed vegetables + salad",
            "dinner": "Khichdi + steamed fish + tomato rasam",
        },
        "notes": "Focus on calorie-dense nutritious food. Address chemo-related nausea with ginger tea.",
    },
    "thyroid": {
        "allowed":    ["Selenium-rich: Brazil nuts (2/day), eggs, tuna", "Zinc: pumpkin seeds, chickpeas", "Iodine: iodised salt, seaweed", "Iron: spinach, dal"],
        "avoid":      ["Raw goitrogens in excess: cabbage, broccoli, soy (cooking reduces risk)", "Processed soy", "Fluoride excess"],
        "key_nutrients": ["Iodine", "Selenium", "Zinc", "Iron", "Vitamin D"],
        "meal_plan":  {
            "breakfast": "Eggs (2) + whole wheat toast + Brazil nut (1-2)",
            "lunch": "Rice + palak dal + fish curry",
            "dinner": "Roti + chicken + steamed pumpkin",
        },
        "notes": "Take levothyroxine 30-60 min before breakfast. Avoid high-fibre or dairy too close to medication.",
    },
    "liver_disease": {
        "allowed":    ["Papaya", "Turmeric", "Garlic", "Amla", "Coffee (moderate)", "Oats", "Leafy greens", "Berries"],
        "avoid":      ["Alcohol (completely)", "Fatty/oily foods", "Raw shellfish", "High iron foods (haemochromatosis)", "Salt (if oedema)"],
        "key_nutrients": ["Antioxidants", "B vitamins", "Adequate protein", "Low fat", "No alcohol"],
        "meal_plan":  {
            "breakfast": "Papaya + oats + amla juice",
            "lunch": "Steamed rice + moong dal + bottle gourd curry",
            "dinner": "2 rotis + steamed fish + light vegetable soup",
        },
        "notes": "Avoid alcohol completely. Cirrhosis patients need specialised nutritionist guidance.",
    },
}

VITAMIN_DEFICIENCY_SYMPTOMS: Dict[str, Dict] = {
    "Vitamin D":     {"symptoms": ["Bone pain", "Muscle weakness", "Fatigue", "Depression", "Frequent infections", "Hair loss"], "food_sources": ["Sunlight (15-20 min/day)", "Egg yolk", "Fish (sardines)", "Fortified milk"], "daily_requirement": "600-800 IU (adults)", "deficiency_risk": "Very high in India — 70-80% deficient"},
    "Vitamin B12":   {"symptoms": ["Fatigue", "Tingling hands/feet", "Memory problems", "Pale skin", "Sore tongue", "Anaemia"], "food_sources": ["Meat", "Fish", "Eggs", "Dairy", "Fortified foods"], "daily_requirement": "2.4 mcg/day", "deficiency_risk": "Very high in vegetarians and elderly"},
    "Iron":          {"symptoms": ["Fatigue", "Pale skin", "Shortness of breath", "Cold hands", "Brittle nails", "Pica"], "food_sources": ["Spinach", "Drumstick leaves", "Jaggery", "Dates", "Lentils", "Meat"], "daily_requirement": "8-18 mg/day (women need more)", "deficiency_risk": "53% of Indian women deficient"},
    "Vitamin C":     {"symptoms": ["Bleeding gums", "Slow wound healing", "Fatigue", "Scurvy (severe)", "Easy bruising"], "food_sources": ["Amla (highest)", "Guava", "Citrus fruits", "Tomato", "Capsicum"], "daily_requirement": "65-90 mg/day", "deficiency_risk": "Moderate — poor diet variety"},
    "Calcium":       {"symptoms": ["Muscle cramps", "Brittle nails", "Dental problems", "Osteoporosis", "Numbness"], "food_sources": ["Milk", "Curd", "Paneer", "Sesame seeds", "Ragi", "Drumstick"], "daily_requirement": "1000-1200 mg/day", "deficiency_risk": "High — insufficient dairy in many Indians"},
    "Vitamin A":     {"symptoms": ["Night blindness", "Dry eyes", "Dry skin", "Frequent infections", "Poor growth in children"], "food_sources": ["Carrot", "Mango", "Papaya", "Egg yolk", "Liver", "Spinach"], "daily_requirement": "700-900 mcg RAE/day", "deficiency_risk": "High in children — major cause of blindness in India"},
    "Folate (B9)":   {"symptoms": ["Megaloblastic anaemia", "Fatigue", "Mouth sores", "Neural tube defects (pregnancy)"], "food_sources": ["Spinach", "Lentils", "Chickpeas", "Asparagus", "Folic acid supplement"], "daily_requirement": "400-600 mcg/day (800 in pregnancy)", "deficiency_risk": "High in women of reproductive age"},
    "Zinc":          {"symptoms": ["Poor wound healing", "Hair loss", "Loss of taste/smell", "Frequent infections", "Growth retardation"], "food_sources": ["Pumpkin seeds", "Chickpeas", "Cashews", "Meat", "Eggs"], "daily_requirement": "8-11 mg/day", "deficiency_risk": "Moderate — low in vegetarian diets"},
    "Iodine":        {"symptoms": ["Goitre", "Hypothyroidism", "Fatigue", "Weight gain", "Mental sluggishness"], "food_sources": ["Iodised salt", "Seaweed", "Fish", "Dairy"], "daily_requirement": "150 mcg/day", "deficiency_risk": "Reduced with iodised salt — but still present in hilly areas"},
    "Omega-3":       {"symptoms": ["Dry skin", "Depression", "Poor concentration", "Dry eyes", "Joint pain"], "food_sources": ["Fatty fish (mackerel, sardines)", "Flaxseeds", "Walnuts", "Chia seeds"], "daily_requirement": "1.1-1.6 g ALA/day; 250-500 mg EPA+DHA/day", "deficiency_risk": "High in vegetarians"},
}

RDA_VALUES: Dict[str, Dict] = {
    "adult_male":      {"calories": 2320, "protein_g": 60, "calcium_mg": 1000, "iron_mg": 17, "vitA_mcg": 900, "vitC_mg": 65, "vitD_iu": 600, "folate_mcg": 400},
    "adult_female":    {"calories": 1900, "protein_g": 55, "calcium_mg": 1000, "iron_mg": 21, "vitA_mcg": 700, "vitC_mg": 65, "vitD_iu": 600, "folate_mcg": 400},
    "pregnant":        {"calories": 2200, "protein_g": 78, "calcium_mg": 1200, "iron_mg": 35, "vitA_mcg": 900, "vitC_mg": 85, "vitD_iu": 600, "folate_mcg": 600},
    "lactating":       {"calories": 2480, "protein_g": 74, "calcium_mg": 1200, "iron_mg": 21, "vitA_mcg": 950, "vitC_mg": 120, "vitD_iu": 600, "folate_mcg": 500},
    "child_1_3":       {"calories": 1000, "protein_g": 16, "calcium_mg": 700, "iron_mg": 9, "vitA_mcg": 300, "vitC_mg": 40, "vitD_iu": 600, "folate_mcg": 150},
    "child_4_6":       {"calories": 1350, "protein_g": 20, "calcium_mg": 1000, "iron_mg": 13, "vitA_mcg": 400, "vitC_mg": 25, "vitD_iu": 600, "folate_mcg": 200},
    "teen_13_15":      {"calories": 2200, "protein_g": 54, "calcium_mg": 1300, "iron_mg": 21, "vitA_mcg": 600, "vitC_mg": 65, "vitD_iu": 600, "folate_mcg": 400},
    "elderly":         {"calories": 1800, "protein_g": 60, "calcium_mg": 1200, "iron_mg": 10, "vitA_mcg": 700, "vitC_mg": 65, "vitD_iu": 800, "folate_mcg": 400},
}


class NutritionCalculator:
    def calculate_meal(self, foods: List[Tuple[str, float]]) -> Dict:
        totals = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0,
                  "fiber_g": 0.0, "iron_mg": 0.0, "calcium_mg": 0.0,
                  "vitC_mg": 0.0, "vitA_mcg": 0.0, "folate_mcg": 0.0, "cost_inr": 0.0}
        breakdown = []
        for name, grams in foods:
            food = self._find_food(name)
            if not food:
                continue
            ratio = grams / food["g"]
            row = {"food": name, "grams": grams,
                   "kcal": round(food["kcal"] * ratio, 1),
                   "protein": round(food["prot"] * ratio, 1),
                   "carbs": round(food["carb"] * ratio, 1),
                   "fat": round(food["fat"] * ratio, 1)}
            breakdown.append(row)
            totals["calories"]   += food["kcal"] * ratio
            totals["protein_g"]  += food["prot"] * ratio
            totals["carbs_g"]    += food["carb"] * ratio
            totals["fat_g"]      += food["fat"] * ratio
            totals["fiber_g"]    += food["fiber"] * ratio
            totals["iron_mg"]    += food["fe"] * ratio
            totals["calcium_mg"] += food["ca"] * ratio
            totals["vitC_mg"]    += food["vitC"] * ratio
            totals["vitA_mcg"]   += food["vitA"] * ratio
            totals["folate_mcg"] += food["folate"] * ratio
            totals["cost_inr"]   += food["price"] * (grams / 100)
        return {k: round(v, 1) for k, v in totals.items()} | {"breakdown": breakdown}

    def _find_food(self, name: str) -> Optional[Dict]:
        if name in INDIAN_FOOD_DB:
            return INDIAN_FOOD_DB[name]
        matches = difflib.get_close_matches(name, INDIAN_FOOD_DB.keys(), n=1, cutoff=0.6)
        return INDIAN_FOOD_DB[matches[0]] if matches else None

    def bmi(self, weight_kg: float, height_cm: float) -> Dict:
        h = height_cm / 100
        bmi = round(weight_kg / h ** 2, 1)
        cat = "Underweight" if bmi < 18.5 else "Normal" if bmi < 23 else "Overweight" if bmi < 27.5 else "Obese"
        return {"bmi": bmi, "category": cat}

    def bmr(self, weight: float, height: float, age: int, gender: str) -> float:
        if gender.lower() == "male":
            return round(10 * weight + 6.25 * height - 5 * age + 5, 1)
        return round(10 * weight + 6.25 * height - 5 * age - 161, 1)

    def daily_target(self, age: int, gender: str, activity: str, weight: float, height: float) -> Dict:
        bmr = self.bmr(weight, height, age, gender)
        factors = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725, "very_active": 1.9}
        tdee = round(bmr * factors.get(activity, 1.55))
        return {"calories": tdee, "protein_g": round(weight * 0.8), "carbs_g": round(tdee * 0.5 / 4),
                "fat_g": round(tdee * 0.3 / 9), "fiber_g": 30}


class VitaminDeficiencyDetector:
    def detect(self, symptoms: List[str]) -> List[Dict]:
        sym_lower = [s.lower() for s in symptoms]
        hits = []
        for nutrient, info in VITAMIN_DEFICIENCY_SYMPTOMS.items():
            count = sum(1 for s in info["symptoms"] if any(s.lower() in sym for sym in sym_lower))
            if count > 0:
                hits.append({"nutrient": nutrient, "probability_score": count,
                             "matched_symptoms": [s for s in info["symptoms"] if any(s.lower() in sym for sym in sym_lower)],
                             "food_sources": info["food_sources"],
                             "daily_requirement": info["daily_requirement"]})
        return sorted(hits, key=lambda x: x["probability_score"], reverse=True)

    def analyze_diet(self, foods_eaten: List[str]) -> Dict:
        totals = {"iron_mg": 0, "calcium_mg": 0, "vitC_mg": 0, "vitD": 0, "b12": 0, "folate_mcg": 0}
        for food in foods_eaten:
            f = INDIAN_FOOD_DB.get(food)
            if f:
                totals["iron_mg"]    += f.get("fe", 0)
                totals["calcium_mg"] += f.get("ca", 0)
                totals["vitC_mg"]    += f.get("vitC", 0)
                totals["b12"]        += f.get("b12", 0)
                totals["folate_mcg"] += f.get("folate", 0)
        gaps = {k: "Adequate" if v >= 10 else "May be deficient" for k, v in totals.items()}
        return {"daily_totals": totals, "assessment": gaps}


class DietPlanner:
    def plan_for_condition(self, condition: str, budget_inr: int = 100) -> Dict:
        plan = DISEASE_DIET_PLANS.get(condition, DISEASE_DIET_PLANS["diabetes"])
        return {"condition": condition, "meal_plan": plan["meal_plan"], "allowed": plan["allowed"],
                "avoid": plan["avoid"], "notes": plan["notes"], "budget_inr": budget_inr}

    def budget_meal(self, budget_inr: int = 100, calories_target: int = 600) -> List[Dict]:
        options = []
        for name, food in INDIAN_FOOD_DB.items():
            cost_per_100g = food["price"]
            if cost_per_100g <= budget_inr * 0.4:
                kcal_per_rupee = food["kcal"] / max(cost_per_100g, 1)
                options.append({"food": name, "serving_g": food["g"], "kcal": food["kcal"],
                                 "cost_inr": round(cost_per_100g * food["g"] / 100, 1),
                                 "kcal_per_rupee": round(kcal_per_rupee, 1),
                                 "protein_g": food["prot"]})
        return sorted(options, key=lambda x: x["kcal_per_rupee"], reverse=True)[:10]

    def weekly_plan(self, condition: str, preferences: List[str] = None) -> Dict:
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        plan = DISEASE_DIET_PLANS.get(condition, DISEASE_DIET_PLANS["diabetes"])
        return {day: plan["meal_plan"] for day in days}


class StreetFoodAnalyzer:
    STREET_FOOD_RISKS = {
        "Pav Bhaji":    {"hygiene_risk": "Medium", "kcal": 380, "sodium_risk": "High (700mg per serving)"},
        "Masala Dosa":  {"hygiene_risk": "Low", "kcal": 350, "sodium_risk": "Medium"},
        "Bhel Puri":    {"hygiene_risk": "Medium-High", "kcal": 180, "sodium_risk": "High"},
        "Vada":         {"hygiene_risk": "Low", "kcal": 160, "sodium_risk": "Medium"},
        "Pakora":       {"hygiene_risk": "Medium", "kcal": 180, "sodium_risk": "Medium"},
    }

    def analyze(self, food: str, quantity: int = 1) -> Dict:
        base = INDIAN_FOOD_DB.get(food, {})
        risk = self.STREET_FOOD_RISKS.get(food, {"hygiene_risk": "Unknown", "sodium_risk": "Unknown"})
        return {"food": food, "quantity": quantity,
                "total_kcal": round(base.get("kcal", 0) * quantity, 0),
                "hygiene_risk": risk.get("hygiene_risk", "Unknown"),
                "sodium_risk": risk.get("sodium_risk", "Unknown"),
                "recommendation": "Eat occasionally. Choose freshly prepared food at busy stalls."}


class SupplementRecommender:
    def recommend(self, age: int, gender: str, conditions: List[str],
                  diet_type: str = "vegetarian") -> List[Dict]:
        recs = []
        if diet_type in ["vegetarian", "vegan"] or age >= 50:
            recs.append({"supplement": "Vitamin B12", "dose": "500 mcg/day",
                         "reason": "Not found in plant foods; essential for nerve function", "cost_monthly_inr": 150})
        if age >= 5:
            recs.append({"supplement": "Vitamin D3", "dose": "1000-2000 IU/day",
                         "reason": "70-80% of Indians are deficient", "cost_monthly_inr": 100})
        if gender.lower() == "female" and age < 50:
            recs.append({"supplement": "Iron + Folic Acid", "dose": "100mg Fe + 500mcg FA",
                         "reason": "Iron deficiency anaemia affects 53% of Indian women", "cost_monthly_inr": 50})
        if "diabetes" in conditions:
            recs.append({"supplement": "Chromium Picolinate", "dose": "200 mcg/day",
                         "reason": "Improves insulin sensitivity", "cost_monthly_inr": 200})
        if "arthritis" in conditions or age >= 55:
            recs.append({"supplement": "Calcium + Vitamin D3", "dose": "500mg Ca + 1000 IU D3",
                         "reason": "Bone health — osteoporosis prevention", "cost_monthly_inr": 120})
        if diet_type == "vegan":
            recs.append({"supplement": "Omega-3 (Algal DHA)", "dose": "300mg DHA/day",
                         "reason": "Vegan source of DHA — brain and heart health", "cost_monthly_inr": 400})
        return recs


def search_food(query: str) -> List[Dict]:
    query_low = query.lower()
    results   = []
    for name, food in INDIAN_FOOD_DB.items():
        if query_low in name.lower():
            results.append({"name": name, **food})
    if not results:
        matches = difflib.get_close_matches(query, INDIAN_FOOD_DB.keys(), n=5, cutoff=0.4)
        results = [{"name": m, **INDIAN_FOOD_DB[m]} for m in matches]
    return results[:8]
