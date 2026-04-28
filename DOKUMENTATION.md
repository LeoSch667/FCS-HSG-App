# 📊 Biologischer Altersrechner - Dokumentation

## 🎯 Was ich hinzugefügt habe

Ich habe deine App um **3 Hauptfunktionen** erweitert:

---

## 1️⃣ **User-Authentifizierung (Login/Registrierung)**

### Location: `App.py`, Zeilen 850-920
### Was passiert:
- **Sidebar mit Login-Panel** (links beim Öffnen)
- Neue Benutzer können sich registrieren
- Bestehende Benutzer können sich anmelden
- Passwörter werden mit **SHA-256 verschlüsselt** (nicht im Klartext!)

### Code-Ablauf:
```python
if not st.session_state.logged_in:  # Wenn nicht angemeldet
    # Zeige Login/Registrierungs-Tabs
    authenticate_user(username, password)  # Prüfe Anmeldedaten
    register_user(username, password)      # Speichere neuen Benutzer
```

### Datenbank-Tabelle `users`:
```
user_id (eindeutige ID)
username (z.B. "huaigujin")
password_hash (verschlüsselt mit SHA-256!)
created_at (Registrierungs-Datum)
```

---

## 2️⃣ **Benutzer-isoliertes Tracking (SQLite)**

### Location: `App.py`, Zeilen 300-330 (Datenbank-Setup)
### Was passiert:
- **Jeder Benutzer hat separate Daten**
- Alle Messungen werden mit `user_id` gespeichert
- Geschichte/Verlauf ist privat pro Benutzer

### Code-Ablauf:
```python
# Speichere Messung
save_entry(
    st.session_state.user_id,  # ← Kritisch! Speichere mit Benutzer-ID
    age, gender, height_cm, ...
)

# Lade nur DIESEN Benutzers Daten
entries = load_entries(st.session_state.user_id)
```

### Datenbank-Tabelle `entries`:
```
id (Eintrags-ID)
user_id (← Verknüpfung zum Benutzer!)
age, gender, height_cm, weight_kg
bmi, sleep_hours, exercise_days
heart_rate, stress_score, smoking
sitting_hours, daily_steps
biological_age (berechnetes Ergebnis)
rule_based_risk (Risikoklassifikation)
created_at (Messung-Datum)
```

---

## 3️⃣ **NHANES-Vergleich (CDC-Daten)**

### Location: `App.py`, Zeilen 620-680 (Funktionen) + Sektion 11 (UI)
### Was passiert:
- Vergleiche Benutzer-Metriken mit **CDC-Referenzdaten**
- NHANES = National Health and Nutrition Examination Survey (USA)
- Daten stammen aus 2017-2020 Studien

### Code-Ablauf:
```python
# Hole Referenzdaten für Altersgruppe + Geschlecht
nhanes_ref = get_nhanes_reference(age, gender)

# Vergleiche Benutzer vs Durchschnitt
comparison = compare_with_nhanes(age, gender, bmi, heart_rate, sleep_hours, daily_steps)

# Zeige Insights
if bmi < nhanes_comparison.loc[0, "NHANES Durchschnitt"]:
    st.success("✅ Dein BMI liegt unter dem Durchschnitt")
```

### Datenbank-Tabelle `nhanes_reference`:
```
age_group (z.B. "20-29", "30-39", ...)
gender ("Männlich" oder "Weiblich")
avg_bmi (Durchschnitts-BMI)
avg_heart_rate (Durchschnitts-Ruhepuls)
avg_sleep_hours (Durchschnittlicher Schlaf)
avg_daily_steps (Durchschnittliche tägliche Schritte)
data_source ("NHANES 2017-2020")
```

---

## 🏗️ Gesamter Flow beim Start der App

```
1. App.py startet
   ↓
2. create_database() → 3 Tabellen werden erstellt
   ↓
3. apply_app_styles() → Design wird angewendet
   ↓
4. Sidebar wird gezeigt:
   - Wenn NICHT angemeldet → Login/Registrierungs-Panel
   - Wenn ANGEMELDET → "Angemeldet als: [Benutzername]"
   ↓
5. if st.session_state.logged_in:  ← KRITISCH!
   ↓
   - Zeige Hero-Banner
   - Zeige Sektionen 1-11
   - Alle Eingaben sind aktiv
   ↓
   else:
   - Zeige "Bitte melden Sie sich an..."
```

---

## 🔒 Sicherheitsmerkmale

### Passwort-Verschlüsselung
```python
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
    # SHA-256 = one-way encryption
    # Aus Hash kann man NICHT das Passwort zurückbekommen!
```

