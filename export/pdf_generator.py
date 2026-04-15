from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

styles = getSampleStyleSheet()

def create_din_pdf(filename, project, results, df_rooms, text, n_ald, n_uld, paths):

    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    elements.append(Paragraph("Lüftungskonzept DIN 1946-6", styles["Title"]))
    elements.append(Spacer(1,10))

    elements.append(Paragraph("Projekt", styles["Heading2"]))
    elements.append(Paragraph(f"Fläche: {project['ANE']} m²", styles["Normal"]))

    elements.append(Spacer(1,10))

    elements.append(Paragraph("Ergebnisse", styles["Heading2"]))
    elements.append(Paragraph(f"Feuchteschutz: {results['q_required']:.1f}", styles["Normal"]))
    elements.append(Paragraph(f"Abluft: {results['q_abluft']:.1f}", styles["Normal"]))

    elements.append(Spacer(1,10))

    elements.append(Paragraph("ALD / ÜLD", styles["Heading2"]))
    elements.append(Paragraph(f"ALD: {n_ald}", styles["Normal"]))
    elements.append(Paragraph(f"ÜLD: {n_uld}", styles["Normal"]))

    elements.append(Spacer(1,10))

    elements.append(Paragraph("Luftpfade", styles["Heading2"]))
    for p in paths:
        elements.append(Paragraph(" → ".join(p), styles["Normal"]))

    doc.build(elements)
