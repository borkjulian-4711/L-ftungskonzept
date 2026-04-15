from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()

def table_style():
    return [
        ("GRID", (0,0), (-1,-1), 0.8, colors.black),
        ("FONTSIZE", (0,0), (-1,-1), 9),
    ]

def create_multi_pdf(file, project):

    doc = SimpleDocTemplate(file, pagesize=A4)
    elements = []

    for name, data in project.items():

        meta = data["meta"]
        res = data["res"]

        # Kopf
        elements.append(Paragraph("<b>Lüftungskonzept DIN 1946-6 (Anhang E)</b>", styles["Title"]))
        elements.append(Spacer(1,10))

        elements.append(Table([
            ["Projekt", meta["projekt"]],
            ["Adresse", meta["adresse"]],
            ["Wohnung", name],
            ["Bearbeiter", meta["bearbeiter"]],
        ], style=table_style()))

        elements.append(Spacer(1,10))

        # Bewertung
        elements.append(Paragraph("<b>Bewertung</b>", styles["Heading3"]))

        elements.append(Table([
            ["Feuchteschutz erfüllt", "Ja" if res["delta"]<=0 else "Nein"],
            ["Maßnahmen erforderlich", "Ja" if res["delta"]>0 else "Nein"],
        ], style=table_style()))

        # Räume
        elements.append(Spacer(1,10))
        elements.append(Paragraph("<b>Räume</b>", styles["Heading3"]))

        data_table = [["Raum","Typ","Abluft"]]
        for _, r in res["df"].iterrows():
            data_table.append([r["Raum"], r["Typ"], r["Abluft (m³/h)"]])

        elements.append(Table(data_table, repeatRows=1, style=table_style()))

        # Luftführung
        elements.append(Spacer(1,10))
        elements.append(Paragraph("<b>Luftführung</b>", styles["Heading3"]))

        flow = [["Von","Nach","m³/h","ÜLD"]]
        for (a,b), d in res["uld_edges"].items():
            flow.append([a,b,d["Volumenstrom"],d["Anzahl"]])

        elements.append(Table(flow, repeatRows=1, style=table_style()))

        # Text
        elements.append(Spacer(1,10))
        elements.append(Paragraph("<b>Beschreibung</b>", styles["Heading3"]))
        elements.append(Paragraph(res["text"], styles["Normal"]))

        elements.append(PageBreak())

    doc.build(elements)
