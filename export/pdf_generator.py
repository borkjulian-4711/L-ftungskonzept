from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus.tableofcontents import TableOfContents
import os

styles = getSampleStyleSheet()


def create_multi_pdf(path, data):

    doc = SimpleDocTemplate(path)
    story = []

    for name, content in data.items():

        firma = content["firma"]
        meta = content["meta"]
        res = content["res"]

        # -----------------------------
        # LOGO
        # -----------------------------
        if os.path.exists(firma["logo_path"]):
            story.append(Image(firma["logo_path"], width=5*cm, height=2.5*cm))

        story.append(Spacer(1, 20))

        # -----------------------------
        # DECKBLATT
        # -----------------------------
        story.append(Paragraph("LÜFTUNGSKONZEPT", styles["Title"]))
        story.append(Spacer(1, 20))

        story.append(Paragraph(f"Projekt: {meta['projekt']}", styles["Normal"]))
        story.append(Paragraph(f"Adresse: {meta['adresse']}", styles["Normal"]))
        story.append(Paragraph(f"Bearbeiter: {meta['bearbeiter']}", styles["Normal"]))
        story.append(Paragraph(f"Datum: {meta['datum']}", styles["Normal"]))

        story.append(PageBreak())

        # -----------------------------
        # INHALTSVERZEICHNIS
        # -----------------------------
        toc = TableOfContents()
        story.append(Paragraph("Inhaltsverzeichnis", styles["Heading1"]))
        story.append(toc)
        story.append(PageBreak())

        # -----------------------------
        # TEXT
        # -----------------------------
        story.append(Paragraph("Lüftungskonzept", styles["Heading1"]))
        story.append(Paragraph(res["formblatt_e"], styles["Normal"]))
        story.append(PageBreak())

        # -----------------------------
        # UNTERSCHRIFT
        # -----------------------------
        story.append(Spacer(1, 40))
        story.append(Paragraph("Unterschrift / Stempel", styles["Normal"]))
        story.append(Spacer(1, 40))
        story.append(Paragraph("__________________________", styles["Normal"]))
        story.append(PageBreak())

        # -----------------------------
        # FORMBLATT C
        # -----------------------------
        table_data = [["Raum", "Zuluft", "Abluft"]]

        for _, r in res["df_rooms"].iterrows():
            table_data.append([
                r["Raum"],
                r.get("Zuluft (m³/h)", 0),
                r.get("Abluft (m³/h)", 0)
            ])

        table = Table(table_data)
        table.setStyle([("GRID", (0,0), (-1,-1), 0.5, colors.black)])

        story.append(Paragraph("Formblatt C", styles["Heading2"]))
        story.append(table)
        story.append(PageBreak())

        # -----------------------------
        # FORMBLATT E
        # -----------------------------
        s = res["summary"]

        table = Table([
            ["Zuluft", s["zu"]],
            ["Abluft", s["ab"]],
            ["Infiltration", s["inf"]],
            ["Differenz", s["diff"]],
            ["Ergebnis", s["status"]],
        ])

        table.setStyle([("GRID", (0,0), (-1,-1), 0.5, colors.black)])

        story.append(Paragraph("Formblatt E", styles["Heading2"]))
        story.append(table)

    doc.build(story)
