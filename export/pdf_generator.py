from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()


# -----------------------------
# FORMULAR-STIL
# -----------------------------
def form_table(data, colWidths=None):
    return Table(
        data,
        colWidths=colWidths,
        style=[
            ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ],
    )


def section(title):
    return Paragraph(f"<b>{title}</b>", styles["Heading3"])


# -----------------------------
# PDF GENERATOR
# -----------------------------
def create_multi_pdf(file, project):

    doc = SimpleDocTemplate(file, pagesize=A4)
    elements = []

    for name, data in project.items():

        meta = data["meta"]
        res = data["res"]

        # -----------------------------
        # 1. TITEL
        # -----------------------------
        elements.append(Paragraph(
            "<b>1. Prüfung lufttechnische Maßnahmen (LtM)</b>",
            styles["Title"]
        ))
        elements.append(Spacer(1, 10))

        # -----------------------------
        # 2. GEBÄUDEDATEN
        # -----------------------------
        elements.append(section("Gebäudedaten"))

        elements.append(form_table([
            ["Projekt", meta.get("projekt", "")],
            ["Adresse", meta.get("adresse", "")],
            ["Wohnung", name],
            ["Bearbeiter", meta.get("bearbeiter", "")]
        ], colWidths=[180, 300]))

        elements.append(Spacer(1, 10))

        # -----------------------------
        # 3. PARAMETER
        # -----------------------------
        elements.append(section("Berechnungsparameter"))

        elements.append(form_table([
            ["Feuchteschutz (m³/h)", round(res["q_required"], 1)],
            ["Abluft gesamt (m³/h)", round(res["q_abluft"], 1)],
            ["Differenz", round(res["delta"], 1)],
            ["ALD Anzahl", res["n_ald"]],
            ["ÜLD Anzahl", res["n_uld"]],
        ]))

        elements.append(Spacer(1, 10))

        # -----------------------------
        # 4. RÄUME
        # -----------------------------
        elements.append(section("Raumdaten"))

        room_data = [["Raum", "Typ", "Abluft (m³/h)"]]

        for _, r in res["df"].iterrows():
            room_data.append([
                r["Raum"],
                r["Typ"],
                r.get("Abluft (m³/h)", "")
            ])

        elements.append(form_table(room_data))

        elements.append(Spacer(1, 10))

        # -----------------------------
        # 5. LUFTFÜHRUNG
        # -----------------------------
        elements.append(section("Luftführung"))

        flow_data = [["Von", "Nach", "Volumenstrom", "ÜLD"]]

        for (a, b), d in res["uld_edges"].items():
            flow_data.append([
                a,
                b,
                f"{d['Volumenstrom']} m³/h",
                d["Anzahl"]
            ])

        elements.append(form_table(flow_data))

        elements.append(Spacer(1, 10))

        # -----------------------------
        # 6. BEWERTUNG
        # -----------------------------
        elements.append(section("Bewertung"))

        elements.append(form_table([
            ["Feuchteschutz erfüllt", "☑" if res["delta"] <= 0 else "☐"],
            ["Maßnahmen erforderlich", "☑" if res["delta"] > 0 else "☐"],
        ]))

        elements.append(Spacer(1, 10))

        # -----------------------------
        # 7. TEXT
        # -----------------------------
        elements.append(section("Zusammenfassung"))

        elements.append(Paragraph(res["text"], styles["Normal"]))

        elements.append(PageBreak())

    doc.build(elements)
