import streamlit as st
import pandas as pd
import sqlite3


# ------------------------------------------------------------
# SCHRITT 1: Datenbank erstellen
# ------------------------------------------------------------

def create_database():
    connection = sqlite3.connect("biological_age_simple.db")
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


# ------------------------------------------------------------
# SCHRITT 2: Resultat speichern
# ------------------------------------------------------------

def save_entry(age, gender, height_cm, weight_kg, bmi, sleep_hours,
               exercise_days, heart_rate, stress_score, smoking,
               sitting_hours, weekly_steps, biological_age):

    connection = sqlite3.connect("biological_age_simple.db")
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


# ------------------------------------------------------------
# SCHRITT 3: Gespeicherte Resultate laden
# ------------------------------------------------------------

def load_entries():
    connection = sqlite3.connect("biological_age_simple.db")
    data = pd.read_sql_query("SELECT * FROM entries", connection)
    connection.close()
    return data


# ------------------------------------------------------------
# SCHRITT 4: BMI berechnen
# ------------------------------------------------------------

def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m * height_m)
    return bmi


# ------------------------------------------------------------
# SCHRITT 5: Biologisches Alter berechnen
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
# ------------------------------------------------------------

def generate_recommendations(sleep_hours, exercise_days, bmi, heart_rate,
                             stress_score, smoking, sitting_hours, weekly_steps):

    recommendations = []

    if smoking == "Yes":
        recommendations.append(
            "Smoking: This has the strongest negative effect in the prototype. "
            "Try to reduce or stop smoking first. "
            "Learn more: https://www.cdc.gov/tobacco/campaign/tips/quit-smoking/"
        )

    if bmi >= 30:
        recommendations.append(
            "BMI: Your BMI is in the obese range. "
            "A gradual reduction of body weight could strongly improve the result. "
            "Learn more: https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight"
        )
    elif bmi >= 25:
        recommendations.append(
            "BMI: Your BMI is in the overweight range. "
            "Improving BMI could reduce the estimated biological age. "
            "Learn more: https://www.cdc.gov/healthy-weight-growth/index.html"
        )
    elif bmi < 18.5:
        recommendations.append(
            "BMI: Your BMI is below the normal range. "
            "A healthier body weight could improve the result. "
            "Learn more: https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html"
        )

    if sleep_hours < 6:
        recommendations.append(
            "Sleep: Your sleep duration is low. "
            "Try to move closer to 7–9 hours per night. "
            "Learn more: https://www.cdc.gov/sleep/"
        )
    elif sleep_hours < 7:
        recommendations.append(
            "Sleep: Your sleep is slightly below the recommended range. "
            "Try to add 30 minutes of sleep per night. "
            "Learn more: https://www.cdc.gov/sleep/about/index.html"
        )

    if exercise_days == 0:
        recommendations.append(
            "Exercise: You reported no exercise days. "
            "Start with 1 or 2 short sessions per week. "
            "Learn more: https://www.who.int/news-room/fact-sheets/detail/physical-activity"
        )
    elif exercise_days < 3:
        recommendations.append(
            "Exercise: You are below 3 exercise days per week. "
            "Try to add one additional exercise day. "
            "Learn more: https://www.cdc.gov/physical-activity-basics/guidelines/adults.html"
        )

    if heart_rate > 80:
        recommendations.append(
            "Resting heart rate: Your value is relatively high. "
            "Regular walking, cycling, or cardio could improve this. "
            "Learn more: https://www.cdc.gov/physical-activity-basics/benefits/index.html"
        )

    if stress_score >= 8:
        recommendations.append(
            "Stress: Your stress score is high. "
            "Try to improve recovery, sleep, and daily breaks. "
            "Learn more: https://www.who.int/news-room/questions-and-answers/item/stress"
        )
    elif stress_score >= 5:
        recommendations.append(
            "Stress: Your stress score is moderate. "
            "Monitor whether stress affects your sleep or concentration. "
            "Learn more: https://www.cdc.gov/mental-health/living-with/index.html"
        )

    if sitting_hours > 9:
        recommendations.append(
            "Sitting time: Your sitting time is high. "
            "Try to stand up more often and add walking breaks. "
            "Learn more: https://www.who.int/news-room/fact-sheets/detail/physical-activity"
        )

    if weekly_steps < 30000:
        recommendations.append(
            "Weekly steps: Your weekly step count is low. "
            "Try to add 1,000 steps per day as a first goal. "
            "Learn more: https://www.cdc.gov/physical-activity-basics/adding-adults/index.html"
        )
    elif weekly_steps < 50000:
        recommendations.append(
            "Weekly steps: Your weekly step count is moderate. "
            "Try to move closer to 50,000 steps per week. "
            "Learn more: https://www.cdc.gov/physical-activity-basics/adding-adults/index.html"
        )

    if len(recommendations) == 0:
        recommendations.append(
            "No major negative factor was detected in this simple prototype. "
            "General health information: https://www.who.int/health-topics"
        )

    return recommendations


