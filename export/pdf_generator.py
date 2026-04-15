from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
import os

styles = getSampleStyleSheet()

LOGO_PATH = "assets/logo.png"


# -----------------------------
# Tabellenstil
# -----------------------------
def table_style():
    return [
        ("GRID", (0,0), (-1,-1), 0.8, colors.black),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]


# -----------------------------
# Header / Footer mit Logo
# -----------------------------
def header_footer(canvas, doc):

    canvas.saveState()

    width, height = A4

    # Logo
    if os.path.exists(LOGO_PATH):
        canvas.drawImage(
            LOGO_PATH,
            30,
            height - 60,
            width=120,
            preserveAspectRatio=True,
            mask='auto'
        )

    # Firmenblock rechts
    canvas.setFont("Helvetica", 9)

    canvas.drawRightString(width - 30, height - 30, "Ingenieurbüro Mustermann")
    canvas.drawRightString(width - 30, height - 42, "Musterstraße 1")
    canvas.drawRightString(width - 30, height - 54, "12345 Musterstadt")
    canvas.drawRightString(width - 30, height - 66, "info@buero.de")

    # Linie unter Header
    canvas.line(30, height - 75, width - 30, height - 75)

    # Footer
    page_num = canvas.getPageNumber()
    canvas.drawRightString(width - 30, 15, f"Seite {page_num}")

    canvas.restoreState()


# -----------------------------
# PDF erstellen
# -----------------------------
def create_multi_pdf(file, project):

    doc = SimpleDocTemplate(
        file,
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=90,
        bottomMargin=30
    )

    elements = []

    for name, data in project.items():

        meta = data["meta"]
        res = data["res"]

        # Titel
        elements.append(Paragraph(
            "<b>Lüftungskonzept nach DIN 1946-6</b>",
            styles["Title"]
        ))
        elements.append(Spacer(1, 10))

        # Projektblock
        elements.append(Table([
            ["Projekt", meta["projekt"]],
            ["Adresse", meta["adresse"]],
            ["Wohnung", name],
            ["Bearbeiter", meta["bearbeiter"]],
        ], colWidths=[150, 350], style=table_style()))

        elements.append(Spacer(1, 10))

        # Bewertung
        elements.append(Paragraph("<b>Bewertung</b>", styles["Heading3"]))

        elements.append(Table([
            ["Feuchteschutz erfüllt", "Ja" if res["delta"]<=0 else "Nein"],
            ["Maßnahmen erforderlich", "Ja" if res["delta"]>0 else "Nein"],
        ], style=table_style()))

        # Räume
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("<b>Räume</b>", styles["Heading3"]))

        room_data = [["Raum","Typ","Abluft"]]

        for _, r in res["df"].iterrows():
            room_data.append([
                r["Raum"],
                r["Typ"],
                r["Abluft (m³/h)"]
            ])

        elements.append(Table(room_data, repeatRows=1, style=table_style()))

        # Luftführung
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("<b>Luftführung</b>", styles["Heading3"]))

        flow_data = [["Von","Nach","m³/h","ÜLD"]]

        for (a,b), d in res["uld_edges"].items():
            flow_data.append([
                a,
                b,
                d["Volumenstrom"],
                d["Anzahl"]
            ])

        elements.append(Table(flow_data, repeatRows=1, style=table_style()))

        # Text
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("<b>Beschreibung</b>", styles["Heading3"]))
        elements.append(Paragraph(res["text"], styles["Normal"]))

        elements.append(PageBreak())

    doc.build(
        elements,
        onFirstPage=header_footer,
        onLaterPages=header_footer
    )
