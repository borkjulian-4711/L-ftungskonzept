from reportlab.platypus import *
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()

def create_multi_pdf(file, project):

    doc = SimpleDocTemplate(file, pagesize=A4)
    elements = []

    for name, data in project.items():

        res = data["res"]

        # Formblatt C
        elements.append(Paragraph("Formblatt C", styles["Heading2"]))

        for level, values in res["formblatt_c"].items():
            elements.append(Paragraph(
                f"{level}: erforderlich {values['erforderlich']} / vorhanden {values['vorhanden']} → {values['status']}",
                styles["Normal"]
            ))

        elements.append(PageBreak())

    doc.build(elements)
