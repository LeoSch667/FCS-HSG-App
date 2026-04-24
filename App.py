import streamlit as st
import pandas as pd
import sqlite3


# ------------------------------------------------------------
# SCHRITT 1: Datenbank erstellen
# ------------------------------------------------------------

def create_database():
    connection = sqlite3.connect("biological_age_v5.db")
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
            daily_steps INTEGER,
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
               sitting_hours, daily_steps, biological_age):

    connection = sqlite3.connect("biological_age_v5.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO entries (
            age, gender, height_cm, weight_kg, bmi, sleep_hours,
            exercise_days, heart_rate, stress_score, smoking,
            sitting_hours, daily_steps, biological_age
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        age, gender, height_cm, weight_kg, bmi, sleep_hours,
        exercise_days, heart_rate, stress_score, smoking,
        sitting_hours, daily_steps, biological_age
    ))

    connection.commit()
    connection.close()


# ------------------------------------------------------------
# SCHRITT 3: Gespeicherte Resultate laden
# ------------------------------------------------------------

def load_entries():
    connection = sqlite3.connect("biological_age_v5.db")
    data = pd.read_sql_query("SELECT * FROM entries", connection)
    connection.close()
    return data


# ------------------------------------------------------------
# SCHRITT 4: Verlauf löschen
# ------------------------------------------------------------

def clear_database():
    connection = sqlite3.connect("biological_age_v5.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM entries")
    connection.commit()
    connection.close()


# ------------------------------------------------------------
# SCHRITT 5: BMI berechnen
# ------------------------------------------------------------

def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m * height_m)
    return bmi


# ------------------------------------------------------------
# SCHRITT 6: Biologisches Alter berechnen
# ------------------------------------------------------------

def calculate_biological_age(age, sleep_hours, exercise_days, bmi,
                             heart_rate, stress_score, smoking,
                             sitting_hours, daily_steps):

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

    if stress_score >= 18:
        biological_age = biological_age + 4
    elif stress_score <= 8:
        biological_age = biological_age - 1

    if smoking == "Yes":
        biological_age = biological_age + 7

    if sitting_hours > 9:
        biological_age = biological_age + 3

    if daily_steps < 4000:
        biological_age = biological_age + 3
    elif daily_steps >= 10000:
        biological_age = biological_age - 2

    return biological_age


# ------------------------------------------------------------
# SCHRITT 7: Einflussfaktoren berechnen
# Diese Funktion zeigt, welche Faktoren das Resultat verändern.
# ------------------------------------------------------------

def get_factor_impacts(sleep_hours, exercise_days, bmi, heart_rate,
                       stress_score, smoking, sitting_hours, daily_steps):

    factors = []
    impacts = []

    if sleep_hours < 6:
        factors.append("Low sleep")
        impacts.append(4)
    elif sleep_hours >= 7 and sleep_hours <= 9:
        factors.append("Good sleep")
        impacts.append(-2)

    if exercise_days == 0:
        factors.append("No exercise")
        impacts.append(4)
    elif exercise_days >= 3:
        factors.append("Regular exercise")
        impacts.append(-3)

    if bmi >= 30:
        factors.append("Obese BMI")
        impacts.append(6)
    elif bmi >= 25:
        factors.append("Overweight BMI")
        impacts.append(3)
    elif bmi < 18.5:
        factors.append("Underweight BMI")
        impacts.append(2)

    if heart_rate > 80:
        factors.append("High heart rate")
        impacts.append(3)
    elif heart_rate < 60:
        factors.append("Low resting heart rate")
        impacts.append(-1)

    if stress_score >= 18:
        factors.append("High stress")
        impacts.append(4)
    elif stress_score <= 8:
        factors.append("Low stress")
        impacts.append(-1)

    if smoking == "Yes":
        factors.append("Smoking")
        impacts.append(7)

    if sitting_hours > 9:
        factors.append("High sitting time")
        impacts.append(3)

    if daily_steps < 4000:
        factors.append("Low daily steps")
        impacts.append(3)
    elif daily_steps >= 10000:
        factors.append("High daily steps")
        impacts.append(-2)

    impact_table = pd.DataFrame({
        "Factor": factors,
        "Impact": impacts
    })

    return impact_table


