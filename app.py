import streamlit as st
import pandas as pd
import tempfile

from logic.ventilation import calculate_ventilation
from logic.room_airflows import apply_room_airflows
from logic.ventilation_levels import calculate_ventilation_levels
from logic.air_network import propagate_flows, calculate_uld
from logic.formblatt_c import evaluate_formblatt_c
from logic.formblatt_d import evaluate_formblatt_d
from logic.formblatt_e import generate_formblatt_e
from export.pdf_generator import create_multi_pdf


st.title("🌀 Lüftungskonzept DIN 1946-6")

# -----------------------------
# PARAMETER
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
    "Raum": ["Wohnzimmer","Flur","Bad"],
    "Typ": ["Zuluft","Überström","Abluft"],
    "Kategorie (DIN 1946-6)": ["Wohnzimmer","Flur","Bad"],
    "Überströmt nach": ["Flur","Bad",""]
}), num_rows="dynamic")

# -----------------------------
# VOLLMENSTROM
# -----------------------------
df_rooms = apply_room_airflows(df_rooms)

st.subheader("Raumdaten mit Volumenstrom")
st.dataframe(df_rooms)

# -----------------------------
# LUFTNETZ
# -----------------------------
flows = propagate_flows(df_rooms)

st.subheader("Luftströme im Netz")

for r, f in flows.items():
    st.write(f"{r}: {round(f,1)} m³/h")

# -----------------------------
# ÜLD
# -----------------------------
uld = calculate_uld(flows, df_rooms)

st.subheader("Überströmöffnungen")

for (a,b), d in uld.items():
    st.write(f"{a} → {b}: {d['Anzahl']} ÜLD ({d['Volumenstrom']} m³/h)")

# -----------------------------
# GESAMT
# -----------------------------
q_req, q_ab, delta, df_res = calculate_ventilation(df_rooms, ANE, 0.3)

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
