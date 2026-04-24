import streamlit as st
import pandas as pd
import sqlite3


# ------------------------------------------------------------
# SCHRITT 1: Datenbank erstellen
# Hier wird eine SQLite-Datenbank erstellt.
# Wenn die Tabelle bereits existiert, wird sie nicht nochmals erstellt.
# ------------------------------------------------------------

def create_database():
    connection = sqlite3.connect("biological_age.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            real_age INTEGER,
            gender TEXT,
            height_cm REAL,
            weight_kg REAL,
            bmi REAL,
            sleep_hours REAL,
            exercise_days INTEGER,
            heart_rate INTEGER,
            stress_level INTEGER,
            smoking TEXT,
            sitting_hours REAL,
            biological_age REAL
        )
    """)

    connection.commit()
    connection.close()


# ------------------------------------------------------------
# SCHRITT 2: Resultate in der Datenbank speichern
# Diese Funktion speichert alle Benutzereingaben und das Resultat.
# ------------------------------------------------------------

def save_entry(real_age, gender, height_cm, weight_kg, bmi, sleep_hours,
               exercise_days, heart_rate, stress_level, smoking,
               sitting_hours, biological_age):

    connection = sqlite3.connect("biological_age.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO entries (
            real_age, gender, height_cm, weight_kg, bmi, sleep_hours,
            exercise_days, heart_rate, stress_level, smoking,
            sitting_hours, biological_age
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        real_age, gender, height_cm, weight_kg, bmi, sleep_hours,
        exercise_days, heart_rate, stress_level, smoking,
        sitting_hours, biological_age
    ))

    connection.commit()
    connection.close()


# ------------------------------------------------------------
# SCHRITT 3: Gespeicherte Resultate laden
# Die gespeicherten Einträge werden mit Pandas als Tabelle geladen.
# ------------------------------------------------------------

def load_entries():
    connection = sqlite3.connect("biological_age.db")
    data = pd.read_sql_query("SELECT * FROM entries", connection)
    connection.close()
    return data


# ------------------------------------------------------------
# SCHRITT 4: BMI berechnen
# Formel: BMI = Gewicht / (Grösse in Meter)^2
# ------------------------------------------------------------

def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m * height_m)
    return bmi


# ------------------------------------------------------------
# SCHRITT 5: BMI-Kategorie bestimmen
# Diese Funktion verwendet if / elif / else.
# ------------------------------------------------------------

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
# SCHRITT 6: Biologisches Alter berechnen
# Dies ist kein medizinisches Modell, sondern ein einfacher Prototyp.
# Das Alter wird aufgrund einfacher Regeln angepasst.
# ------------------------------------------------------------

def calculate_biological_age(real_age, sleep_hours, exercise_days, bmi,
                             heart_rate, stress_level, smoking, sitting_hours):

    biological_age = real_age

    if sleep_hours < 6:
        biological_age = biological_age + 4
    elif sleep_hours >= 7:
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

    if stress_level >= 8:
        biological_age = biological_age + 4
    elif stress_level <= 3:
        biological_age = biological_age - 1

    if smoking == "Yes":
        biological_age = biological_age + 7

    if sitting_hours > 9:
        biological_age = biological_age + 3

    return biological_age


# ------------------------------------------------------------
# SCHRITT 7: Streamlit App starten
# Hier beginnt die sichtbare Web-App.
# ------------------------------------------------------------

create_database()

st.title("Biological Age Estimator")
st.write("Estimate your biological age based on simple lifestyle factors.")


# ------------------------------------------------------------
# SCHRITT 8: Separater BMI Calculator
# Diese Sektion berechnet den BMI separat.
# ------------------------------------------------------------

st.header("BMI Calculator")

gender = st.selectbox("Gender", ["Male", "Female"])
age_for_bmi = st.slider("Age for BMI calculation", 10, 100, 25)
height_cm = st.slider("Height (cm)", 100, 220, 175)
weight_kg = st.slider("Weight (kg)", 30, 160, 70)

calculated_bmi = calculate_bmi(weight_kg, height_cm)
bmi_category = get_bmi_category(calculated_bmi)

st.write("Calculated BMI:", round(calculated_bmi, 2))
st.write("BMI category:", bmi_category)


# ------------------------------------------------------------
# SCHRITT 9: Eingaben für den Biological Age Estimator
# Der BMI wird automatisch aus dem BMI Calculator übernommen.
# ------------------------------------------------------------

st.header("Biological Age Inputs")

real_age = st.slider("Real age", 15, 80, 25)
sleep_hours = st.slider("Sleep per night", 0.0, 12.0, 7.0)
exercise_days = st.slider("Exercise days per week", 0, 7, 3)
heart_rate = st.slider("Resting heart rate", 40, 120, 70)
stress_level = st.slider("Stress level", 1, 10, 5)
smoking = st.selectbox("Do you smoke?", ["No", "Yes"])
sitting_hours = st.slider("Sitting hours per day", 0.0, 16.0, 7.0)


# ------------------------------------------------------------
# SCHRITT 10: Biologisches Alter berechnen
# Die Funktion wird mit den Benutzereingaben aufgerufen.
# ------------------------------------------------------------

biological_age = calculate_biological_age(
    real_age,
    sleep_hours,
    exercise_days,
    calculated_bmi,
    heart_rate,
    stress_level,
    smoking,
    sitting_hours
)

age_gap = biological_age - real_age


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
# SCHRITT 12: Resultat speichern
# Der Button braucht einen eindeutigen key.
# ------------------------------------------------------------

if st.button("Save result", key="save_result_button"):
    save_entry(
        real_age,
        gender,
        height_cm,
        weight_kg,
        calculated_bmi,
        sleep_hours,
        exercise_days,
        heart_rate,
        stress_level,
        smoking,
        sitting_hours,
        biological_age
    )
    st.success("Result saved.")


# ------------------------------------------------------------
# SCHRITT 13: Gespeicherte Resultate anzeigen
# Wenn Resultate vorhanden sind, werden sie als Tabelle angezeigt.
# Zusätzlich wird ein einfacher Line Chart gezeigt.
# ------------------------------------------------------------

st.header("Saved Results")

entries = load_entries()

if len(entries) > 0:
    st.write(entries)
    st.line_chart(entries["biological_age"])
else:
    st.write("No saved results yet.")


# ------------------------------------------------------------
# SCHRITT 14: Hinweis zum Projekt
# Wichtig, weil es kein medizinisches Diagnosetool ist.
# ------------------------------------------------------------

with st.expander("Implementation note"):
    st.write(
        "This is not a medical diagnostic tool. "
        "It is a course project prototype based on simple Python rules, "
        "Streamlit inputs, SQLite storage and basic data visualization."
    )