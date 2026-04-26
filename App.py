import sqlite3

import pandas as pd
import streamlit as st
from sklearn.neighbors import KNeighborsClassifier


st.set_page_config(
    page_title="Biologischer Altersrechner",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def apply_app_styles():
    st.markdown(
        """
        <style>
        :root {
            --navy: #102a43;
            --navy-soft: #1f3c5b;
            --beige: #f5efe4;
            --beige-strong: #eadfce;
            --sky: #dcecf7;
            --sky-strong: #bfd9ea;
            --text-soft: #5f6c7b;
            --white: #ffffff;
        }

        .stApp {
            background: linear-gradient(180deg, #fbf8f2 0%, #f5efe4 100%);
            color: var(--navy);
        }

        .main .block-container {
            max-width: 1180px;
            padding-top: 1.2rem;
            padding-bottom: 4rem;
        }

        h1, h2, h3, label, .stMarkdown, .stText, p {
            color: var(--navy);
        }

        .hero-shell {
            background: var(--white);
            border: 1px solid rgba(16, 42, 67, 0.08);
            border-radius: 28px;
            padding: 1.25rem;
            box-shadow: 0 20px 45px rgba(16, 42, 67, 0.08);
            margin-bottom: 1.3rem;
        }

        .hero-copy {
            text-align: center;
            padding: 0.8rem 0 1rem 0;
        }

        .hero-kicker {
            color: var(--navy-soft);
            text-transform: uppercase;
            letter-spacing: 0.18em;
            font-size: 0.8rem;
            font-weight: 700;
        }

        .hero-title {
            font-size: 3.1rem;
            line-height: 1.05;
            font-weight: 800;
            margin: 0.6rem 0 0.7rem 0;
            color: var(--navy);
        }

        .hero-text {
            font-size: 1.05rem;
            color: var(--text-soft);
            max-width: 760px;
            margin: 0 auto;
            line-height: 1.7;
        }

        .hero-image {
            width: 100%;
            height: 420px;
            object-fit: cover;
            border-radius: 22px;
            display: block;
            margin-top: 0.3rem;
        }

        .notice-box {
            background: linear-gradient(135deg, var(--sky) 0%, var(--beige) 100%);
            border: 1px solid rgba(16, 42, 67, 0.08);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
            color: var(--navy);
        }

        .section-card {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(16, 42, 67, 0.08);
            border-radius: 24px;
            padding: 1.35rem 1.35rem 1rem 1.35rem;
            margin: 1rem 0;
            box-shadow: 0 14px 36px rgba(16, 42, 67, 0.06);
        }

        .section-topline {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .section-number {
            width: 44px;
            height: 44px;
            border-radius: 999px;
            background: var(--navy);
            color: var(--beige);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1rem;
            flex-shrink: 0;
        }

        .section-kicker {
            color: var(--navy-soft);
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-size: 0.75rem;
            font-weight: 800;
            margin-bottom: 0.35rem;
        }

        .section-title {
            font-size: 1.8rem;
            line-height: 1.15;
            font-weight: 800;
            color: var(--navy);
            margin: 0;
        }

        .section-text {
            color: var(--text-soft);
            margin-top: 0.45rem;
            line-height: 1.65;
            max-width: 760px;
        }

        [data-testid="stMetric"] {
            background: linear-gradient(180deg, #ffffff 0%, #f8f3ea 100%);
            border: 1px solid rgba(16, 42, 67, 0.08);
            border-radius: 18px;
            padding: 0.9rem 1rem;
        }

        .stButton > button {
            background: var(--navy);
            color: #fff8ef;
            border: none;
            border-radius: 999px;
            padding: 0.6rem 1.2rem;
            font-weight: 700;
        }

        .stButton > button:hover {
            background: var(--navy-soft);
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
        <div class="hero-shell">
            <div class="hero-copy">
                <div class="hero-kicker">Persönlicher Gesundheitsprototyp</div>
                <div class="hero-title">Biologischer Altersrechner</div>
                <div class="hero-text">
                    Entdecke, wie Lebensstil, Stress, Bewegung und Regeneration dein biologisches Altersprofil beeinflussen.
                    Zusätzlich nutzt dieser Prototyp ein einfaches KNN-Modell, um ein Risikoprofil vorherzusagen. Test test test
                </div>
            </div>
            <img
                class="hero-image"
                src="https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=1600&q=80"
                alt="Gesundheitsmotiv"
            />
        </div>
        """,
        unsafe_allow_html=True,
    )


def open_section(number, kicker, title, description):
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-topline">
                <div>
                    <div class="section-kicker">{kicker}</div>
                    <h2 class="section-title">{title}</h2>
                    <div class="section-text">{description}</div>
                </div>
                <div class="section-number">{number}</div>
            </div>
        """,
        unsafe_allow_html=True,
    )


def close_section():
    st.markdown("</div>", unsafe_allow_html=True)


def create_database():
    connection = sqlite3.connect("biological_age_knn.db")
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
            rule_based_risk TEXT,
            knn_risk TEXT
        )
        """
    )

    connection.commit()
    connection.close()


