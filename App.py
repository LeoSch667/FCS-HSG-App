import streamlit as st
import pandas as pd
import sqlite3


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


def load_entries():
    connection = sqlite3.connect("biological_age_simple.db")
    data = pd.read_sql_query("SELECT * FROM entries", connection)
    connection.close()
    return data


def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m * height_m)
    return bmi


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


def generate_recommendations(sleep_hours, exercise_days, bmi, heart_rate,
                             stress_score, smoking, sitting_hours, weekly_steps):

    recommendations = []

    if smoking == "Yes":
        recommendations.append("Smoking: strongest negative factor. Learn more: https://www.cdc.gov/tobacco/campaign/tips/quit-smoking/")

    if bmi >= 30:
        recommendations.append("BMI: obese range. A gradual weight reduction could strongly improve the result. Learn more: https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight")
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
        recommendations.append("Resting heart rate: relatively high. Regular walking, cycling, or cardio could help. Learn more: https://www.cdc.gov/physical-activity-basics/benefits/index.html")

    if stress_score >= 8:
        recommendations.append("Stress: high stress score. Improve recovery, sleep, and daily breaks. Learn more: https://www.who.int/news-room/questions-and-answers/item/stress")
    elif stress_score >= 5:
        recommendations.append("Stress: moderate stress score. Monitor sleep and concentration. Learn more: https://www.cdc.gov/mental-health/living-with/index.html")

    if sitting_hours > 9:
        recommendations.append("Sitting time: high sitting time. Add walking breaks and stand up more often. Learn more: https://www.who.int/news-room/fact-sheets/detail/physical-activity")

    if weekly_steps < 30000:
        recommendations.append("Weekly steps: low step count. Try to add 1,000 steps per day. Learn more: https://www.cdc.gov/physical-activity-basics/adding-adults/index.html")
    elif weekly_steps < 50000:
        recommendations.append("Weekly steps: moderate step count. Try to move closer to 50,000 steps per week. Learn more: https://www.cdc.gov/physical-activity-basics/adding-adults/index.html")

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

st.write("Enter your basic information, estimate your biological age, and receive simple recommendations.")

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

st.subheader("BMI Result")
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
        "Sleep per night in hours",
        min_value=0.0,
        max_value=24.0,
        value=7.0,
        step=0.25
    )

    exercise_days = st.slider("Exercise days per week", 0, 7, 3)

    heart_rate = st.slider("Resting heart rate", 40, 120, 70)

with col4:
    sitting_hours = st.number_input(
        "Sitting time per day in hours",
        min_value=0.0,
        max_value=24.0,
        value=7.0,
        step=0.25
    )

    weekly_steps = st.number_input(
        "Average weekly steps",
        min_value=0,
        max_value=200000,
        value=50000,
        step=1000
    )

    smoking = st.selectbox("Do you smoke?", ["No", "Yes"])

st.subheader("Stress Questionnaire")
st.write("Answer each question from 0 to 4.")

col5, col6, col7 = st.columns(3)

with col5:
    overwhelmed = st.slider("Overwhelmed?", 0, 4, 2)

with col6:
    sleep_problem = st.slider("Stress affects sleep?", 0, 4, 2)

with col7:
    concentration_problem = st.slider("Stress affects concentration?", 0, 4, 2)

stress_score = overwhelmed + sleep_problem + concentration_problem

st.write("Stress score:", stress_score, "out of 12")

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
    weekly_steps
)

age_gap = biological_age - age

col8, col9 = st.columns(2)

with col8:
    st.metric("Real age", age)

with col9:
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
    weekly_steps
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
        weekly_steps,
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