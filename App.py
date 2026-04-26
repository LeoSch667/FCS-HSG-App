import sqlite3

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Biologischer Altersrechner",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    return weight_kg / (height_m * height_m)


def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Untergewicht"
    if bmi < 25:
        return "Normalgewicht"
    if bmi < 30:
        return "Übergewicht"
    return "Adipositas"


def calculate_biological_age(age, sleep_hours, exercise_days, bmi, heart_rate, stress_score, smoking, sitting_hours, daily_steps):
    biological_age = age

    if sleep_hours < 6:
        biological_age += 4
    elif 7 <= sleep_hours <= 9:
        biological_age -= 2

    if exercise_days == 0:
        biological_age += 4
    elif exercise_days >= 3:
        biological_age -= 3

    if bmi >= 30:
        biological_age += 6
    elif bmi >= 25:
        biological_age += 3
    elif bmi < 18.5:
        biological_age += 2

    if heart_rate > 80:
        biological_age += 3
    elif heart_rate < 60:
        biological_age -= 1

    if stress_score >= 18:
        biological_age += 4
    elif stress_score <= 8:
        biological_age -= 1

    if smoking == "Ja":
        biological_age += 7

    if sitting_hours > 9:
        biological_age += 3

    if daily_steps < 4000:
        biological_age += 3
    elif daily_steps >= 10000:
        biological_age -= 2

    return biological_age


def predict_rule_based_risk(age_gap):
    if age_gap <= 0:
        return "Niedriges Risiko"
    if age_gap <= 5:
        return "Mittleres Risiko"
    return "Hohes Risiko"


def calculate_health_score(age_gap):
    score = 100 - age_gap * 5
    return max(0, min(100, score))


def get_profile_category(age_gap):
    if age_gap <= -3:
        return "Ausgezeichnetes Profil"
    if age_gap <= 2:
        return "Ausgeglichenes Profil"
    if age_gap <= 7:
        return "Verbesserung empfohlen"
    return "Hohes Verbesserungspotenzial"


def create_database():
    connection = sqlite3.connect("biological_age.db")
    cursor = connection.cursor()

    cursor.execute(
        """
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
        """
    )

    connection.commit()
    connection.close()


def save_entry(age, gender, height_cm, weight_kg, bmi, sleep_hours, exercise_days, heart_rate, stress_score, smoking, sitting_hours, daily_steps, biological_age, risk_profile):
    connection = sqlite3.connect("biological_age.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO entries (
            age, gender, height_cm, weight_kg, bmi, sleep_hours,
            exercise_days, heart_rate, stress_score, smoking,
            sitting_hours, daily_steps, biological_age, risk_profile
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            age, gender, height_cm, weight_kg, bmi, sleep_hours,
            exercise_days, heart_rate, stress_score, smoking,
            sitting_hours, daily_steps, biological_age, risk_profile
        ),
    )

    connection.commit()
    connection.close()


def load_entries():
    connection = sqlite3.connect("biological_age.db")
    data = pd.read_sql_query("SELECT * FROM entries", connection)
    connection.close()
    return data


def clear_database():
    connection = sqlite3.connect("biological_age.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM entries")
    connection.commit()
    connection.close()


def get_factor_impacts(sleep_hours, exercise_days, bmi, heart_rate, stress_score, smoking, sitting_hours, daily_steps):
    factors = []
    impacts = []

    if smoking == "Ja":
        factors.append("Rauchen")
        impacts.append(7)

    if bmi >= 30:
        factors.append("BMI im Adipositas-Bereich")
        impacts.append(6)
    elif bmi >= 25:
        factors.append("BMI im Übergewichtsbereich")
        impacts.append(3)
    elif bmi < 18.5:
        factors.append("BMI im Untergewichtsbereich")
        impacts.append(2)

    if sleep_hours < 6:
        factors.append("Zu wenig Schlaf")
        impacts.append(4)
    elif 7 <= sleep_hours <= 9:
        factors.append("Guter Schlaf")
        impacts.append(-2)

    if exercise_days == 0:
        factors.append("Keine Bewegung")
        impacts.append(4)
    elif exercise_days >= 3:
        factors.append("Regelmäßige Bewegung")
        impacts.append(-3)

    if heart_rate > 80:
        factors.append("Hoher Ruhepuls")
        impacts.append(3)
    elif heart_rate < 60:
        factors.append("Niedriger Ruhepuls")
        impacts.append(-1)

    if stress_score >= 18:
        factors.append("Hoher Stress")
        impacts.append(4)
    elif stress_score <= 8:
        factors.append("Niedriger Stress")
        impacts.append(-1)

    if sitting_hours > 9:
        factors.append("Hohe Sitzzeit")
        impacts.append(3)

    if daily_steps < 4000:
        factors.append("Wenige tägliche Schritte")
        impacts.append(3)
    elif daily_steps >= 10000:
        factors.append("Viele tägliche Schritte")
        impacts.append(-2)

    return pd.DataFrame({"Faktor": factors, "Einfluss": impacts})


