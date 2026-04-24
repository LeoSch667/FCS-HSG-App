import streamlit as st
import pandas as pd
import sqlite3


def create_database():
    connection = sqlite3.connect("biological_age.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            real_age INTEGER,
            sleep_hours REAL,
            exercise_days INTEGER,
            bmi REAL,
            heart_rate INTEGER,
            stress_level INTEGER,
            smoking TEXT,
            sitting_hours REAL,
            biological_age REAL
        )
    """)

    connection.commit()
    connection.close()


def save_entry(real_age, sleep_hours, exercise_days, bmi, heart_rate,
               stress_level, smoking, sitting_hours, biological_age):

    connection = sqlite3.connect("biological_age.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO entries (
            real_age, sleep_hours, exercise_days, bmi, heart_rate,
            stress_level, smoking, sitting_hours, biological_age
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        real_age, sleep_hours, exercise_days, bmi, heart_rate,
        stress_level, smoking, sitting_hours, biological_age
    ))

    connection.commit()
    connection.close()


def load_entries():
    connection = sqlite3.connect("biological_age.db")
    data = pd.read_sql_query("SELECT * FROM entries", connection)
    connection.close()
    return data


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

    if bmi >= 25:
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


create_database()

st.title("Biological Age Estimator")
st.write("Estimate your biological age based on simple lifestyle factors.")

st.header("User Inputs")

real_age = st.slider("Real age", 15, 80, 25)
sleep_hours = st.slider("Sleep per night", 0.0, 12.0, 7.0)
exercise_days = st.slider("Exercise days per week", 0, 7, 3)
bmi = st.slider("BMI", 15.0, 40.0, 23.0)
heart_rate = st.slider("Resting heart rate", 40, 120, 70)
stress_level = st.slider("Stress level", 1, 10, 5)
smoking = st.selectbox("Do you smoke?", ["No", "Yes"])
sitting_hours = st.slider("Sitting hours per day", 0.0, 16.0, 7.0)

biological_age = calculate_biological_age(
    real_age,
    sleep_hours,
    exercise_days,
    bmi,
    heart_rate,
    stress_level,
    smoking,
    sitting_hours
)

st.header("Result")

st.metric("Estimated biological age", biological_age)

age_gap = biological_age - real_age

if age_gap > 0:
    st.write("Your biological age is higher than your real age.")
elif age_gap < 0:
    st.write("Your biological age is lower than your real age.")
else:
    st.write("Your biological age is equal to your real age.")

st.write("Age gap:", age_gap)

if st.button("Save result", key="save_result_button"):
    save_entry(
        real_age,
        sleep_hours,
        exercise_days,
        bmi,
        heart_rate,
        stress_level,
        smoking,
        sitting_hours,
        biological_age
    )
    st.success("Result saved.")

st.header("Saved Results")

entries = load_entries()

if len(entries) > 0:
    st.write(entries)
    st.line_chart(entries["biological_age"])
else:
    st.write("No saved results yet.")

with st.expander("Implementation note"):
    st.write(
        "This is not a medical diagnostic tool. It is a course project prototype. "
        "The biological-age target is a transparent teaching index created from "
        "the same user-input features."
    )


st.write("Age gap:", age_gap)


if st.button("Save result"):
    save_entry(
        real_age,
        sleep_hours,
        exercise_days,
        bmi,
        heart_rate,
        stress_level,
        smoking,
        sitting_hours,
        biological_age
    )
    st.success("Result saved.")

st.header("Saved Results")

entries = load_entries()

if len(entries) > 0:
    st.write(entries)
    st.line_chart(entries["biological_age"])
else:
    st.write("No saved results yet.")