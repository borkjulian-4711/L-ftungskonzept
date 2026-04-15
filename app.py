import streamlit as st
import pandas as pd
import tempfile
import matplotlib.pyplot as plt
import networkx as nx

from logic.ventilation import *
from logic.checks import run_checks
from export.pdf_generator import create_din_pdf
from ui.floorplan import upload_floorplan, define_rooms
from logic.floorplan_logic import auto_connect_rooms

st.title("🌀 Lüftungskonzept Tool")

# -----------------------------
# Sidebar
# -----------------------------
ANE = st.sidebar.number_input("Fläche", 30, 300, 80)
fWS = st.sidebar.selectbox("fWS", [0.2, 0.3, 0.4])

# -----------------------------
# Grundriss
# -----------------------------
st.header("Grundriss")

image = upload_floorplan()

rooms_pos = define_rooms()

# -----------------------------
# automatische Verbindungen
# -----------------------------
edges_auto = auto_connect_rooms(rooms_pos)

st.subheader("Automatische Verbindungen")

for e in edges_auto:
    st.write(f"{e[0]} ↔ {e[1]}")

# -----------------------------
# Raumtabelle
# -----------------------------
st.header("Raumdaten")

df_rooms = st.data_editor(
    pd.DataFrame({
        "Raum": [r["name"] for r in rooms_pos] if rooms_pos else ["Wohnzimmer"],
        "Typ": ["Zuluft"],
        "Innenliegend": [False],
        "Kategorie": ["Wohnraum"],
        "DIN 18017 Kategorie": [""]
    }),
    num_rows="dynamic",
    column_config={
        "Typ": st.column_config.SelectboxColumn(
            options=["Zuluft","Überström","Abluft"]
        ),
        "Kategorie": st.column_config.SelectboxColumn(
            options=["Wohnraum","Schlafzimmer","Flur","Küche","Bad","WC"]
        ),
        "DIN 18017 Kategorie": st.column_config.SelectboxColumn(
            options=["","R-ZD","R-BD","R-PN","R-PD"]
        )
    }
)

# -----------------------------
# Berechnung
# -----------------------------
if st.button("Berechnen"):

    q_required, q_abluft, delta, df_result = calculate_ventilation(df_rooms, ANE, fWS)
    n_ald, _ = calculate_ald(delta, df_result)

    G = build_graph_from_edges(edges_auto)
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
        "warnings": warnings,
        "graph": G
    }

# -----------------------------
# Anzeige
# -----------------------------
if "res" in st.session_state:

    r = st.session_state["res"]

    st.header("Ergebnisse")

    st.write("Feuchteschutz:", r["q_required"])
    st.write("Abluft:", r["q_abluft"])

    st.write("ALD:", r["n_ald"])
    st.write("ÜLD:", r["n_uld"])

    # Fehler
    for e in r["errors"]:
        st.error(e)

    for w in r["warnings"]:
        st.warning(w)

    if not r["errors"] and not r["warnings"]:
        st.success("System OK")

    # Graph
    st.subheader("Luftströmung")

    fig, ax = plt.subplots()
    pos = nx.spring_layout(r["graph"])
    nx.draw(r["graph"], pos, with_labels=True, node_color="lightblue", ax=ax)

    st.pyplot(fig)

    # PDF
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
