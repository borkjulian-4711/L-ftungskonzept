from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, PageBreak
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

styles = getSampleStyleSheet()

# -----------------------------
# FORMBLATT C
# -----------------------------
def add_formblatt_c(story, df_rooms):

    story.append(Paragraph("Formblatt C – Raumweise Luftvolumenströme", styles["Heading2"]))
    story.append(Spacer(1, 10))

    table_data = [[
        "Raum", "Nutzung", "Fläche",
        "Zuluft", "Abluft", "Innenliegend", "Überströmt"
    ]]

    for _, row in df_rooms.iterrows():
        table_data.append([
            str(row.get("Raum", "")),
            str(row.get("Kategorie (DIN 1946-6)", "")),
            str(row.get("Fläche", "")),
            str(int(row.get("Zuluft (m³/h)", 0))),
            str(int(row.get("Abluft (m³/h)", 0))),
            "Ja" if row.get("Innenliegend", False) else "Nein",
            str(row.get("Überströmt nach", ""))
        ])

    total_zu = int(df_rooms["Zuluft (m³/h)"].sum())
    total_ab = int(df_rooms["Abluft (m³/h)"].sum())

    table_data.append(["Summe", "", "", total_zu, total_ab, "", ""])

    table = Table(
        table_data,
        colWidths=[3.5*cm, 3.5*cm, 2.2*cm, 2.5*cm, 2.5*cm, 2.5*cm, 3*cm],
        repeatRows=1
    )

    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("LINEABOVE", (0,-1), (-1,-1), 1, colors.black)
    ]))

    story.append(table)
    story.append(PageBreak())


# -----------------------------
# PRÜFPROTOKOLL
# -----------------------------
def add_validation_report(story, errors, warnings, summary):

    story.append(Paragraph("DIN-Prüfprotokoll", styles["Heading1"]))
    story.append(Spacer(1, 10))

    table = Table([
        ["Parameter", "Wert"],
        ["qv", f"{summary['qv']} m³/h"],
        ["Zuluft", f"{summary['zu']} m³/h"],
        ["Abluft", f"{summary['ab']} m³/h"],
        ["Infiltration", f"{summary['inf']} m³/h"],
    ])

    table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.black)
    ]))

    story.append(table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Fehler:", styles["Heading2"]))
    for e in errors:
        story.append(Paragraph(f"❌ {e}", styles["Normal"]))

    story.append(Paragraph("Hinweise:", styles["Heading2"]))
    for w in warnings:
        story.append(Paragraph(f"⚠️ {w}", styles["Normal"]))

    story.append(PageBreak())


# -----------------------------
# FORMBLATT E
# -----------------------------
def add_formblatt_e(story, text):

    story.append(Paragraph("Formblatt E – Lüftungskonzept", styles["Heading2"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(text, styles["Normal"]))
    story.append(PageBreak())


# -----------------------------
# PDF GENERATOR
# -----------------------------
def create_multi_pdf(filename, data):

    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []

    for _, content in data.items():

        meta = content["meta"]
        res = content["res"]

        story.append(Paragraph("Lüftungskonzept DIN 1946-6", styles["Title"]))
        story.append(Spacer(1, 20))

        story.append(Paragraph(f"Projekt: {meta['projekt']}", styles["Normal"]))
        story.append(Paragraph(f"Adresse: {meta['adresse']}", styles["Normal"]))
        story.append(PageBreak())

        add_formblatt_c(story, res["df_rooms"])
        add_formblatt_e(story, res["formblatt_e"])
        add_validation_report(
            story,
            res["validation"]["errors"],
            res["validation"]["warnings"],
            res["validation"]["summary"]
        )

    doc.build(story)
