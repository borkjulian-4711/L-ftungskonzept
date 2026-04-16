import streamlit as st
import pandas as pd
import tempfile

from config import FIRMA
import logic.din1946_core as core

from logic.air_network import propagate_flows, calculate_uld
from logic.din18017 import apply_din18017
from logic.infiltration import (
    get_ez_din,
    calculate_infiltration_din,
    calculate_shaft_flow
)
from logic.ald import calculate_ald_din
from logic.system_logic import evaluate_system
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
ANE = st.number_input("Wohnfläche ANE (m²)", 30, 300, 80)

levels = core.calculate_levels(ANE)
level = st.selectbox("Lüftungsstufe", list(levels.keys()))
qv_selected = levels[level]

st.write("qv:", qv_selected, "m³/h")


# -----------------------------
# RÄUME
# -----------------------------
df_rooms = pd.DataFrame({
    "Raum": ["Wohnzimmer", "Schlafzimmer", "Bad"],
    "Typ": ["Zuluft", "Zuluft", "Abluft"],
    "Kategorie (DIN 1946-6)": ["Wohnzimmer", "Schlafzimmer", "Bad"]
})

df_rooms = st.data_editor(df_rooms, num_rows="dynamic")

df_rooms = core.distribute_airflows(df_rooms, qv_selected)
df_rooms = core.apply_exhaust_values(df_rooms)
df_rooms = apply_din18017(df_rooms)

st.dataframe(df_rooms)


# -----------------------------
# INFILTRATION
# -----------------------------
wind = st.selectbox("Wind", ["windschwach", "windstark"])
Aenv = st.number_input("Hüllfläche", 10.0, 500.0, 200.0)
luftdicht = st.checkbox("luftdicht")

ez = get_ez_din("EFH", wind, luftdicht)
q_inf = calculate_infiltration_din(Aenv, ez)


# -----------------------------
# SCHACHT
# -----------------------------
shaft = st.checkbox("Schachtlüftung")

q_shaft = calculate_shaft_flow() if shaft else 0


# -----------------------------
# SYSTEMLOGIK
# -----------------------------
q_mech = df_rooms["Abluft (m³/h)"].sum()

if system == "freie Lüftung":
    q_supply = q_inf + q_shaft

elif system == "ventilatorgestützt":
    df_rooms, zu, ab = core.dimension_ventilation_system(df_rooms, qv_selected)
    q_supply = zu

elif system == "kombiniert":
    q_supply = q_mech + q_inf + q_shaft


# -----------------------------
# ALD
# -----------------------------
ald = calculate_ald_din(qv_selected, q_supply, wind)
st.write("ALD:", ald)


# -----------------------------
# SYSTEMBEWERTUNG
# -----------------------------
res = evaluate_system(q_mech, qv_selected, q_supply)
st.write("Status:", res["status"])


# -----------------------------
# PDF
# -----------------------------
if st.button("PDF Export"):

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    create_multi_pdf(tmp.name, {
        "WE1": {
            "meta": project_data,
            "firma": firm_data,
            "res": {
                "df_rooms": df_rooms,
                "summary": {
                    "zu": q_supply,
                    "ab": q_mech,
                    "inf": q_inf,
                    "diff": q_supply - q_mech,
                    "status": res["status"]
                }
            }
        }
    })

    with open(tmp.name, "rb") as f:
        st.download_button("Download PDF", f)
