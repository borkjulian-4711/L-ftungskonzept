import streamlit as st
import pandas as pd
import tempfile

from logic.ventilation import (
    calculate_ventilation,
    calculate_ald,
    build_airflow_graph,
    check_airflow,
    calculate_uld_from_graph
)

from export.pdf_generator import create_din_pdf

st.title("🌀 Lüftungskonzept Tool")

ANE = st.sidebar.number_input("Fläche", 30, 300, 80)
fWS = st.sidebar.selectbox("fWS", [0.2, 0.3, 0.4])

df_rooms = st.data_editor(pd.DataFrame({
    "Raum": ["Wohnzimmer", "Flur", "Bad"],
    "Typ": ["Zuluft", "Überström", "Abluft"],
    "Innenliegend": [False, False, True],
    "Kategorie": ["", "", "Bad"],
    "DIN 18017 Kategorie": ["", "", "R-ZD"]
}), num_rows="dynamic")

if st.button("Berechnen"):

    q_required, q_abluft, delta, df_result = calculate_ventilation(df_rooms, ANE, fWS)

    n_ald, ald_dist = calculate_ald(delta, df_result)

    G = build_airflow_graph(df_result)

    paths, missing = check_airflow(G, df_result)

    n_uld, uld_edges = calculate_uld_from_graph(G, paths, df_result)

    st.subheader("Ergebnisse")
    st.write("Feuchteschutz:", q_required)
    st.write("Abluft:", q_abluft)

    st.subheader("ALD")
    st.write(n_ald, "Stück")

    st.subheader("Luftpfade")
    for p in paths:
        st.write(" → ".join(p))

    if missing:
        st.error(f"Keine Verbindung für: {missing}")

    st.subheader("ÜLD (Kanten)")
    for edge, n in uld_edges.items():
        st.write(f"{edge[0]} → {edge[1]}: {n} ÜLD")

    if st.button("PDF"):

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

        create_din_pdf(
            tmp.name,
            {"ANE": ANE},
            {"q_required": q_required, "q_abluft": q_abluft},
            df_result,
            "",
            n_ald,
            n_uld,
            paths
        )

        with open(tmp.name, "rb") as f:
            st.download_button("Download", f)
