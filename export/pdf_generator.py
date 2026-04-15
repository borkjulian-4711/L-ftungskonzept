from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

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
def add_page_numbers(canvas, doc):
    page_num = canvas.getPageNumber()
    text = f"Seite {page_num}"

    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(550, 15, text)

    # Header
    canvas.drawString(30, 820, "Lüftungskonzept DIN 1946-6")


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
    # Titel
    # -----------------------------
    elements.append(Paragraph("<b>LÜFTUNGSKONZEPT</b>", styles["Title"]))
    elements.append(Spacer(1, 10))

    # -----------------------------
    # 1. Allgemein
    # -----------------------------
    elements.append(Paragraph("<b>1. Allgemeine Angaben</b>", styles["Heading3"]))

    elements.append(Table([
        ["Fläche (ANE)", f"{ANE} m²"]
    ], colWidths=[200, 300], style=table_style()))

    elements.append(Spacer(1, 10))

    # -----------------------------
    # 2. Bewertung
    # -----------------------------
    notwendig = res["delta"] > 0

    elements.append(Paragraph("<b>2. Bewertung</b>", styles["Heading3"]))

    elements.append(Table([
        ["Feuchteschutz erfüllt", cb(not notwendig)],
        ["Maßnahmen erforderlich", cb(notwendig)]
    ], colWidths=[350, 100], style=table_style()))

    elements.append(Spacer(1, 10))

    # -----------------------------
    # 3. Luftmengen
    # -----------------------------
    elements.append(Paragraph("<b>3. Luftmengen</b>", styles["Heading3"]))

    elements.append(Table([
        ["Feuchteschutz", f"{round(res['q_required'],1)} m³/h"],
        ["Abluft", f"{round(res['q_abluft'],1)} m³/h"],
        ["Δ", f"{round(res['delta'],1)} m³/h"],
    ], colWidths=[250, 200], style=table_style()))

    elements.append(Spacer(1, 10))

    # -----------------------------
    # 4. Räume (MEHRSEITIG!)
    # -----------------------------
    elements.append(Paragraph("<b>4. Räume</b>", styles["Heading3"]))

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
    # 5. Luftführung (MEHRSEITIG)
    # -----------------------------
    elements.append(Paragraph("<b>5. Luftführung</b>", styles["Heading3"]))

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
    elements.append(PageBreak())

    # -----------------------------
    # 6. Komponenten
    # -----------------------------
    elements.append(Paragraph("<b>6. Komponenten</b>", styles["Heading3"]))

    elements.append(Table([
        ["ALD", f"{res['n_ald']}"],
        ["ÜLD", f"{res['n_uld']}"]
    ], colWidths=[250, 200], style=table_style()))

    elements.append(Spacer(1, 10))

    # -----------------------------
    # 7. Prüfung
    # -----------------------------
    elements.append(Paragraph("<b>7. Prüfung</b>", styles["Heading3"]))

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

    # -----------------------------
    # 8. Unterschrift
    # -----------------------------
    elements.append(Paragraph("<b>8. Bestätigung</b>", styles["Heading3"]))

    elements.append(Table([
        ["Ort, Datum", ""],
        ["Unterschrift", ""]
    ], colWidths=[200, 300], rowHeights=[25, 40], style=table_style()))

    # -----------------------------
    # BUILD (mit Header/Footer!)
    # -----------------------------
    doc.build(
        elements,
        onFirstPage=add_page_numbers,
        onLaterPages=add_page_numbers
    )
