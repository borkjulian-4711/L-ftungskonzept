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
        "Raum",
        "Nutzung",
        "Fläche",
        "Zuluft",
        "Abluft",
        "Überströmt"
    ]]

    for _, row in df_rooms.iterrows():
        table_data.append([
            str(row.get("Raum", "")),
            str(row.get("Kategorie (DIN 1946-6)", "")),
            str(row.get("Fläche", "")),
            str(int(row.get("Zuluft (m³/h)", 0))),
            str(int(row.get("Abluft (m³/h)", 0))),
            str(row.get("Überströmt nach", ""))
        ])

    total_zu = int(df_rooms["Zuluft (m³/h)"].sum())
    total_ab = int(df_rooms["Abluft (m³/h)"].sum())

    table_data.append(["Summe", "", "", total_zu, total_ab, ""])

    table = Table(
        table_data,
        colWidths=[4*cm, 4*cm, 2.5*cm, 3*cm, 3*cm, 3.5*cm],
        repeatRows=1
    )

    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (3, 1), (4, -1), "RIGHT"),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))

    story.append(table)
    story.append(PageBreak())


# -----------------------------
# FORMBLATT E (PRÜFBERICHT)
# -----------------------------
def add_formblatt_e(story, text):

    story.append(Paragraph("Formblatt E – Lüftungskonzept", styles["Heading2"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph(text, styles["Normal"]))
    story.append(Spacer(1, 30))

    table = Table([
        ["Ort, Datum", "Unterschrift"],
        ["", ""]
    ], colWidths=[8*cm, 8*cm], rowHeights=[1*cm, 2*cm])

    table.setStyle(TableStyle([
        ("LINEABOVE", (0, 1), (0, 1), 0.5, colors.black),
        ("LINEABOVE", (1, 1), (1, 1), 0.5, colors.black)
    ]))

    story.append(table)
    story.append(PageBreak())


# -----------------------------
# PDF GENERATOR
# -----------------------------
def create_multi_pdf(filename, data):

    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []

    for _, content in data.items():

        meta = content.get("meta", {})
        firma = content.get("firma", {})
        res = content.get("res", {})

        # Deckblatt
        story.append(Paragraph("Lüftungskonzept DIN 1946-6", styles["Title"]))
        story.append(Spacer(1, 20))

        story.append(Paragraph(f"Projekt: {meta.get('projekt','')}", styles["Normal"]))
        story.append(Paragraph(f"Adresse: {meta.get('adresse','')}", styles["Normal"]))
        story.append(Spacer(1, 10))

        story.append(Paragraph(firma.get("name", ""), styles["Normal"]))
        story.append(Paragraph(firma.get("anschrift", ""), styles["Normal"]))

        story.append(PageBreak())

        # Formblatt C
        if "df_rooms" in res:
            add_formblatt_c(story, res["df_rooms"])

        # Formblatt E (Bericht)
        if "formblatt_e" in res:
            add_formblatt_e(story, res["formblatt_e"])

    doc.build(story)
