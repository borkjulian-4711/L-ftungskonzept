from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas

styles = getSampleStyleSheet()

# TOC Styles
styles.add(ParagraphStyle(name='TOCHeading', fontSize=14, spaceAfter=10))


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

    story.append(PageBreak())


# -----------------------------
# INHALTSVERZEICHNIS
# -----------------------------
def create_toc(story):

    story.append(Paragraph("Inhaltsverzeichnis", styles["Heading1"]))

    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(fontSize=10, name='TOC1', leftIndent=20, firstLineIndent=-20)
    ]

    story.append(toc)
    story.append(PageBreak())


# -----------------------------
# UNTERSCHRIFT
# -----------------------------
def add_signature(story):

    story.append(Spacer(1, 40))

    table = Table([
        ["Ort, Datum", "Unterschrift / Stempel"],
        ["____________________", "____________________________"]
    ], colWidths=[8*cm, 8*cm])

    table.setStyle(TableStyle([
        ("LINEABOVE", (0,1), (0,1), 0.5, colors.black),
        ("LINEABOVE", (1,1), (1,1), 0.5, colors.black),
    ]))

    story.append(table)
    story.append(PageBreak())


# -----------------------------
# FORMBLATT C
# -----------------------------
def add_formblatt_c(story, df_rooms):

    story.append(Paragraph("Formblatt C – Raumweise Luftvolumenströme", styles["Heading2"]))
    story.append(Spacer(1, 10))

    table_data = [[
        "Raum", "Typ", "Fläche",
        "Zuluft", "Abluft", "Überströmt"
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
    ]))

    story.append(table)
    story.append(PageBreak())


# -----------------------------
# FORMBLATT E
# -----------------------------
def add_formblatt_e(story, summary):

    story.append(Paragraph("Formblatt E – Luftmengenbilanz", styles["Heading2"]))
    story.append(Spacer(1, 10))

    table_data = [
        ["Parameter", "Wert"],
        ["Zuluft", f"{summary['zu']}"],
        ["Abluft", f"{summary['ab']}"],
        ["Infiltration", f"{summary['inf']}"],
        ["Differenz", f"{summary['diff']}"],
        ["Ergebnis", summary["status"]],
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

        # Inhaltsverzeichnis
        create_toc(story)

        # Haupttext
        story.append(Paragraph("Lüftungskonzept", styles["Heading1"]))
        story.append(Spacer(1, 20))
        story.append(Paragraph(res.get("formblatt_e","").replace("\n","<br/>"), styles["Normal"]))
        story.append(PageBreak())

        # Unterschrift
        add_signature(story)

        # Anlagen
        story.append(Paragraph("Anlagen", styles["Heading1"]))
        story.append(PageBreak())

        add_formblatt_c(story, res.get("df_rooms"))
        add_formblatt_e(story, res.get("summary"))

    def on_page(canvas, doc):
        add_header_footer(canvas, doc, firma, meta)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
