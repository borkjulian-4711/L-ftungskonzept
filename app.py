import streamlit as st
import pandas as pd
import tempfile

# CONFIG (Firma fix)
from config import FIRMA

# DIN Kern
import logic.din1946_core as core

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

# Text
from logic.text_generator import generate_concept_text

# Validierung
from logic.validation import validate_din

# PDF
from export.pdf_generator import create_multi_pdf


st.title("🌀 Lüftungskonzept DIN 1946-6 + DIN 18017-3")

# -----------------------------
# FIRMA (fest)
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
st.header("Projektangaben")

projekt_name = st.text_input("Projekt")
adresse = st.text_input("Projektadresse")
bearbeiter = st.text_input("Bearbeiter")
datum = st.date_input("Datum")

project_data = {
    "projekt": projekt_name,
    "adresse": adresse,
    "bearbeiter": bearbeiter,
    "datum": str(datum)
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

personen = st.number_input("Personen", 1, 10, 2)
nutzung = st.selectbox("Nutzung", ["normal", "reduziert", "hoch"])

formblatt_b = evaluate_formblatt_b(
    gebaeudetyp, baujahr, 1,
    personen, nutzung, True, "mittel"
)

# -----------------------------
# GRUNDLAGEN
# -----------------------------
ANE = st.number_input("Wohnfläche ANE (m²)", 30, 300, 80)

qv = core.calculate_qv_ges(ANE)
levels = core.calculate_levels(qv)

level = st.selectbox("Lüftungsstufe", list(levels.keys()))
qv_selected = levels[level]

# -----------------------------
# RÄUME
# -----------------------------
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
# NETZ
# -----------------------------
flows = propagate_flows(df_rooms)
uld = calculate_uld(flows, df_rooms)

# -----------------------------
# BILANZ
# -----------------------------
zu, ab, _ = core.balance_system(df_rooms)

# Infiltration
q_inf = calculate_infiltration(40, get_ez("windschwach", gebaeudetyp))

q_eff = zu + q_inf
delta = q_eff - ab

result = evaluate_system(ab, qv_selected, q_inf)

# -----------------------------
# TEXT
# -----------------------------
mode = st.selectbox("Textstil", ["kurz", "lang", "behördlich"])

formblatt_e = generate_concept_text(
    {"levels": levels, "formblatt_d": {"massnahme": result["status"]}},
    project_data,
    mode
)

st.text_area("Konzept", formblatt_e, height=300)

# -----------------------------
# SUMMARY
# -----------------------------
summary = {
    "zu": zu,
    "ab": ab,
    "inf": q_inf,
    "diff": delta,
    "status": result["status"]
}

# -----------------------------
# PDF
# -----------------------------
if st.button("📄 PDF Export"):

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    create_multi_pdf(tmp.name, {
        "WE1": {
            "meta": project_data,
            "firma": firm_data,
            "res": {
                "formblatt_a": formblatt_a,
                "formblatt_b": formblatt_b,
                "formblatt_e": formblatt_e,
                "df_rooms": df_rooms,
                "summary": summary
            }
        }
    })

    with open(tmp.name, "rb") as f:
        st.download_button("Download PDF", f)
