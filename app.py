
import streamlit as st
import pandas as pd
import tempfile
import matplotlib.pyplot as plt
import networkx as nx

from logic.ventilation import *
from logic.checks import run_checks
from export.pdf_generator import create_din_pdf

st.title("🌀 Lüftungskonzept Tool")

# Sidebar
ANE = st.sidebar.number_input("Fläche", 30, 300, 80)
fWS = st.sidebar.selectbox("fWS", [0.2, 0.3, 0.4])

# Räume
st.subheader("Räume")

df_rooms = st.data_editor(
    pd.DataFrame({
        "Raum": ["Wohnzimmer", "Flur", "Bad"],
        "Typ": ["Zuluft", "Überström", "Abluft"],
        "Innenliegend": [False, False, True],
        "Kategorie": ["Wohnraum", "Flur", "Bad"],
        "DIN 18017 Kategorie": ["", "", "R-ZD"]
    }),
    num_rows="dynamic",
    column_config={
        "Typ": st.column_config.SelectboxColumn(
            options=["Zuluft", "Überström", "Abluft"]
        ),
        "Kategorie": st.column_config.SelectboxColumn(
            options=["Wohnraum","Schlafzimmer","Flur","Küche","Bad","WC"]
        ),
        "DIN 18017 Kategorie": st.column_config.SelectboxColumn(
            options=["","R-ZD","R-BD","R-PN","R-PD"]
        ),
    }
)

# Verbindungen
st.subheader("Verbindungen")

df_edges = st.data_editor(pd.DataFrame({
    "Von": ["Wohnzimmer","Flur"],
    "Nach": ["Flur","Bad"]
}), num_rows="dynamic")

# Berechnung
if st.button("Berechnen"):

    q_required, q_abluft, delta, df_result = calculate_ventilation(df_rooms, ANE, fWS)
    n_ald, _ = calculate_ald(delta, df_result)

    G = build_real_graph(df_edges)
    paths = calculate_paths(G, df_result)
    n_uld, uld_edges = calculate_uld_from_paths(paths)

    errors, warnings = run_checks(df_result, G, {"delta": delta})

    st.session_state["res"] = {
        "q_required": q_required,
        "q_abluft": q_abluft,
        "delta": delta,
        "df": df_result,
        "n_ald": n_ald,
        "n_uld": n_uld,
        "paths": paths,
        "errors": errors,
        "warnings": warnings
    }

# Anzeige
if "res" in st.session_state:

    r = st.session_state["res"]

    st.subheader("Ergebnisse")
    st.write("Feuchteschutz:", r["q_required"])
    st.write("Abluft:", r["q_abluft"])

    st.write("ALD:", r["n_ald"])
    st.write("ÜLD:", r["n_uld"])

    st.subheader("Prüfung")

    for e in r["errors"]:
        st.error(e)

    for w in r["warnings"]:
        st.warning(w)

    if not r["errors"] and not r["warnings"]:
        st.success("OK")

    st.subheader("Luftgraph")

    fig, ax = plt.subplots()
    pos = nx.spring_layout(build_real_graph(df_edges))
    nx.draw(build_real_graph(df_edges), pos, with_labels=True, ax=ax)
    st.pyplot(fig)

    if st.button("📄 PDF"):

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

        create_din_pdf(
            tmp.name,
            {"ANE": ANE},
            r,
            r["df"],
            r["errors"],
            r["warnings"],
            r["n_ald"],
            r["n_uld"],
            r["paths"]
        )

        with open(tmp.name, "rb") as f:
            st.download_button("Download PDF", f)