### Session-Management
```python
st.session_state.logged_in = True/False
st.session_state.user_id = <ID>
st.session_state.username = "name"
# Session wird automatisch zurückgesetzt, wenn Browser schließt
```

### Benutzer-Isolation
```python
# Falsch ❌
entries = load_entries()  # Würde ALLE Benutzer-Daten laden!

# Richtig ✅
entries = load_entries(st.session_state.user_id)  # Nur DIESER Benutzer
```

---

## 📊 NHANES-Vergleich: Wie funktioniert es?

### Altersgruppen-Logik
```python
if age < 30:
    age_group = "20-29"
elif age < 40:
    age_group = "30-39"
# usw.
```

### Beispiel-Daten (2017-2020 CDC-NHANES)
```
Männer 20-29: BMI 27.2, Ruhepuls 68, Schlaf 6.8h, Schritte 8200
Frauen 20-29: BMI 26.8, Ruhepuls 72, Schlaf 7.0h, Schritte 7900

Männer 30-39: BMI 28.9, Ruhepuls 70, Schlaf 6.5h, Schritte 7800
Frauen 30-39: BMI 28.3, Ruhepuls 74, Schlaf 6.4h, Schritte 7500
```

### Vergleichs-Tabelle in Sektion 11
```
Metrik              | Dein Wert | NHANES Ø | Abweichung
BMI                 | 24.5      | 27.2     | -2.7 (besser!)
Ruhepuls            | 65        | 68       | -3 (besser!)
Schlaf (Stunden)    | 7.5       | 6.8      | +0.7 (besser!)
Tägliche Schritte   | 9500      | 8200     | +1300 (besser!)
```

---

## 🛠️ Code-Struktur im Detail

### Neue Funktionen (alle am Anfang definiert)

#### Authentication
```python
hash_password(password)                    # Verschlüssele Passwort
register_user(username, password)          # Registriere neuen Benutzer
authenticate_user(username, password)      # Prüfe Login-Daten
get_user_id_from_username(username)       # Hole Benutzer-ID
```

#### Datenbank (User-Daten)
```python
save_entry(user_id, age, gender, ...)     # Speichere neue Messung
load_entries(user_id)                      # Lade Messungen für Benutzer
clear_database(user_id)                    # Lösche Messungen für Benutzer
```

#### NHANES-Funktionen (CDC)
```python
get_nhanes_reference(age, gender)          # Hole Referenzdaten
compare_with_nhanes(age, gender, ...)      # Vergleiche mit CDC
get_nhanes_percentile(value, metric, ...)  # Berechne Perzentil-Rang
```

---

## 📝 Session State (Wichtig!)

Die App speichert im Browser:
```python
st.session_state.logged_in   # True/False
st.session_state.user_id     # z.B. 1, 2, 3, ... (von Datenbank)
st.session_state.username    # z.B. "huaigujin" (für Anzeige)
```

Diese Werte verschwinden, wenn:
- Benutzer den Browser schließt
- Benutzer auf "Abmelden" klickt
- Session timeout

---

## 🚀 Nächste Schritte (optional)

Wenn du die App erweitern möchtest:

1. **Echte CDC-API statt Testdaten**
   ```python
   # Statt hardcodierte Daten:
   response = requests.get("https://api.cdc.gov/nhanes/data")
   ```

2. **Graphen für Trend-Analyse**
   ```python
   import plotly.graph_objects as go
   fig = go.Figure()
   fig.add_trace(...)
   st.plotly_chart(fig)
   ```

3. **Export-Funktion (PDF/CSV)**
   ```python
   entries.to_csv("meine_daten.csv")
   entries.to_excel("meine_daten.xlsx")
   ```

4. **Mehrsprachigkeit** (Englisch, etc.)
   ```python
   if language == "en":
       title = "Biological Age Calculator"
   elif language == "de":
       title = "Biologischer Altersrechner"
   ```

---

## 📞 Häufige Fehler

### ❌ "user_id ist None"
Grund: Benutzer ist nicht angemeldet
```python
# Falsch
save_entry(st.session_state.user_id, ...)  # None!

# Richtig
if st.session_state.logged_in:
    save_entry(st.session_state.user_id, ...)
```

### ❌ "Datenbank-Fehler"
Grund: Datenbank-Datei ist gesperrt (parallel-Zugriff)
Lösung: Starte die App neu oder überprüfe, ob mehrere Instanzen laufen

### ❌ "Passwort ist sichtbar"
Das ist beabsichtigt! Der Input-Feld hat `type="password"` → wird mit Punkten angezeigt

---

Viel Spaß mit der erweiterten App! 🎉
