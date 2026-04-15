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

    # Projekt
    elements.append(Paragraph("1. Projekt", styles["Heading2"]))
    elements.append(Table([
        ["Fläche", f"{project['ANE']} m²"],
        ["Feuchteschutz", f"{results['q_required']:.1f}"],
        ["Abluft", f"{results['q_abluft']:.1f}"],
    ], style=[("GRID",(0,0),(-1,-1),1,colors.black)]))

    elements.append(Spacer(1, 10))

    notwendig = results["delta"] > 0

    elements.append(Paragraph("2. Bewertung", styles["Heading2"]))
    elements.append(Table([
        ["Maßnahmen erforderlich", checkbox(notwendig)],
        ["Feuchteschutz erfüllt", checkbox(not notwendig)],
    ], style=[("GRID",(0,0),(-1,-1),1,colors.black)]))

    elements.append(Spacer(1, 10))

    elements.append(Paragraph("3. Räume", styles["Heading2"]))

    data = [["Raum", "Typ", "Abluft"]]
    for _, r in df_rooms.iterrows():
        data.append([r["Raum"], r["Typ"], r["Abluft (m³/h)"]])

    elements.append(Table(data, style=[("GRID",(0,0),(-1,-1),1,colors.black)]))

    elements.append(Spacer(1, 10))

    elements.append(Paragraph("4. Komponenten", styles["Heading2"]))
    elements.append(Table([
        ["ALD", n_ald],
        ["ÜLD", n_uld],
    ], style=[("GRID",(0,0),(-1,-1),1,colors.black)]))

    elements.append(Spacer(1, 10))

    elements.append(Paragraph("5. Luftpfade", styles["Heading2"]))
    for p in paths:
        elements.append(Paragraph(" → ".join(p), styles["Normal"]))

    elements.append(Spacer(1, 10))

    elements.append(Paragraph("6. Prüfung", styles["Heading2"]))

    for e in errors:
        elements.append(Paragraph(f"FEHLER: {e}", styles["Normal"]))

    for w in warnings:
        elements.append(Paragraph(f"HINWEIS: {w}", styles["Normal"]))

    if not errors and not warnings:
        elements.append(Paragraph("Keine Auffälligkeiten", styles["Normal"]))

    elements.append(Spacer(1, 20))

    elements.append(Paragraph("7. Unterschrift", styles["Heading2"]))
    elements.append(Table([
        ["Ort, Datum", ""],
        ["Unterschrift", ""],
    ], colWidths=[200,250], rowHeights=[30,40],
       style=[("GRID",(0,0),(-1,-1),1,colors.black)]))

    doc.build(elements)
