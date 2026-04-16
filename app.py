import streamlit as st
import pandas as pd
import tempfile

# CONFIG
from config import FIRMA

# DIN Kern
import logic.din1946_core as core

# Luftnetz
from logic.air_network import propagate_flows, calculate_uld

# DIN 18017
from logic.din18017 import apply_din18017

# Infiltration + Schacht
from logic.infiltration import (
    get_ez_din,
    calculate_infiltration_din,
    calculate_shaft_flow
)

# ALD
from logic.ald import calculate_ald_din

# Systembewertung
from logic.system_logic import evaluate_system

# Formblätter
from logic.formblatt_a import evaluate_formblatt_a
from logic.formblatt_b import evaluate_formblatt_b

# Text
from logic.text_generator import generate_concept_text

# Validierung
from logic.validation import validate_din

# PDF
from export.pdf_generator import create_multi_pdf


st.title("🌀 Lüftungskonzept DIN 1946-6 + DIN 18017-3")


# -----------------------------
# FIRMA
# -----------------------------
st.header("Firma")

st.write(FIRMA["name"])
st.write(FIRMA["anschrift"])
st.write(FIRMA["kontakt"])

firm_data = {
    "firma": FIRMA["name"],
    "anschrift": FIRMA["anschrift"],
    "kontakt": FIRMA["kontakt"],
    "logo_path": FIRMA["logo_path"]
}


# -----------------------------
# PROJEKT
# -----------------------------
st.header("Projekt")

projekt = st.text_input("Projektname")
adresse = st.text_input("Adresse")
bearbeiter = st.text_input("Bearbeiter")

project_data = {
    "projekt": projekt,
    "adresse": adresse,
    "bearbeiter": bearbeiter
}


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
luftdicht = st.checkbox("Gebäude luftdicht")

formblatt_a = evaluate_formblatt_a(
    neubau, sanierung, fensteranteil, luftdicht
)


# -----------------------------
# FORMBLATT B
# -----------------------------
st.header("Formblatt B")

gebaeudetyp = st.selectbox("Gebäudetyp", ["EFH", "DHH", "MFH", "Wohnung"])
baujahr = st.number_input("Baujahr", 1900, 2025, 2000)
personen = st.number_input("Personen", 1, 10, 2)

formblatt_b = evaluate_formblatt_b(
    gebaeudetyp, baujahr, 1,
    personen, "normal", True, "mittel"
)


# -----------------------------
# GRUNDLAGEN
# -----------------------------
st.header("Grunddaten")

ANE = st.number_input("Wohnfläche ANE (m²)", 30, 300, 80)

levels = core.calculate_levels(ANE)

level = st.selectbox("Lüftungsstufe", list(levels.keys()))
qv_selected = levels[level]

st.write("Volumenstrom:", qv_selected, "m³/h")


# -----------------------------
# RÄUME
# -----------------------------
st.header("Räume")

df_rooms = pd.DataFrame({
    "Raum": ["Wohnzimmer", "Flur", "Bad"],
    "Fläche": [20, 10, 6],
    "Typ": ["Zuluft", "Überström", "Abluft"],
    "Kategorie (DIN 1946-6)": ["Wohnzimmer", "Flur", "Bad"],
    "Überströmt nach": ["Flur", "Bad", ""]
})

df_rooms = st.data_editor(df_rooms, num_rows="dynamic")

df_rooms = core.distribute_airflows(df_rooms, qv_selected)
df_rooms = core.apply_exhaust_values(df_rooms)
df_rooms = apply_din18017(df_rooms)

st.dataframe(df_rooms)


# -----------------------------
# LUFTNETZ
# -----------------------------
flows = propagate_flows(df_rooms)

st.subheader("Luftnetz")
for r, f in flows.items():
    st.write(r, ":", round(f, 1))


# -----------------------------
# INFILTRATION
# -----------------------------
st.header("Infiltration")

wind = st.selectbox("Wind", ["windschwach", "windstark"])
Aenv = st.number_input("Hüllfläche", 10.0, 500.0, 200.0)

ez = get_ez_din(gebaeudetyp, wind, luftdicht)
q_inf = calculate_infiltration_din(Aenv, ez)

st.write("ez:", ez)
st.write("Infiltration:", q_inf)


# -----------------------------
# SCHACHTLÜFTUNG
# -----------------------------
st.header("Schachtlüftung")

shaft_active = st.checkbox("Schacht vorhanden")

if shaft_active:
    height = st.number_input("Höhe (m)", 2.0, 20.0, 8.0)
    delta_t = st.number_input("ΔT (K)", 1.0, 30.0, 10.0)
    area = st.number_input("Querschnitt (m²)", 0.01, 0.1, 0.02)

    q_shaft = calculate_shaft_flow(height, delta_t, area)
else:
    q_shaft = 0

st.write("Schachtvolumenstrom:", q_shaft)


# -----------------------------
# ALD
# -----------------------------
st.header("ALD")

q_total_passive = q_inf + q_shaft

ald_result = calculate_ald_din(
    qv_selected,
    q_total_passive,
    wind
)

st.write(ald_result)


# -----------------------------
# SYSTEM
# -----------------------------
result = evaluate_system(
    df_rooms["Abluft (m³/h)"].sum(),
    qv_selected,
    q_total_passive
)

st.write("System:", result["status"])


# -----------------------------
# TEXT
# -----------------------------
text = generate_concept_text(
    {"levels": levels},
    project_data,
    "lang"
)

st.text_area("Konzept", text)


# -----------------------------
# PDF
# -----------------------------
if st.button("PDF"):

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    create_multi_pdf(tmp.name, {
        "WE1": {
            "meta": project_data,
            "firma": firm_data,
            "res": {
                "formblatt_a": formblatt_a,
                "formblatt_b": formblatt_b,
                "formblatt_e": text,
                "df_rooms": df_rooms,
                "summary": {
                    "zu": df_rooms["Zuluft (m³/h)"].sum(),
                    "ab": df_rooms["Abluft (m³/h)"].sum(),
                    "inf": q_inf,
                    "diff": q_total_passive,
                    "status": result["status"]
                }
            }
        }
    })

    with open(tmp.name, "rb") as f:
        st.download_button("Download", f)
