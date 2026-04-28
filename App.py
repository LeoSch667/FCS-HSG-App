import sqlite3
import hashlib
import requests
import numpy as np
from datetime import datetime

import pandas as pd
import streamlit as st

# ===============================
# 📊 BIOLOGISCHER ALTERSRECHNER MIT USER-TRACKING
# ===============================
# Diese App kombiniert:
# 1. Regelbasierte Berechnung des biologischen Alters
# 2. User-Management mit Passwort-Schutz
# 3. NHANES-Vergleiche mit CDC-Referenzdaten
# 4. SQLite-Datenbank für persönliches Tracking
# ===============================
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
                    Dieser Prototyp nutzt eine einfache regelbasierte Logik, um dein biologisches Alter und dein Risikoprofil zu schätzen.
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
    connection = sqlite3.connect("biological_age.db")
    cursor = connection.cursor()

    # Users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Entries table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """
    )

    # NHANES reference data table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS nhanes_reference (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age_group TEXT,
            gender TEXT,
            avg_bmi REAL,
            avg_heart_rate INTEGER,
            avg_sleep_hours REAL,
            avg_daily_steps INTEGER,
            data_source TEXT
        )
        """
    )

    # Check if NHANES reference data already exists
    cursor.execute("SELECT COUNT(*) FROM nhanes_reference")
    if cursor.fetchone()[0] == 0:
        # Insert sample NHANES reference data
        nhanes_data = [
            ("20-29", "Männlich", 27.2, 68, 6.8, 8200, "NHANES 2017-2020"),
            ("20-29", "Weiblich", 26.8, 72, 7.0, 7900, "NHANES 2017-2020"),
            ("30-39", "Männlich", 28.9, 70, 6.5, 7800, "NHANES 2017-2020"),
            ("30-39", "Weiblich", 28.3, 74, 6.4, 7500, "NHANES 2017-2020"),
            ("40-49", "Männlich", 29.8, 72, 6.3, 7400, "NHANES 2017-2020"),
            ("40-49", "Weiblich", 29.2, 76, 6.2, 7000, "NHANES 2017-2020"),
            ("50-59", "Männlich", 29.6, 75, 6.0, 6900, "NHANES 2017-2020"),
            ("50-59", "Weiblich", 29.4, 78, 5.9, 6500, "NHANES 2017-2020"),
            ("60-69", "Männlich", 28.8, 77, 5.8, 6200, "NHANES 2017-2020"),
            ("60-69", "Weiblich", 28.5, 79, 5.7, 5800, "NHANES 2017-2020"),
        ]
        
        cursor.executemany(
            """
            INSERT INTO nhanes_reference (age_group, gender, avg_bmi, avg_heart_rate, avg_sleep_hours, avg_daily_steps, data_source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            nhanes_data,
        )

    connection.commit()
    connection.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password):
    """Register a new user"""
    connection = sqlite3.connect("biological_age.db")
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hash_password(password)),
        )
        connection.commit()
        connection.close()
        return True, "Benutzer erfolgreich registriert!"
    except sqlite3.IntegrityError:
        connection.close()
        return False, "Benutzername existiert bereits!"
    except Exception as e:
        connection.close()
        return False, f"Fehler: {str(e)}"


def authenticate_user(username, password):
    """Authenticate user login"""
    connection = sqlite3.connect("biological_age.db")
    cursor = connection.cursor()
    cursor.execute(
        "SELECT user_id FROM users WHERE username = ? AND password_hash = ?",
        (username, hash_password(password)),
    )
    result = cursor.fetchone()
    connection.close()
    return result[0] if result else None


def get_user_id_from_username(username):
    """Get user ID from username"""
    connection = sqlite3.connect("biological_age.db")
    cursor = connection.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    connection.close()
    return result[0] if result else None


def save_entry(
    user_id,  # ← Eindeutige Benutzer-ID aus Datenbank (wichtig für Isolation!)
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
):
    """
    Speichere eine Gesundheits-Messung mit Benutzer-ID in der Datenbank.
    Jede Messung ist mit einem Benutzer verknüpft → Daten sind privat!
    """
    connection = sqlite3.connect("biological_age.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO entries (
            user_id, age, gender, height_cm, weight_kg, bmi, sleep_hours,
            exercise_days, heart_rate, stress_score, smoking,
            sitting_hours, daily_steps, biological_age,
            rule_based_risk
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
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
        ),
    )

    connection.commit()
    connection.close()


def load_entries(user_id):
    """
    Lade alle Gesundheits-Messungen für einen bestimmten Benutzer.
    
    WICHTIG: Mit user_id filtern → andere Benutzer sehen diese Daten NICHT!
    Die Daten sind nach Datum sortiert (neueste zuerst).
    """
    connection.close()
    return data


def clear_database(user_id):
    connection = sqlite3.connect("biological_age.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM entries WHERE user_id = ?", (user_id,))
    connection.commit()
    connection.close()


