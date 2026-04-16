from reportlab.platypus import *
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()

def create_multi_pdf(file, project):

    doc = SimpleDocTemplate(file, pagesize=A4)
    elements = []

    for name, data in project.items():

        res = data["res"]

        elements.append(Paragraph("Lüftungskonzept DIN 1946-6", styles["Title"]))

        elements.append(Spacer(1,10))

        # A–D kurz darstellen
        elements.append(Paragraph("Formblatt A–D", styles["Heading2"]))
        elements.append(Paragraph(str(res["formblatt_a"]), styles["Normal"]))
        elements.append(Paragraph(str(res["formblatt_b"]), styles["Normal"]))
        elements.append(Paragraph(str(res["formblatt_c"]), styles["Normal"]))
        elements.append(Paragraph(str(res["formblatt_d"]), styles["Normal"]))

        elements.append(Spacer(1,10))

        # Formblatt E
        elements.append(Paragraph("Formblatt E – Ergebnis", styles["Heading2"]))
        elements.append(Paragraph(res["formblatt_e"], styles["Normal"]))

        elements.append(PageBreak())

    doc.build(elements)
