from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from datetime import datetime

styles = getSampleStyleSheet()


# -----------------------------
# Checkbox
# -----------------------------
def cb(val):
    return "☑" if val else "☐"


# -----------------------------
# Tabellenstil
# -----------------------------
def table_style():
    return [
        ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]


# -----------------------------
# Header/Footer
# -----------------------------
def header_footer(canvas, doc):
    canvas.setFont("Helvetica", 9)

    # Header
    canvas.drawString(30, 820, "Lüftungskonzept nach DIN 1946-6")

    # Footer
    page_num = canvas.getPageNumber()
    canvas.drawRightString(550, 15, f"Seite {page_num}")


# -----------------------------
# PDF erstellen
# -----------------------------
def create_pdf(filename, ANE, res):

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=40,
        bottomMargin=30
    )

    elements = []

    # -----------------------------
    # KOPFBEREICH (FORMULAR)
    # -----------------------------
    elements.append(Paragraph("<b>LÜFTUNGSKONZEPT NACH DIN 1946-6</b>", styles["Title"]))
    elements.append(Spacer(1, 8))

    projekt_table = Table([
        ["Projekt", "Wohnung 1"],
        ["Adresse", "—"],
        ["Bearbeiter", "—"],
        ["Datum", datetime.today().strftime("%d.%m.%Y")]
    ], colWidths=[150, 350])

    projekt_table.setStyle(table_style())
    elements.append(projekt_table)
    elements.append(Spacer(1, 10))

    # -----------------------------
    # 1. Bewertung
    # -----------------------------
    notwendig = res["delta"] > 0

    elements.append(Paragraph("<b>1. Bewertung</b>", styles["Heading3"]))

    elements.append(Table([
        ["Feuchteschutz erfüllt", cb(not notwendig)],
        ["Lüftungstechnische Maßnahmen erforderlich", cb(notwendig)]
    ], colWidths=[400, 100], style=table_style()))

    elements.append(Spacer(1, 10))

    # -----------------------------
    # 2. Luftmengen
    # -----------------------------
    elements.append(Paragraph("<b>2. Luftmengen</b>", styles["Heading3"]))

    elements.append(Table([
        ["Fläche (ANE)", f"{ANE} m²"],
        ["Feuchteschutz", f"{round(res['q_required'],1)} m³/h"],
        ["Abluft gesamt", f"{round(res['q_abluft'],1)} m³/h"],
        ["Differenz", f"{round(res['delta'],1)} m³/h"]
    ], colWidths=[250, 250], style=table_style()))

    elements.append(Spacer(1, 10))

    # -----------------------------
    # 3. Räume
    # -----------------------------
    elements.append(Paragraph("<b>3. Räume</b>", styles["Heading3"]))

    data = [["Raum", "Typ", "Kategorie", "Abluft"]]

    for _, r in res["df"].iterrows():
        data.append([
            r["Raum"],
            r["Typ"],
            r["Kategorie"],
            f"{round(r['Abluft (m³/h)'],1)}"
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(table_style())
    elements.append(table)

    elements.append(PageBreak())

    # -----------------------------
    # 4. Luftführung
    # -----------------------------
    elements.append(Paragraph("<b>4. Luftführung</b>", styles["Heading3"]))

    flow_data = [["Von", "Nach", "Volumenstrom", "ÜLD"]]

    for (a, b), d in res["uld_edges"].items():
        flow_data.append([
            a,
            b,
            f"{d['Volumenstrom']} m³/h",
            d["Anzahl"]
        ])

    table = Table(flow_data, repeatRows=1)
    table.setStyle(table_style())
    elements.append(table)

    elements.append(Spacer(1, 10))

    # -----------------------------
    # 5. Komponenten
    # -----------------------------
    elements.append(Paragraph("<b>5. Komponenten</b>", styles["Heading3"]))

    elements.append(Table([
        ["ALD", f"{res['n_ald']} Stück"],
        ["ÜLD", f"{res['n_uld']} Stück"]
    ], colWidths=[250, 250], style=table_style()))

    elements.append(Spacer(1, 10))

    # -----------------------------
    # 6. Prüfung
    # -----------------------------
    elements.append(Paragraph("<b>6. Prüfung</b>", styles["Heading3"]))

    check_data = []

    if res["errors"]:
        for e in res["errors"]:
            check_data.append([f"FEHLER: {e}"])

    if res["warnings"]:
        for w in res["warnings"]:
            check_data.append([f"HINWEIS: {w}"])

    if not check_data:
        check_data = [["Keine Auffälligkeiten"]]

    table = Table(check_data)
    table.setStyle(table_style())
    elements.append(table)

    elements.append(Spacer(1, 20))
elements.append(Paragraph("<b>Textliche Beschreibung</b>", styles["Heading3"]))
elements.append(Paragraph(res["text"], styles["Normal"]))
elements.append(Spacer(1, 10))
    # -----------------------------
    # 7. UNTERSCHRIFT
    # -----------------------------
    elements.append(Paragraph("<b>7. Bestätigung</b>", styles["Heading3"]))

    unterschrift = Table([
        ["Ort, Datum", ""],
        ["Planer (Name)", ""],
        ["Unterschrift", ""],
    ], colWidths=[200, 300], rowHeights=[25, 25, 40])

    unterschrift.setStyle(table_style())
    elements.append(unterschrift)

    # -----------------------------
    # BUILD
    # -----------------------------
    doc.build(
        elements,
        onFirstPage=header_footer,
        onLaterPages=header_footer
    )