def get_nhanes_reference(age, gender):
    """Get NHANES reference data for user's age and gender"""
    connection = sqlite3.connect("biological_age.db")
    cursor = connection.cursor()
    
    # Determine age group
    if age < 30:
        age_group = "20-29"
    elif age < 40:
        age_group = "30-39"
    elif age < 50:
        age_group = "40-49"
    elif age < 60:
        age_group = "50-59"
    else:
        age_group = "60-69"
    
    cursor.execute(
        "SELECT * FROM nhanes_reference WHERE age_group = ? AND gender = ?",
        (age_group, gender),
    )
    result = cursor.fetchone()
    connection.close()
    
    if result:
        return {
            "age_group": result[1],
            "gender": result[2],
            "avg_bmi": result[3],
            "avg_heart_rate": result[4],
            "avg_sleep_hours": result[5],
            "avg_daily_steps": result[6],
            "data_source": result[7],
        }
    return None


def compare_with_nhanes(age, gender, bmi, heart_rate, sleep_hours, daily_steps):
    """Compare user's health metrics with NHANES reference data"""
    nhanes = get_nhanes_reference(age, gender)
    
    if not nhanes:
        return None
    
    comparison = {
        "Metrik": ["BMI", "Ruhepuls", "Schlaf (Stunden)", "Tägliche Schritte"],
        "Dein Wert": [round(bmi, 2), heart_rate, round(sleep_hours, 2), daily_steps],
        "NHANES Durchschnitt": [
            round(nhanes["avg_bmi"], 2),
            nhanes["avg_heart_rate"],
            round(nhanes["avg_sleep_hours"], 2),
            int(nhanes["avg_daily_steps"]),
        ],
        "Abweichung": [
            round(bmi - nhanes["avg_bmi"], 2),
            heart_rate - nhanes["avg_heart_rate"],
            round(sleep_hours - nhanes["avg_sleep_hours"], 2),
            daily_steps - int(nhanes["avg_daily_steps"]),
        ],
    }
    
    return pd.DataFrame(comparison)


def get_nhanes_percentile(value, metric, age, gender):
    """Estimate percentile rank compared to NHANES data"""
    nhanes = get_nhanes_reference(age, gender)
    
    if not nhanes:
        return None
    
    # Simplified percentile calculation based on standard deviations
    if metric == "bmi":
        avg = nhanes["avg_bmi"]
        std = 3.5  # Approximate standard deviation
        z_score = (value - avg) / std
    elif metric == "heart_rate":
        avg = nhanes["avg_heart_rate"]
        std = 8
        z_score = (value - avg) / std
    elif metric == "sleep":
        avg = nhanes["avg_sleep_hours"]
        std = 1.2
        z_score = (value - avg) / std
    elif metric == "steps":
        avg = nhanes["avg_daily_steps"]
        std = 2500
        z_score = (value - avg) / std
    else:
        return None
    
    # Simple approximation of percentile from z-score
    from scipy import stats
    try:
        percentile = stats.norm.cdf(z_score) * 100
        return round(percentile, 1)
    except:
        return None


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

apply_app_styles()

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None

