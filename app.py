import streamlit as st
import pandas as pd
import tempfile

from logic.ventilation import (
    calculate_ventilation,
    calculate_ald,
    build_graph_from_rooms,
    calculate_paths,
    calculate_uld_from_graph
)

from logic.ventilation_levels import calculate_ventilation_levels
from logic.text_generator import generate_concept_text
from logic.validation import validate_inputs
from logic.airflow_intelligence import auto_connect_rooms
from logic.formblatt_a import evaluate_formblatt_a
from logic.formblatt_b import evaluate_formblatt_b
from export.pdf_generator import create_multi_pdf


# -----------------------------
# SESSION STATE
# -----------------------------
if "project" not in st.session_state:
    st.session_state["project"] = {}

if "counter" not in st.session_state:
    st.session_state["counter"] = 1

if "auto_df" not in st.session_state:
    st.session_state["auto_df"] = None


st.title("🌀 Lüftungskonzept nach DIN 1946-6")

# -----------------------------
# PROJEKTDATEN
# -----------------------------
st.header("Projektdaten")

projekt = st.text_input("Projektname")
adresse = st.text_input("Adresse")
bearbeiter = st.text_input("Bearbeiter")

meta = {
    "projekt": projekt,
    "adresse": adresse,
    "bearbeiter": bearbeiter
}

# -----------------------------
# FORMBLATT A
# -----------------------------
st.header("Formblatt A – Notwendigkeit")

neubau = st.checkbox("Neubau")
sanierung = st.checkbox("Sanierung")
fensteranteil = st.slider("Fenster erneuert (%)", 0, 100, 50) / 100
luftdicht = st.checkbox("Luftdicht")

formblatt_a = evaluate_formblatt_a(
    neubau, sanierung, fensteranteil, luftdicht
)

# -----------------------------
# FORMBLATT B
# -----------------------------
st.header("Formblatt B – Gebäudedaten")

gebaeudetyp = st.selectbox(
    "Gebäudetyp",
    ["Einfamilienhaus", "Mehrfamilienhaus", "Wohnung"]
)

baujahr = st.number_input("Baujahr", 1900, 2025, 2000)
wohneinheiten = st.number_input("Wohneinheiten", 1, 50, 1)

personen = st.number_input("Personen", 1, 10, 2)

nutzung = st.selectbox(
    "Nutzung",
    ["normal", "reduziert", "hoch"]
)

fensterlueftung = st.checkbox("Fensterlüftung möglich")
infiltration = st.selectbox(
    "Infiltration",
    ["hoch", "mittel", "gering"]
)

formblatt_b = evaluate_formblatt_b(
    gebaeudetyp,
    baujahr,
    wohneinheiten,
    personen,
    nutzung,
    fensterlueftung,
    infiltration
)

st.write("Hinweise:", formblatt_b["hinweise"])

# -----------------------------
# WOHNUNGEN
# -----------------------------
st.header("Wohnungen")

if st.button("➕ Wohnung hinzufügen"):
    name = f"WE{st.session_state['counter']}"
    st.session_state["project"][name] = {}
    st.session_state["counter"] += 1

if not st.session_state["project"]:
    st.stop()

flat = st.selectbox("Wohnung", list(st.session_state["project"].keys()))

# -----------------------------
# PARAMETER
# -----------------------------
ANE = st.number_input("Fläche", 30, 300, 80)
fWS = st.selectbox("fWS", [0.2, 0.3, 0.4])

levels = calculate_ventilation_levels(ANE, fWS)

# -----------------------------
# RAUMTABELLE
# -----------------------------
df_rooms = st.data_editor(pd.DataFrame({
    "Raum": ["Wohnzimmer", "Bad"],
    "Typ": ["Zuluft", "Abluft"]
}), num_rows="dynamic")

# -----------------------------
# BERECHNUNG
# -----------------------------
errors, _ = validate_inputs(df_rooms)

if not errors:

    q_req, q_ab, delta, df_res = calculate_ventilation(df_rooms, ANE, fWS)

    text = generate_concept_text(
        ANE,
        {
            "q_required": q_req,
            "q_abluft": q_ab,
            "delta": delta,
            "df": df_res,
            "n_ald": 0,
            "n_uld": 0,
            "uld_edges": {}
        }
    )

    st.session_state["project"][flat] = {
        "meta": meta,
        "res": {
            "levels": levels,
            "formblatt_a": formblatt_a,
            "formblatt_b": formblatt_b,
            "text": text
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
