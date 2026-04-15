import streamlit as st
import pandas as pd
import tempfile
import matplotlib.pyplot as plt
import networkx as nx

from logic.ventilation import (
    calculate_ventilation,
    calculate_ald,
    build_graph_from_rooms,
    calculate_paths,
    calculate_uld_from_graph
)

from logic.checks import run_checks
from logic.text_generator import generate_concept_text
from export.pdf_generator import create_pdf

st.title("🌀 Lüftungskonzept nach DIN 1946-6")

# Sidebar
ANE = st.sidebar.number_input("Fläche Nutzungseinheit (m²)", 30, 300, 80)
fWS = st.sidebar.selectbox("Faktor fWS", [0.2, 0.3, 0.4])

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

st.subheader("Räume & Luftführung")

df_rooms = st.data_editor(
    pd.DataFrame({
        "Raum": ["Wohnzimmer","Flur","Bad"],
        "Typ": ["Zuluft","Überström","Abluft"],
        "Innenliegend": [False,False,True],
        "Kategorie": ["Wohnzimmer","Flur","Bad"],
        "DIN 18017 Kategorie": ["","","R-ZD (ca. 40 m³/h)"],
        "Überströmt nach": ["Flur","Bad",""]
    }),
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Typ": st.column_config.SelectboxColumn(options=["Zuluft","Überström","Abluft"]),
        "Kategorie": st.column_config.SelectboxColumn(options=raum_kategorien),
        "DIN 18017 Kategorie": st.column_config.SelectboxColumn(options=din18017_kategorien),
        "Innenliegend": st.column_config.CheckboxColumn(),
        "Überströmt nach": st.column_config.TextColumn()
    }
)
st.subheader("Textausgabe")

text_mode = st.selectbox(
    "Textvariante wählen",
    ["lang", "kurz", "behoerde"]
)
if st.button("Berechnen"):

    q_req, q_ab, delta, df_res = calculate_ventilation(df_rooms, ANE, fWS)
    n_ald = calculate_ald(delta)

    G = build_graph_from_rooms(df_res)
    paths = calculate_paths(G, df_res)

    n_uld, uld_edges = calculate_uld_from_graph(G, df_res, paths)

    errors, warnings = run_checks(df_res, G, delta)

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

    st.session_state["res"] = {
        "q_required": q_req,
        "q_abluft": q_ab,
        "delta": delta,
        "df": df_res,
        "n_ald": n_ald,
        "n_uld": n_uld,
        "uld_edges": uld_edges,
        "paths": paths,
        "errors": errors,
        "warnings": warnings,
        "graph": G,
        "text": text
    }

# Anzeige
if "res" in st.session_state:

    r = st.session_state["res"]

    st.subheader("Ergebnisse")

    st.write("Feuchteschutz:", r["q_required"])
    st.write("Abluft:", r["q_abluft"])
    st.write("ALD:", r["n_ald"])
    st.write("ÜLD:", r["n_uld"])

    st.subheader("Raumwerte")
    st.dataframe(r["df"], use_container_width=True)

    st.subheader("Überströmöffnungen")
    for (a, b), d in r["uld_edges"].items():
        st.write(f"{a} → {b}: {d['Anzahl']} ÜLD ({d['Volumenstrom']} m³/h)")

    st.subheader("Konzeptbeschreibung")
    st.text_area("Fließtext", r["text"], height=300)

    st.subheader("Prüfung")
    for e in r["errors"]:
        st.error(e)
    for w in r["warnings"]:
        st.warning(w)

    st.subheader("Luftströmung")

    fig, ax = plt.subplots()
    pos = nx.spring_layout(r["graph"])
    nx.draw(r["graph"], pos, with_labels=True, ax=ax)
    st.pyplot(fig)

    if st.button("PDF erzeugen"):

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

        create_pdf(tmp.name, ANE, r)

        with open(tmp.name, "rb") as f:
            st.download_button("Download PDF", f)
