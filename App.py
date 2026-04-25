import streamlit as st
import pandas as pd
import sqlite3


# ------------------------------------------------------------
# SCHRITT 1: Datenbank erstellen
# ------------------------------------------------------------

def create_database():
    connection = sqlite3.connect("biological_age_rule_based.db")
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
            biological_age REAL,
            risk_profile TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_entry(age, gender, height_cm, weight_kg, bmi, sleep_hours,
               exercise_days, heart_rate, stress_score, smoking,
               sitting_hours, daily_steps, biological_age, risk_profile):

    connection = sqlite3.connect("biological_age_rule_based.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO entries (
            age, gender, height_cm, weight_kg, bmi, sleep_hours,
            exercise_days, heart_rate, stress_score, smoking,
            sitting_hours, daily_steps, biological_age, risk_profile
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        age, gender, height_cm, weight_kg, bmi, sleep_hours,
        exercise_days, heart_rate, stress_score, smoking,
        sitting_hours, daily_steps, biological_age, risk_profile
    ))

    connection.commit()
    connection.close()


def load_entries():
    connection = sqlite3.connect("biological_age_rule_based.db")
    data = pd.read_sql_query("SELECT * FROM entries", connection)
    connection.close()
    return data


def clear_database():
    connection = sqlite3.connect("biological_age_rule_based.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM entries")
    connection.commit()
    connection.close()


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
# SCHRITT 3: Biologisches Alter berechnen
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
# SCHRITT 4: Rule-based Risk Classification
# Diese Funktion ersetzt das Machine-Learning-Modul.
# Sie klassifiziert das Risiko anhand des Age Gap.
# ------------------------------------------------------------

def predict_risk_profile(age_gap):
    if age_gap <= 0:
        return "Low risk"
    elif age_gap <= 5:
        return "Medium risk"
    else:
        return "High risk"


# ------------------------------------------------------------
# SCHRITT 5: Health Score berechnen
# ------------------------------------------------------------

def calculate_health_score(age_gap):
    score = 100 - age_gap * 5

    if score > 100:
        score = 100

    if score < 0:
        score = 0

    return score


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
# SCHRITT 6: Einflussfaktoren berechnen
# ------------------------------------------------------------

def get_factor_impacts(sleep_hours, exercise_days, bmi, heart_rate,
                       stress_score, smoking, sitting_hours, daily_steps):

    factors = []
    impacts = []

    if smoking == "Yes":
        factors.append("Smoking")
        impacts.append(7)

    if bmi >= 30:
        factors.append("Obese BMI")
        impacts.append(6)
    elif bmi >= 25:
        factors.append("Overweight BMI")
        impacts.append(3)
    elif bmi < 18.5:
        factors.append("Underweight BMI")
        impacts.append(2)

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

    if sitting_hours > 9:
        factors.append("High sitting time")
        impacts.append(3)

    if daily_steps < 4000:
        factors.append("Low daily steps")
        impacts.append(3)
    elif daily_steps >= 10000:
        factors.append("High daily steps")
        impacts.append(-2)

    table = pd.DataFrame({
        "Factor": factors,
        "Impact": impacts
    })

    return table


def get_top_priorities(impact_table):
    negative_impacts = impact_table[impact_table["Impact"] > 0]
    negative_impacts = negative_impacts.sort_values("Impact", ascending=False)
    top_priorities = negative_impacts.head(3)
    return top_priorities


# ------------------------------------------------------------
# SCHRITT 7: Smart Scenario
# ------------------------------------------------------------

def generate_smart_scenario(sleep_hours, exercise_days, stress_score,
                            sitting_hours, daily_steps):

    new_sleep = sleep_hours
    new_exercise = exercise_days
    new_stress = stress_score
    new_sitting = sitting_hours
    new_steps = daily_steps

    if sleep_hours < 7:
        new_sleep = 7.5

    if exercise_days < 3:
        new_exercise = 3

    if stress_score > 12:
        new_stress = 10

    if sitting_hours > 8:
        new_sitting = 7

    if daily_steps < 7000:
        new_steps = 8000

    return new_sleep, new_exercise, new_stress, new_sitting, new_steps


