import streamlit as st
import pandas as pd
import tempfile

from config import FIRMA
import logic.din1946_core as core

from logic.infiltration import (
    get_ez_din,
    calculate_infiltration_din,
    calculate_shaft_flow
)

from logic.ald import calculate_ald_din
from logic.system_logic import evaluate_system
from logic.text_generator import generate_concept_text
from logic.validation import validate_din
from logic.correction_engine import generate_corrections
from logic.auto_fix import auto_fix_system

from export.pdf_generator import create_multi_pdf


st.title("🌀 Lüftungskonzept DIN 1946-6")


# -----------------------------
# PROJEKT
# -----------------------------
projekt = st.text_input("Projekt")
adresse = st.text_input("Adresse")
bearbeiter = st.text_input("Bearbeiter")

project_data = {
    "projekt": projekt,
    "adresse": adresse,
    "bearbeiter": bearbeiter
}


# -----------------------------
# SYSTEM
# -----------------------------
system = st.selectbox(
    "System",
    ["freie Lüftung", "ventilatorgestützt", "kombiniert"]
)


# -----------------------------
# GRUNDLAGEN
# -----------------------------
ANE = st.number_input("Wohnfläche ANE (m²)", 30, 300, 80)

levels = core.calculate_levels(ANE)
level = st.selectbox("Lüftungsstufe", list(levels.keys()))
qv_selected = levels[level]

st.write("qv:", qv_selected, "m³/h")


# -----------------------------
# RAUMTABELLE (MIT DROPDOWNS)
# -----------------------------
default_df = pd.DataFrame({
    "Raum": ["Wohnzimmer", "Schlafzimmer", "Bad"],
    "Fläche": [20, 15, 6],
    "Typ": ["Zuluft", "Zuluft", "Abluft"],
    "Kategorie (DIN 1946-6)": ["Wohnzimmer", "Schlafzimmer", "Bad"],
    "Innenliegend": [False, False, True],
    "DIN 18017 Kategorie": ["", "", "R-ZD"],
    "Überströmt nach": ["Flur", "Flur", ""]
})

typ_options = ["Zuluft", "Überström", "Abluft"]

din_options = [
    "Wohnzimmer", "Schlafzimmer", "Kinderzimmer",
    "Arbeitszimmer", "Küche", "Bad", "WC",
    "Flur", "Abstellraum"
]

din18017_options = ["", "R-ZD", "R-BD", "R-PN", "R-PD"]

raumliste = default_df["Raum"].tolist()

df_rooms = st.data_editor(
    default_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Typ": st.column_config.SelectboxColumn(options=typ_options),
        "Kategorie (DIN 1946-6)": st.column_config.SelectboxColumn(options=din_options),
        "DIN 18017 Kategorie": st.column_config.SelectboxColumn(options=din18017_options),
        "Innenliegend": st.column_config.CheckboxColumn(),
        "Überströmt nach": st.column_config.SelectboxColumn(options=[""] + raumliste)
    }
)

df_rooms = df_rooms.fillna("")


# -----------------------------
# BERECHNUNG
# -----------------------------
df_rooms = core.distribute_airflows(df_rooms, qv_selected)
df_rooms = core.apply_exhaust_values(df_rooms)

st.dataframe(df_rooms)


# -----------------------------
# INFILTRATION
# -----------------------------
wind = st.selectbox("Wind", ["windschwach", "windstark"])
Aenv = st.number_input("Hüllfläche Aenv", 10.0, 500.0, 200.0)
luftdicht = st.checkbox("luftdicht")

ez = get_ez_din("EFH", wind, luftdicht)
q_inf = calculate_infiltration_din(Aenv, ez)


# -----------------------------
# SCHACHT
# -----------------------------
shaft = st.checkbox("Schachtlüftung")
q_shaft = calculate_shaft_flow() if shaft else 0


# -----------------------------
# SYSTEMLOGIK
# -----------------------------
q_mech = df_rooms["Abluft (m³/h)"].sum()

if system == "freie Lüftung":
    q_supply = q_inf + q_shaft

elif system == "ventilatorgestützt":
    df_rooms, zu, ab = core.dimension_ventilation_system(df_rooms, qv_selected)
    q_supply = zu

elif system == "kombiniert":
    q_supply = q_mech + q_inf + q_shaft


# -----------------------------
# ALD
# -----------------------------
ald = calculate_ald_din(qv_selected, q_supply, wind)
st.write("ALD:", ald)


# -----------------------------
# SYSTEMBEWERTUNG
# -----------------------------
res = evaluate_system(q_mech, qv_selected, q_supply)
st.write("Status:", res["status"])


# -----------------------------
# VALIDIERUNG
# -----------------------------
errors, warnings = validate_din(
    df_rooms,
    qv_selected,
    q_supply,
    system
)

st.header("DIN-Prüfung")

for e in errors:
    st.error(e)

for w in warnings:
    st.warning(w)

if not errors:
    st.success("DIN-Anforderungen erfüllt")


# -----------------------------
# AUTO-FIX
# -----------------------------
st.header("Auto-Fix")

if st.button("🔧 System automatisch korrigieren"):

    df_rooms, msg = auto_fix_system(
        df_rooms,
        qv_selected,
        q_supply
    )

    st.success(msg)
    st.dataframe(df_rooms)


# -----------------------------
# KORREKTUREN
# -----------------------------
st.header("Korrekturvorschläge")

corrections = generate_corrections(
    df_rooms,
    errors,
    qv_selected,
    q_supply
)

for c in corrections:
    st.info(c)


# -----------------------------
# PRÜFBERICHT
# -----------------------------
summary = {
    "qv": qv_selected,
    "zu": q_supply,
    "ab": q_mech,
    "inf": q_inf,
    "status": res["status"]
}

report = generate_concept_text(
    {
        "levels": levels,
        "result": res,
        "summary": summary
    },
    project_data
)

st.text_area("Prüfbericht", report, height=400)


# -----------------------------
# PDF EXPORT
# -----------------------------
if st.button("📄 PDF Export"):

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    create_multi_pdf(tmp.name, {
        "WE1": {
            "meta": project_data,
            "firma": FIRMA,
            "res": {
                "df_rooms": df_rooms,
                "formblatt_e": report,
                "validation": {
                    "errors": errors,
                    "warnings": warnings,
                    "summary": summary
                },
                "corrections": corrections
            }
        }
    })

    with open(tmp.name, "rb") as f:
        st.download_button(
            label="Download PDF",
            data=f,
            file_name="Lueftungskonzept.pdf",
            mime="application/pdf"
        )
