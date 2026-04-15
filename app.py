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
# RAUMTABELLE
# -----------------------------
st.subheader("Räume & Luftführung")

df_rooms = st.data_editor(
    pd.DataFrame({
        "Raum": ["Wohnzimmer", "Flur", "Bad"],
        "Typ": ["Zuluft", "Überström", "Abluft"],
        "Innenliegend": [False, False, True],
        "Kategorie (DIN 1946-6)": ["Wohnzimmer", "Flur", "Bad"],
        "DIN 18017 Kategorie": ["", "", "R-ZD (ca. 40 m³/h)"],
        "Überströmt nach": ["Flur", "Bad", ""]
    }),
    num_rows="dynamic",
    use_container_width=True,
    column_config={

        "Raum": st.column_config.TextColumn("Raumname"),

        "Typ": st.column_config.SelectboxColumn(
            "Raumtyp",
            options=["Zuluft", "Überström", "Abluft"]
        ),

        "Kategorie (DIN 1946-6)": st.column_config.SelectboxColumn(
            "Raumkategorie",
            options=raum_kategorien
        ),

        "DIN 18017 Kategorie": st.column_config.SelectboxColumn(
            "Abluft nach DIN 18017-3",
            options=din18017_kategorien
        ),

        "Innenliegend": st.column_config.CheckboxColumn("Innenliegend"),

        "Überströmt nach": st.column_config.SelectboxColumn(
            "Überströmt nach",
            options=["", "Wohnzimmer", "Flur", "Bad"]
        )
    }
)

# -----------------------------
# TEXTVARIANTE
# -----------------------------
st.subheader("Textausgabe")

text_mode = st.selectbox(
    "Textvariante wählen",
    {
        "Langtext (Standard)": "lang",
        "Kurztext": "kurz",
        "Behördentext": "behoerde"
    }
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
            "text": text,
            "warnings": warnings
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

if st.button("📄 Gesamt-PDF erzeugen"):

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    create_multi_pdf(tmp.name, st.session_state["project"])

    with open(tmp.name, "rb") as f:
        st.download_button("Download PDF", f)
