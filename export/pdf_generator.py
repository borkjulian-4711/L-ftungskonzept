from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

styles = getSampleStyleSheet()

def checkbox(val):
    return "☑" if val else "☐"


def create_din_pdf(filename, project, results, df_rooms, errors, warnings, n_ald, n_uld, paths):

    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    elements.append(Paragraph("LÜFTUNGSKONZEPT NACH DIN 1946-6", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Projekt", styles["Heading2"]))
    elements.append(Paragraph(f"Fläche: {project['ANE']} m²", styles["Normal"]))

    notwendig = results["delta"] > 0

    elements.append(Paragraph("Bewertung", styles["Heading2"]))
    elements.append(Paragraph(f"Maßnahmen erforderlich: {checkbox(notwendig)}", styles["Normal"]))

    elements.append(Spacer(1, 10))

    elements.append(Paragraph("ALD / ÜLD", styles["Heading2"]))
    elements.append(Paragraph(f"ALD: {n_ald}", styles["Normal"]))
    elements.append(Paragraph(f"ÜLD: {n_uld}", styles["Normal"]))

    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Luftpfade", styles["Heading2"]))
    for p in paths:
        elements.append(Paragraph(" → ".join(p), styles["Normal"]))

    doc.build(elements)
