from reportlab.platypus import *
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()


# -----------------------------
# STYLES
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
# PDF
# -----------------------------
def create_multi_pdf(file, project):

    doc = SimpleDocTemplate(file, pagesize=A4)
    elements = []

    for name, data in project.items():

        res = data["res"]

        # =============================
        # TITEL
        # =============================
        elements.append(Paragraph(
            "<b>LÜFTUNGSKONZEPT NACH DIN 1946-6</b>",
            styles["Title"]
        ))

        elements.append(Spacer(1, 10))

        # =============================
        # 1. ALLGEMEINE ANGABEN
        # =============================
        elements.append(Paragraph("<b>1. Allgemeine Angaben</b>", styles["Heading3"]))

        elements.append(box_table([
            ["Wohnung", name],
            ["Projekt", data.get("meta", {}).get("projekt", "")],
            ["Adresse", data.get("meta", {}).get("adresse", "")],
            ["Bearbeiter", data.get("meta", {}).get("bearbeiter", "")],
        ], colWidths=[150, 300]))

        elements.append(Spacer(1, 10))

        # =============================
        # 2. FORMBLATT A
        # =============================
        elements.append(Paragraph("<b>2. Notwendigkeit Lüftungskonzept</b>", styles["Heading3"]))

        fb_a = res["formblatt_a"]

        elements.append(box_table([
            ["Lüftungskonzept erforderlich", checkbox(fb_a["erforderlich"])],
            ["Begründung", fb_a["begruendung"]],
        ], colWidths=[300, 150]))

        elements.append(Spacer(1, 10))

        # =============================
        # 3. FORMBLATT B
        # =============================
        elements.append(Paragraph("<b>3. Gebäudedaten</b>", styles["Heading3"]))

        fb_b = res["formblatt_b"]

        b_data = []
        for k, v in fb_b.items():
            b_data.append([k, str(v)])

        elements.append(box_table(b_data, colWidths=[200, 250]))

        elements.append(Spacer(1, 10))

        # =============================
        # 4. FORMBLATT C
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
        # 5. FORMBLATT D
        # =============================
        elements.append(Paragraph("<b>5. Maßnahmen</b>", styles["Heading3"]))

        fb_d = res["formblatt_d"]

        elements.append(box_table([
            ["Maßnahme", fb_d["massnahme"]],
            ["Begründung", fb_d["begruendung"]],
        ]))

        elements.append(Spacer(1, 10))

        # =============================
        # 6. FORMBLATT E
        # =============================
        elements.append(Paragraph("<b>6. Ergebnis / Konzept</b>", styles["Heading3"]))

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

    doc.build(elements)
