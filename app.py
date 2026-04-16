import streamlit as st
import pandas as pd
import tempfile

from logic.ventilation import calculate_ventilation
from logic.room_airflows import apply_room_airflows
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


st.title("🌀 Lüftungskonzept DIN 1946-6")

# -----------------------------
# FORMBLATT B (relevant für Nutzung)
# -----------------------------
personen = st.number_input("Personen", 1, 10, 2)
nutzung = st.selectbox("Nutzung", ["normal","reduziert","hoch"])

ANE = st.number_input("Fläche", 30, 300, 80)

levels = calculate_ventilation_levels(ANE, personen, nutzung)

st.subheader("Lüftungsstufen")
st.write(levels)

# -----------------------------
# RAUMTABELLE
# -----------------------------
df_rooms = st.data_editor(pd.DataFrame({
    "Raum": ["Wohnzimmer","Bad","WC"],
    "Typ": ["Zuluft","Abluft","Abluft"],
    "Kategorie (DIN 1946-6)": ["Wohnzimmer","Bad","WC"]
}), num_rows="dynamic")

# -----------------------------
# VOLLMENSTROM AUTOMATISCH
# -----------------------------
df_rooms = apply_room_airflows(df_rooms)

st.subheader("Raumweise Volumenströme")

st.dataframe(df_rooms)

# -----------------------------
# BERECHNUNG
# -----------------------------
q_req, q_ab, delta, df_res = calculate_ventilation(df_rooms, ANE, 0.3)

st.write("Abluft gesamt:", q_ab)
st.write("Feuchteschutz:", q_req)
st.write("Differenz:", delta)

# -----------------------------
# FORMBLATT C–E
# -----------------------------
formblatt_c = evaluate_formblatt_c(levels, q_ab)

formblatt_d = evaluate_formblatt_d(
    {"erforderlich": True},
    {"fensterlueftung": True},
    formblatt_c
)

formblatt_e = generate_formblatt_e({
    "levels": levels,
    "formblatt_d": formblatt_d
})

st.text_area("Konzept", formblatt_e)

# -----------------------------
# EXPORT
# -----------------------------
if st.button("PDF Export"):

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    create_multi_pdf(tmp.name, {
        "WE1": {
            "res": {
                "levels": levels,
                "formblatt_c": formblatt_c,
                "formblatt_d": formblatt_d,
                "formblatt_e": formblatt_e
            }
        }
    })

    with open(tmp.name, "rb") as f:
        st.download_button("Download", f)
