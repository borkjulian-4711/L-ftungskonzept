import streamlit as st
import pandas as pd

from logic.din1946_core import (
    calculate_qv_ges,
    calculate_levels,
    distribute_airflows,
    apply_exhaust_values,
    balance_system
)

st.title("🌀 DIN 1946-6 – Normkonforme Berechnung")

# -----------------------------
# INPUT
# -----------------------------
st.header("Gebäudedaten")

ANE = st.number_input("Wohnfläche ANE (m²)", 30, 300, 80)

system = st.selectbox("System", [
    "freie Lüftung",
    "ventilatorgestützt",
    "kombiniert"
])

# -----------------------------
# BERECHNUNG qv
# -----------------------------
qv = calculate_qv_ges(ANE)

levels = calculate_levels(qv)

st.subheader("Lüftungsstufen")
st.write(levels)

selected_level = st.selectbox("Auslegungsstufe", list(levels.keys()))

qv_selected = levels[selected_level]

st.write("Auslegungsvolumenstrom:", qv_selected, "m³/h")

# -----------------------------
# RAUMTABELLE
# -----------------------------
st.header("Räume")

df_rooms = st.data_editor(pd.DataFrame({
    "Raum": ["Wohnzimmer", "Schlafzimmer", "Bad"],
    "Fläche": [20, 15, 6],
    "Typ": ["Zuluft", "Zuluft", "Abluft"],
    "Kategorie (DIN 1946-6)": ["Wohnzimmer", "Schlafzimmer", "Bad"]
}), num_rows="dynamic")

df_rooms = df_rooms.fillna(0)

# -----------------------------
# VERTEILUNG
# -----------------------------
df_rooms = distribute_airflows(df_rooms, qv_selected)

df_rooms = apply_exhaust_values(df_rooms)

st.subheader("Raumweise Luftmengen")
st.dataframe(df_rooms)

# -----------------------------
# BILANZ
# -----------------------------
zu, ab, diff = balance_system(df_rooms)

st.subheader("Bilanz")

st.write("Zuluft:", zu)
st.write("Abluft:", ab)
st.write("Differenz:", diff)

# -----------------------------
# BEWERTUNG
# -----------------------------
if abs(diff) < 10:
    st.success("System ausgeglichen")
else:
    st.warning("System nicht ausgeglichen – Anpassung erforderlich")
