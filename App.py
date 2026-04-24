import streamlit as st
import pandas as pd
import sqlite3


def create_database():
    connection = sqlite3.connect("biological_age_v4.db")
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


def save_entry(age, gender, height_cm, weight_kg, bmi, sleep_hours,
               exercise_days, heart_rate, stress_score, smoking,
               sitting_hours, daily_steps, biological_age):

    connection = sqlite3.connect("biological_age_v4.db")
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


def load_entries():
    connection = sqlite3.connect("biological_age_v4.db")
    data = pd.read_sql_query("SELECT * FROM entries", connection)
    connection.close()
    return data


def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m * height_m)
    return bmi


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


def generate_recommendations(sleep_hours, exercise_days, bmi, heart_rate,
                             stress_score, smoking, sitting_hours, daily_steps):

    recommendations = []

    if smoking == "Yes":
        recommendations.append("Smoking: strongest negative factor. Learn more: https://www.cdc.gov/tobacco/campaign/tips/quit-smoking/")

    if bmi >= 30:
        recommendations.append("BMI: obese range. Weight reduction could strongly improve the result. Learn more: https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight")
    elif bmi >= 25:
        recommendations.append("BMI: overweight range. Improving BMI could reduce the estimated biological age. Learn more: https://www.cdc.gov/healthy-weight-growth/index.html")
    elif bmi < 18.5:
        recommendations.append("BMI: underweight range. A healthier body weight could improve the result. Learn more: https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html")

    if sleep_hours < 6:
        recommendations.append("Sleep: low sleep duration. Try to move closer to 7–9 hours per night. Learn more: https://www.cdc.gov/sleep/")
    elif sleep_hours < 7:
        recommendations.append("Sleep: slightly below the recommended range. Try to add 30 minutes per night. Learn more: https://www.cdc.gov/sleep/about/index.html")

    if exercise_days == 0:
        recommendations.append("Exercise: no exercise days. Start with 1 or 2 short sessions per week. Learn more: https://www.who.int/news-room/fact-sheets/detail/physical-activity")
    elif exercise_days < 3:
        recommendations.append("Exercise: below 3 days per week. Try to add one additional exercise day. Learn more: https://www.cdc.gov/physical-activity-basics/guidelines/adults.html")

    if heart_rate > 80:
        recommendations.append("Resting heart rate: relatively high. Regular cardio could help. Learn more: https://www.cdc.gov/physical-activity-basics/benefits/index.html")

    if stress_score >= 18:
        recommendations.append("Stress: high perceived stress. Focus on control, recovery, breaks, and sleep. Learn more: https://www.who.int/news-room/questions-and-answers/item/stress")
    elif stress_score >= 12:
        recommendations.append("Stress: moderate perceived stress. Monitor overload, sleep, and concentration. Learn more: https://www.cdc.gov/mental-health/living-with/index.html")

    if sitting_hours > 9:
        recommendations.append("Sitting time: high sitting time. Add walking breaks and stand up more often. Learn more: https://www.who.int/news-room/fact-sheets/detail/physical-activity")

    if daily_steps < 4000:
        recommendations.append("Daily steps: low daily step count. Try to add 1,000 steps per day. Learn more: https://www.cdc.gov/physical-activity-basics/adding-adults/index.html")
    elif daily_steps < 7000:
        recommendations.append("Daily steps: moderate but improvable. Try to move closer to 7,000–10,000 daily steps. Learn more: https://www.cdc.gov/physical-activity-basics/adding-adults/index.html")

    if len(recommendations) == 0:
        recommendations.append("No major negative factor was detected. General health information: https://www.who.int/health-topics")

    return recommendations


create_database()

st.title("Biological Age Estimator")

st.warning(
    "This is not a medical diagnostic tool. "
    "It is a course project prototype based on simple Python rules, "
    "Streamlit inputs, SQLite storage and basic data visualization."
)

st.write("Use a dot for decimal time values. Example: 7.5 = 7 hours and 30 minutes.")

st.divider()

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

st.header("2. Biological Age Inputs")

st.info("The app uses the age and BMI from the BMI Calculator above.")

col3, col4 = st.columns(2)

with col3:
    sleep_hours = st.number_input(
        "Sleep per night in hours, e.g. 7.5",
        min_value=0.0,
        max_value=24.0,
        value=7.0,
        step=0.25
    )

    exercise_days = st.slider("Exercise days per week", 0, 7, 3)

    heart_rate = st.slider("Resting heart rate", 40, 120, 70)

with col4:
    sitting_hours = st.number_input(
        "Sitting time per day in hours, e.g. 8.5",
        min_value=0.0,
        max_value=24.0,
        value=7.0,
        step=0.25
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
st.write("Inspired by common perceived stress questionnaires. Answer from 0 = never to 4 = very often.")

stress_1 = st.slider("How often did you feel unable to control important things in your life?", 0, 4, 2)
stress_2 = st.slider("How often did you feel nervous or stressed?", 0, 4, 2)
stress_3 = st.slider("How often did you feel that difficulties were piling up?", 0, 4, 2)
stress_4 = st.slider("How often did you feel confident about handling personal problems?", 0, 4, 2)
stress_5 = st.slider("How often did you feel that things were going your way?", 0, 4, 2)
stress_6 = st.slider("How often did you feel you could not cope with all the things you had to do?", 0, 4, 2)

stress_score = stress_1 + stress_2 + stress_3 + (4 - stress_4) + (4 - stress_5) + stress_6

st.write("Stress score:", stress_score, "out of 24")

st.divider()

st.header("3. Result")

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

col5, col6 = st.columns(2)

with col5:
    st.metric("Real age", age)

with col6:
    st.metric("Estimated biological age", round(biological_age, 1))

st.write("Age gap:", round(age_gap, 1))

if age_gap > 0:
    st.write("Your biological age is higher than your real age.")
elif age_gap < 0:
    st.write("Your biological age is lower than your real age.")
else:
    st.write("Your biological age is equal to your real age.")

st.divider()

st.header("4. Recommendations")

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

st.header("5. Save Result")

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

st.header("6. Saved Results")

entries = load_entries()

if len(entries) > 0:
    st.write(entries)
    st.line_chart(entries["biological_age"])
else:
    st.write("No saved results yet.")