def save_entry(
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
    rule_based_risk,
    knn_risk,
):
    connection = sqlite3.connect("biological_age_knn.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO entries (
            age, gender, height_cm, weight_kg, bmi, sleep_hours,
            exercise_days, heart_rate, stress_score, smoking,
            sitting_hours, daily_steps, biological_age,
            rule_based_risk, knn_risk
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
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
            rule_based_risk,
            knn_risk,
        ),
    )

    connection.commit()
    connection.close()


def load_entries():
    connection = sqlite3.connect("biological_age_knn.db")
    data = pd.read_sql_query("SELECT * FROM entries", connection)
    connection.close()
    return data


def clear_database():
    connection = sqlite3.connect("biological_age_knn.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM entries")
    connection.commit()
    connection.close()


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


def calculate_biological_age(
    age,
    sleep_hours,
    exercise_days,
    bmi,
    heart_rate,
    stress_score,
    smoking,
    sitting_hours,
    daily_steps,
):
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


def predict_risk_profile(age_gap):
    if age_gap <= 0:
        return "Niedriges Risiko"
    if age_gap <= 5:
        return "Mittleres Risiko"
    return "Hohes Risiko"


def train_knn_model():
    training_data = [
        [25, 7.5, 4, 22, 60, 6, 0, 5, 12000],
        [30, 8.0, 3, 23, 62, 7, 0, 6, 10000],
        [40, 7.0, 3, 24, 65, 8, 0, 7, 9000],
        [35, 6.5, 2, 27, 75, 12, 0, 8, 6500],
        [45, 6.0, 1, 28, 78, 14, 0, 9, 5500],
        [50, 6.5, 2, 29, 80, 13, 0, 9, 6000],
        [45, 5.0, 0, 31, 90, 20, 1, 11, 3000],
        [55, 5.5, 0, 34, 88, 19, 1, 10, 2500],
        [38, 5.0, 1, 32, 85, 18, 1, 12, 3500],
    ]

    training_labels = [
        "Niedriges Risiko",
        "Niedriges Risiko",
        "Niedriges Risiko",
        "Mittleres Risiko",
        "Mittleres Risiko",
        "Mittleres Risiko",
        "Hohes Risiko",
        "Hohes Risiko",
        "Hohes Risiko",
    ]

    model = KNeighborsClassifier(n_neighbors=3)
    model.fit(training_data, training_labels)

    return model


def predict_knn_risk_profile(
    model,
    age,
    sleep_hours,
    exercise_days,
    bmi,
    heart_rate,
    stress_score,
    smoking,
    sitting_hours,
    daily_steps,
):
    if smoking == "Ja":
        smoking_value = 1
    else:
        smoking_value = 0

    user_data = [
        [
            age,
            sleep_hours,
            exercise_days,
            bmi,
            heart_rate,
            stress_score,
            smoking_value,
            sitting_hours,
            daily_steps,
        ]
    ]

    prediction = model.predict(user_data)
    return prediction[0]


