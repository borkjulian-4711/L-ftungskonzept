from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

styles = getSampleStyleSheet()


# -----------------------------
# HEADER / FOOTER
# -----------------------------
def add_header_footer(c: canvas.Canvas, doc, firma, meta):

    c.setFont("Helvetica", 8)

    # Kopfzeile
    c.drawString(2*cm, 28*cm, firma.get("firma", ""))
    c.drawRightString(19*cm, 28*cm, meta.get("projekt", ""))

    # Fußzeile
    c.drawString(2*cm, 1.5*cm, firma.get("kontakt", ""))
    c.drawRightString(19*cm, 1.5*cm, f"Seite {doc.page}")


# -----------------------------
# DECKBLATT
# -----------------------------
def create_cover(story, firma, meta):

    # Logo
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
# HAUPT-PDF
# -----------------------------
def create_multi_pdf(path, data):

    doc = SimpleDocTemplate(path)
    story = []

    for name, content in data.items():

        firma = content.get("firma", {})
        meta = content.get("meta", {})
        res = content.get("res", {})

        # -----------------------------
        # DECKBLATT
        # -----------------------------
        create_cover(story, firma, meta)

        # -----------------------------
        # INHALT
        # -----------------------------
        text = res.get("formblatt_e", "")

        story.append(Paragraph("<b>Lüftungskonzept</b>", styles["Heading2"]))
        story.append(Spacer(1, 20))

        story.append(Paragraph(text.replace("\n", "<br/>"), styles["Normal"]))

        story.append(PageBreak())

    # -----------------------------
    # BUILD mit HEADER/FOOTER
    # -----------------------------
    def on_page(canvas, doc):
        add_header_footer(canvas, doc, firma, meta)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
