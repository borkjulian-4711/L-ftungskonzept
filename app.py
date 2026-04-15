import streamlit as st
import pandas as pd
import tempfile

from logic.ventilation import *
from logic.text_generator import generate_concept_text
from export.pdf_generator import create_multi_pdf

# -----------------------------
# Projekt State
# -----------------------------
if "project" not in st.session_state:
    st.session_state["project"] = {}

if "counter" not in st.session_state:
    st.session_state["counter"] = 1

st.title("🌀 Lüftungskonzept Tool")

# -----------------------------
# Projektinfos (Anhang E)
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
# Wohnung erstellen
# -----------------------------
st.header("Wohnungen")

suffix = st.text_input("Zusatz (optional)")

if st.button("➕ Wohnung hinzufügen"):

    name = f"WE{st.session_state['counter']}"
    if suffix:
        name += f" – {suffix}"

    st.session_state["project"][name] = {}
    st.session_state["counter"] += 1

if not st.session_state["project"]:
    st.stop()

flat = st.selectbox("Wohnung wählen", list(st.session_state["project"].keys()))

# -----------------------------
# Eingaben
# -----------------------------
ANE = st.number_input("Fläche", 30, 300, 80)
fWS = st.selectbox("fWS", [0.2,0.3,0.4])

df_rooms = st.data_editor(
    pd.DataFrame({
        "Raum":["Wohnzimmer","Bad"],
        "Typ":["Zuluft","Abluft"],
        "Innenliegend":[False,True],
        "Kategorie":["Wohnzimmer","Bad"],
        "DIN 18017 Kategorie":["","R-ZD"],
        "Überströmt nach":["Bad",""]
    }),
    num_rows="dynamic"
)

mode = st.selectbox("Text", ["lang","kurz","behoerde"])

# -----------------------------
# Berechnung
# -----------------------------
if st.button("Berechnen"):

    q_req, q_ab, delta, df_res = calculate_ventilation(df_rooms, ANE, fWS)
    n_ald = calculate_ald(delta)

    G = build_graph_from_rooms(df_res)
    paths = calculate_paths(G, df_res)
    n_uld, uld_edges = calculate_uld_from_graph(G, df_res, paths)

    text = generate_concept_text(ANE, {
        "q_required": q_req,
        "q_abluft": q_ab,
        "delta": delta,
        "df": df_res,
        "n_ald": n_ald,
        "n_uld": n_uld,
        "uld_edges": uld_edges
    }, mode)

    st.session_state["project"][flat] = {
        "meta": meta,
        "res": {
            "q_required": q_req,
            "q_abluft": q_ab,
            "delta": delta,
            "df": df_res,
            "n_ald": n_ald,
            "n_uld": n_uld,
            "uld_edges": uld_edges,
            "text": text
        }
    }

# -----------------------------
# Export
# -----------------------------
st.header("Export")

if st.button("📄 Gesamt-PDF"):

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    create_multi_pdf(tmp.name, st.session_state["project"])

    with open(tmp.name, "rb") as f:
        st.download_button("Download", f)