# Sidebar: User Authentication
with st.sidebar:
    st.markdown("### 👤 Benutzer")
    
    if not st.session_state.logged_in:
        # WENN NICHT ANGEMELDET: Zeige Login-Panel
        tab1, tab2 = st.tabs(["Anmelden", "Registrieren"])
        
        with tab1:
            st.markdown("**Bestehender Benutzer**")
            username = st.text_input("Benutzername", key="login_username")
            password = st.text_input("Passwort", type="password", key="login_password")
            
            if st.button("Anmelden"):
                user_id = authenticate_user(username, password)
                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.success(f"Willkommen, {username}!")
                    st.rerun()
                else:
                    st.error("Benutzername oder Passwort falsch!")
        
        with tab2:
            st.markdown("**Neuer Benutzer**")
            new_username = st.text_input("Benutzername wählen", key="reg_username")
            new_password = st.text_input("Passwort", type="password", key="reg_password")
            new_password_confirm = st.text_input("Passwort wiederholen", type="password", key="reg_password_confirm")
            
            if st.button("Registrieren"):
                if new_password != new_password_confirm:
                    st.error("Passwörter stimmen nicht überein!")
                elif len(new_password) < 4:
                    st.error("Passwort muss mindestens 4 Zeichen lang sein!")
                else:
                    success, message = register_user(new_username, new_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    else:
        st.markdown(f"**Angemeldet als:** {st.session_state.username}")
        # LOGOUT-Button: Setzt alle Session-States zurück
        if st.button("Abmelden"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()

# Main app only visible if logged in
if st.session_state.logged_in:
    render_hero()

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

    open_section(
        "4",
        "Dashboard",
        "Gesundheits-Dashboard",
        "Sieh dein aktuelles Alter, das geschätzte biologische Alter, den Health Score und das regelbasierte Risiko auf einen Blick.",
    )

    col9, col10, col11, col12 = st.columns(4)

    with col9:
        st.metric("Reales Alter", age)

    with col10:
        st.metric("Biologisches Alter", round(biological_age, 1))

    with col11:
        st.metric("Health Score", round(health_score, 1))

    with col12:
        st.metric("Regelbasiertes Risiko", rule_based_risk)

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
        "6",
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
        "7",
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

    col13, col14, col15 = st.columns(3)

    with col13:
        st.metric("Aktuelles biologisches Alter", round(biological_age, 1))

    with col14:
        st.metric("Biologisches Alter im Szenario", round(new_biological_age, 1))

    with col15:
        st.metric("Verbesserungspotenzial", round(improvement, 1))

    close_section()

    open_section(
        "8",
        "Roadmap",
        "Persönliche Gesundheits-Roadmap",
        "Übersetze die wichtigsten Belastungsfaktoren in einen konkreten Vier-Wochen-Plan.",
    )

    roadmap = generate_roadmap(top_priorities)

    for step in roadmap:
        st.write("- " + step)

    close_section()

    open_section(
        "9",
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
        "10",
        "Tracking",
        "Speichern und Fortschritt verfolgen",
        "Speichere Ergebnisse in deinem persönlichen Profil und beobachte, wie sich dein biologisches Alter über mehrere Eingaben verändert.",
    )

    if st.button("Save result", key="save_result_button"):
        # Speichere alle Werte MIT der aktuellen Benutzer-ID
        # So bleiben die Daten privat für diesen Benutzer!
        save_entry(
            st.session_state.user_id,
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
        )
        st.success("Ergebnis gespeichert.")

    # Lade ALLE Messungen für diesen Benutzer (nicht andere!)
    entries = load_entries(st.session_state.user_id)

    if len(entries) > 0:
        st.subheader("Verlauf")

        first_age = entries["biological_age"].iloc[-1]
        latest_age = entries["biological_age"].iloc[0]
        progress = latest_age - first_age

        col16, col17, col18 = st.columns(3)

        with col16:
            st.metric("Erstes gespeichertes biologisches Alter", round(first_age, 1))

        with col17:
            st.metric("Letztes gespeichertes biologisches Alter", round(latest_age, 1))

        with col18:
            st.metric("Veränderung", round(progress, 1))

        st.write(entries[["age", "biological_age", "bmi", "sleep_hours", "exercise_days", "created_at"]])
        st.line_chart(entries["biological_age"].reset_index(drop=True))
    else:
        st.write("Noch keine gespeicherten Ergebnisse vorhanden.")

    if st.button("Verlauf löschen", key="clear_history_button"):
        clear_database(st.session_state.user_id)
        st.success("Verlauf gelöscht.")

    close_section()

    # ===== SEKTION 11: NHANES-BENCHMARK (NEU!) =====
    # NHANES = National Health and Nutrition Examination Survey
    # Dies sind echte CDC-Durchschnittswerte der USA (2017-2020)
    # Vergleiche deine Metriken mit nationalen Benchmarks!
    open_section(
        "11",
        "Benchmark",
        "Vergleich mit NHANES-Daten",
        "Siehe, wie deine Gesundheitskennzahlen im Vergleich zu nationalen Durchschnittswerten des CDC abschneiden.",
    )

    nhanes_comparison = compare_with_nhanes(age, gender, bmi, heart_rate, sleep_hours, daily_steps)

    # Wenn Referenzdaten für diese Altersgruppe + Geschlecht existieren:
    if nhanes_comparison is not None:
        st.write("**Deine Metriken im Vergleich mit NHANES-Referenzdaten:**")
        st.dataframe(nhanes_comparison, hide_index=True)
        
        # Add insights
        st.write("**Insights:**")
        
        if bmi < nhanes_comparison.loc[0, "NHANES Durchschnitt"]:
            st.success(f"✅ Dein BMI liegt unter dem Durchschnitt")
        elif bmi > nhanes_comparison.loc[0, "NHANES Durchschnitt"] + 2:
            st.warning(f"⚠️ Dein BMI liegt über dem Durchschnitt")
        
        if heart_rate < nhanes_comparison.loc[1, "NHANES Durchschnitt"]:
            st.success(f"✅ Dein Ruhepuls ist niedriger als der Durchschnitt (bessere Ausdauer)")
        elif heart_rate > nhanes_comparison.loc[1, "NHANES Durchschnitt"] + 5:
            st.warning(f"⚠️ Dein Ruhepuls ist höher als der Durchschnitt")
        
        if sleep_hours > nhanes_comparison.loc[2, "NHANES Durchschnitt"]:
            st.success(f"✅ Du schläfst mehr als der Durchschnitt")
        elif sleep_hours < nhanes_comparison.loc[2, "NHANES Durchschnitt"] - 1:
            st.warning(f"⚠️ Du schläfst weniger als der Durchschnitt")
        
        if daily_steps > nhanes_comparison.loc[3, "NHANES Durchschnitt"]:
            st.success(f"✅ Du machst mehr Schritte als der Durchschnitt")
        else:
            st.warning(f"⚠️ Du machst weniger Schritte als der Durchschnitt")
    else:
        st.info("NHANES-Referenzdaten nicht verfügbar")

    close_section()

# FALLBACK: Wenn Benutzer nicht angemeldet ist, zeige Nachricht
else:
    st.info("👤 Bitte melden Sie sich an oder registrieren Sie sich, um die App zu nutzen.")
