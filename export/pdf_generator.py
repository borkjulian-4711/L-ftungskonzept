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

    # -----------------------------
    # Titel
    # -----------------------------
    elements.append(Paragraph("LÜFTUNGSKONZEPT NACH DIN 1946-6", styles["Title"]))
    elements.append(Spacer(1, 12))

    # -----------------------------
    # Projekt
    # -----------------------------
    elements.append(Paragraph("1. Projektangaben", styles["Heading2"]))

    elements.append(Table([
        ["Fläche", f"{project['ANE']} m²"],
        ["Feuchteschutz erforderlich", f"{results['q_required']:.1f} m³/h"],
        ["Abluft vorhanden", f"{results['q_abluft']:.1f} m³/h"],
    ], style=[("GRID",(0,0),(-1,-1),1,colors.black)]))

    elements.append(Spacer(1, 12))

    # -----------------------------
    # Bewertung
    # -----------------------------
    notwendig = results["delta"] > 0

    elements.append(Paragraph("2. Notwendigkeit lüftungstechnischer Maßnahmen", styles["Heading2"]))

    elements.append(Table([
        ["Maßnahmen erforderlich", checkbox(notwendig)],
        ["Feuchteschutz erfüllt", checkbox(not notwendig)],
    ], style=[("GRID",(0,0),(-1,-1),1,colors.black)]))

    elements.append(Spacer(1, 12))

    # -----------------------------
    # System
    # -----------------------------
    elements.append(Paragraph("3. Lüftungssystem", styles["Heading2"]))

    elements.append(Table([
        ["Freie Lüftung", checkbox(notwendig)],
        ["Abluftsystem (DIN 18017-3)", checkbox(True)],
        ["Kombiniertes System", checkbox(True)],
    ], style=[("GRID",(0,0),(-1,-1),1,colors.black)]))

    elements.append(Spacer(1, 12))

    # -----------------------------
    # Räume
    # -----------------------------
    elements.append(Paragraph("4. Räume", styles["Heading2"]))

    data = [["Raum", "Typ", "Abluft"]]

    for _, r in df_rooms.iterrows():
        data.append([r["Raum"], r["Typ"], r["Abluft (m³/h)"]])

    elements.append(Table(data, style=[("GRID",(0,0),(-1,-1),1,colors.black)]))

    elements.append(Spacer(1, 12))

    # -----------------------------
    # ALD / ÜLD
    # -----------------------------
    elements.append(Paragraph("5. Lüftungskomponenten", styles["Heading2"]))

    elements.append(Table([
        ["ALD erforderlich", f"{n_ald} Stück"],
        ["ÜLD erforderlich", f"{n_uld} Stück"],
    ], style=[("GRID",(0,0),(-1,-1),1,colors.black)]))

    elements.append(Spacer(1, 12))

    # -----------------------------
    # Luftpfade
    # -----------------------------
    elements.append(Paragraph("6. Luftführung", styles["Heading2"]))

    for p in paths:
        elements.append(Paragraph(" → ".join(p), styles["Normal"]))

    elements.append(Spacer(1, 12))

    # -----------------------------
    # Prüfung
    # -----------------------------
    elements.append(Paragraph("7. Prüfung", styles["Heading2"]))

    for e in errors:
        elements.append(Paragraph(f"FEHLER: {e}", styles["Normal"]))

    for w in warnings:
        elements.append(Paragraph(f"HINWEIS: {w}", styles["Normal"]))

    if not errors and not warnings:
        elements.append(Paragraph("Keine Auffälligkeiten", styles["Normal"]))

    elements.append(Spacer(1, 20))

    # -----------------------------
    # Unterschrift
    # -----------------------------
    elements.append(Paragraph("8. Bestätigung", styles["Heading2"]))

    elements.append(Table([
        ["Ort, Datum", ""],
        ["Unterschrift", ""],
    ], colWidths=[200, 250], rowHeights=[30, 40],
       style=[("GRID",(0,0),(-1,-1),1,colors.black)]))

    doc.build(elements)
