import streamlit as st
import pandas as pd
import tempfile

from logic.ventilation import calculate_ventilation
from logic.room_airflows import apply_room_airflows
from logic.ventilation_levels import calculate_ventilation_levels
from logic.air_network import propagate_flows, calculate_uld

from logic.formblatt_a import evaluate_formblatt_a
from logic.formblatt_b import evaluate_formblatt_b
from logic.formblatt_c import evaluate_formblatt_c
from logic.formblatt_d import evaluate_formblatt_d
from logic.formblatt_e import generate_formblatt_e

from export.pdf_generator import create_multi_pdf


# -----------------------------
# INIT
# -----------------------------
st.title("🌀 Lüftungskonzept nach DIN 1946-6")

# -----------------------------
# FORMBLATT A
# -----------------------------
st.header("Formblatt A – Notwendigkeit")

neubau = st.checkbox("Neubau")
sanierung = st.checkbox("Sanierung")
fensteranteil = st.slider("Fensteranteil (%)", 0, 100, 50) / 100
luftdicht = st.checkbox("Luftdicht")

formblatt_a = evaluate_formblatt_a(
    neubau,
    sanierung,
    fensteranteil,
    luftdicht
)

st.write(formblatt_a)


# -----------------------------
# FORMBLATT B
# -----------------------------
st.header("Formblatt B – Gebäudedaten")

gebaeudetyp = st.selectbox("Gebäudetyp", ["EFH", "MFH", "Wohnung"])
baujahr = st.number_input("Baujahr", 1900, 2025, 2000)
wohneinheiten = st.number_input("Wohneinheiten", 1, 50, 1)

personen = st.number_input("Personen", 1, 10, 2)
nutzung = st.selectbox("Nutzung", ["normal", "reduziert", "hoch"])

fensterlueftung = st.checkbox("Fensterlüftung möglich")
infiltration = st.selectbox("Infiltration", ["hoch", "mittel", "gering"])

formblatt_b = evaluate_formblatt_b(
    gebaeudetyp,
    baujahr,
    wohneinheiten,
    personen,
    nutzung,
    fensterlueftung,
    infiltration
)

st.write(formblatt_b)


# -----------------------------
# LÜFTUNGSSTUFEN
# -----------------------------
st.header("Lüftungsstufen")

ANE = st.number_input("Fläche Nutzungseinheit (m²)", 30, 300, 80)

levels = calculate_ventilation_levels(
    ANE,
    personen,
    nutzung
)

st.write(levels)


# -----------------------------
# RAUMTABELLE
# -----------------------------
st.header("Räume & Luftführung")

df_rooms = st.data_editor(pd.DataFrame({
    "Raum": ["Wohnzimmer", "Flur", "Bad"],
    "Typ": ["Zuluft", "Überström", "Abluft"],
    "Kategorie (DIN 1946-6)": ["Wohnzimmer", "Flur", "Bad"],
    "Überströmt nach": ["Flur", "Bad", ""]
}), num_rows="dynamic")

df_rooms = df_rooms.fillna("")

# -----------------------------
# VOLUMENSTRÖME
# -----------------------------
df_rooms = apply_room_airflows(df_rooms)

st.subheader("Raumweise Volumenströme")
st.dataframe(df_rooms)


# -----------------------------
# LUFTNETZ
# -----------------------------
flows = propagate_flows(df_rooms)

st.subheader("Luftströme im Netz")

for r, f in flows.items():
    st.write(f"{r}: {round(f, 1)} m³/h")


# -----------------------------
# ÜLD
# -----------------------------
uld = calculate_uld(flows, df_rooms)

st.subheader("Überströmöffnungen")

for (a, b), d in uld.items():
    st.write(f"{a} → {b}: {d['Anzahl']} ÜLD ({d['Volumenstrom']} m³/h)")


# -----------------------------
# GESAMTBERECHNUNG
# -----------------------------
q_req, q_ab, delta, df_res = calculate_ventilation(df_rooms, ANE, 0.3)

st.header("Gesamtergebnis")

st.write("Feuchteschutz erforderlich:", round(q_req, 1))
st.write("Abluft vorhanden:", round(q_ab, 1))
st.write("Differenz:", round(delta, 1))


# -----------------------------
# FORMBLATT C
# -----------------------------
formblatt_c = evaluate_formblatt_c(levels, q_ab)

st.header("Formblatt C – Nachweis")

for k, v in formblatt_c.items():
    st.write(f"{k}: Soll {v['erforderlich']} / Ist {v['vorhanden']} → {v['status']}")


# -----------------------------
# FORMBLATT D
# -----------------------------
formblatt_d = evaluate_formblatt_d(
    formblatt_a,
    formblatt_b,
    formblatt_c
)

st.header("Formblatt D – Maßnahmen")

st.write(formblatt_d)


# -----------------------------
# FORMBLATT E
# -----------------------------
formblatt_e = generate_formblatt_e({
    "levels": levels,
    "formblatt_d": formblatt_d
})

st.header("Formblatt E – Konzept")

st.text_area("Konzepttext", formblatt_e, height=300)


# -----------------------------
# PDF EXPORT
# -----------------------------
st.header("Export")

if st.button("📄 PDF Export"):

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    create_multi_pdf(tmp.name, {
        "WE1": {
            "meta": {
                "projekt": "Projekt",
                "adresse": "Adresse",
                "bearbeiter": "Bearbeiter"
            },
            "res": {
                "formblatt_a": formblatt_a,
                "formblatt_b": formblatt_b,
                "formblatt_c": formblatt_c,
                "formblatt_d": formblatt_d,
                "formblatt_e": formblatt_e,
                "levels": levels
            }
        }
    })

    with open(tmp.name, "rb") as f:
        st.download_button("Download PDF", f)
