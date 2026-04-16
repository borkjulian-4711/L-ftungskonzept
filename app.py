import streamlit as st
import pandas as pd
import tempfile

# DIN Kern
from logic.din1946_core import (
    calculate_qv_ges,
    calculate_levels,
    distribute_airflows,
    apply_exhaust_values,
    balance_system,
    balance_ventilation_system
)

# Luftnetz
from logic.air_network import propagate_flows, calculate_uld

# DIN 18017
from logic.din18017 import apply_din18017

# Infiltration
from logic.infiltration import (
    get_ez,
    calculate_infiltration,
    calculate_effective_supply
)

# ALD
from logic.ald import calculate_ald

# Systembewertung
from logic.system_logic import evaluate_system

# Formblätter
from logic.formblatt_a import evaluate_formblatt_a
from logic.formblatt_b import evaluate_formblatt_b
from logic.formblatt_c import evaluate_formblatt_c
from logic.formblatt_d import evaluate_formblatt_d
from logic.formblatt_e import generate_formblatt_e

# Validierung
from logic.validation import validate_din

# PDF
from export.pdf_generator import create_multi_pdf


# -----------------------------
# TITLE
# -----------------------------
st.title("🌀 Lüftungskonzept DIN 1946-6 + DIN 18017-3")

# -----------------------------
# SYSTEM
# -----------------------------
system = st.selectbox(
    "Lüftungssystem",
    ["freie Lüftung", "ventilatorgestützt", "kombiniert"]
)

# -----------------------------
# FORMBLATT A
# -----------------------------
st.header("Formblatt A")

neubau = st.checkbox("Neubau")
sanierung = st.checkbox("Sanierung")
fensteranteil = st.slider("Fensteranteil (%)", 0, 100, 50) / 100
luftdicht = st.checkbox("Luftdicht")

formblatt_a = evaluate_formblatt_a(
    neubau, sanierung, fensteranteil, luftdicht
)

# -----------------------------
# FORMBLATT B
# -----------------------------
st.header("Formblatt B")

gebaeudetyp = st.selectbox("Gebäudetyp", ["EFH", "MFH", "Wohnung"])
baujahr = st.number_input("Baujahr", 1900, 2025, 2000)
wohneinheiten = st.number_input("Wohneinheiten", 1, 50, 1)

personen = st.number_input("Personen", 1, 10, 2)
nutzung = st.selectbox("Nutzung", ["normal", "reduziert", "hoch"])

fensterlueftung = st.checkbox("Fensterlüftung möglich")
infiltration_mode = st.selectbox("Infiltration", ["hoch", "mittel", "gering"])

formblatt_b = evaluate_formblatt_b(
    gebaeudetyp, baujahr, wohneinheiten,
    personen, nutzung, fensterlueftung, infiltration_mode
)

# -----------------------------
# GRUNDLAGEN
# -----------------------------
st.header("Grunddaten")

ANE = st.number_input("Wohnfläche ANE (m²)", 30, 300, 80)

qv = calculate_qv_ges(ANE)
levels = calculate_levels(qv)

st.subheader("Lüftungsstufen")
st.write(levels)

level = st.selectbox("Auslegungsstufe", list(levels.keys()))
qv_selected = levels[level]

# -----------------------------
# RAUMTABELLE
# -----------------------------
st.header("Räume & Luftführung")

default_df = pd.DataFrame({
    "Raum": ["Wohnzimmer", "Flur", "Bad"],
    "Fläche": [20, 10, 6],
    "Typ": ["Zuluft", "Überström", "Abluft"],
    "Kategorie (DIN 1946-6)": ["Wohnzimmer", "Flur", "Bad"],
    "Innenliegend": [False, False, True],
    "DIN 18017 Kategorie": ["", "", "R-ZD"],
    "Überströmt nach": ["Flur", "Bad", ""]
})

typ_options = ["Zuluft", "Überström", "Abluft"]

din1946_options = [
    "Wohnzimmer", "Schlafzimmer", "Kinderzimmer",
    "Arbeitszimmer", "Küche", "Bad", "WC",
    "Flur", "Abstellraum", "Hauswirtschaftsraum"
]

din18017_options = ["", "R-ZD", "R-BD", "R-PN", "R-PD"]

raumliste = default_df["Raum"].tolist()