def calculate_health_score(age_gap):
    score = 100 - age_gap * 5

    if score > 100:
        score = 100

    if score < 0:
        score = 0

    return score


def get_profile_category(age_gap):
    if age_gap <= -3:
        return "Ausgezeichnetes Profil"
    if age_gap <= 2:
        return "Ausgeglichenes Profil"
    if age_gap <= 7:
        return "Verbesserung empfohlen"
    return "Hohes Verbesserungspotenzial"


def get_factor_impacts(
    sleep_hours,
    exercise_days,
    bmi,
    heart_rate,
    stress_score,
    smoking,
    sitting_hours,
    daily_steps,
):
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


def get_top_priorities(impact_table):
    negative_impacts = impact_table[impact_table["Einfluss"] > 0]
    negative_impacts = negative_impacts.sort_values("Einfluss", ascending=False)
    return negative_impacts.head(3)


def generate_smart_scenario(
    sleep_hours,
    exercise_days,
    stress_score,
    sitting_hours,
    daily_steps,
):
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


def generate_roadmap(top_priorities):
    roadmap = []

    if len(top_priorities) == 0:
        roadmap.append("Woche 1: Behalte deine aktuellen gesunden Gewohnheiten bei.")
        roadmap.append("Woche 2: Beobachte deine Werte weiterhin bewusst.")
        roadmap.append("Woche 3: Verbessere gezielt eine kleine Gewohnheit.")
        roadmap.append("Woche 4: Gib deine Werte erneut ein und vergleiche das Ergebnis.")
        return roadmap

    counter = 1

    for _, row in top_priorities.iterrows():
        factor = row["Faktor"]

        if factor == "Rauchen":
            roadmap.append(f"Woche {counter}: Konzentriere dich darauf, Rauchauslöser zu reduzieren.")
        elif factor == "BMI im Adipositas-Bereich" or factor == "BMI im Übergewichtsbereich":
            roadmap.append(f"Woche {counter}: Arbeite an gewichtsspezifischen Gewohnheiten und mehr Alltagsbewegung.")
        elif factor == "Zu wenig Schlaf":
            roadmap.append(f"Woche {counter}: Verbessere gezielt deine Schlafdauer.")
        elif factor == "Keine Bewegung":
            roadmap.append(f"Woche {counter}: Ergänze ein oder zwei kurze Bewegungseinheiten.")
        elif factor == "Hoher Stress":
            roadmap.append(f"Woche {counter}: Reduziere Stress durch Pausen, Planung und besseren Schlaf.")
        elif factor == "Hohe Sitzzeit":
            roadmap.append(f"Woche {counter}: Unterbrich langes Sitzen mit kurzen Gehpausen.")
        elif factor == "Wenige tägliche Schritte":
            roadmap.append(f"Woche {counter}: Erhöhe deine täglichen Schritte um 1.000.")
        elif factor == "Hoher Ruhepuls":
            roadmap.append(f"Woche {counter}: Ergänze moderates Ausdauertraining.")
        else:
            roadmap.append(f"Woche {counter}: Verbessere gezielt den Bereich {factor}.")

        counter += 1

    roadmap.append("Woche 4: Gib deine Werte erneut ein und vergleiche deinen Fortschritt.")
    return roadmap