def generate_recommendations(sleep_hours, exercise_days, bmi, heart_rate, stress_score, smoking, sitting_hours, daily_steps):
    recommendations = []

    if smoking == "Ja":
        recommendations.append("Rauchen reduzieren oder beenden: Rauchen ist einer der stärksten negativen Faktoren.")

    if bmi >= 25:
        recommendations.append("BMI verbessern: mehr Bewegung, bessere Ernährung und regelmäßige Gewichtskontrolle.")
    elif bmi < 18.5:
        recommendations.append("BMI stabilisieren: gesunde Gewichtszunahme und ausreichende Nährstoffzufuhr prüfen.")

    if sleep_hours < 7:
        recommendations.append("Schlaf verbessern: Zielwert 7 bis 9 Stunden pro Nacht.")

    if exercise_days < 3:
        recommendations.append("Bewegung erhöhen: mindestens 3 aktive Tage pro Woche anstreben.")

    if heart_rate > 80:
        recommendations.append("Ruhepuls senken: regelmäßiges moderates Ausdauertraining kann helfen.")

    if stress_score >= 12:
        recommendations.append("Stress reduzieren: Pausen, Planung, Schlaf und bewusste Erholung verbessern.")

    if sitting_hours > 9:
        recommendations.append("Sitzzeit reduzieren: regelmäßige Gehpausen einbauen.")

    if daily_steps < 7000:
        recommendations.append("Schritte erhöhen: täglich schrittweise Richtung 8'000 bis 10'000 Schritte gehen.")

    if not recommendations:
        recommendations.append("Keine größeren negativen Faktoren erkannt. Bestehende Gewohnheiten beibehalten.")

    return recommendations


def generate_smart_scenario(sleep_hours, exercise_days, stress_score, sitting_hours, daily_steps):
    new_sleep = 7.5 if sleep_hours < 7 else sleep_hours
    new_exercise = 3 if exercise_days < 3 else exercise_days
    new_stress = 10 if stress_score > 12 else stress_score
    new_sitting = 7 if sitting_hours > 8 else sitting_hours
    new_steps = 8000 if daily_steps < 7000 else daily_steps

    return new_sleep, new_exercise, new_stress, new_sitting, new_steps


create_database()

st.title("Biologischer Altersrechner")
st.write(
    "Dieser Prototyp berechnet ein geschätztes biologisches Alter anhand einfacher regelbasierter Logik. "
    "Er ist kein medizinisches Diagnoseinstrument."
)

st.header("1. Persönliches Profil")

col1, col2 = st.columns(2)

with col1:
    gender = st.selectbox("Geschlecht", ["Männlich", "Weiblich"])
    age = st.slider("Alter", 10, 100, 25)

with col2:
    height_cm = st.slider("Größe in cm", 100, 220, 175)
    weight_kg = st.slider("Gewicht in kg", 30, 160, 70)

bmi = calculate_bmi(weight_kg, height_cm)
bmi_category = get_bmi_category(bmi)

col3, col4 = st.columns(2)

with col3:
    st.metric("BMI", round(bmi, 2))

with col4:
    st.metric("BMI-Kategorie", bmi_category)

st.header("2. Lebensstil")

col5, col6 = st.columns(2)

with col5:
    sleep_hours = st.number_input("Schlaf pro Nacht in Stunden", 0.0, 24.0, 7.5, 0.25)
    exercise_days = st.slider("Bewegungstage pro Woche", 0, 7, 3)
    heart_rate = st.slider("Ruhepuls", 40, 120, 70)

with col6:
    sitting_hours = st.number_input("Sitzzeit pro Tag in Stunden", 0.0, 24.0, 7.5, 0.25)
    daily_steps = st.number_input("Durchschnittliche Schritte pro Tag", 0, 25000, 7000, 500)
    smoking = st.selectbox("Rauchst du?", ["Nein", "Ja"])

st.header("3. Stress-Check")

st.write("Antwortskala: 0 = nie, 4 = sehr oft")

col7, col8 = st.columns(2)

