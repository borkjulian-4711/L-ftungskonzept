from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas

styles = getSampleStyleSheet()


# -----------------------------
# HEADER / FOOTER
# -----------------------------
def add_header_footer(c: canvas.Canvas, doc, firma, meta):
    c.setFont("Helvetica", 8)

    # Kopf
    c.drawString(2*cm, 28*cm, firma.get("firma", ""))
    c.drawRightString(19*cm, 28*cm, meta.get("projekt", ""))

    # Fuß
    c.drawString(2*cm, 1.5*cm, firma.get("kontakt", ""))
    c.drawRightString(19*cm, 1.5*cm, f"Seite {doc.page}")


# -----------------------------
# DECKBLATT
# -----------------------------
def create_cover(story, firma, meta):

    if firma.get("logo"):
        logo = firma["logo"]
        with open("temp_logo.png", "wb") as f:
            f.write(logo.read())
        story.append(Image("temp_logo.png", width=6*cm, height=3*cm))

    story.append(Spacer(1, 40))
    story.append(Paragraph("<b>LÜFTUNGSKONZEPT</b>", styles["Title"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph("nach DIN 1946-6", styles["Heading2"]))
    story.append(Spacer(1, 40))

    story.append(Paragraph(f"<b>Projekt:</b> {meta.get('projekt','')}", styles["Normal"]))
    story.append(Paragraph(f"<b>Adresse:</b> {meta.get('adresse','')}", styles["Normal"]))
    story.append(Paragraph(f"<b>Bearbeiter:</b> {meta.get('bearbeiter','')}", styles["Normal"]))
    story.append(Paragraph(f"<b>Datum:</b> {meta.get('datum','')}", styles["Normal"]))

    story.append(Spacer(1, 60))

    story.append(Paragraph(firma.get("firma",""), styles["Normal"]))
    story.append(Paragraph(firma.get("anschrift",""), styles["Normal"]))
    story.append(Paragraph(firma.get("kontakt",""), styles["Normal"]))

    story.append(PageBreak())


# -----------------------------
# FORMBLATT A
# -----------------------------
def add_formblatt_a(story, data):

    story.append(Paragraph("<b>Formblatt A – Notwendigkeit Lüftungskonzept</b>", styles["Heading2"]))
    story.append(Spacer(1, 10))

    table_data = [
        ["Kriterium", "Ergebnis"],
        ["Neubau", str(data.get("neubau",""))],
        ["Sanierung", str(data.get("sanierung",""))],
        ["Luftdicht", str(data.get("luftdicht",""))],
        ["Ergebnis", str(data.get("ergebnis",""))],
    ]

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ]))

    story.append(table)
    story.append(PageBreak())


# -----------------------------
# FORMBLATT B
# -----------------------------
def add_formblatt_b(story, data):

    story.append(Paragraph("<b>Formblatt B – Gebäudeangaben</b>", styles["Heading2"]))
    story.append(Spacer(1, 10))

    table_data = [
        ["Parameter", "Wert"],
        ["Gebäudetyp", data.get("gebaeudetyp","")],
        ["Baujahr", str(data.get("baujahr",""))],
        ["Personen", str(data.get("personen",""))],
    ]

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ]))

    story.append(table)
    story.append(PageBreak())


# -----------------------------
# FORMBLATT C (RAUMTABELLE)
# -----------------------------
def add_formblatt_c(story, df_rooms):

    story.append(Paragraph("<b>Formblatt C – Raumweise Luftvolumenströme</b>", styles["Heading2"]))
    story.append(Spacer(1, 10))

    table_data = [[
        "Raum", "Typ", "Fläche (m²)",
        "Zuluft (m³/h)", "Abluft (m³/h)", "Überströmt nach"
    ]]

    for _, row in df_rooms.iterrows():
        table_data.append([
            str(row.get("Raum","")),
            str(row.get("Typ","")),
            str(row.get("Fläche","")),
            str(row.get("Zuluft (m³/h)",0)),
            str(row.get("Abluft (m³/h)",0)),
            str(row.get("Überströmt nach",""))
        ])

    table = Table(table_data, repeatRows=1)

    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ]))

    story.append(table)
    story.append(PageBreak())


# -----------------------------
# FORMBLATT E (BILANZ)
# -----------------------------
def add_formblatt_e(story, summary):

    story.append(Paragraph("<b>Formblatt E – Luftmengenbilanz</b>", styles["Heading2"]))
    story.append(Spacer(1, 10))

    table_data = [
        ["Parameter", "Wert"],
        ["Zuluft gesamt", f"{summary.get('zu',0)} m³/h"],
        ["Abluft gesamt", f"{summary.get('ab',0)} m³/h"],
        ["Infiltration", f"{summary.get('inf',0)} m³/h"],
        ["Differenz", f"{summary.get('diff',0)} m³/h"],
        ["Ergebnis", summary.get("status","")]
    ]

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ]))

    story.append(table)
    story.append(PageBreak())


# -----------------------------
# MAIN PDF
# -----------------------------
def create_multi_pdf(path, data):

    doc = SimpleDocTemplate(path)
    story = []

    for name, content in data.items():

        firma = content.get("firma", {})
        meta = content.get("meta", {})
        res = content.get("res", {})

        # Deckblatt
        create_cover(story, firma, meta)

        # Text
        story.append(Paragraph("<b>Lüftungskonzept</b>", styles["Heading2"]))
        story.append(Spacer(1, 20))
        story.append(Paragraph(res.get("formblatt_e","").replace("\n","<br/>"), styles["Normal"]))
        story.append(PageBreak())

        # Anlagen
        story.append(Paragraph("<b>Anlagen</b>", styles["Heading1"]))
        story.append(PageBreak())

        add_formblatt_a(story, res.get("formblatt_a", {}))
        add_formblatt_b(story, res.get("formblatt_b", {}))
        add_formblatt_c(story, res.get("df_rooms"))
        add_formblatt_e(story, res.get("summary"))

    def on_page(canvas, doc):
        add_header_footer(canvas, doc, firma, meta)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
