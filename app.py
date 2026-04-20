import streamlit as st
import pandas as pd
import tempfile

from config import FIRMA
import logic.din1946_core as core

from logic.text_generator import generate_concept_text
from logic.correction_engine import generate_corrections
from logic.auto_fix import auto_fix_system

from logic.test_cases import get_test_cases
from logic.test_runner import run_tests
from logic.normative_pipeline import NormativeInput, run_normative_calculation

from export.pdf_generator import create_multi_pdf


st.title("🌀 Lüftungskonzept DIN 1946-6 + DIN 18017")
st.caption("Kompletter Neuaufbau des Rechenkerns: ein zentraler normativer Pipeline-Lauf steuert Berechnung, Validierung und Nachweis.")


# -----------------------------
# SESSION INIT
# -----------------------------
if "df_rooms" not in st.session_state:
    st.session_state.df_rooms = pd.DataFrame({
        "Raum": ["Wohnzimmer", "Schlafzimmer", "Bad"],
        "Fläche": [20, 15, 6],
        "Typ": ["Zuluft", "Zuluft", "Abluft"],
        "Kategorie (DIN 1946-6)": ["Wohnzimmer", "Schlafzimmer", "Bad"],
        "Innenliegend": [False, False, True],
        "DIN 18017 Kategorie": ["", "", "R-ZD"],
        "Überströmt nach": ["", "", ""]
    })


# -----------------------------
# PROJEKT
# -----------------------------
st.header("Projekt")

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
st.header("System")

system = st.selectbox(
    "Lüftungssystem",
    ["freie Lüftung", "ventilatorgestützt", "kombiniert"]
)


# -----------------------------
# GRUNDLAGEN
# -----------------------------
st.header("Grundlagen")

ANE = st.number_input("Wohnfläche ANE (m²)", 30, 300, 80)

levels = core.calculate_levels(ANE)
level = st.selectbox("Lüftungsstufe", list(levels.keys()))
qv_selected = levels[level]

st.write("Erforderlicher Volumenstrom:", qv_selected, "m³/h")


# -----------------------------
# RAUMTABELLE (DROPDOWNS STABIL)
# -----------------------------
st.header("Räume & Luftführung")

df_rooms = st.session_state.df_rooms

typ_options = ["Zuluft", "Überström", "Abluft"]

din_options = [
    "Wohnzimmer", "Schlafzimmer", "Kinderzimmer",
    "Arbeitszimmer", "Küche", "Bad", "WC",
    "Flur", "Abstellraum"
]

din18017_options = ["", "R-ZD", "R-BD", "R-PN", "R-PD"]

raumliste = df_rooms["Raum"].tolist()

edited_df = st.data_editor(
    df_rooms,
    num_rows="dynamic",
    use_container_width=True,
    key="room_editor",
    column_config={
        "Typ": st.column_config.SelectboxColumn(options=typ_options),
        "Kategorie (DIN 1946-6)": st.column_config.SelectboxColumn(options=din_options),
        "DIN 18017 Kategorie": st.column_config.SelectboxColumn(options=din18017_options),
        "Innenliegend": st.column_config.CheckboxColumn(),
        "Überströmt nach": st.column_config.SelectboxColumn(options=[""] + raumliste)
    }
)

# 👉 WICHTIG: speichern!
st.session_state.df_rooms = edited_df.copy()
df_rooms = edited_df.fillna("")


wind = st.selectbox("Wind", ["windschwach", "windstark"])
Aenv = st.number_input("Hüllfläche Aenv (m²)", 10.0, 500.0, 200.0)
luftdicht = st.checkbox("luftdicht")


# -----------------------------
# SCHACHT
# -----------------------------
shaft = st.checkbox("Schachtlüftung")


# -----------------------------
# BERECHNUNG (NEUER PIPELINE-LAUF)
# -----------------------------
result = run_normative_calculation(
    df_rooms,
    NormativeInput(
        ane=ANE,
        level=level,
        system=system,
        wind=wind,
        aenv=Aenv,
        luftdicht=luftdicht,
        shaft_enabled=shaft,
    ),
)

df_rooms = result.rooms
qv_selected = result.qv_required
q_inf = result.q_inf
q_shaft = result.q_shaft
q_mech = result.q_mech
q_supply = result.q_supply

st.subheader("Berechnete Luftmengen")
st.dataframe(df_rooms)


# -----------------------------
# ALD
# -----------------------------
st.header("ALD")

ald = result.ald
st.write(ald)


# -----------------------------
# SYSTEMBEWERTUNG
# -----------------------------
st.header("Systembewertung")

res = result.system_result
st.write("Status:", res["status"])


# -----------------------------
# VALIDIERUNG
# -----------------------------
st.header("DIN-Prüfung")

errors, warnings = result.errors, result.warnings

for e in errors:
    st.error(e)

for w in warnings:
    st.warning(w)

if not errors:
    st.success("DIN-Anforderungen erfüllt")

st.subheader("Audit Trail")
for entry in result.audit_trail:
    st.caption(f"• {entry}")


# -----------------------------
# AUTO-FIX (JETZT RICHTIG!)
# -----------------------------
st.header("Auto-Fix")

if st.button("🔧 Auto-Fix anwenden"):

    fixed_df = auto_fix_system(
        st.session_state.df_rooms,
        qv_selected
    )

    st.session_state.df_rooms = fixed_df

    st.success("Auto-Fix wurde angewendet")

    st.rerun()


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
st.header("Prüfbericht")

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

st.text_area("Bericht", report, height=400)


# -----------------------------
# TESTS
# -----------------------------
st.header("Automatische DIN-Tests")

if st.button("🧪 Tests ausführen"):

    results = run_tests(get_test_cases())

    for r in results:
        if r["Status"] == "PASS":
            st.success(f"{r['Test']} → PASS")
        else:
            st.error(f"{r['Test']} → FAIL: {r['Details']}")


# -----------------------------
# PDF EXPORT
# -----------------------------
st.header("Export")

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