# ------------------------------------------------------------
# SCHRITT 8: Empfehlungen generieren
# ------------------------------------------------------------

def generate_recommendations(sleep_hours, exercise_days, bmi, heart_rate,
                             stress_score, smoking, sitting_hours, daily_steps):

    recommendations = []

    if smoking == "Yes":
        recommendations.append(
            "Smoking: This is the strongest negative factor in this prototype. "
            "Try to reduce or stop smoking first. "
            "Learn more: https://www.cdc.gov/tobacco/campaign/tips/quit-smoking/"
        )

    if bmi >= 30:
        recommendations.append(
            "BMI: Your BMI is in the obese range. Gradual weight reduction could strongly improve the result. "
            "Learn more: https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight"
        )
    elif bmi >= 25:
        recommendations.append(
            "BMI: Your BMI is in the overweight range. Improving BMI could reduce your estimated biological age. "
            "Learn more: https://www.cdc.gov/healthy-weight-growth/index.html"
        )
    elif bmi < 18.5:
        recommendations.append(
            "BMI: Your BMI is below the normal range. A healthier body weight could improve the result. "
            "Learn more: https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html"
        )

    if sleep_hours < 6:
        recommendations.append(
            "Sleep: Your sleep duration is low. Try to move closer to 7–9 hours per night. "
            "Learn more: https://www.cdc.gov/sleep/"
        )
    elif sleep_hours < 7:
        recommendations.append(
            "Sleep: Your sleep is slightly below the recommended range. Try to add 30 minutes per night. "
            "Learn more: https://www.cdc.gov/sleep/about/index.html"
        )

    if exercise_days == 0:
        recommendations.append(
            "Exercise: You reported no exercise days. Start with 1 or 2 short sessions per week. "
            "Learn more: https://www.who.int/news-room/fact-sheets/detail/physical-activity"
        )
    elif exercise_days < 3:
        recommendations.append(
            "Exercise: You are below 3 exercise days per week. Try to add one additional exercise day. "
            "Learn more: https://www.cdc.gov/physical-activity-basics/guidelines/adults.html"
        )

    if heart_rate > 80:
        recommendations.append(
            "Resting heart rate: Your value is relatively high. Regular walking, cycling, or cardio could help. "
            "Learn more: https://www.cdc.gov/physical-activity-basics/benefits/index.html"
        )

    if stress_score >= 18:
        recommendations.append(
            "Stress: Your perceived stress score is high. Focus on control, recovery, breaks, and sleep. "
            "Learn more: https://www.who.int/news-room/questions-and-answers/item/stress"
        )
    elif stress_score >= 12:
        recommendations.append(
            "Stress: Your perceived stress score is moderate. Monitor overload, sleep, and concentration. "
            "Learn more: https://www.cdc.gov/mental-health/living-with/index.html"
        )

    if sitting_hours > 9:
        recommendations.append(
            "Sitting time: Your sitting time is high. Add walking breaks and stand up more often. "
            "Learn more: https://www.who.int/news-room/fact-sheets/detail/physical-activity"
        )

    if daily_steps < 4000:
        recommendations.append(
            "Daily steps: Your daily step count is low. Try to add 1,000 steps per day. "
            "Learn more: https://www.cdc.gov/physical-activity-basics/adding-adults/index.html"
        )
    elif daily_steps < 7000:
        recommendations.append(
            "Daily steps: Your step count is moderate but improvable. Try to move closer to 7,000–10,000 daily steps. "
            "Learn more: https://www.cdc.gov/physical-activity-basics/adding-adults/index.html"
        )

    if len(recommendations) == 0:
        recommendations.append(
            "No major negative factor was detected. "
            "General health information: https://www.who.int/health-topics"
        )

    return recommendations


# ------------------------------------------------------------
# SCHRITT 9: App starten
# ------------------------------------------------------------

