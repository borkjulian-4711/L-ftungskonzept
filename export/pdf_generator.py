from reportlab.platypus import *
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()

def create_multi_pdf(file, project):

    doc = SimpleDocTemplate(file, pagesize=A4)
    elements = []

    for name, data in project.items():

        res = data["res"]

        # Formblatt D
        elements.append(Paragraph("Formblatt D – Maßnahmen", styles["Heading2"]))

        elements.append(Paragraph(
            f"Maßnahme: {res['formblatt_d']['massnahme']}",
            styles["Normal"]
        ))

        elements.append(Paragraph(
            f"Begründung: {res['formblatt_d']['begruendung']}",
            styles["Normal"]
        ))

        elements.append(PageBreak())

    doc.build(elements)
