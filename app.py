import streamlit as st
import pandas as pd
import tempfile

from logic.ventilation import calculate_ventilation
from logic.room_airflows import apply_room_airflows
from logic.ventilation_levels import calculate_ventilation_levels
from logic.air_network import propagate_flows, calculate_uld

from logic.din18017 import apply_din18017, check_moisture_protection

from logic.formblatt_a import evaluate_formblatt_a
from logic.formblatt_b import evaluate_formblatt_b
from logic.formblatt_c import evaluate_formblatt_c
from logic.formblatt_d import evaluate_formblatt_d
from logic.formblatt_e import generate_formblatt_e
from logic.validation import validate_din

from export.pdf_generator import create_multi_pdf


st.title("🌀 Lüftungskonzept DIN 1946-6 + DIN 18017-3")

# -----------------------------
# PARAMETER
# -----------------------------
personen = st.number_input("Personen", 1, 10, 2)
nutzung = st.selectbox("Nutzung", ["normal","reduziert","hoch"])
ANE = st.number_input("Fläche (m²)", 30, 300, 80)

levels = calculate_ventilation_levels(ANE, personen, nutzung)

st.subheader("Lüftungsstufen")
st.write(levels)

# -----------------------------
# RAUMTABELLE (ERWEITERT)
# -----------------------------
st.header("Räume & Luftführung")

default_df = pd.DataFrame({
    "Raum": ["Wohnzimmer", "Flur", "Bad"],
    "Typ": ["Zuluft", "Überström", "Abluft"],
    "Kategorie (DIN 1946-6)": ["Wohnzimmer", "Flur", "Bad"],
    "Innenliegend": [False, False, True],
    "DIN 18017 Kategorie": ["", "", "R-ZD"],
    "Überströmt nach": ["Flur", "Bad", ""]
})

typ_options = ["Zuluft", "Überström", "Abluft"]

din_options = [
    "Wohnzimmer","Schlafzimmer","Kinderzimmer","Arbeitszimmer",
    "Küche","Bad","WC","Flur"
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
# VOLUMENSTRÖME
# -----------------------------
df_rooms = apply_room_airflows(df_rooms)
df_rooms = apply_din18017(df_rooms)

st.subheader("Volumenströme (inkl. DIN 18017)")
st.dataframe(df_rooms)

# -----------------------------
# LUFTNETZ
# -----------------------------
flows = propagate_flows(df_rooms)

st.subheader("Luftnetz")

for r, f in flows.items():
    st.write(f"{r}: {round(f,1)} m³/h")

# -----------------------------
# ÜLD
# -----------------------------
uld = calculate_uld(flows, df_rooms)

st.subheader("ÜLD")

for (a,b), d in uld.items():
    st.write(f"{a} → {b}: {d['Anzahl']} Stück")

# -----------------------------
# GESAMT
# -----------------------------
q_req, q_ab, delta, df_res = calculate_ventilation(df_rooms, ANE, 0.3)

# -----------------------------
# DIN 18017 CHECK
# -----------------------------
feuchteschutz_ok = check_moisture_protection(q_req, q_ab)

st.subheader("Feuchteschutz")

if feuchteschutz_ok:
    st.success("Feuchteschutz durch Abluftsystem erfüllt")
else:
    st.error("Zusätzliche Maßnahmen erforderlich (z. B. ALD)")

# -----------------------------
# VALIDIERUNG
# -----------------------------
errors, warnings = validate_din(df_rooms, flows, q_req, q_ab)

if errors:
    st.error(errors)

if warnings:
    st.warning(warnings)

# -----------------------------
# FORMBLÄTTER
# -----------------------------
formblatt_c = evaluate_formblatt_c(levels, q_ab)

formblatt_d = evaluate_formblatt_d(
    {"erforderlich": True},
    {"fensterlueftung": True},
    formblatt_c
)

formblatt_e = generate_formblatt_e({
    "levels": levels,
    "formblatt_d": formblatt_d
})

st.text_area("Konzept", formblatt_e)

# -----------------------------
# EXPORT
# -----------------------------
if st.button("PDF Export"):

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    create_multi_pdf(tmp.name, {
        "WE1": {
            "meta": {},
            "res": {
                "formblatt_c": formblatt_c,
                "formblatt_d": formblatt_d,
                "formblatt_e": formblatt_e,
                "levels": levels
            }
        }
    })

    with open(tmp.name, "rb") as f:
        st.download_button("Download PDF", f)