df_rooms = st.data_editor(
    default_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Typ": st.column_config.SelectboxColumn(options=typ_options),
        "Kategorie (DIN 1946-6)": st.column_config.SelectboxColumn(options=din1946_options),
        "DIN 18017 Kategorie": st.column_config.SelectboxColumn(options=din18017_options),
        "Innenliegend": st.column_config.CheckboxColumn(),
        "Überströmt nach": st.column_config.SelectboxColumn(options=[""] + raumliste)
    }
)

df_rooms = df_rooms.fillna(0)

# -----------------------------
# DIN VERTEILUNG
# -----------------------------
df_rooms = distribute_airflows(df_rooms, qv_selected)
df_rooms = apply_exhaust_values(df_rooms)
df_rooms = apply_din18017(df_rooms)

st.subheader("Raumweise Luftmengen")
st.dataframe(df_rooms)

# -----------------------------
# LUFTNETZ
# -----------------------------
flows = propagate_flows(df_rooms)

st.subheader("Luftnetz")

for r, f in flows.items():
    st.write(f"{r}: {round(f,1)} m³/h")

# -----------------------------
# ÜLD
# -----------------------------
uld = calculate_uld(flows, df_rooms)

st.subheader("Überströmöffnungen")

for (a, b), d in uld.items():
    st.write(f"{a} → {b}: {d['Anzahl']} Stück ({d['Volumenstrom']} m³/h)")

# -----------------------------
# BILANZ
# -----------------------------
if system == "ventilatorgestützt":
    df_rooms, zu, ab = balance_ventilation_system(df_rooms)
else:
    zu, ab, _ = balance_system(df_rooms)

# -----------------------------
# INFILTRATION
# -----------------------------
st.header("Infiltration")

wind = st.selectbox("Windgebiet", ["windschwach", "windstark"])
Aenv = st.number_input("Hüllfläche Aenv (m²)", 10.0, 500.0, 40.0)

ez = get_ez(wind, gebaeudetyp)
q_inf = calculate_infiltration(Aenv, ez)

# -----------------------------
# GESAMTBILANZ
# -----------------------------
if system == "freie Lüftung":
    q_eff = calculate_effective_supply(zu, q_inf)
elif system == "kombiniert":
    q_eff = zu + q_inf
else:
    q_eff = zu

delta = q_eff - ab

st.subheader("Gesamtbilanz")

st.write("Zuluft:", zu)
st.write("Infiltration:", q_inf)
st.write("Effektiv:", q_eff)
st.write("Abluft:", ab)
st.write("Differenz:", delta)

# -----------------------------
# SYSTEMBEWERTUNG
# -----------------------------
q_mech = df_rooms[df_rooms["Typ"] == "Abluft"]["Abluft (m³/h)"].sum()

result = evaluate_system(q_mech, qv_selected, q_inf)

st.header("Systembewertung")

st.write("Status:", result["status"])

# -----------------------------
# ALD
# -----------------------------
st.header("ALD-Auslegung")

if result["ald"]:
    q_needed = max(0, qv_selected - (q_mech + q_inf))

    ald = calculate_ald(q_needed)

    st.warning("ALD erforderlich")
    st.write("Anzahl:", ald["anzahl"])
else:
    st.success("Keine ALDs erforderlich")

# -----------------------------
# VALIDIERUNG
# -----------------------------
errors, warnings = validate_din(df_rooms, flows, qv_selected, ab)

if errors:
    st.error(errors)

if warnings:
    st.warning(warnings)

# -----------------------------
# FORMBLÄTTER
# -----------------------------
formblatt_c = evaluate_formblatt_c(levels, ab)

formblatt_d = evaluate_formblatt_d(
    formblatt_a,
    formblatt_b,
    formblatt_c
)

formblatt_e = generate_formblatt_e({
    "levels": levels,
    "formblatt_d": formblatt_d
})

st.header("Konzept")
st.text_area("Text", formblatt_e, height=250)

# -----------------------------
# PDF EXPORT
# -----------------------------
st.header("Export")

if st.button("📄 PDF Export"):

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    create_multi_pdf(tmp.name, {
        "WE1": {
            "meta": {
                "projekt": "Projekt",
                "adresse": "Adresse",
                "bearbeiter": "Bearbeiter"
            },
            "res": {
                "formblatt_a": formblatt_a,
                "formblatt_b": formblatt_b,
                "formblatt_c": formblatt_c,
                "formblatt_d": formblatt_d,
                "formblatt_e": formblatt_e,
                "levels": levels
            }
        }
    })

    with open(tmp.name, "rb") as f:
        st.download_button("Download PDF", f)
