import streamlit as st
import pandas as pd
import tempfile

from logic.ventilation import calculate_ventilation, calculate_ald_uld
from export.pdf_generator import create_din_pdf

st.title("Lüftungskonzept Tool")

# Sidebar
ANE = st.sidebar.number_input("Fläche (m²)", 30, 300, 80)

fWS = st.sidebar.selectbox("fWS", [0.2, 0.3, 0.4])

# Räume
df_rooms = st.data_editor(pd.DataFrame({
    "Raum": ["Wohnzimmer", "Bad"],
    "Typ": ["Zuluft", "Abluft"],
    "Innenliegend": [False, True],
    "Kategorie": ["", "Bad"]
}), num_rows="dynamic")

if st.button("Berechnen"):

    q_required, q_abluft, delta, df_result = calculate_ventilation(df_rooms, ANE, fWS)
    n_ald, n_uld, dist = calculate_ald_uld(delta, df_result)

    st.write("Feuchteschutz:", q_required)
    st.write("Abluft:", q_abluft)

    st.write("ALD:", n_ald)
    st.write("ÜLD:", n_uld)

    text = f"ALD: {n_ald}, ÜLD: {n_uld}"

    if st.button("PDF erzeugen"):

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

        create_din_pdf(
            tmp.name,
            {"name": "Projekt", "ANE": ANE, "fWS": fWS},
            {"q_required": q_required, "q_abluft": q_abluft, "delta": delta},
            df_result,
            text,
            n_ald,
            n_uld
        )

        with open(tmp.name, "rb") as f:
            st.download_button("Download PDF", f, file_name="report.pdf")