from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

styles = getSampleStyleSheet()


# -----------------------------
# Checkbox
# -----------------------------
def checkbox(val):
    return "☑" if val else "☐"


# -----------------------------
# PDF erstellen
# -----------------------------
def create_pdf(filename, ANE, res):

    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    # -----------------------------
    # Titel
    # -----------------------------
    elements.append(Paragraph("LÜFTUNGSKONZEPT NACH DIN 1946-6", styles["Title"]))
    elements.append(Spacer(1, 12))

    # -----------------------------
    # 1. Projekt
    # -----------------------------
    elements.append(Paragraph("1. Allgemeine Angaben", styles["Heading2"]))

    table = Table([
        ["Nutzungseinheit", "Wohnung"],
        ["Fläche (ANE)", f"{ANE} m²"],
    ], colWidths=[200, 250])

    table.setStyle([("GRID", (0,0), (-1,-1), 1, colors.black)])
    elements.append(table)
    elements.append(Spacer(1, 10))

    # -----------------------------
    # 2. Lüftungskonzept notwendig?
    # -----------------------------
    notwendig = res["delta"] > 0

    elements.append(Paragraph("2. Erfordernis lüftungstechnischer Maßnahmen", styles["Heading2"]))

    table = Table([
        ["Lüftungskonzept erforderlich", checkbox(True)],
        ["Feuchteschutz erfüllt ohne Maßnahmen", checkbox(not notwendig)],
        ["Zusätzliche Maßnahmen erforderlich", checkbox(notwendig)],
    ], colWidths=[350, 100])

    table.setStyle([("GRID", (0,0), (-1,-1), 1, colors.black)])
    elements.append(table)
    elements.append(Spacer(1, 10))

    # -----------------------------
    # 3. Lüftungssystem
    # -----------------------------
    elements.append(Paragraph("3. Gewähltes Lüftungssystem", styles["Heading2"]))

    table = Table([
        ["Freie Lüftung", checkbox(True)],
        ["Abluftsystem nach DIN 18017-3", checkbox(True)],
        ["Kombiniertes System", checkbox(True)],
    ], colWidths=[350, 100])

    table.setStyle([("GRID", (0,0), (-1,-1), 1, colors.black)])
    elements.append(table)
    elements.append(Spacer(1, 10))

    # -----------------------------
    # 4. Luftmengen
    # -----------------------------
    elements.append(Paragraph("4. Luftvolumenströme", styles["Heading2"]))

    table = Table([
        ["Feuchteschutz (erforderlich)", f"{round(res['q_required'],1)} m³/h"],
        ["Abluft gesamt", f"{round(res['q_abluft'],1)} m³/h"],
        ["Differenz", f"{round(res['delta'],1)} m³/h"],
    ], colWidths=[300, 150])

    table.setStyle([("GRID", (0,0), (-1,-1), 1, colors.black)])
    elements.append(table)
    elements.append(Spacer(1, 10))

    # -----------------------------
    # 5. Räume
    # -----------------------------
    elements.append(Paragraph("5. Raumliste", styles["Heading2"]))

    data = [["Raum", "Typ", "Kategorie", "Abluft (m³/h)"]]

    for _, r in res["df"].iterrows():
        data.append([
            r["Raum"],
            r["Typ"],
            r["Kategorie"],
            round(r["Abluft (m³/h)"], 1)
        ])

    table = Table(data)
    table.setStyle([("GRID", (0,0), (-1,-1), 1, colors.black)])
    elements.append(table)
    elements.append(Spacer(1, 10))

    # -----------------------------
    # 6. Lüftungselemente
    # -----------------------------
    elements.append(Paragraph("6. Lüftungselemente", styles["Heading2"]))

    table = Table([
        ["Außenluftdurchlässe (ALD)", f"{res['n_ald']} Stück"],
        ["Überströmöffnungen (ÜLD)", f"{res['n_uld']} Stück"],
    ], colWidths=[300, 150])

    table.setStyle([("GRID", (0,0), (-1,-1), 1, colors.black)])
    elements.append(table)
    elements.append(Spacer(1, 10))

    # -----------------------------
    # 7. Luftführung
    # -----------------------------
    elements.append(Paragraph("7. Luftführung", styles["Heading2"]))

    for (a, b), data in res["uld_edges"].items():
        elements.append(
            Paragraph(
                f"{a} → {b}: {data['Anzahl']} ÜLD "
                f"({data['Volumenstrom']} m³/h)",
                styles["Normal"]
            )
        )

    elements.append(Spacer(1, 10))

    # -----------------------------
    # 8. Prüfung
    # -----------------------------
    elements.append(Paragraph("8. Prüfung / Bewertung", styles["Heading2"]))

    for e in res["errors"]:
        elements.append(Paragraph(f"FEHLER: {e}", styles["Normal"]))

    for w in res["warnings"]:
        elements.append(Paragraph(f"HINWEIS: {w}", styles["Normal"]))

    if not res["errors"] and not res["warnings"]:
        elements.append(Paragraph("Keine Auffälligkeiten", styles["Normal"]))

    elements.append(Spacer(1, 20))

    # -----------------------------
    # 9. Unterschrift
    # -----------------------------
    elements.append(Paragraph("9. Bestätigung", styles["Heading2"]))

    table = Table([
        ["Ort, Datum", ""],
        ["Unterschrift Planer", ""],
    ], colWidths=[200, 250], rowHeights=[30, 40])

    table.setStyle([("GRID", (0,0), (-1,-1), 1, colors.black)])
    elements.append(table)

    # -----------------------------
    # PDF bauen
    # -----------------------------
    doc.build(elements)
