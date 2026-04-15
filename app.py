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
from export.pdf_generator import create_pdf


st.title("🌀 Lüftungskonzept nach DIN 1946-6")

# -----------------------------
# Sidebar
# -----------------------------
ANE = st.sidebar.number_input("Fläche Nutzungseinheit (m²)", 30, 300, 80)
fWS = st.sidebar.selectbox("Faktor fWS", [0.2, 0.3, 0.4])

# -----------------------------
# Raumkategorien DIN 1946-6
# -----------------------------
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

# -----------------------------
# DIN 18017 Kategorien mit Anzeige
# -----------------------------
din18017_kategorien = [
    "",
    "R-ZD (ca. 40 m³/h)",
    "R-BD (ca. 32 m³/h)",
    "R-PN (ca. 48 m³/h)",
    "R-PD (ca. 40 m³/h)"
]

# -----------------------------
# Raumtabelle
# -----------------------------
st.subheader("Räume & Luftführung")

df_rooms = st.data_editor(
    pd.DataFrame({
        "Raum": ["Wohnzimmer", "Flur", "Bad"],
        "Typ": ["Zuluft", "Überström", "Abluft"],
        "Innenliegend": [False, False, True],
        "Kategorie": ["Wohnzimmer", "Flur", "Bad"],
        "DIN 18017 Kategorie": ["", "", "R-ZD (ca. 40 m³/h)"],
        "Überströmt nach": ["Flur", "Bad", ""]
    }),
    num_rows="dynamic",
    use_container_width=True,
    column_config={

        "Typ": st.column_config.SelectboxColumn(
            "Raumtyp",
            options=["Zuluft", "Überström", "Abluft"]
        ),

        "Kategorie": st.column_config.SelectboxColumn(
            "Raum nach DIN 1946-6",
            options=raum_kategorien
        ),

        "DIN 18017 Kategorie": st.column_config.SelectboxColumn(
            "DIN 18017 Kategorie",
            options=din18017_kategorien
        ),

        "Innenliegend": st.column_config.CheckboxColumn("Innenliegend"),

        "Überströmt nach": st.column_config.TextColumn(
            "Überströmt nach (Raumname)"
        )
    }
)

# -----------------------------
# Berechnung
# -----------------------------
if st.button("🔄 Berechnen"):

    q_req, q_ab, delta, df_res = calculate_ventilation(df_rooms, ANE, fWS)
    n_ald = calculate_ald(delta)

    G = build_graph_from_rooms(df_res)
    paths = calculate_paths(G, df_res)

    n_uld, uld_edges = calculate_uld_from_graph(G, df_res, paths)

    errors, warnings = run_checks(df_res, G, delta)

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
        "graph": G
    }

# -----------------------------
# Ergebnisse anzeigen
# -----------------------------
if "res" in st.session_state:

    r = st.session_state["res"]

    st.subheader("Ergebnisse")

    col1, col2, col3 = st.columns(3)

    col1.metric("Feuchteschutz", round(r["q_required"], 1))
    col2.metric("Abluft gesamt", round(r["q_abluft"], 1))
    col3.metric("Δ Volumenstrom", round(r["delta"], 1))

    st.write(f"**ALD erforderlich:** {r['n_ald']} Stück")
    st.write(f"**ÜLD gesamt:** {r['n_uld']} Stück")

    # -----------------------------
    # Raumwerte
    # -----------------------------
    st.subheader("Raumwerte")

    st.dataframe(
        r["df"][[
            "Raum",
            "Kategorie",
            "DIN 18017 Kategorie",
            "Abluft (m³/h)"
        ]],
        use_container_width=True
    )

    # -----------------------------
    # ÜLD je Verbindung
    # -----------------------------
    st.subheader("Überströmöffnungen (ÜLD)")

    for (a, b), data in r["uld_edges"].items():
        st.write(
            f"{a} → {b}: "
            f"{data['Anzahl']} ÜLD "
            f"(Volumenstrom: {data['Volumenstrom']} m³/h)"
        )

    # -----------------------------
    # Prüfung
    # -----------------------------
    st.subheader("Prüfung")

    for e in r["errors"]:
        st.error(e)

    for w in r["warnings"]:
        st.warning(w)

    if not r["errors"] and not r["warnings"]:
        st.success("System OK")

    # -----------------------------
    # Graph
    # -----------------------------
    st.subheader("Luftströmung")

    fig, ax = plt.subplots()
    pos = nx.spring_layout(r["graph"])
    nx.draw(r["graph"], pos, with_labels=True, node_color="lightblue", ax=ax)

    st.pyplot(fig)

    # -----------------------------
    # PDF Export
    # -----------------------------
    st.subheader("Export")

    if st.button("📄 PDF erzeugen"):

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

        create_pdf(tmp.name, ANE, r)

        with open(tmp.name, "rb") as f:
            st.download_button(
                "📥 PDF herunterladen",
                f,
                file_name="lueftungskonzept.pdf"
            )
