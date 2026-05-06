# 🗺️ AI-Driven Tourism Demand Forecasting System

An intelligent analytics dashboard built with Streamlit that predicts 
tourist demand and identifies overcrowding risks at popular Indian 
destinations using Machine Learning.

---

## 🔗 Live Demo
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://tourism-demand-forecasting.streamlit.app)

---

## 📌 Project Overview

This project was developed as part of the 8th Semester Internship at 
**Infolabz IT Services, Rajkot** under Gujarat Technological University.

The system analyzes a real-world Indian tourism dataset of **20,000 records** 
spanning 2023–2025, covering **321 tourist places** across **29 states** and 
**6 geographic zones** of India.

---

## 🚀 Features

- **5-Page Interactive Dashboard** with global sidebar filters
- **Cascading Zone → State filter** logic
- **Tourism Overview** — KPIs, top places, zone distribution
- **Demand & Trends** — month-wise trends, season-weather heatmap
- **Overcrowding Risk Analysis** — High/Medium/Low risk classification
- **ML-Powered Predictor** — Real-time visitor demand prediction
- **Downloadable filtered dataset**

---

## 🤖 Machine Learning

| Detail | Value |
|--------|-------|
| Algorithm | Random Forest Regressor |
| Training Records | 16,000 |
| Test Records | 4,000 |
| R² Score | 0.8065 |
| MAE | 109.36 visitors |
| Features Used | 11 |
| Outlier Capping | 99th percentile (2,064) |

### Top Features by Importance
1. Review Count (Lakhs) — 66.8%
2. Season — 14.5%
3. Google Rating — 3.5%

---

## 🏗️ Project Structure

tourism-demand-forecasting/
│
├── app.py                 # Main Streamlit dashboard (5 pages)
├── train_model.py         # ML model training script
├── travel_data.csv        # Tourism dataset (20,000 rows)
├── model.pkl              # Trained Random Forest model
├── encoders.pkl           # Label encoders for categorical features
├── model_info.pkl         # Model metadata and risk ranges
└── requirements.txt       # Python dependencies


## 📊 Dashboard Pages

| Page | Description |
|------|-------------|
| 📂 Dataset Explorer | Filter, search, and download raw data |
| 📊 Tourism Overview | KPIs, zone charts, revenue analysis |
| 📈 Demand & Trends | Monthly trends, heatmaps, YoY comparison |
| 🚨 Overcrowding Risk | Risk classification and alert cards |
| 🤖 Data Assistant | ML-powered visitor demand predictor |

---

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| Dashboard | Streamlit, streamlit-option-menu |
| Visualization | Plotly Express, Plotly Graph Objects |
| ML Model | Scikit-Learn (RandomForestRegressor) |
| Data Processing | Pandas, NumPy |
| Model Saving | Joblib |
| Language | Python 3.x |

---

## ⚙️ Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/[YOUR_USERNAME]/tourism-demand-forecasting.git

# 2. Navigate to project folder
cd tourism-demand-forecasting

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

---

## 📁 Dataset Info

- **Source:** Kaggle — Indian Tourism Dataset
- **Records:** 20,000 rows, 25 columns
- **Years:** 2023, 2024, 2025
- **Places:** 321 unique tourist destinations
- **States:** 29 Indian states
- **Zones:** 6 geographic zones

---

## 👨‍💻 Author

**[YOUR FULL NAME]**
B.E. Computer Engineering — 8th Semester
Gujarat Technological University
Internship at Infolabz IT Services, Rajkot

[![GitHub](https://img.shields.io/badge/GitHub-aryankasundra509-black?logo=github)](https://github.com/aryankasundra509)