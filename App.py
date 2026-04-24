import streamlit as st
import pandas as pd
import sqlite3


# ------------------------------------------------------------
# SCHRITT 1: Datenbank erstellen
# ------------------------------------------------------------

def create_database():
    connection = sqlite3.connect("biological_age_pro.db")
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

    connection = sqlite3.connect("biological_age_pro.db")
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
# SCHRITT 3: Daten laden
# ------------------------------------------------------------

def load_entries():
    connection = sqlite3.connect("biological_age_pro.db")
    data = pd.read_sql_query("SELECT * FROM entries", connection)
    connection.close()
    return data


# ------------------------------------------------------------
# SCHRITT 4: Daten löschen
# ------------------------------------------------------------

def clear_database():
    connection = sqlite3.connect("biological_age_pro.db")
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
# SCHRITT 6: BMI Kategorie bestimmen
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
# SCHRITT 7: Biologisches Alter berechnen
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
# SCHRITT 8: Einflussfaktoren berechnen
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
# SCHRITT 9: Health Score berechnen
# Einfacher Score von 0 bis 100 für eine professionellere Darstellung.
# ------------------------------------------------------------

def calculate_health_score(age_gap):
    health_score = 100 - age_gap * 5

    if health_score > 100:
        health_score = 100

    if health_score < 0:
        health_score = 0

    return health_score


# ------------------------------------------------------------
# SCHRITT 10: Kategorie bestimmen
# ------------------------------------------------------------

def get_profile_category(age_gap):
    if age_gap <= -3:
        return "Excellent profile"
    elif age_gap <= 2:
        return "Balanced profile"
    elif age_gap <= 7:
        return "Improvement recommended"
    else:
        return "High improvement potential"


# ------------------------------------------------------------
# SCHRITT 11: Empfehlungen generieren
# ------------------------------------------------------------

def generate_recommendations(sleep_hours, exercise_days, bmi, heart_rate,
                             stress_score, smoking, sitting_hours, daily_steps):

    recommendations = []

    if smoking == "Yes":
        recommendations.append("Smoking: This is the strongest negative factor. Priority: reduce or stop smoking. Learn more: https://www.cdc.gov/tobacco/campaign/tips/quit-smoking/")

    if bmi >= 30:
        recommendations.append("BMI: Your BMI is in the obese range. Priority: gradual weight reduction and regular activity. Learn more: https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight")
    elif bmi >= 25:
        recommendations.append("BMI: Your BMI is in the overweight range. Priority: improve BMI through activity and nutrition. Learn more: https://www.cdc.gov/healthy-weight-growth/index.html")
    elif bmi < 18.5:
        recommendations.append("BMI: Your BMI is below the normal range. Priority: healthier body weight and muscle mass. Learn more: https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html")

    if sleep_hours < 6:
        recommendations.append("Sleep: Your sleep duration is low. Priority: move closer to 7-9 hours per night. Learn more: https://www.cdc.gov/sleep/")
    elif sleep_hours < 7:
        recommendations.append("Sleep: Slightly below recommended range. Priority: add 30 minutes per night. Learn more: https://www.cdc.gov/sleep/about/index.html")

    if exercise_days == 0:
        recommendations.append("Exercise: No exercise days. Priority: start with 1 or 2 short sessions per week. Learn more: https://www.who.int/news-room/fact-sheets/detail/physical-activity")
    elif exercise_days < 3:
        recommendations.append("Exercise: Below 3 days per week. Priority: add one additional exercise day. Learn more: https://www.cdc.gov/physical-activity-basics/guidelines/adults.html")

    if heart_rate > 80:
        recommendations.append("Resting heart rate: Relatively high. Priority: regular walking, cycling or cardio. Learn more: https://www.cdc.gov/physical-activity-basics/benefits/index.html")

    if stress_score >= 18:
        recommendations.append("Stress: High perceived stress. Priority: recovery, breaks, sleep and workload control. Learn more: https://www.who.int/news-room/questions-and-answers/item/stress")
    elif stress_score >= 12:
        recommendations.append("Stress: Moderate perceived stress. Priority: monitor sleep, concentration and overload. Learn more: https://www.cdc.gov/mental-health/living-with/index.html")

    if sitting_hours > 9:
        recommendations.append("Sitting time: High sitting time. Priority: add walking breaks and stand up more often. Learn more: https://www.who.int/news-room/fact-sheets/detail/physical-activity")

    if daily_steps < 4000:
        recommendations.append("Daily steps: Low daily step count. Priority: add 1,000 steps per day. Learn more: https://www.cdc.gov/physical-activity-basics/adding-adults/index.html")
    elif daily_steps < 7000:
        recommendations.append("Daily steps: Moderate but improvable. Priority: move closer to 7,000-10,000 daily steps. Learn more: https://www.cdc.gov/physical-activity-basics/adding-adults/index.html")

    if len(recommendations) == 0:
        recommendations.append("No major negative factor was detected. General health information: https://www.who.int/health-topics")

    return recommendations