# ------------------------------------------------------------
# SCHRITT 7: App starten
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
# ------------------------------------------------------------

st.header("BMI Calculator")

gender = st.selectbox("Gender", ["Male", "Female"])
age = st.slider("Age", 10, 100, 25)
height_cm = st.slider("Height in cm", 100, 220, 175)
weight_kg = st.slider("Weight in kg", 30, 160, 70)

bmi = calculate_bmi(weight_kg, height_cm)

st.write("Calculated BMI:", round(bmi, 2))

if bmi < 18.5:
    st.write("BMI category: Underweight")
elif bmi < 25:
    st.write("BMI category: Normal weight")
elif bmi < 30:
    st.write("BMI category: Overweight")
else:
    st.write("BMI category: Obese")


# ------------------------------------------------------------
# SCHRITT 9: Eingaben für biologisches Alter
# ------------------------------------------------------------

st.header("Biological Age Inputs")

st.write("Age used for biological age:", age)
st.write("BMI used for biological age:", round(bmi, 2))

sleep_hours_input = st.number_input("Sleep hours per night", min_value=0, max_value=24, value=7)
sleep_minutes_input = st.number_input("Sleep minutes per night", min_value=0, max_value=59, value=0)

sleep_hours = sleep_hours_input + sleep_minutes_input / 60

exercise_days = st.slider("Exercise days per week", 0, 7, 3)
heart_rate = st.slider("Resting heart rate", 40, 120, 70)

st.subheader("Stress Questionnaire")
st.write("Answer each question from 0 to 4.")

overwhelmed = st.slider("How often do you feel overwhelmed?", 0, 4, 2)
sleep_problem = st.slider("How often does stress affect your sleep?", 0, 4, 2)
concentration_problem = st.slider("How often does stress affect your concentration?", 0, 4, 2)

stress_score = overwhelmed + sleep_problem + concentration_problem

st.write("Stress score:", stress_score, "out of 12")

smoking = st.selectbox("Do you smoke?", ["No", "Yes"])

sitting_hours_input = st.number_input("Sitting hours per day", min_value=0, max_value=24, value=7)
sitting_minutes_input = st.number_input("Sitting minutes per day", min_value=0, max_value=59, value=0)

sitting_hours = sitting_hours_input + sitting_minutes_input / 60

weekly_steps = st.number_input("Average weekly steps", min_value=0, max_value=200000, value=50000)


# ------------------------------------------------------------
# SCHRITT 10: Resultat berechnen
# ------------------------------------------------------------

biological_age = calculate_biological_age(
    age,
    sleep_hours,
    exercise_days,
    bmi,
    heart_rate,
    stress_score,
    smoking,
    sitting_hours,
    weekly_steps
)

age_gap = biological_age - age


# ------------------------------------------------------------
# SCHRITT 11: Resultat anzeigen
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
    bmi,
    heart_rate,
    stress_score,
    smoking,
    sitting_hours,
    weekly_steps
)

for recommendation in recommendations:
    st.write("- " + recommendation)


# ------------------------------------------------------------
# SCHRITT 13: Resultat speichern
# ------------------------------------------------------------

if st.button("Save result", key="save_result_button"):
    save_entry(
        age,
        gender,
        height_cm,
        weight_kg,
        bmi,
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