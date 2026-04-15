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

if "auto_df" not in st.session_state:
    st.session_state["auto_df"] = None


st.title("🌀 Lüftungskonzept nach DIN 1946-6")

# -----------------------------
# PROJEKTDATEN
# -----------------------------
st.header("Projektdaten")

projekt = st.text_input("Projektname", key="projekt")
adresse = st.text_input("Adresse", key="adresse")
bearbeiter = st.text_input("Bearbeiter", key="bearbeiter")

meta = {
    "projekt": projekt,
    "adresse": adresse,
    "bearbeiter": bearbeiter
}

# -----------------------------
# WOHNUNGEN
# -----------------------------
st.header("Wohnungen")

suffix = st.text_input("Bezeichnung (optional)", key="suffix")

if st.button("➕ Wohnung hinzufügen", key="add_flat"):

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
    list(st.session_state["project"].keys()),
    key="flat_select"
)

# -----------------------------
# PARAMETER
# -----------------------------
st.header("Eingabedaten")

ANE = st.number_input(
    "Fläche Nutzungseinheit (m²)",
    30, 300, 80,
    key="ane"
)

fWS = st.selectbox(
    "Faktor fWS",
    [0.2, 0.3, 0.4],
    key="fws"
)

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
# DATENQUELLE (AUTO ODER DEFAULT)
# -----------------------------
default_df = pd.DataFrame({
    "Raum": ["Wohnzimmer", "Flur", "Bad"],
    "Typ": ["Zuluft", "Überström", "Abluft"],
    "Innenliegend": [False, False, True],
    "Kategorie (DIN 1946-6)": ["Wohnzimmer", "Flur", "Bad"],
    "DIN 18017 Kategorie": ["", "", "R-ZD (ca. 40 m³/h)"],
    "Überströmt nach": ["Flur", "Bad", ""]
})

if st.session_state["auto_df"] is not None:
    default_df = st.session_state["auto_df"]

# -----------------------------
# RAUMTABELLE
# -----------------------------
st.subheader("Räume & Luftführung")

df_rooms = st.data_editor(
    default_df,
    num_rows="dynamic",
    use_container_width=True,
    key="rooms_editor",
    column_config={

        "Typ": st.column_config.SelectboxColumn(
            options=["Zuluft", "Überström", "Abluft"]
        ),

        "Kategorie (DIN 1946-6)": st.column_config.SelectboxColumn(
            options=raum_kategorien
        ),

        "DIN 18017 Kategorie": st.column_config.SelectboxColumn(
            options=din18017_kategorien
        )
    }
)

# -----------------------------
# INTELLIGENTE LUFTFÜHRUNG
# -----------------------------
st.subheader("Intelligente Luftführung")

if st.button("🧠 Luftführung automatisch erzeugen", key="auto_airflow"):
    st.session_state["auto_df"] = auto_connect_rooms(df_rooms)
    st.rerun()

# -----------------------------
# TEXTVARIANTE
# -----------------------------
text_mode = st.selectbox(
    "Textvariante",
    ["lang", "kurz", "behoerde"],
    key="text_mode"
)

# -----------------------------
# VALIDIERUNG
# -----------------------------
errors, warnings = validate_inputs(df_rooms)

if errors:
    st.error("❌ Fehler in den Eingaben:")
    for e in errors:
        st.write("- " + e)

elif warnings:
    st.warning("⚠️ Hinweise:")
    for w in warnings:
        st.write("- " + w)

# -----------------------------
# AUTO-BERECHNUNG
# -----------------------------
if not errors:

    q_req, q_ab, delta, df_res = calculate_ventilation(df_rooms, ANE, fWS)
    n_ald = calculate_ald(delta)

    G = build_graph_from_rooms(df_res)
    paths = calculate_paths(G, df_res)
    n_uld, uld_edges = calculate_uld_from_graph(G, df_res, paths)

    text = generate_concept_text(
        ANE,
        {
            "q_required": q_req,
            "q_abluft": q_ab,
            "delta": delta,
            "df": df_res,
            "n_ald": n_ald,
            "n_uld": n_uld,
            "uld_edges": uld_edges
        },
        mode=text_mode
    )

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
# ERGEBNISSE
# -----------------------------
if flat in st.session_state["project"]:

    flat_data = st.session_state["project"][flat]

    if "res" in flat_data:

        data = flat_data["res"]

        st.header("Ergebnisse")

        st.write("Feuchteschutz:", round(data["q_required"], 1))
        st.write("Abluft:", round(data["q_abluft"], 1))
        st.write("ALD:", data["n_ald"])
        st.write("ÜLD:", data["n_uld"])

        st.subheader("Überströmöffnungen")

        for (a, b), d in data["uld_edges"].items():
            st.write(f"{a} → {b}: {d['Anzahl']} ÜLD ({d['Volumenstrom']} m³/h)")

        st.subheader("Konzeptbeschreibung")
        st.text_area("Text", data["text"], height=300)

# -----------------------------
# PDF EXPORT
# -----------------------------
st.header("Export")

if st.button("📄 Gesamt-PDF erzeugen", key="pdf_export"):

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    create_multi_pdf(tmp.name, st.session_state["project"])

    with open(tmp.name, "rb") as f:
        st.download_button("Download PDF", f)
