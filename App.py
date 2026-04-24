import streamlit as st
import pandas as pd
import sqlite3


# ------------------------------------------------------------
# SCHRITT 1: Datenbank erstellen
# Neue Datenbank-Version, damit es keine Probleme mit alten Spalten gibt.
# ------------------------------------------------------------

def create_database():
    connection = sqlite3.connect("biological_age_v2.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age INTEGER,
            gender TEXT,
            height_cm REAL,
            weight_kg REAL,
            bmi REAL,
            sleep_hours REAL,
            exercise_days INTEGER,
            heart_rate INTEGER,
            stress_score INTEGER,
            smoking TEXT,
            sitting_hours REAL,
            weekly_steps INTEGER,
            biological_age REAL
        )
    """)

    connection.commit()
    connection.close()


def save_entry(age, gender, height_cm, weight_kg, bmi, sleep_hours,
               exercise_days, heart_rate, stress_score, smoking,
               sitting_hours, weekly_steps, biological_age):

    connection = sqlite3.connect("biological_age_v2.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO entries (
            age, gender, height_cm, weight_kg, bmi, sleep_hours,
            exercise_days, heart_rate, stress_score, smoking,
            sitting_hours, weekly_steps, biological_age
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        age, gender, height_cm, weight_kg, bmi, sleep_hours,
        exercise_days, heart_rate, stress_score, smoking,
        sitting_hours, weekly_steps, biological_age
    ))

    connection.commit()
    connection.close()


def load_entries():
    connection = sqlite3.connect("biological_age_v2.db")
    data = pd.read_sql_query("SELECT * FROM entries", connection)
    connection.close()
    return data


# ------------------------------------------------------------
# SCHRITT 2: BMI berechnen
# ------------------------------------------------------------

def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m * height_m)
    return bmi


def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


# ------------------------------------------------------------
# SCHRITT 3: Zeit in Dezimalstunden umwandeln
# Beispiel: 7 Stunden 30 Minuten = 7.5 Stunden
# ------------------------------------------------------------

def convert_to_hours(hours, minutes):
    total_hours = hours + minutes / 60
    return total_hours


# ------------------------------------------------------------
# SCHRITT 4: Stress-Fragebogen berechnen
# Jede Antwort gibt Punkte. Mehr Punkte = höheres Stressniveau.
# ------------------------------------------------------------

def calculate_stress_score(overwhelmed, sleep_problem, concentration_problem):
    stress_score = overwhelmed + sleep_problem + concentration_problem
    return stress_score


# ------------------------------------------------------------
# SCHRITT 5: Biologisches Alter berechnen
# Ein einfacher regelbasierter Prototyp.
# ------------------------------------------------------------

def calculate_biological_age(age, sleep_hours, exercise_days, bmi,
                             heart_rate, stress_score, smoking,
                             sitting_hours, weekly_steps):

    biological_age = age

    if sleep_hours < 6:
        biological_age = biological_age + 4
    elif sleep_hours >= 7 and sleep_hours <= 9:
        biological_age = biological_age - 2

    if exercise_days == 0:
        biological_age = biological_age + 4
    elif exercise_days >= 3:
        biological_age = biological_age - 3

    if bmi >= 30:
        biological_age = biological_age + 6
    elif bmi >= 25:
        biological_age = biological_age + 3
    elif bmi < 18.5:
        biological_age = biological_age + 2

    if heart_rate > 80:
        biological_age = biological_age + 3
    elif heart_rate < 60:
        biological_age = biological_age - 1

    if stress_score >= 8:
        biological_age = biological_age + 4
    elif stress_score <= 3:
        biological_age = biological_age - 1

    if smoking == "Yes":
        biological_age = biological_age + 7

    if sitting_hours > 9:
        biological_age = biological_age + 3

    if weekly_steps < 30000:
        biological_age = biological_age + 3
    elif weekly_steps >= 70000:
        biological_age = biological_age - 2

    return biological_age


# ------------------------------------------------------------
# SCHRITT 6: Empfehlungen generieren
# Die App prüft, welche Faktoren das Resultat negativ beeinflussen.
# ------------------------------------------------------------

def generate_recommendations(sleep_hours, exercise_days, bmi, heart_rate,
                             stress_score, smoking, sitting_hours, weekly_steps):

    recommendations = []

    if smoking == "Yes":
        recommendations.append("Smoking has the strongest negative effect in this prototype. Reducing or stopping smoking would improve the result most.")

    if bmi >= 30:
        recommendations.append("BMI is in the obese range. A lower BMI would strongly improve the biological age estimate.")
    elif bmi >= 25:
        recommendations.append("BMI is in the overweight range. Improving BMI could reduce the estimated biological age.")

    if sleep_hours < 6:
        recommendations.append("Sleep duration is low. Increasing sleep closer to 7–9 hours could improve the result.")

    if exercise_days == 0:
        recommendations.append("Exercise frequency is very low. Adding regular weekly exercise would improve the result.")
    elif exercise_days < 3:
        recommendations.append("Exercise could be improved. The prototype rewards at least 3 exercise days per week.")

    if stress_score >= 8:
        recommendations.append("Stress score is high. Lower stress would improve the result.")

    if heart_rate > 80:
        recommendations.append("Resting heart rate is relatively high. Improving cardiovascular fitness could improve the result.")

    if sitting_hours > 9:
        recommendations.append("Sitting time is high. Reducing daily sitting time could improve the result.")

    if weekly_steps < 30000:
        recommendations.append("Weekly steps are low. Increasing average weekly steps could improve the result.")

    if len(recommendations) == 0:
        recommendations.append("No major negative factor was detected in this simple prototype.")

    return recommendations


# ------------------------------------------------------------
# SCHRITT 7: Streamlit App starten
# ------------------------------------------------------------

create_database()

st.title("Biological Age Estimator")

st.warning(
    "This is not a medical diagnostic tool. "
    "It is a course project prototype based on simple Python rules, "
    "Streamlit inputs, SQLite storage and basic data visualization."
)


# ------------------------------------------------------------
# SCHRITT 8: BMI Calculator
# Alter wird hier angegeben und später wiederverwendet.
# ------------------------------------------------------------

st.header("BMI Calculator")

gender = st.selectbox("Gender", ["Male", "Female"])
age = st.slider("Age", 10, 100, 25)
height_cm = st.slider("Height (cm)", 100, 220, 175)
weight_kg = st.slider("Weight (kg)", 30, 160, 70)

calculated_bmi = calculate_bmi(weight_kg, height_cm)
bmi_category = get_bmi_category(calculated_bmi)

st.write("Calculated BMI:", round(calculated_bmi, 2))
st.write("BMI category:", bmi_category)


# ------------------------------------------------------------
# SCHRITT 9: Biological Age Inputs
# Das Alter und der BMI werden aus dem BMI Calculator übernommen.
# ------------------------------------------------------------

st.header("Biological Age Inputs")

st.write("Age used for biological age:", age)
st.write("BMI used for biological age:", round(calculated_bmi, 2))

sleep_h = st.slider("Sleep hours per night", 0, 12, 7)
sleep_m = st.slider("Sleep minutes per night", 0, 59, 0)
sleep_hours = convert_to_hours(sleep_h, sleep_m)

exercise_days = st.slider("Exercise days per week", 0, 7, 3)
heart_rate = st.slider("Resting heart rate", 40, 120, 70)

st.subheader("Stress Questionnaire")
st.write("Answer each question from 0 to 4.")

overwhelmed = st.slider("How often do you feel overwhelmed?", 0, 4, 2)
sleep_problem = st.slider("How often does stress affect your sleep?", 0, 4, 2)
concentration_problem = st.slider("How often does stress affect your concentration?", 0, 4, 2)

stress_score = calculate_stress_score(
    overwhelmed,
    sleep_problem,
    concentration_problem
)

st.write("Stress score:", stress_score, "out of 12")

smoking = st.selectbox("Do you smoke?", ["No", "Yes"])

sitting_h = st.slider("Sitting hours per day", 0, 16, 7)
sitting_m = st.slider("Sitting minutes per day", 0, 59, 0)
sitting_hours = convert_to_hours(sitting_h, sitting_m)

weekly_steps = st.slider("Average weekly steps", 0, 120000, 50000)


# ------------------------------------------------------------
# SCHRITT 10: Resultat berechnen
# ------------------------------------------------------------

biological_age = calculate_biological_age(
    age,
    sleep_hours,
    exercise_days,
    calculated_bmi,
    heart_rate,
    stress_score,
    smoking,
    sitting_hours,
    weekly_steps
)

age_gap = biological_age - age


# ------------------------------------------------------------
# SCHRITT 11: Resultate anzeigen
# ------------------------------------------------------------

st.header("Result")

st.metric("Estimated biological age", round(biological_age, 1))
st.write("Age gap:", round(age_gap, 1))

if age_gap > 0:
    st.write("Your biological age is higher than your real age.")
elif age_gap < 0:
    st.write("Your biological age is lower than your real age.")
else:
    st.write("Your biological age is equal to your real age.")


# ------------------------------------------------------------
# SCHRITT 12: Empfehlungen anzeigen
# ------------------------------------------------------------

st.header("Recommendations")

recommendations = generate_recommendations(
    sleep_hours,
    exercise_days,
    calculated_bmi,
    heart_rate,
    stress_score,
    smoking,
    sitting_hours,
    weekly_steps
)

for recommendation in recommendations:
    st.write("-", recommendation)


# ------------------------------------------------------------
# SCHRITT 13: Resultat speichern
# ------------------------------------------------------------

if st.button("Save result", key="save_result_button"):
    save_entry(
        age,
        gender,
        height_cm,
        weight_kg,
        calculated_bmi,
        sleep_hours,
        exercise_days,
        heart_rate,
        stress_score,
        smoking,
        sitting_hours,
        weekly_steps,
        biological_age
    )
    st.success("Result saved.")


# ------------------------------------------------------------
# SCHRITT 14: Gespeicherte Resultate anzeigen
# ------------------------------------------------------------

st.header("Saved Results")

entries = load_entries()

if len(entries) > 0:
    st.write(entries)
    st.line_chart(entries["biological_age"])
else:
    st.write("No saved results yet.")