# ------------------------------------------------------------
# SCHRITT 12: 7-Day Action Plan generieren
# Das ist das neue innovative Element.
# ------------------------------------------------------------

def generate_action_plan(sleep_hours, exercise_days, stress_score,
                         sitting_hours, daily_steps, smoking):

    plan = []

    if sleep_hours < 7:
        plan.append("Day 1: Go to bed 30 minutes earlier than usual.")
    else:
        plan.append("Day 1: Keep your current sleep routine stable.")

    if daily_steps < 7000:
        plan.append("Day 2: Add a 15-minute walk after lunch or dinner.")
    else:
        plan.append("Day 2: Maintain your current walking routine.")

    if sitting_hours > 9:
        plan.append("Day 3: Stand up for 5 minutes every hour.")
    else:
        plan.append("Day 3: Keep sitting time under control.")

    if exercise_days < 3:
        plan.append("Day 4: Add one short workout or active walk.")
    else:
        plan.append("Day 4: Keep your exercise rhythm.")

    if stress_score >= 12:
        plan.append("Day 5: Take 10 minutes for breathing, planning or a quiet walk.")
    else:
        plan.append("Day 5: Continue your current stress management.")

    if smoking == "Yes":
        plan.append("Day 6: Identify one smoking trigger and reduce it.")
    else:
        plan.append("Day 6: Focus on one healthy habit you want to maintain.")

    plan.append("Day 7: Re-enter your values and compare your new biological age.")

    return plan


# ------------------------------------------------------------
# SCHRITT 13: App starten
# ------------------------------------------------------------

create_database()

st.title("Biological Age Estimator")
st.subheader("A simple health prototype based on lifestyle inputs")

st.warning(
    "This is not a medical diagnostic tool. "
    "It is a course project prototype based on simple Python rules, "
    "Streamlit inputs, SQLite storage and basic data visualization."
)

st.divider()


# ------------------------------------------------------------
# SCHRITT 14: Layout - Startbereich
# ------------------------------------------------------------

st.header("1. Personal Profile")

col1, col2 = st.columns(2)

with col1:
    gender = st.selectbox("Gender", ["Male", "Female"])
    age = st.slider("Age", 10, 100, 25)

with col2:
    height_cm = st.slider("Height in cm", 100, 220, 175)
    weight_kg = st.slider("Weight in kg", 30, 160, 70)

bmi = calculate_bmi(weight_kg, height_cm)
bmi_category = get_bmi_category(bmi)

col3, col4 = st.columns(2)

with col3:
    st.metric("Calculated BMI", round(bmi, 2))

with col4:
    st.metric("BMI Category", bmi_category)

st.divider()


# ------------------------------------------------------------
# SCHRITT 15: Lifestyle Inputs
# ------------------------------------------------------------

st.header("2. Lifestyle Inputs")

col5, col6 = st.columns(2)

with col5:
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

with col6:
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

st.divider()


# ------------------------------------------------------------
# SCHRITT 16: Stress Test
# ------------------------------------------------------------

st.header("3. Stress Check")
st.write("Answer from 0 = never to 4 = very often.")

col7, col8 = st.columns(2)

with col7:
    stress_1 = st.slider("Unable to control important things?", 0, 4, 2)
    stress_2 = st.slider("Nervous or stressed?", 0, 4, 2)
    stress_3 = st.slider("Difficulties piling up?", 0, 4, 2)

with col8:
    stress_4 = st.slider("Confident handling problems?", 0, 4, 2)
    stress_5 = st.slider("Things going your way?", 0, 4, 2)
    stress_6 = st.slider("Unable to cope with tasks?", 0, 4, 2)

stress_score = stress_1 + stress_2 + stress_3 + (4 - stress_4) + (4 - stress_5) + stress_6

