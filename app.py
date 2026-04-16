import streamlit as st
import pandas as pd
import tempfile

from logic.ventilation import calculate_ventilation
from logic.ventilation_levels import calculate_ventilation_levels
from logic.formblatt_a import evaluate_formblatt_a
from logic.formblatt_b import evaluate_formblatt_b
from logic.formblatt_c import evaluate_formblatt_c
from logic.formblatt_d import evaluate_formblatt_d
from logic.formblatt_e import generate_formblatt_e
from export.pdf_generator import create_multi_pdf


# -----------------------------
# SESSION STATE
# -----------------------------
if "project" not in st.session_state:
    st.session_state["project"] = {}

if "counter" not in st.session_state:
    st.session_state["counter"] = 1


st.title("🌀 Lüftungskonzept DIN 1946-6")

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

gebaeudetyp = st.selectbox("Gebäudetyp",
    ["EFH","MFH","Wohnung"])

baujahr = st.number_input("Baujahr", 1900, 2025, 2000)
wohneinheiten = st.number_input("Wohneinheiten", 1, 50, 1)
personen = st.number_input("Personen", 1, 10, 2)

nutzung = st.selectbox("Nutzung", ["normal","reduziert","hoch"])
fensterlueftung = st.checkbox("Fensterlüftung möglich")
infiltration = st.selectbox("Infiltration", ["hoch","mittel","gering"])

formblatt_b = evaluate_formblatt_b(
    gebaeudetyp, baujahr, wohneinheiten,
    personen, nutzung, fensterlueftung, infiltration
)

# -----------------------------
# PARAMETER
# -----------------------------
ANE = st.number_input("Fläche (m²)", 30, 300, 80)

# 🔥 NEUE BERECHNUNG
levels = calculate_ventilation_levels(
    ANE,
    personen,
    nutzung
)

st.subheader("Lüftungsstufen (normnah)")

st.write(levels)

# -----------------------------
# RAUMDATEN
# -----------------------------
df_rooms = st.data_editor(pd.DataFrame({
    "Raum": ["Wohnzimmer","Bad"],
    "Typ": ["Zuluft","Abluft"],
    "Abluft (m³/h)": [0, 40]
}), num_rows="dynamic")

# -----------------------------
# BERECHNUNG
# -----------------------------
q_req, q_ab, delta, df_res = calculate_ventilation(df_rooms, ANE, 0.3)

formblatt_c = evaluate_formblatt_c(levels, q_ab)

formblatt_d = evaluate_formblatt_d(
    formblatt_a,
    formblatt_b,
    formblatt_c
)

formblatt_e = generate_formblatt_e({
    "levels": levels,
    "formblatt_d": formblatt_d
})

st.text_area("Konzept", formblatt_e, height=300)

# -----------------------------
# SPEICHERN
# -----------------------------
st.session_state["project"]["WE1"] = {
    "res": {
        "formblatt_a": formblatt_a,
        "formblatt_b": formblatt_b,
        "formblatt_c": formblatt_c,
        "formblatt_d": formblatt_d,
        "formblatt_e": formblatt_e,
        "levels": levels
    }
}

# -----------------------------
# EXPORT
# -----------------------------
if st.button("PDF Export"):

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    create_multi_pdf(tmp.name, st.session_state["project"])

    with open(tmp.name, "rb") as f:
        st.download_button("Download", f)