# ------------------------------------------------------------
# SCHRITT 8: Personal Roadmap
# ------------------------------------------------------------

def generate_roadmap(top_priorities):
    roadmap = []

    if len(top_priorities) == 0:
        roadmap.append("Week 1: Maintain your current healthy habits.")
        roadmap.append("Week 2: Continue tracking your values.")
        roadmap.append("Week 3: Try to improve one small habit.")
        roadmap.append("Week 4: Re-enter your values and compare your result.")
    else:
        counter = 1

        for index, row in top_priorities.iterrows():
            factor = row["Factor"]

            if factor == "Smoking":
                roadmap.append("Week " + str(counter) + ": Focus on reducing smoking triggers.")
            elif factor == "Obese BMI" or factor == "Overweight BMI":
                roadmap.append("Week " + str(counter) + ": Focus on weight-related habits and daily movement.")
            elif factor == "Low sleep":
                roadmap.append("Week " + str(counter) + ": Focus on improving sleep duration.")
            elif factor == "No exercise":
                roadmap.append("Week " + str(counter) + ": Add one or two short exercise sessions.")
            elif factor == "High stress":
                roadmap.append("Week " + str(counter) + ": Reduce stress through breaks, planning and sleep.")
            elif factor == "High sitting time":
                roadmap.append("Week " + str(counter) + ": Reduce sitting time with walking breaks.")
            elif factor == "Low daily steps":
                roadmap.append("Week " + str(counter) + ": Increase daily steps by 1,000.")
            elif factor == "High heart rate":
                roadmap.append("Week " + str(counter) + ": Add moderate cardio activity.")
            else:
                roadmap.append("Week " + str(counter) + ": Improve " + factor + ".")

            counter = counter + 1

        roadmap.append("Week 4: Re-enter your values and compare your progress.")

    return roadmap


# ------------------------------------------------------------
# SCHRITT 9: Empfehlungen
# ------------------------------------------------------------

def generate_recommendations(sleep_hours, exercise_days, bmi, heart_rate,
                             stress_score, smoking, sitting_hours, daily_steps):

    recommendations = []

    if smoking == "Yes":
        recommendations.append("Smoking: strongest negative factor. Learn more: https://www.cdc.gov/tobacco/campaign/tips/quit-smoking/")

    if bmi >= 30:
        recommendations.append("BMI: obese range. Learn more: https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight")
    elif bmi >= 25:
        recommendations.append("BMI: overweight range. Learn more: https://www.cdc.gov/healthy-weight-growth/index.html")
    elif bmi < 18.5:
        recommendations.append("BMI: underweight range. Learn more: https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html")

    if sleep_hours < 7:
        recommendations.append("Sleep: try to move closer to 7-9 hours per night. Learn more: https://www.cdc.gov/sleep/")

    if exercise_days < 3:
        recommendations.append("Exercise: try to reach at least 3 exercise days per week. Learn more: https://www.who.int/news-room/fact-sheets/detail/physical-activity")

    if heart_rate > 80:
        recommendations.append("Resting heart rate: regular cardio could help. Learn more: https://www.cdc.gov/physical-activity-basics/benefits/index.html")

    if stress_score >= 12:
        recommendations.append("Stress: perceived stress is elevated. Learn more: https://www.who.int/news-room/questions-and-answers/item/stress")

    if sitting_hours > 9:
        recommendations.append("Sitting time: add walking breaks. Learn more: https://www.who.int/news-room/fact-sheets/detail/physical-activity")

    if daily_steps < 7000:
        recommendations.append("Daily steps: increase walking gradually. Learn more: https://www.cdc.gov/physical-activity-basics/adding-adults/index.html")

    if len(recommendations) == 0:
        recommendations.append("No major negative factor detected. General information: https://www.who.int/health-topics")

    return recommendations


# ------------------------------------------------------------
# SCHRITT 10: App Start
# ------------------------------------------------------------

create_database()

st.title("Biological Age Estimator")
st.subheader("Interactive health prototype with rule-based classification")

st.warning(
    "This is not a medical diagnostic tool. "
    "The biological age and risk profile are based on simple rule-based logic."
)

st.divider()