def generate_recommendations(
    sleep_hours,
    exercise_days,
    bmi,
    heart_rate,
    stress_score,
    smoking,
    sitting_hours,
    daily_steps,
):
    recommendations = []

    if smoking == "Ja":
        recommendations.append(
            "Rauchen: stärkster negativer Faktor. Mehr dazu: "
            "https://www.cdc.gov/tobacco/campaign/tips/quit-smoking/"
        )

    if bmi >= 30:
        recommendations.append(
            "BMI: Bereich Adipositas. Mehr dazu: "
            "https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight"
        )
    elif bmi >= 25:
        recommendations.append(
            "BMI: Bereich Übergewicht. Mehr dazu: "
            "https://www.cdc.gov/healthy-weight-growth/index.html"
        )
    elif bmi < 18.5:
        recommendations.append(
            "BMI: Bereich Untergewicht. Mehr dazu: "
            "https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html"
        )

    if sleep_hours < 7:
        recommendations.append(
            "Schlaf: versuche, näher an 7 bis 9 Stunden pro Nacht zu kommen. Mehr dazu: "
            "https://www.cdc.gov/sleep/"
        )

    if exercise_days < 3:
        recommendations.append(
            "Bewegung: versuche mindestens 3 aktive Tage pro Woche zu erreichen. Mehr dazu: "
            "https://www.who.int/news-room/fact-sheets/detail/physical-activity"
        )

    if heart_rate > 80:
        recommendations.append(
            "Ruhepuls: regelmäßiges Ausdauertraining könnte helfen. Mehr dazu: "
            "https://www.cdc.gov/physical-activity-basics/benefits/index.html"
        )

    if stress_score >= 12:
        recommendations.append(
            "Stress: dein wahrgenommenes Stressniveau ist erhöht. Mehr dazu: "
            "https://www.who.int/news-room/questions-and-answers/item/stress"
        )

    if sitting_hours > 9:
        recommendations.append(
            "Sitzzeit: baue regelmäßige Gehpausen ein. Mehr dazu: "
            "https://www.who.int/news-room/fact-sheets/detail/physical-activity"
        )

    if daily_steps < 7000:
        recommendations.append(
            "Tägliche Schritte: erhöhe deine Bewegung schrittweise. Mehr dazu: "
            "https://www.cdc.gov/physical-activity-basics/adding-adults/index.html"
        )

    if len(recommendations) == 0:
        recommendations.append(
            "Keine großen negativen Faktoren erkannt. Allgemeine Informationen: "
            "https://www.who.int/health-topics"
        )

    return recommendations


create_database()
knn_model = train_knn_model()

apply_app_styles()
render_hero()

st.markdown(
    """
    <div class="notice-box">
        Dies ist kein medizinisches Diagnoseinstrument. Das biologische Alter basiert auf einfacher regelbasierter Logik.
        Das KNN-Risikoprofil ist ein Machine-Learning-Prototyp mit synthetischen Trainingsbeispielen und dient nur zur
        Veranschaulichung der im Kurs behandelten k-nearest-neighbor-Methode.
    </div>
    """,
    unsafe_allow_html=True,
)

open_section(
    "1",
    "Profil",
    "Persönliches Profil",
    "Starte mit den grundlegenden Körperdaten. Diese Werte nutzt die App, um den BMI zu berechnen und deine Basis zu bestimmen.",
)

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
    st.metric("Berechneter BMI", round(bmi, 2))

with col4:
    st.metric("BMI-Kategorie", bmi_category)

close_section()

open_section(
    "2",
    "Lebensstil",
    "Lebensstil-Eingaben",
    "Erfasse Gewohnheiten, die Regeneration, Bewegung und deine tägliche körperliche Belastung beeinflussen.",
)

col5, col6 = st.columns(2)

with col5:
    sleep_hours = st.number_input(
        "Schlaf pro Nacht in Stunden",
        min_value=0.0,
        max_value=24.0,
        value=7.50,
        step=0.25,
        format="%.2f",
    )
    exercise_days = st.slider("Bewegungstage pro Woche", 0, 7, 3)
    heart_rate = st.slider("Ruhepuls", 40, 120, 70)