with col7:
    stress_1 = st.slider("Konntest du wichtige Dinge nicht kontrollieren?", 0, 4, 2)
    stress_2 = st.slider("Warst du nervös oder gestresst?", 0, 4, 2)
    stress_3 = st.slider("Hatten sich Schwierigkeiten angehäuft?", 0, 4, 2)

with col8:
    stress_4 = st.slider("Konntest du Probleme selbstbewusst angehen?", 0, 4, 2)
    stress_5 = st.slider("Liefen Dinge so, wie du es wolltest?", 0, 4, 2)
    stress_6 = st.slider("Konntest du Aufgaben kaum bewältigen?", 0, 4, 2)

stress_score = stress_1 + stress_2 + stress_3 + (4 - stress_4) + (4 - stress_5) + stress_6
st.metric("Stresswert", f"{stress_score} / 24")

biological_age = calculate_biological_age(
    age, sleep_hours, exercise_days, bmi, heart_rate,
    stress_score, smoking, sitting_hours, daily_steps
)

age_gap = biological_age - age
health_score = calculate_health_score(age_gap)
risk_profile = predict_rule_based_risk(age_gap)
profile_category = get_profile_category(age_gap)

st.header("4. Gesundheits-Dashboard")

col9, col10, col11, col12 = st.columns(4)

with col9:
    st.metric("Reales Alter", age)

with col10:
    st.metric("Biologisches Alter", round(biological_age, 1))

with col11:
    st.metric("Health Score", round(health_score, 1))

with col12:
    st.metric("Risikoprofil", risk_profile)

st.write("Profilkategorie:", profile_category)
st.write("Altersdifferenz:", round(age_gap, 1), "Jahre")

if age_gap <= -3:
    st.success("Dein biologisches Alter liegt deutlich unter deinem realen Alter.")
elif age_gap <= 2:
    st.info("Dein biologisches Alter liegt nahe an deinem realen Alter.")
else:
    st.warning("Dein biologisches Alter liegt über deinem realen Alter. Verbesserung empfohlen.")

st.header("5. Einflussanalyse")

impact_table = get_factor_impacts(
    sleep_hours, exercise_days, bmi, heart_rate,
    stress_score, smoking, sitting_hours, daily_steps
)

if len(impact_table) > 0:
    st.write(impact_table)
    st.bar_chart(impact_table, x="Faktor", y="Einfluss")
else:
    st.write("Keine relevanten Einflussfaktoren erkannt.")

st.header("6. Smart-What-if-Simulator")

new_sleep, new_exercise, new_stress, new_sitting, new_steps = generate_smart_scenario(
    sleep_hours, exercise_days, stress_score, sitting_hours, daily_steps
)

scenario_table = pd.DataFrame(
    {
        "Kennzahl": ["Schlaf", "Bewegungstage", "Stresswert", "Sitzzeit", "Tägliche Schritte"],
        "Aktuell": [sleep_hours, exercise_days, stress_score, sitting_hours, daily_steps],
        "Vorgeschlagen": [new_sleep, new_exercise, new_stress, new_sitting, new_steps],
    }
)

st.write(scenario_table)

new_biological_age = calculate_biological_age(
    age, new_sleep, new_exercise, bmi, heart_rate,
    new_stress, smoking, new_sitting, new_steps
)

improvement = biological_age - new_biological_age

col13, col14, col15 = st.columns(3)

with col13:
    st.metric("Aktuelles biologisches Alter", round(biological_age, 1))

with col14:
    st.metric("Szenario-Alter", round(new_biological_age, 1))

with col15:
    st.metric("Verbesserungspotenzial", round(improvement, 1))

st.header("7. Empfehlungen")

recommendations = generate_recommendations(
    sleep_hours, exercise_days, bmi, heart_rate,
    stress_score, smoking, sitting_hours, daily_steps
)

for recommendation in recommendations:
    st.write("- " + recommendation)

st.header("8. Verlauf speichern")

if st.button("Resultat speichern"):
    save_entry(
        age, gender, height_cm, weight_kg, bmi, sleep_hours,
        exercise_days, heart_rate, stress_score, smoking,
        sitting_hours, daily_steps, biological_age, risk_profile
    )
    st.success("Ergebnis gespeichert.")

entries = load_entries()

if len(entries) > 0:
    st.subheader("Gespeicherter Verlauf")
    st.write(entries)
    st.line_chart(entries["biological_age"])

if st.button("Verlauf löschen"):
    clear_database()
    st.success("Verlauf gelöscht.")
