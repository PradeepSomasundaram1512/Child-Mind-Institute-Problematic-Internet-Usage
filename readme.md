# 🧠 Child Mind Institute — Problematic Internet Use Dashboard

This project is a multi-page interactive dashboard developed using **Plotly Dash** and **Dash Mantine Components**. It visualizes patterns related to **Problematic Internet Use (PIU)** in children and adolescents using physical, psychological, and behavioral indicators.

> ⚠️ Dataset files are private and will not be shared in this repository due to licensing and privacy constraints.

---

## 📂 Project Structure

<pre> CAPSTONE - FINAL/ ├── app.py # Main Dash app entry point ├── data_loader.py # Data loading & preprocessing script ├── test.py # Test script (optional/for debugging) ├── submission.csv # Final predictions (not pushed to GitHub) ├── Capstone_latest.ipynb # Notebook version of project (optional) │ ├── assets/ │ └── thumbnail.jpg # Dashboard logo or image asset │ ├── pages/ # Contains all individual dashboard pages │ ├── actigraphy_dashboard.py │ ├── body_composition_dashboard.py │ ├── demographics_dashboard.py │ ├── fitness_sii_dashboard.py │ ├── internet_behaviour_dashboard.py │ ├── prediction_dashboard.py │ └── psych_wellbeing_dashboard.py │ ├── child-mind-institute-problematic-internet-use/ │ ├── train.csv │ ├── test.csv │ ├── submission.csv │ ├── sample_submission.csv │ ├── data_dictionary.csv │ ├── series_train.parquet │ └── series_test.parquet </pre>

---

## 📊 Dashboards Included

- **Predictions** – Final predicted `sii` scores for the test dataset
- **Demographics & SII** – Gender and age distribution vs PIU severity
- **Physical Fitness** – Endurance stage/time metrics and their relation to SII
- **Body Composition** – BMI, body fat %, and water distribution patterns
- **Psychological Wellbeing** – Depression & functioning scores by SII
- **Internet Usage** – Screen time vs age and SII severity
- **Actigraphy Patterns** – Hourly movement, light exposure, and night activity

---

## 🚀 How to Run the App Locally

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/piu-dashboard.git
cd piu-dashboard
```


### 2. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate      # On Windows use: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip freeze > requirements.txt # You can generate the requirements file 

```

### 4. Add Dataset Files
Place your dataset files inside the child-mind-institute-problematic-internet-use/ folder as shown in the project tree. These files will not be pushed to GitHub due to .gitignore rules.

### 5. Run the App
```bash
python app.py
```
Visit http://127.0.0.1:8050 in your browser to view the dashboard.


## 🧠 Authors
Bharath Genji Mohanaranga
MS Data Science, George Washington University

Pradeep Somasundaram
MS Data Science, George Washington University