with col6:
    sitting_hours = st.number_input(
        "Sitzzeit pro Tag in Stunden",
        min_value=0.0,
        max_value=24.0,
        value=7.50,
        step=0.25,
        format="%.2f",
    )
    daily_steps = st.number_input(
        "Durchschnittliche Schritte pro Tag",
        min_value=0,
        max_value=25000,
        value=7000,
        step=500,
    )
    smoking = st.selectbox("Rauchst du?", ["Nein", "Ja"])

close_section()

open_section(
    "3",
    "Stress",
    "Stress-Check",
    "Beantworte den kurzen Fragebogen auf einer Skala von 0 bis 4. Der Gesamtwert fließt in die Schätzung des biologischen Alters ein.",
)

st.write("Antwortskala: 0 = nie bis 4 = sehr oft.")

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

close_section()

biological_age = calculate_biological_age(
    age,
    sleep_hours,
    exercise_days,
    bmi,
    heart_rate,
    stress_score,
    smoking,
    sitting_hours,
    daily_steps,
)

age_gap = biological_age - age
health_score = calculate_health_score(age_gap)
profile_category = get_profile_category(age_gap)

rule_based_risk = predict_risk_profile(age_gap)

knn_risk = predict_knn_risk_profile(
    knn_model,
    age,
    sleep_hours,
    exercise_days,
    bmi,
    heart_rate,
    stress_score,
    smoking,
    sitting_hours,
    daily_steps,
)

open_section(
    "4",
    "Dashboard",
    "Gesundheits-Dashboard",
    "Sieh dein aktuelles Alter, das geschätzte biologische Alter, den Health Score, das regelbasierte Risiko und das KNN-Risikoprofil auf einen Blick.",
)

col9, col10, col11, col12, col13 = st.columns(5)

with col9:
    st.metric("Reales Alter", age)

with col10:
    st.metric("Biologisches Alter", round(biological_age, 1))

with col11:
    st.metric("Health Score", round(health_score, 1))

with col12:
    st.metric("Regelbasiertes Risiko", rule_based_risk)

with col13:
    st.metric("KNN-Risiko", knn_risk)

st.write("Regelbasierte Kategorie:", profile_category)
st.write("Altersdifferenz:", round(age_gap, 1), "Jahre")

if age_gap <= -3:
    st.success("Dein biologisches Alter liegt deutlich unter deinem realen Alter.")
elif age_gap <= 2:
    st.info("Dein biologisches Alter liegt nahe an deinem realen Alter.")
else:
    st.warning("Dein biologisches Alter liegt über deinem realen Alter. Verbesserung empfohlen.")

close_section()

open_section(
    "5",
    "Machine Learning",
    "KNN-Modell-Erklärung",
    "Das KNN-Modell vergleicht dein Profil mit einfachen Trainingsbeispielen und ordnet dich der ähnlichsten Risikogruppe zu.",
)

st.write("Verwendete Eingabewerte für KNN:")
knn_input_table = pd.DataFrame(
    {
        "Variable": [
            "Alter",
            "Schlaf",
            "Bewegungstage",
            "BMI",
            "Ruhepuls",
            "Stresswert",
            "Rauchen",
            "Sitzzeit",
            "Tägliche Schritte",
        ],
        "Wert": [
            age,
            sleep_hours,
            exercise_days,
            round(bmi, 2),
            heart_rate,
            stress_score,
            smoking,
            sitting_hours,
            daily_steps,
        ],
    }
)

st.write(knn_input_table)

close_section()

open_section(
    "6",
    "Fokus",
    "Top-3-Prioritäten",
    "Diese Faktoren wirken sich aktuell am stärksten negativ aus und sind die sinnvollsten Hebel für Verbesserungen.",
)

impact_table = get_factor_impacts(
    sleep_hours,
    exercise_days,
    bmi,
    heart_rate,
    stress_score,
    smoking,
    sitting_hours,
    daily_steps,
)

top_priorities = get_top_priorities(impact_table)

