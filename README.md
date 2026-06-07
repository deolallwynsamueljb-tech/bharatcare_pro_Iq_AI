# BharatCare Pro IQ — AI Health Intelligence Platform for India

A comprehensive AI-powered healthcare platform built for India, covering disease detection, drug intelligence, mental health, nutrition, emergency response, epidemic monitoring, and women & child health.

## Features

| Module | Description |
|---|---|
| **AI Chatbot** | NLP-powered health chatbot with symptom understanding |
| **Disease Database** | Searchable database of diseases with symptoms and treatments |
| **DrugIQ** | Drug information, interactions, and dosage intelligence |
| **Emergency Engine** | Emergency symptom triage and nearest facility guidance |
| **EpiWatch** | Epidemic and outbreak monitoring and alerts |
| **Health Calculators** | BMI, BMR, blood pressure, risk score calculators |
| **MindCare** | Mental health assessment with VADER sentiment analysis |
| **Nutrition Engine** | Personalised nutrition and dietary recommendations |
| **Women & Child Health** | Maternal, infant, and child health guidance |

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| NLP | NLTK, VADER Sentiment |
| ML | scikit-learn, imbalanced-learn |
| Data | pandas, numpy, scipy |
| Visualisation | Plotly, matplotlib |
| Model Persistence | joblib |

## Project Structure

```
bharatcare_pro_Iq_AI/
├── app.py                  # Main Streamlit entry point
├── chatbot_engine.py       # NLP chatbot logic
├── disease_database.py     # Disease knowledge base
├── drugiq_engine.py        # Drug intelligence module
├── emergency_engine.py     # Emergency triage engine
├── epiwatch_engine.py      # Epidemic monitoring
├── health_calculators.py   # Health metric calculators
├── mindcare_engine.py      # Mental health module
├── ml_pipeline.py          # ML training and prediction pipeline
├── nlp_engine.py           # NLP processing utilities
├── nutrition_engine.py     # Nutrition recommendation engine
├── womenchild_engine.py    # Women & child health module
├── generate_data.py        # Synthetic health data generator
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## License

MIT