# ------------------------------------------------------------
# SCHRITT 11: Personal Profile
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
    st.metric("BMI category", bmi_category)

st.divider()


# ------------------------------------------------------------
# SCHRITT 12: Lifestyle Inputs
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
# SCHRITT 13: Stress Check
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
# SCHRITT 14: Health Dashboard
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
risk_profile = predict_risk_profile(age_gap)

st.header("4. Health Dashboard")

col9, col10, col11, col12 = st.columns(4)

with col9:
    st.metric("Real age", age)

with col10:
    st.metric("Biological age", round(biological_age, 1))

with col11:
    st.metric("Health score", round(health_score, 1))

with col12:
    st.metric("Risk profile", risk_profile)

st.write("Rule-based category:", profile_category)
st.write("Age gap:", round(age_gap, 1), "years")

if age_gap <= -3:
    st.success("Your biological age is clearly below your real age.")
elif age_gap <= 2:
    st.info("Your biological age is close to your real age.")
else:
    st.warning("Your biological age is above your real age. Improvement recommended.")

st.divider()


# ------------------------------------------------------------
# SCHRITT 15: Top 3 Priorities
# ------------------------------------------------------------

st.header("5. Top 3 Priorities")

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

top_priorities = get_top_priorities(impact_table)

if len(top_priorities) > 0:
    st.write("These factors increase your biological age the most:")
    st.write(top_priorities)
else:
    st.write("No negative priority detected.")

st.divider()


# ------------------------------------------------------------
# SCHRITT 16: Factor Impact Analysis
# ------------------------------------------------------------

st.header("6. Factor Impact Analysis")

if len(impact_table) > 0:
    st.write(impact_table)
    st.bar_chart(impact_table, x="Factor", y="Impact")
else:
    st.write("No factor changed the biological age in this prototype.")

st.divider()


# ------------------------------------------------------------
# SCHRITT 17: Smart What-if Simulator
# ------------------------------------------------------------

st.header("7. Smart What-if Simulator")

new_sleep, new_exercise, new_stress, new_sitting, new_steps = generate_smart_scenario(
    sleep_hours,
    exercise_days,
    stress_score,
    sitting_hours,
    daily_steps
)

scenario_table = pd.DataFrame({
    "Metric": ["Sleep", "Exercise days", "Stress score", "Sitting time", "Daily steps"],
    "Current": [sleep_hours, exercise_days, stress_score, sitting_hours, daily_steps],
    "Suggested": [new_sleep, new_exercise, new_stress, new_sitting, new_steps]
})

st.write(scenario_table)

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

improvement = biological_age - new_biological_age

col13, col14, col15 = st.columns(3)

with col13:
    st.metric("Current biological age", round(biological_age, 1))

with col14:
    st.metric("Suggested biological age", round(new_biological_age, 1))

with col15:
    st.metric("Improvement potential", round(improvement, 1))

st.divider()


# ------------------------------------------------------------
# SCHRITT 18: Personal Roadmap
# ------------------------------------------------------------

st.header("8. Personal Health Roadmap")

roadmap = generate_roadmap(top_priorities)

for step in roadmap:
    st.write("- " + step)

st.divider()


# ------------------------------------------------------------
# SCHRITT 19: Learning Resources
# ------------------------------------------------------------

st.header("9. Learning Resources")

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
# SCHRITT 20: Save and Track Progress
# ------------------------------------------------------------

st.header("10. Save and Track Progress")

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
        biological_age,
        risk_profile
    )
    st.success("Result saved.")

entries = load_entries()

if len(entries) > 0:
    st.subheader("Progress history")

    first_age = entries["biological_age"].iloc[0]
    latest_age = entries["biological_age"].iloc[-1]
    progress = latest_age - first_age

    col16, col17, col18 = st.columns(3)

    with col16:
        st.metric("First saved biological age", round(first_age, 1))

    with col17:
        st.metric("Latest biological age", round(latest_age, 1))

    with col18:
        st.metric("Progress", round(progress, 1))

    st.write(entries)
    st.line_chart(entries["biological_age"])

else:
    st.write("No saved results yet.")

if st.button("Clear history", key="clear_history_button"):
    clear_database()
    st.success("History deleted.")