if len(top_priorities) > 0:
    st.write("Diese Faktoren erhöhen dein biologisches Alter aktuell am stärksten:")
    st.write(top_priorities)
else:
    st.write("Keine negativen Prioritäten erkannt.")

close_section()

open_section(
    "7",
    "Analyse",
    "Einflussanalyse der Faktoren",
    "Hier siehst du, wie jeder Faktor die regelbasierte Altersschätzung verändert.",
)

if len(impact_table) > 0:
    st.write(impact_table)
    st.bar_chart(impact_table, x="Faktor", y="Einfluss")
else:
    st.write("In diesem Prototyp verändert aktuell kein Faktor das biologische Alter.")

close_section()

open_section(
    "8",
    "Szenario",
    "Smart-What-if-Simulator",
    "Vergleiche deine aktuellen Werte mit einem ausgeglicheneren Lebensstil-Szenario.",
)

new_sleep, new_exercise, new_stress, new_sitting, new_steps = generate_smart_scenario(
    sleep_hours,
    exercise_days,
    stress_score,
    sitting_hours,
    daily_steps,
)

scenario_table = pd.DataFrame(
    {
        "Kennzahl": [
            "Schlaf",
            "Bewegungstage",
            "Stresswert",
            "Sitzzeit",
            "Tägliche Schritte",
        ],
        "Aktuell": [sleep_hours, exercise_days, stress_score, sitting_hours, daily_steps],
        "Vorgeschlagen": [new_sleep, new_exercise, new_stress, new_sitting, new_steps],
    }
)

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
    new_steps,
)

improvement = biological_age - new_biological_age

col14, col15, col16 = st.columns(3)

with col14:
    st.metric("Aktuelles biologisches Alter", round(biological_age, 1))

with col15:
    st.metric("Biologisches Alter im Szenario", round(new_biological_age, 1))

with col16:
    st.metric("Verbesserungspotenzial", round(improvement, 1))

close_section()

open_section(
    "9",
    "Roadmap",
    "Persönliche Gesundheits-Roadmap",
    "Übersetze die wichtigsten Belastungsfaktoren in einen konkreten Vier-Wochen-Plan.",
)

roadmap = generate_roadmap(top_priorities)

for step in roadmap:
    st.write("- " + step)

close_section()

open_section(
    "10",
    "Ressourcen",
    "Weiterführende Informationen",
    "Nutze diese Hinweise und Links, um die wichtigsten Einflussfaktoren hinter deinem Ergebnis besser zu verstehen.",
)

recommendations = generate_recommendations(
    sleep_hours,
    exercise_days,
    bmi,
    heart_rate,
    stress_score,
    smoking,
    sitting_hours,
    daily_steps,
)

for recommendation in recommendations:
    st.write("- " + recommendation)

close_section()

open_section(
    "11",
    "Tracking",
    "Speichern und Fortschritt verfolgen",
    "Speichere Ergebnisse lokal in der Datenbank und beobachte, wie sich dein biologisches Alter über mehrere Eingaben verändert.",
)

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
        rule_based_risk,
        knn_risk,
    )
    st.success("Ergebnis gespeichert.")

entries = load_entries()

if len(entries) > 0:
    st.subheader("Verlauf")

    first_age = entries["biological_age"].iloc[0]
    latest_age = entries["biological_age"].iloc[-1]
    progress = latest_age - first_age

    col17, col18, col19 = st.columns(3)

    with col17:
        st.metric("Erstes gespeichertes biologisches Alter", round(first_age, 1))

    with col18:
        st.metric("Letztes gespeichertes biologisches Alter", round(latest_age, 1))

    with col19:
        st.metric("Veränderung", round(progress, 1))

    st.write(entries)
    st.line_chart(entries["biological_age"])
else:
    st.write("Noch keine gespeicherten Ergebnisse vorhanden.")

if st.button("Verlauf löschen", key="clear_history_button"):
    clear_database()
    st.success("Verlauf gelöscht.")

close_section()
