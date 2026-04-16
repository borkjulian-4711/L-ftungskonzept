from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()

def table_style():
    return [
        ("GRID", (0,0), (-1,-1), 0.8, colors.black),
        ("FONTSIZE", (0,0), (-1,-1), 8),
    ]

def create_multi_pdf(file, project):

    doc = SimpleDocTemplate(file, pagesize=A4)
    elements = []

    for name, data in project.items():

        meta = data["meta"]
        res = data["res"]

        elements.append(Paragraph("Formblatt A", styles["Heading2"]))

        elements.append(Table([
            ["Lüftungskonzept erforderlich",
             "Ja" if res["formblatt_a"]["erforderlich"] else "Nein"],
            ["Begründung", res["formblatt_a"]["begruendung"]],
        ], style=table_style()))

        elements.append(Spacer(1,10))

        elements.append(Paragraph("Lüftungsstufen", styles["Heading3"]))
        elements.append(Table([
            ["FL", res["levels"]["FL"]],
            ["RL", res["levels"]["RL"]],
            ["NL", res["levels"]["NL"]],
            ["IL", res["levels"]["IL"]],
        ], style=table_style()))

        elements.append(PageBreak())

    doc.build(elements)
