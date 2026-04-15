import streamlit as st
import pandas as pd
import tempfile

from logic.ventilation import calculate_ventilation, calculate_ald_uld
from export.pdf_generator import create_din_pdf

st.title("🌀 Lüftungskonzept Tool")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Projekt")

ANE = st.sidebar.number_input("Fläche (m²)", 30, 300, 80)

fWS = st.sidebar.selectbox("fWS", [0.2, 0.3, 0.4])

# -----------------------------
# Räume
# -----------------------------
st.subheader("Räume")

df_rooms = st.data_editor(pd.DataFrame({
    "Raum": ["Wohnzimmer", "Schlafzimmer", "Bad"],
    "Typ": ["Zuluft", "Zuluft", "Abluft"],
    "Innenliegend": [False, False, True],
    "Kategorie": ["", "", "Bad"]
}), num_rows="dynamic")

# -----------------------------
# Berechnung
# -----------------------------
if st.button("Berechnen"):

    q_required, q_abluft, delta, df_result = calculate_ventilation(df_rooms, ANE, fWS)
    n_ald, n_uld, dist = calculate_ald_uld(delta, df_result)

    st.subheader("Ergebnisse")

    col1, col2, col3 = st.columns(3)

    col1.metric("Feuchteschutz", f"{round(q_required,1)} m³/h")
    col2.metric("Abluft", f"{round(q_abluft,1)} m³/h")

    if delta > 0:
        col3.metric("Fehlend", f"{round(delta,1)} m³/h", delta_color="inverse")
    else:
        col3.metric("Reserve", f"{round(abs(delta),1)} m³/h")

    st.divider()

    st.subheader("ALD / ÜLD")

    st.write(f"**ALD:** {n_ald} Stück")
    st.write(f"**ÜLD:** {n_uld} Stück")

    if dist:
        st.write("**Verteilung ALD:**")
        for room, count in dist.items():
            st.write(f"- {room}: {count} Stück")

    st.divider()

    st.subheader("Raumübersicht")
    st.dataframe(df_result, use_container_width=True)

    # -----------------------------
    # PDF
    # -----------------------------
    text = f"""
Feuchteschutz: {q_required} m³/h  
Abluft: {q_abluft} m³/h  

ALD: {n_ald} Stück  
ÜLD: {n_uld} Stück  
"""

    st.divider()

    if st.button("📄 PDF erzeugen"):

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
            st.download_button("📥 Download PDF", f, file_name="lueftungskonzept.pdf")