create_database()

st.title("Biological Age Estimator")

st.warning(
    "This is not a medical diagnostic tool. "
    "It is a course project prototype based on simple Python rules, "
    "Streamlit inputs, SQLite storage and basic data visualization."
)

st.divider()


# ------------------------------------------------------------
# SCHRITT 10: BMI Calculator
# ------------------------------------------------------------

st.header("1. BMI Calculator")

col1, col2 = st.columns(2)

with col1:
    gender = st.selectbox("Gender", ["Male", "Female"])
    age = st.slider("Age", 10, 100, 25)

with col2:
    height_cm = st.slider("Height in cm", 100, 220, 175)
    weight_kg = st.slider("Weight in kg", 30, 160, 70)

bmi = calculate_bmi(weight_kg, height_cm)

st.metric("Calculated BMI", round(bmi, 2))

if bmi < 18.5:
    st.write("BMI category: Underweight")
elif bmi < 25:
    st.write("BMI category: Normal weight")
elif bmi < 30:
    st.write("BMI category: Overweight")
else:
    st.write("BMI category: Obese")

st.divider()


# ------------------------------------------------------------
# SCHRITT 11: Eingaben für biologisches Alter
# ------------------------------------------------------------

st.header("2. Biological Age Inputs")

st.info("The app uses the age and BMI from the BMI Calculator above.")

col3, col4 = st.columns(2)

with col3:
    sleep_hours = st.number_input(
        "Sleep per night in hours",
        min_value=0.0,
        max_value=24.0,
        value=7.50,
        step=0.25,
        format="%.2f"
    )

    exercise_days = st.slider("Exercise days per week", 0, 7, 3)

    heart_rate = st.slider("Resting heart rate", 40, 120, 70)

with col4:
    sitting_hours = st.number_input(
        "Sitting time per day in hours",
        min_value=0.0,
        max_value=24.0,
        value=7.50,
        step=0.25,
        format="%.2f"
    )

    daily_steps = st.number_input(
        "Average daily steps",
        min_value=0,
        max_value=25000,
        value=7000,
        step=500
    )

    smoking = st.selectbox("Do you smoke?", ["No", "Yes"])

st.subheader("Stress Questionnaire")
st.write("Answer from 0 = never to 4 = very often.")

stress_1 = st.slider("Unable to control important things?", 0, 4, 2)
stress_2 = st.slider("Nervous or stressed?", 0, 4, 2)
stress_3 = st.slider("Difficulties piling up?", 0, 4, 2)
stress_4 = st.slider("Confident handling problems?", 0, 4, 2)
stress_5 = st.slider("Things going your way?", 0, 4, 2)
stress_6 = st.slider("Unable to cope with tasks?", 0, 4, 2)

stress_score = stress_1 + stress_2 + stress_3 + (4 - stress_4) + (4 - stress_5) + stress_6

st.write("Stress score:", stress_score, "out of 24")

st.divider()


# ------------------------------------------------------------
# SCHRITT 12: Resultat berechnen
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
    daily_steps
)

age_gap = biological_age - age

st.header("3. Result")

col5, col6 = st.columns(2)

with col5:
    st.metric("Real age", age)

with col6:
    st.metric("Estimated biological age", round(biological_age, 1))

st.write("Age gap:", round(age_gap, 1))

if age_gap <= -3:
    st.success("Final category: Excellent lifestyle profile")
elif age_gap <= 2:
    st.info("Final category: Balanced profile")
else:
    st.warning("Final category: Improvement recommended")

if age_gap > 0:
    st.write("Your biological age is higher than your real age.")
elif age_gap < 0:
    st.write("Your biological age is lower than your real age.")
else:
    st.write("Your biological age is equal to your real age.")

st.divider()


# ------------------------------------------------------------
# SCHRITT 13: Score Explanation
# ------------------------------------------------------------

st.header("4. Score Explanation")

impact_table = get_factor_impacts(
    sleep_hours,
    exercise_days,
    bmi,
    heart_rate,
    stress_score,
    smoking,
    sitting_hours,
    daily_steps
)