st.metric("Stress score", str(stress_score) + " / 24")

st.divider()


# ------------------------------------------------------------
# SCHRITT 17: Hauptresultat
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
health_score = calculate_health_score(age_gap)
profile_category = get_profile_category(age_gap)

st.header("4. Health Dashboard")

col9, col10, col11 = st.columns(3)

with col9:
    st.metric("Real age", age)

with col10:
    st.metric("Biological age", round(biological_age, 1))

with col11:
    st.metric("Health score", round(health_score, 1))

st.write("Profile category:", profile_category)
st.write("Age gap:", round(age_gap, 1), "years")

if age_gap <= -3:
    st.success("Your biological age is clearly below your real age.")
elif age_gap <= 2:
    st.info("Your biological age is close to your real age.")
else:
    st.warning("Your biological age is above your real age. Improvement recommended.")

st.divider()


# ------------------------------------------------------------
# SCHRITT 18: Einflussanalyse
# ------------------------------------------------------------

st.header("5. Factor Impact Analysis")

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
    st.write(impact_table)
    st.bar_chart(impact_table, x="Factor", y="Impact")
else:
    st.write("No factor changed the biological age in this prototype.")

st.divider()


# ------------------------------------------------------------
# SCHRITT 19: What-if Simulator
# ------------------------------------------------------------

st.header("6. What-if Simulator")
st.write("Simulate small lifestyle changes and compare the result.")

col12, col13 = st.columns(2)

with col12:
    new_sleep = st.number_input(
        "New sleep per night",
        min_value=0.0,
        max_value=24.0,
        value=sleep_hours,
        step=0.25,
        format="%.2f"
    )

    new_exercise = st.slider("New exercise days per week", 0, 7, exercise_days)

with col13:
    new_steps = st.number_input(
        "New average daily steps",
        min_value=0,
        max_value=25000,
        value=daily_steps,
        step=500
    )

    new_stress = st.slider("New stress score", 0, 24, stress_score)

new_biological_age = calculate_biological_age(
    age,
    new_sleep,
    new_exercise,
    bmi,
    heart_rate,
    new_stress,
    smoking,
    sitting_hours,
    new_steps
)

st.write("Current biological age:", round(biological_age, 1))
st.write("Simulated biological age:", round(new_biological_age, 1))
st.write("Potential improvement:", round(biological_age - new_biological_age, 1), "years")

st.divider()


# ------------------------------------------------------------
# SCHRITT 20: 7-Day Action Plan
# ------------------------------------------------------------

st.header("7. Personal 7-Day Action Plan")

action_plan = generate_action_plan(
    sleep_hours,
    exercise_days,
    stress_score,
    sitting_hours,
    daily_steps,
    smoking
)

for action in action_plan:
    st.write("- " + action)

st.divider()


# ------------------------------------------------------------
# SCHRITT 21: Empfehlungen
# ------------------------------------------------------------

st.header("8. Recommendations")

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
# SCHRITT 22: Demo Profile
# ------------------------------------------------------------

st.header("9. Demo Profiles")

if st.button("Show demo profiles", key="demo_button"):
    healthy_age = calculate_biological_age(22, 8, 4, 22, 58, 6, "No", 5, 12000)
    unhealthy_age = calculate_biological_age(22, 5, 0, 31, 90, 20, "Yes", 11, 3000)

    demo_table = pd.DataFrame({
        "Profile": ["Healthy profile", "Unhealthy profile"],
        "Real age": [22, 22],
        "Biological age": [healthy_age, unhealthy_age]
    })

    st.write(demo_table)
    st.bar_chart(demo_table, x="Profile", y="Biological age")

st.divider()


# ------------------------------------------------------------
# SCHRITT 23: Speichern
# ------------------------------------------------------------

st.header("10. Save Result")

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
# SCHRITT 24: Verlauf
# ------------------------------------------------------------

st.header("11. History")

entries = load_entries()

if len(entries) > 0:
    st.write("Number of saved results:", len(entries))
    st.write("Average biological age:", round(entries["biological_age"].mean(), 2))
    st.write("Average real age:", round(entries["age"].mean(), 2))

    st.write(entries)

    st.line_chart(entries["biological_age"])

else:
    st.write("No saved results yet.")

if st.button("Clear history", key="clear_history_button"):
    clear_database()
    st.success("History deleted.")