import streamlit as st
import pandas as pd
import tempfile
import matplotlib.pyplot as plt
import networkx as nx

from logic.ventilation import (
    calculate_ventilation,
    calculate_ald,
    build_graph,
    calculate_paths,
    calculate_uld
)

from logic.checks import run_checks
from export.pdf_generator import create_pdf

st.title("🌀 Lüftungskonzept nach DIN 1946-6")

# Sidebar
ANE = st.sidebar.number_input("Fläche Nutzungseinheit (m²)", 30, 300, 80)
fWS = st.sidebar.selectbox("fWS", [0.2, 0.3, 0.4])

# DIN 1946 Räume
raum_kategorien = [
    "Wohnzimmer",
    "Schlafzimmer",
    "Kinderzimmer",
    "Arbeitszimmer",
    "Küche",
    "Bad",
    "Duschraum",
    "WC",
    "Flur",
    "Abstellraum",
    "Hauswirtschaftsraum"
]

# Räume
st.subheader("Räume")

df_rooms = st.data_editor(
    pd.DataFrame({
        "Raum": ["Wohnzimmer", "Bad"],
        "Typ": ["Zuluft", "Abluft"],
        "Innenliegend": [False, True],
        "Kategorie": ["Wohnzimmer", "Bad"],
        "DIN 18017 Kategorie": ["", "R-ZD"]
    }),
    num_rows="dynamic",
    column_config={
        "Typ": st.column_config.SelectboxColumn(
            options=["Zuluft", "Überström", "Abluft"]
        ),
        "Kategorie": st.column_config.SelectboxColumn(
            options=raum_kategorien
        ),
"DIN 18017 Kategorie": st.column_config.SelectboxColumn(
    "DIN 18017 Kategorie (inkl. Volumenstrom)",
    options=[
        "",
        "R-ZD (ca. 40 m³/h)",
        "R-BD (ca. 32 m³/h)",
        "R-PN (ca. 48 m³/h)",
        "R-PD (ca. 40 m³/h)"
    ]
)
    }
)

# Verbindungen
st.subheader("Raumverbindungen")

df_edges = st.data_editor(
    pd.DataFrame({
        "Von": ["Wohnzimmer"],
        "Nach": ["Bad"]
    }),
    num_rows="dynamic"
)

# Berechnung
if st.button("Berechnen"):

    q_req, q_ab, delta, df_res = calculate_ventilation(df_rooms, ANE, fWS)
    n_ald = calculate_ald(delta, df_res)

    G = build_graph(df_res, df_edges)
    paths = calculate_paths(G, df_res)
    n_uld, _ = calculate_uld(paths)

    errors, warnings = run_checks(df_res, G, delta)

    st.session_state["res"] = {
        "q_required": q_req,
        "q_abluft": q_ab,
        "delta": delta,
        "df": df_res,
        "n_ald": n_ald,
        "n_uld": n_uld,
        "paths": paths,
        "errors": errors,
        "warnings": warnings,
        "graph": G
    }

# Anzeige
if "res" in st.session_state:

    r = st.session_state["res"]

    st.write("Feuchteschutz:", r["q_required"])
    st.write("Abluft:", r["q_abluft"])
    st.write("ALD:", r["n_ald"])
    st.write("ÜLD:", r["n_uld"])

    for e in r["errors"]:
        st.error(e)

    for w in r["warnings"]:
        st.warning(w)

    if not r["errors"] and not r["warnings"]:
        st.success("System OK")

    fig, ax = plt.subplots()
    pos = nx.spring_layout(r["graph"])
    nx.draw(r["graph"], pos, with_labels=True, ax=ax)
    st.pyplot(fig)

    if st.button("PDF erzeugen"):

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

        create_pdf(tmp.name, ANE, r)

        with open(tmp.name, "rb") as f:
            st.download_button("Download PDF", f)
