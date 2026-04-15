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
# Standard Tabellenstil
# -----------------------------
def table_style():
    return [
        ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]


# -----------------------------
# PDF
# -----------------------------
def create_pdf(filename, ANE, res):

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=20,
        bottomMargin=20
    )

    elements = []

    # -----------------------------
    # HEADER
    # -----------------------------
    elements.append(
        Paragraph("<b>LÜFTUNGSKONZEPT NACH DIN 1946-6</b>", styles["Title"])
    )
    elements.append(Spacer(1, 10))

    # -----------------------------
    # 1. ALLGEMEIN
    # -----------------------------
    elements.append(Paragraph("<b>1. Allgemeine Angaben</b>", styles["Heading3"]))

    t = Table([
        ["Nutzungseinheit", "Wohnung"],
        ["Fläche (ANE)", f"{ANE} m²"],
    ], colWidths=[200, 300])
    t.setStyle(table_style())
    elements.append(t)
    elements.append(Spacer(1, 8))

    # -----------------------------
    # 2. ERFORDERNIS
    # -----------------------------
    notwendig = res["delta"] > 0

    elements.append(Paragraph("<b>2. Erfordernis von Maßnahmen</b>", styles["Heading3"]))

    t = Table([
        ["Lüftungskonzept erforderlich", cb(True)],
        ["Feuchteschutz ausreichend", cb(not notwendig)],
        ["Zusätzliche Maßnahmen erforderlich", cb(notwendig)],
    ], colWidths=[400, 100])
    t.setStyle(table_style())
    elements.append(t)
    elements.append(Spacer(1, 8))

    # -----------------------------
    # 3. SYSTEM
    # -----------------------------
    elements.append(Paragraph("<b>3. Lüftungssystem</b>", styles["Heading3"]))

    t = Table([
        ["Freie Lüftung", cb(True)],
        ["Abluftsystem (DIN 18017-3)", cb(True)],
        ["Kombiniertes System", cb(True)],
    ], colWidths=[400, 100])
    t.setStyle(table_style())
    elements.append(t)
    elements.append(Spacer(1, 8))

    # -----------------------------
    # 4. LUFTMENGEN
    # -----------------------------
    elements.append(Paragraph("<b>4. Luftvolumenströme</b>", styles["Heading3"]))

    t = Table([
        ["Feuchteschutz", f"{round(res['q_required'],1)} m³/h"],
        ["Abluft gesamt", f"{round(res['q_abluft'],1)} m³/h"],
        ["Differenz", f"{round(res['delta'],1)} m³/h"],
    ], colWidths=[300, 200])
    t.setStyle(table_style())
    elements.append(t)
    elements.append(Spacer(1, 8))

    # -----------------------------
    # 5. RÄUME
    # -----------------------------
    elements.append(Paragraph("<b>5. Räume</b>", styles["Heading3"]))

    data = [["Raum", "Typ", "Kategorie", "Abluft"]]

    for _, r in res["df"].iterrows():
        data.append([
            r["Raum"],
            r["Typ"],
            r["Kategorie"],
            f"{round(r['Abluft (m³/h)'],1)}"
        ])

    t = Table(data, colWidths=[120, 80, 180, 80])
    t.setStyle(table_style())
    elements.append(t)
    elements.append(Spacer(1, 8))

    # -----------------------------
    # 6. BAUTEILE
    # -----------------------------
    elements.append(Paragraph("<b>6. Lüftungselemente</b>", styles["Heading3"]))

    t = Table([
        ["ALD", f"{res['n_ald']} Stück"],
        ["ÜLD", f"{res['n_uld']} Stück"],
    ], colWidths=[300, 200])
    t.setStyle(table_style())
    elements.append(t)
    elements.append(Spacer(1, 8))

    # -----------------------------
    # 7. LUFTFÜHRUNG
    # -----------------------------
    elements.append(Paragraph("<b>7. Luftführung</b>", styles["Heading3"]))

    flow_data = [["Von", "Nach", "Volumenstrom", "ÜLD"]]

    for (a, b), d in res["uld_edges"].items():
        flow_data.append([
            a,
            b,
            f"{d['Volumenstrom']} m³/h",
            f"{d['Anzahl']}"
        ])

    t = Table(flow_data, colWidths=[120, 120, 120, 80])
    t.setStyle(table_style())
    elements.append(t)
    elements.append(Spacer(1, 8))

    # -----------------------------
    # 8. PRÜFUNG
    # -----------------------------
    elements.append(Paragraph("<b>8. Prüfung</b>", styles["Heading3"]))

    check_data = []

    if res["errors"]:
        for e in res["errors"]:
            check_data.append([f"FEHLER: {e}"])
    if res["warnings"]:
        for w in res["warnings"]:
            check_data.append([f"HINWEIS: {w}"])

    if not check_data:
        check_data = [["Keine Auffälligkeiten"]]

    t = Table(check_data, colWidths=[500])
    t.setStyle(table_style())
    elements.append(t)
    elements.append(Spacer(1, 12))

    # -----------------------------
    # 9. UNTERSCHRIFT
    # -----------------------------
    elements.append(Paragraph("<b>9. Bestätigung</b>", styles["Heading3"]))

    t = Table([
        ["Ort, Datum", ""],
        ["Unterschrift Planer", ""],
    ], colWidths=[200, 300], rowHeights=[25, 40])

    t.setStyle(table_style())
    elements.append(t)

    # -----------------------------
    # BUILD
    # -----------------------------
    doc.build(elements)
