from reportlab.platypus import *
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from datetime import datetime
import os

styles = getSampleStyleSheet()


# -----------------------------
# KONFIG
# -----------------------------
LOGO_PATH = "logo.png"  # <- dein Logo im Repo


# -----------------------------
# HEADER / FOOTER
# -----------------------------
def draw_header_footer(canvas, doc):

    width, height = A4

    # -----------------------------
    # LOGO (oben rechts)
    # -----------------------------
    if os.path.exists(LOGO_PATH):
        canvas.drawImage(
            LOGO_PATH,
            width - 120,
            height - 70,
            width=100,
            preserveAspectRatio=True,
            mask='auto'
        )

    # -----------------------------
    # TITEL
    # -----------------------------
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(40, height - 40, "Lüftungskonzept nach DIN 1946-6")

    # -----------------------------
    # DATUM
    # -----------------------------
    canvas.setFont("Helvetica", 8)
    canvas.drawString(
        40,
        height - 55,
        f"Erstellt am: {datetime.now().strftime('%d.%m.%Y')}"
    )

    # -----------------------------
    # FUSSZEILE
    # -----------------------------
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(
        width - 40,
        20,
        f"Seite {doc.page}"
    )


# -----------------------------
# TABELLENSTYLE
# -----------------------------
def box_table(data, colWidths=None, rowHeights=None):
    return Table(
        data,
        colWidths=colWidths,
        rowHeights=rowHeights,
        style=[
            ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ],
    )


def checkbox(value):
    return "☑" if value else "☐"


# -----------------------------
# PDF GENERATOR
# -----------------------------
def create_multi_pdf(file, project):

    doc = SimpleDocTemplate(
        file,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=90,
        bottomMargin=40
    )

    elements = []

    for name, data in project.items():

        res = data["res"]
        meta = data.get("meta", {})

        # =============================
        # ALLGEMEINE ANGABEN
        # =============================
        elements.append(Paragraph("<b>1. Allgemeine Angaben</b>", styles["Heading3"]))

        elements.append(box_table([
            ["Projekt", meta.get("projekt", "")],
            ["Adresse", meta.get("adresse", "")],
            ["Wohnung", name],
            ["Bearbeiter", meta.get("bearbeiter", "")],
        ], colWidths=[150, 300]))

        elements.append(Spacer(1, 10))

        # =============================
        # FORMBLATT A
        # =============================
        fb_a = res["formblatt_a"]

        elements.append(Paragraph("<b>2. Notwendigkeit</b>", styles["Heading3"]))

        elements.append(box_table([
            ["Lüftungskonzept erforderlich", checkbox(fb_a["erforderlich"])],
            ["Begründung", fb_a["begruendung"]],
        ]))

        elements.append(Spacer(1, 10))

        # =============================
        # FORMBLATT B
        # =============================
        fb_b = res["formblatt_b"]

        elements.append(Paragraph("<b>3. Gebäudedaten</b>", styles["Heading3"]))

        b_data = [[k, str(v)] for k, v in fb_b.items()]
        elements.append(box_table(b_data))

        elements.append(Spacer(1, 10))

        # =============================
        # FORMBLATT C
        # =============================
        elements.append(Paragraph("<b>4. Lüftungsstufen</b>", styles["Heading3"]))

        c_table = [["Stufe", "Soll", "Ist", "Status"]]

        for k, v in res["formblatt_c"].items():
            c_table.append([
                k,
                v["erforderlich"],
                v["vorhanden"],
                v["status"]
            ])

        elements.append(box_table(c_table))

        elements.append(Spacer(1, 10))

        # =============================
        # FORMBLATT D
        # =============================
        fb_d = res["formblatt_d"]

        elements.append(Paragraph("<b>5. Maßnahmen</b>", styles["Heading3"]))

        elements.append(box_table([
            ["Maßnahme", fb_d["massnahme"]],
            ["Begründung", fb_d["begruendung"]],
        ]))

        elements.append(Spacer(1, 10))

        # =============================
        # FORMBLATT E
        # =============================
        elements.append(Paragraph("<b>6. Ergebnis</b>", styles["Heading3"]))

        elements.append(box_table([
            [res["formblatt_e"]]
        ], colWidths=[450], rowHeights=[120]))

        elements.append(Spacer(1, 20))

        # =============================
        # UNTERSCHRIFT
        # =============================
        elements.append(Paragraph("<b>Unterschrift</b>", styles["Heading3"]))

        elements.append(box_table([
            ["Datum", ""],
            ["Unterschrift", ""],
        ], colWidths=[200, 250], rowHeights=[20, 40]))

        elements.append(PageBreak())

    doc.build(elements, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
