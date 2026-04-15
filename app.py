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

from logic.text_generator import generate_concept_text
from logic.validation import validate_inputs
from logic.airflow_intelligence import auto_connect_rooms
from export.pdf_generator import create_multi_pdf


# -----------------------------
# SESSION STATE
# -----------------------------
if "project" not in st.session_state:
    st.session_state["project"] = {}

if "counter" not in st.session_state:
    st.session_state["counter"] = 1


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
# WOHNUNGEN
# -----------------------------
st.header("Wohnungen")

suffix = st.text_input("Bezeichnung (optional)")

if st.button("➕ Wohnung hinzufügen"):

    name = f"WE{st.session_state['counter']}"

    if suffix:
        name += f" – {suffix}"

    st.session_state["project"][name] = {}
    st.session_state["counter"] += 1

if not st.session_state["project"]:
    st.warning("Bitte mindestens eine Wohnung anlegen")
    st.stop()

flat = st.selectbox(
    "Wohnung auswählen",
    list(st.session_state["project"].keys())
)

# -----------------------------
# PARAMETER
# -----------------------------
st.header("Eingabedaten")

ANE = st.number_input("Fläche Nutzungseinheit (m²)", 30, 300, 80)
fWS = st.selectbox("Faktor fWS", [0.2, 0.3, 0.4])

# -----------------------------
# DIN KATEGORIEN
# -----------------------------
raum_kategorien = [
    "Wohnzimmer","Schlafzimmer","Kinderzimmer","Arbeitszimmer",
    "Küche","Bad","Duschraum","WC","Flur","Abstellraum","Hauswirtschaftsraum"
]

din18017_kategorien = [
    "",
    "R-ZD (ca. 40 m³/h)",
    "R-BD (ca. 32 m³/h)",
    "R-PN (ca. 48 m³/h)",
    "R-PD (ca. 40 m³/h)"
]

# -----------------------------
# AUTO-LUFTFÜHRUNG BUTTON
# -----------------------------
st.subheader("Intelligente Luftführung")

if st.button("🧠 Luftführung automatisch erzeugen"):
    st.session_state["auto_df"] = auto_connect_rooms(df_rooms)
    st.rerun()

# -----------------------------
# RAUMTABELLE
# -----------------------------
st.subheader("Räume & Luftführung")

default_df = pd.DataFrame({
    "Raum": ["Wohnzimmer", "Flur", "Bad"],
    "Typ": ["Zuluft", "Überström", "Abluft"],
    "Innenliegend": [False, False, True],
    "Kategorie (DIN 1946-6)": ["Wohnzimmer", "Flur", "Bad"],
    "DIN 18017 Kategorie": ["", "", "R-ZD (ca. 40 m³/h)"],
    "Überströmt nach": ["Flur", "Bad", ""]
})

if "auto_df" in st.session_state:
    default_df = st.session_state["auto_df"]

df_rooms = st.data_editor(
    default_df,
    num_rows="dynamic",
    use_container_width=True
)

# -----------------------------
# AUTO-LUFTFÜHRUNG (JETZT RICHTIG!)
# -----------------------------
st.subheader("Intelligente Luftführung")

if st.button("🧠 Luftführung automatisch erzeugen"):
    st.session_state["auto_df"] = auto_connect_rooms(df_rooms)
    st.rerun()
# -----------------------------
# TEXTVARIANTE
# -----------------------------
text_mode = st.selectbox(
    "Textvariante",
    ["lang","kurz","behoerde"]
)

# -----------------------------
# VALIDIERUNG
# -----------------------------
errors, warnings = validate_inputs(df_rooms)

if errors:
    st.error("Fehler:")
    for e in errors:
        st.write(e)

elif warnings:
    st.warning("Hinweise:")
    for w in warnings:
        st.write(w)

# -----------------------------
# AUTO-BERECHNUNG
# -----------------------------
if not errors:

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
    }, mode=text_mode)

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
# ERGEBNIS
# -----------------------------
if flat in st.session_state["project"]:

    data = st.session_state["project"][flat]["res"]

    st.header("Ergebnisse")

    st.write("Feuchteschutz:", data["q_required"])
    st.write("Abluft:", data["q_abluft"])
    st.write("ALD:", data["n_ald"])
    st.write("ÜLD:", data["n_uld"])

    for (a,b), d in data["uld_edges"].items():
        st.write(f"{a} → {b}: {d['Anzahl']} ÜLD")

    st.text_area("Text", data["text"], height=300)

# -----------------------------
# EXPORT
# -----------------------------
if st.button("📄 PDF Export"):

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    create_multi_pdf(tmp.name, st.session_state["project"])

    with open(tmp.name, "rb") as f:
        st.download_button("Download", f)
