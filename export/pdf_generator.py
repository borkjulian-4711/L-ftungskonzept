from reportlab.platypus import *
from reportlab.lib import styles
from reportlab.lib.pagesizes import A4

def checkbox(v):
    return "☑" if v else "☐"


def create_pdf(file, ANE, res):

    doc = SimpleDocTemplate(file, pagesize=A4)
    s = styles.getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("Lüftungskonzept DIN 1946-6", s["Title"]))

    elements.append(Paragraph(f"Fläche: {ANE}", s["Normal"]))

    notwendig = res["delta"] > 0

    elements.append(Paragraph(f"Maßnahmen: {checkbox(notwendig)}", s["Normal"]))

    elements.append(Paragraph(f"ALD: {res['n_ald']}", s["Normal"]))
    elements.append(Paragraph(f"ÜLD: {res['n_uld']}", s["Normal"]))

    doc.build(elements)