if len(impact_table) > 0:
    st.write("The following factors changed your estimated biological age:")
    st.write(impact_table)
    st.bar_chart(impact_table, x="Factor", y="Impact")
else:
    st.write("No factor changed the biological age in this prototype.")

st.divider()


# ------------------------------------------------------------
# SCHRITT 14: What-if Simulator
# ------------------------------------------------------------

st.header("5. What-if Simulator")

st.write("Change some values and see how your biological age would change.")

new_sleep = st.number_input(
    "What if sleep per night was:",
    min_value=0.0,
    max_value=24.0,
    value=sleep_hours,
    step=0.25,
    format="%.2f"
)

new_exercise = st.slider("What if exercise days per week were:", 0, 7, exercise_days)

new_sitting = st.number_input(
    "What if sitting time per day was:",
    min_value=0.0,
    max_value=24.0,
    value=sitting_hours,
    step=0.25,
    format="%.2f"
)

new_steps = st.number_input(
    "What if average daily steps were:",
    min_value=0,
    max_value=25000,
    value=daily_steps,
    step=500
)

new_stress = st.slider("What if stress score was:", 0, 24, stress_score)

new_biological_age = calculate_biological_age(
    age,
    new_sleep,
    new_exercise,
    bmi,
    heart_rate,
    new_stress,
    smoking,
    new_sitting,
    new_steps
)

st.write("Current biological age:", round(biological_age, 1))
st.write("What-if biological age:", round(new_biological_age, 1))
st.write("Potential improvement:", round(biological_age - new_biological_age, 1), "years")

st.divider()


# ------------------------------------------------------------
# SCHRITT 15: Demo Profile
# ------------------------------------------------------------

st.header("6. Demo Profiles")

if st.button("Show demo profiles", key="demo_button"):
    healthy_age = calculate_biological_age(
        22, 8, 4, 22, 58, 6, "No", 5, 12000
    )

    unhealthy_age = calculate_biological_age(
        22, 5, 0, 31, 90, 20, "Yes", 11, 3000
    )

    st.write("Healthy profile:")
    st.write("Age: 22, Sleep: 8h, Exercise: 4 days, BMI: 22, No smoking")
    st.write("Estimated biological age:", healthy_age)

    st.write("Unhealthy profile:")
    st.write("Age: 22, Sleep: 5h, Exercise: 0 days, BMI: 31, Smoker")
    st.write("Estimated biological age:", unhealthy_age)

st.divider()


# ------------------------------------------------------------
# SCHRITT 16: Empfehlungen anzeigen
# ------------------------------------------------------------

st.header("7. Recommendations")

recommendations = generate_recommendations(
    sleep_hours,
    exercise_days,
    bmi,
    heart_rate,
    stress_score,
    smoking,
    sitting_hours,
    daily_steps
)

for recommendation in recommendations:
    st.write("- " + recommendation)

st.divider()


# ------------------------------------------------------------
# SCHRITT 17: Resultat speichern
# ------------------------------------------------------------

st.header("8. Save Result")

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
        daily_steps,
        biological_age
    )
    st.success("Result saved.")

st.divider()


# ------------------------------------------------------------
# SCHRITT 18: Gespeicherte Resultate anzeigen
# ------------------------------------------------------------

st.header("9. Saved Results")

entries = load_entries()

if len(entries) > 0:
    st.write("Number of saved results:", len(entries))
    st.write("Average biological age:", round(entries["biological_age"].mean(), 2))
    st.write("Average real age:", round(entries["age"].mean(), 2))

    st.write(entries)

    st.line_chart(entries["biological_age"])

    comparison_data = pd.DataFrame({
        "Age type": ["Real age", "Biological age"],
        "Value": [age, biological_age]
    })

    st.write("Current comparison:")
    st.bar_chart(comparison_data, x="Age type", y="Value")

else:
    st.write("No saved results yet.")

if st.button("Clear history", key="clear_history_button"):
    clear_database()
    st.success("History deleted.")