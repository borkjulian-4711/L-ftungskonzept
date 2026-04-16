from reportlab.platypus import *
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import os

styles = getSampleStyleSheet()

LOGO_PATH = "logo.png"


# -----------------------------
# HEADER / FOOTER
# -----------------------------
def draw_header_footer(canvas, doc):

    width, height = A4

    if os.path.exists(LOGO_PATH):
        canvas.drawImage(LOGO_PATH, width - 120, height - 70, width=100)

    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(40, height - 40, "Lüftungskonzept DIN 1946-6")

    canvas.setFont("Helvetica", 8)
    canvas.drawString(40, height - 55,
        f"Datum: {datetime.now().strftime('%d.%m.%Y')}")

    canvas.drawRightString(width - 40, 20, f"Seite {doc.page}")


# -----------------------------
# HELPER
# -----------------------------
def safe_get(res, key, default):
    return res[key] if key in res else default


def checkbox(value):
    return "☑" if value else "☐"


def box_table(data):
    return Table(data, style=[
        ("GRID", (0,0), (-1,-1), 0.8, colors.black),
        ("FONTSIZE", (0,0), (-1,-1), 8),
    ])


# -----------------------------
# PDF
# -----------------------------
def create_multi_pdf(file, project):

    doc = SimpleDocTemplate(file, pagesize=A4)
    elements = []

    for name, data in project.items():

        res = data.get("res", {})

        # -----------------------------
        # FORM A (optional)
        # -----------------------------
        fb_a = safe_get(res, "formblatt_a", {
            "erforderlich": False,
            "begruendung": "-"
        })

        elements.append(Paragraph("Formblatt A", styles["Heading2"]))
        elements.append(box_table([
            ["Erforderlich", checkbox(fb_a["erforderlich"])],
            ["Begründung", fb_a["begruendung"]],
        ]))

        elements.append(Spacer(1,10))

        # -----------------------------
        # FORM B
        # -----------------------------
        fb_b = safe_get(res, "formblatt_b", {})

        elements.append(Paragraph("Formblatt B", styles["Heading2"]))

        if fb_b:
            elements.append(box_table([[k, str(v)] for k,v in fb_b.items()]))
        else:
            elements.append(Paragraph("Keine Daten", styles["Normal"]))

        elements.append(Spacer(1,10))

        # -----------------------------
        # FORM C
        # -----------------------------
        fb_c = safe_get(res, "formblatt_c", {})

        elements.append(Paragraph("Formblatt C", styles["Heading2"]))

        if fb_c:
            table = [["Stufe","Soll","Ist","Status"]]
            for k,v in fb_c.items():
                table.append([k, v["erforderlich"], v["vorhanden"], v["status"]])
            elements.append(box_table(table))
        else:
            elements.append(Paragraph("Keine Daten", styles["Normal"]))

        elements.append(Spacer(1,10))

        # -----------------------------
        # FORM D
        # -----------------------------
        fb_d = safe_get(res, "formblatt_d", {
            "massnahme": "-",
            "begruendung": "-"
        })

        elements.append(Paragraph("Formblatt D", styles["Heading2"]))
        elements.append(box_table([
            ["Maßnahme", fb_d["massnahme"]],
            ["Begründung", fb_d["begruendung"]],
        ]))

        elements.append(Spacer(1,10))

        # -----------------------------
        # FORM E
        # -----------------------------
        fb_e = safe_get(res, "formblatt_e", "-")

        elements.append(Paragraph("Formblatt E", styles["Heading2"]))
        elements.append(box_table([[fb_e]]))

        elements.append(PageBreak())

    doc.build(elements, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
