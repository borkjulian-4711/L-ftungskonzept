from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, PageBreak
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

styles = getSampleStyleSheet()


def add_formblatt_c(story, df_rooms):

    story.append(Paragraph("Formblatt C – Raumweise Luftvolumenströme", styles["Heading2"]))
    story.append(Spacer(1, 10))

    table_data = [[
        "Raum", "Nutzung", "Fläche",
        "Zuluft", "Abluft", "Innenliegend", "Überströmt"
    ]]

    for _, row in df_rooms.iterrows():
        table_data.append([
            row["Raum"],
            row["Kategorie (DIN 1946-6)"],
            row["Fläche"],
            int(row["Zuluft (m³/h)"]),
            int(row["Abluft (m³/h)"]),
            "Ja" if row["Innenliegend"] else "Nein",
            row["Überströmt nach"]
        ])

    table = Table(table_data, colWidths=[3.5*cm,3.5*cm,2*cm,2.5*cm,2.5*cm,2.5*cm,3*cm])

    table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.black),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey)
    ]))

    story.append(table)
    story.append(PageBreak())


def add_validation_report(story, errors, warnings):

    story.append(Paragraph("DIN-Prüfprotokoll", styles["Heading1"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Fehler:", styles["Heading2"]))
    for e in errors:
        story.append(Paragraph(f"❌ {e}", styles["Normal"]))

    story.append(Paragraph("Hinweise:", styles["Heading2"]))
    for w in warnings:
        story.append(Paragraph(f"⚠️ {w}", styles["Normal"]))

    story.append(PageBreak())


def add_corrections(story, corrections):

    story.append(Paragraph("Korrekturvorschläge", styles["Heading2"]))
    story.append(Spacer(1, 10))

    for c in corrections:
        story.append(Paragraph(f"• {c}", styles["Normal"]))

    story.append(PageBreak())


def add_formblatt_e(story, text):

    story.append(Paragraph("Formblatt E – Lüftungskonzept", styles["Heading2"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(text, styles["Normal"]))
    story.append(PageBreak())


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
        add_validation_report(story, res["validation"]["errors"], res["validation"]["warnings"])
        add_corrections(story, res["corrections"])

    doc.build(story)
