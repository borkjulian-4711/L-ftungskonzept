import streamlit as st
import pandas as pd
import tempfile

from config import FIRMA
import logic.din1946_core as core

from logic.infiltration import (
    get_ez_din,
    calculate_infiltration_din,
    calculate_shaft_flow
)

from logic.ald import calculate_ald_din
from logic.system_logic import evaluate_system
from logic.text_generator import generate_concept_text
from logic.validation import validate_din
from logic.correction_engine import generate_corrections
from logic.auto_fix import auto_fix_system

from export.pdf_generator import create_multi_pdf


st.title("🌀 Lüftungskonzept DIN 1946-6")


# -----------------------------
# PROJEKT
# -----------------------------
projekt = st.text_input("Projekt")
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
    "System",
    ["freie Lüftung", "ventilatorgestützt", "kombiniert"]
)


# -----------------------------
# GRUNDLAGEN
# -----------------------------
ANE = st.number_input("Wohnfläche ANE (m²)", 30, 300, 80)

levels = core.calculate_levels(ANE)
level = st.selectbox("Lüftungsstufe", list(levels.keys()))
qv_selected = levels[level]

st.write("qv:", qv_selected, "m³/h")


# -----------------------------
# RAUMTABELLE
# -----------------------------
df_rooms = pd.DataFrame({
    "Raum": ["Wohnzimmer", "Schlafzimmer", "Bad"],
    "Fläche": [20, 15, 6],
    "Typ": ["Zuluft", "Zuluft", "Abluft"],
    "Kategorie (DIN 1946-6)": ["Wohnzimmer", "Schlafzimmer", "Bad"],
    "Innenliegend": [False, False, True],
    "Überströmt nach": ["Flur", "Flur", ""]
})

df_rooms = st.data_editor(df_rooms, num_rows="dynamic")


# -----------------------------
# BERECHNUNG
# -----------------------------
df_rooms = core.distribute_airflows(df_rooms, qv_selected)
df_rooms = core.apply_exhaust_values(df_rooms)

st.dataframe(df_rooms)


# -----------------------------
# INFILTRATION
# -----------------------------
wind = st.selectbox("Wind", ["windschwach", "windstark"])
Aenv = st.number_input("Aenv", 10.0, 500.0, 200.0)
luftdicht = st.checkbox("luftdicht")

ez = get_ez_din("EFH", wind, luftdicht)
q_inf = calculate_infiltration_din(Aenv, ez)


# -----------------------------
# SYSTEM
# -----------------------------
q_mech = df_rooms["Abluft (m³/h)"].sum()
q_supply = q_mech + q_inf


# -----------------------------
# VALIDIERUNG
# -----------------------------
errors, warnings = validate_din(
    df_rooms,
    qv_selected,
    q_supply,
    system
)

st.header("DIN-Prüfung")

for e in errors:
    st.error(e)

for w in warnings:
    st.warning(w)


# -----------------------------
# AUTO-FIX BUTTON
# -----------------------------
st.header("Auto-Fix")

if st.button("🔧 System automatisch korrigieren"):

    df_rooms, msg = auto_fix_system(
        df_rooms,
        qv_selected,
        q_supply
    )

    st.success(msg)
    st.dataframe(df_rooms)


# -----------------------------
# KORREKTUREN
# -----------------------------
corrections = generate_corrections(
    df_rooms,
    errors,
    qv_selected,
    q_supply
)

for c in corrections:
    st.info(c)


# -----------------------------
# PRÜFBERICHT
# -----------------------------
summary = {
    "qv": qv_selected,
    "zu": q_supply,
    "ab": q_mech,
    "inf": q_inf,
    "status": "OK" if not errors else "NICHT OK"
}

report = generate_concept_text(
    {
        "levels": levels,
        "summary": summary
    },
    project_data
)

st.text_area("Prüfbericht", report)


# -----------------------------
# PDF
# -----------------------------
if st.button("PDF Export"):

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    create_multi_pdf(tmp.name, {
        "WE1": {
            "meta": project_data,
            "res": {
                "df_rooms": df_rooms,
                "formblatt_e": report,
                "validation": {
                    "errors": errors,
                    "warnings": warnings
                },
                "corrections": corrections
            }
        }
    })

    with open(tmp.name, "rb") as f:
        st.download_button(
            "Download PDF",
            f,
            file_name="Lueftungskonzept.pdf",
            mime="application/pdf"
        )
