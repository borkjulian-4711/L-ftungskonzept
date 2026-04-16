# export/pdf_generator.py

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
# FORMBLATT C (DIN-NAH)
# -----------------------------
def add_formblatt_c(story, df_rooms):

    story.append(Paragraph("Formblatt C – Raumweise Luftvolumenströme", styles["Heading2"]))
    story.append(Spacer(1, 10))

    # -----------------------------
    # Tabellenkopf
    # -----------------------------
    table_data = [[
        "Raum",
        "Nutzung",
        "Fläche [m²]",
        "Zuluft [m³/h]",
        "Abluft [m³/h]",
        "Überströmt nach"
    ]]

    # -----------------------------
    # Daten
    # -----------------------------
    for _, row in df_rooms.iterrows():
        table_data.append([
            str(row.get("Raum", "")),
            str(row.get("Kategorie (DIN 1946-6)", "")),
            str(row.get("Fläche", "")),
            str(int(row.get("Zuluft (m³/h)", 0))),
            str(int(row.get("Abluft (m³/h)", 0))),
            str(row.get("Überströmt nach", ""))
        ])

    # -----------------------------
    # Summenzeile
    # -----------------------------
    total_zu = int(df_rooms["Zuluft (m³/h)"].sum())
    total_ab = int(df_rooms["Abluft (m³/h)"].sum())

    table_data.append([
        "Summe",
        "",
        "",
        str(total_zu),
        str(total_ab),
        ""
    ])

    # -----------------------------
    # Tabelle mit Spaltenbreiten
    # -----------------------------
    table = Table(
        table_data,
        colWidths=[
            4 * cm,   # Raum
            4 * cm,   # Nutzung
            2.5 * cm, # Fläche
            3 * cm,   # Zuluft
            3 * cm,   # Abluft
            3.5 * cm  # Überströmung
        ],
        repeatRows=1
    )

    # -----------------------------
    # Styling (DIN-ähnlich)
    # -----------------------------
    table.setStyle(TableStyle([

        # Gitter
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),

        # Kopfzeile
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        # Zahlen rechtsbündig
        ("ALIGN", (3, 1), (4, -1), "RIGHT"),

        # Summenzeile
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),

        # Vertikale Ausrichtung
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        # Padding
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))

    story.append(table)
    story.append(PageBreak())


# -----------------------------
# HAUPTFUNKTION PDF
# -----------------------------
def create_multi_pdf(filename, data):

    doc = SimpleDocTemplate(filename, pagesize=A4)

    story = []

    for name, content in data.items():

        meta = content.get("meta", {})
        firma = content.get("firma", {})
        res = content.get("res", {})

        # -----------------------------
        # Titel
        # -----------------------------
        story.append(Paragraph("Lüftungskonzept DIN 1946-6", styles["Title"]))
        story.append(Spacer(1, 12))

        # -----------------------------
        # Projekt
        # -----------------------------
        story.append(Paragraph(f"Projekt: {meta.get('projekt', '')}", styles["Normal"]))
        story.append(Paragraph(f"Adresse: {meta.get('adresse', '')}", styles["Normal"]))
        story.append(Paragraph(f"Bearbeiter: {meta.get('bearbeiter', '')}", styles["Normal"]))
        story.append(Spacer(1, 12))

        # -----------------------------
        # Firma
        # -----------------------------
        story.append(Paragraph(firma.get("firma", ""), styles["Normal"]))
        story.append(Paragraph(firma.get("anschrift", ""), styles["Normal"]))
        story.append(Spacer(1, 12))

        # -----------------------------
        # Konzepttext
        # -----------------------------
        if "formblatt_e" in res:
            story.append(Paragraph("Konzept", styles["Heading2"]))
            story.append(Spacer(1, 6))
            story.append(Paragraph(res["formblatt_e"], styles["Normal"]))
            story.append(PageBreak())

        # -----------------------------
        # FORMBLATT C
        # -----------------------------
        if "df_rooms" in res:
            add_formblatt_c(story, res["df_rooms"])

    doc.build(story)
