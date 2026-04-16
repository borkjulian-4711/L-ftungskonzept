from reportlab.platypus import *
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()

def create_multi_pdf(file, project):

    doc = SimpleDocTemplate(file, pagesize=A4)
    elements = []

    for name, data in project.items():

        res = data["res"]

        # Formblatt A
        elements.append(Paragraph("Formblatt A", styles["Heading2"]))
        elements.append(Paragraph(str(res["formblatt_a"]), styles["Normal"]))

        elements.append(Spacer(1,10))

        # Formblatt B
        elements.append(Paragraph("Formblatt B", styles["Heading2"]))

        for k, v in res["formblatt_b"].items():
            elements.append(Paragraph(f"{k}: {v}", styles["Normal"]))

        elements.append(Spacer(1,10))

        # Lüftungsstufen
        elements.append(Paragraph("Lüftungsstufen", styles["Heading2"]))
        elements.append(Paragraph(str(res["levels"]), styles["Normal"]))

        elements.append(PageBreak())

    doc.build(elements)
