import streamlit as st
import pandas as pd
import tempfile

from config import FIRMA
import logic.din1946_core as core

from logic.air_network import propagate_flows, calculate_uld
from logic.din18017 import apply_din18017
from logic.infiltration import get_ez_din, calculate_infiltration_din, calculate_shaft_flow
from logic.ald import calculate_ald_din
from logic.system_logic import evaluate_system
from logic.formblatt_a import evaluate_formblatt_a
from logic.formblatt_b import evaluate_formblatt_b
from logic.text_generator import generate_concept_text
from logic.validation import validate_din
from export.pdf_generator import create_multi_pdf


st.title("🌀 Lüftungskonzept DIN 1946-6 + DIN 18017-3")


# -----------------------------
# FIRMA
# -----------------------------
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
ANE = st.number_input("ANE", 30, 300, 80)

levels = core.calculate_levels(ANE)

level = st.selectbox("Stufe", list(levels.keys()))
qv_selected = levels[level]

st.write("qv:", qv_selected)


# -----------------------------
# RÄUME
# -----------------------------
df_rooms = pd.DataFrame({
    "Raum": ["Wohnzimmer", "Bad"],
    "Typ": ["Zuluft", "Abluft"],
    "Kategorie (DIN 1946-6)": ["Wohnzimmer", "Bad"]
})

df_rooms = st.data_editor(df_rooms)

df_rooms = core.distribute_airflows(df_rooms, qv_selected)
df_rooms = core.apply_exhaust_values(df_rooms)
df_rooms = apply_din18017(df_rooms)

st.dataframe(df_rooms)


# -----------------------------
# LUFTNETZ
# -----------------------------
flows = propagate_flows(df_rooms)

for r, f in flows.items():
    st.write(r, f)


# -----------------------------
# INFILTRATION
# -----------------------------
wind = st.selectbox("Wind", ["windschwach", "windstark"])
Aenv = st.number_input("Aenv", 10.0, 500.0, 200.0)
luftdicht = st.checkbox("luftdicht")

ez = get_ez_din("EFH", wind, luftdicht)
q_inf = calculate_infiltration_din(Aenv, ez)

# Schacht
shaft = st.checkbox("Schacht")

if shaft:
    q_shaft = calculate_shaft_flow()
else:
    q_shaft = 0

q_passive = q_inf + q_shaft


# -----------------------------
# SYSTEMBERECHNUNG
# -----------------------------
if system == "ventilatorgestützt":
    df_rooms, zu, ab = core.dimension_ventilation_system(df_rooms, qv_selected)
else:
    zu, ab, _ = core.balance_system(df_rooms)


# -----------------------------
# ALD
# -----------------------------
ald = calculate_ald_din(qv_selected, q_passive, wind)

st.write("ALD:", ald)


# -----------------------------
# SYSTEM
# -----------------------------
res = evaluate_system(ab, qv_selected, q_passive)

st.write(res)


# -----------------------------
# PDF
# -----------------------------
if st.button("PDF"):
    tmp = tempfile.NamedTemporaryFile(delete=False)

    create_multi_pdf(tmp.name, {
        "WE1": {
            "meta": project_data,
            "firma": firm_data,
            "res": {
                "df_rooms": df_rooms,
                "summary": {
                    "zu": zu,
                    "ab": ab,
                    "inf": q_inf,
                    "diff": q_passive,
                    "status": res["status"]
                }
            }
        }
    })

    with open(tmp.name, "rb") as f:
        st.download_button("Download", f)
