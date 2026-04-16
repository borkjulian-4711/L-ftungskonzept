import streamlit as st
import pandas as pd
import tempfile

from logic.ventilation import calculate_ventilation
from logic.room_airflows import apply_room_airflows
from logic.ventilation_levels import calculate_ventilation_levels
from logic.air_network import propagate_flows, calculate_uld

from logic.formblatt_a import evaluate_formblatt_a
from logic.formblatt_b import evaluate_formblatt_b
from logic.formblatt_c import evaluate_formblatt_c
from logic.formblatt_d import evaluate_formblatt_d
from logic.formblatt_e import generate_formblatt_e
from logic.validation import validate_din

from export.pdf_generator import create_multi_pdf


# -----------------------------
# INIT
# -----------------------------
st.title("🌀 Lüftungskonzept nach DIN 1946-6")

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

gebaeudetyp = st.selectbox("Gebäudetyp", ["EFH","MFH","Wohnung"])
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
# LÜFTUNGSSTUFEN
# -----------------------------
st.header("Lüftungsstufen")

ANE = st.number_input("Fläche (m²)", 30, 300, 80)

levels = calculate_ventilation_levels(ANE, personen, nutzung)

st.write(levels)

# -----------------------------
# RAUMTABELLE MIT DROPDOWNS
# -----------------------------
st.header("Räume & Luftführung")

default_df = pd.DataFrame({
    "Raum": ["Wohnzimmer", "Flur", "Bad"],
    "Typ": ["Zuluft", "Überström", "Abluft"],
    "Kategorie (DIN 1946-6)": ["Wohnzimmer", "Flur", "Bad"],
    "Überströmt nach": ["Flur", "Bad", ""]
})

typ_options = ["Zuluft", "Überström", "Abluft"]

din_options = [
    "Wohnzimmer","Schlafzimmer","Kinderzimmer","Arbeitszimmer",
    "Küche","Bad","Duschraum","WC","Flur",
    "Abstellraum","Hauswirtschaftsraum"
]

raumliste = default_df["Raum"].tolist()

df_rooms = st.data_editor(
    default_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={

        "Typ": st.column_config.SelectboxColumn(
            options=typ_options
        ),

        "Kategorie (DIN 1946-6)": st.column_config.SelectboxColumn(
            options=din_options
        ),

        "Überströmt nach": st.column_config.SelectboxColumn(
            options=[""] + raumliste
        )
    }
)

df_rooms = df_rooms.fillna("")

# -----------------------------
# VOLUMENSTRÖME
# -----------------------------
df_rooms = apply_room_airflows(df_rooms)

st.subheader("Volumenströme")
st.dataframe(df_rooms)

# -----------------------------
# LUFTNETZ
# -----------------------------
flows = propagate_flows(df_rooms)

st.subheader("Luftströme")

for r, f in flows.items():
    st.write(f"{r}: {round(f,1)} m³/h")

# -----------------------------
# ÜLD
# -----------------------------
uld = calculate_uld(flows, df_rooms)

st.subheader("ÜLD")

for (a,b), d in uld.items():
    st.write(f"{a} → {b}: {d['Anzahl']} Stück")

# -----------------------------
# BERECHNUNG
# -----------------------------
q_req, q_ab, delta, df_res = calculate_ventilation(df_rooms, ANE, 0.3)

# -----------------------------
# VALIDIERUNG
# -----------------------------
errors, warnings = validate_din(df_rooms, flows, q_req, q_ab)

if errors:
    st.error("❌ Fehler:")
    for e in errors:
        st.write("- " + e)

if warnings:
    st.warning("⚠️ Hinweise:")
    for w in warnings:
        st.write("- " + w)

# -----------------------------
# FORMBLÄTTER
# -----------------------------
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

st.header("Konzept")
st.text_area("Text", formblatt_e, height=250)

# -----------------------------
# EXPORT
# -----------------------------
st.header("Export")

if st.button("PDF Export"):

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
