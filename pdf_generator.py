from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

styles = getSampleStyleSheet()

def checkbox(val):
    return "☑" if val else "☐"


def create_din_pdf(filename, project_data, results, df_rooms, measures_text, n_ald, n_uld):

    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    elements.append(Paragraph("LÜFTUNGSKONZEPT NACH DIN 1946-6", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Projekt
    elements.append(Paragraph("Projektangaben", styles["Heading2"]))
    elements.append(Table([
        ["Projekt", project_data["name"]],
        ["Fläche", project_data["ANE"]],
        ["fWS", project_data["fWS"]],
    ]))

    elements.append(Spacer(1, 10))

    # Ergebnis
    notwendig = results["delta"] > 0

    elements.append(Paragraph("Bewertung", styles["Heading2"]))
    elements.append(Table([
        ["Feuchteschutz erforderlich", round(results["q_required"],1)],
        ["Abluft vorhanden", round(results["q_abluft"],1)],
        ["Maßnahmen erforderlich", checkbox(notwendig)],
    ]))

    elements.append(Spacer(1, 10))

    # ALD / ÜLD
    elements.append(Paragraph("Lüftungskomponenten", styles["Heading2"]))
    elements.append(Table([
        ["ALD", f"{n_ald} Stück"],
        ["ÜLD", f"{n_uld} Stück"],
    ]))

    elements.append(Spacer(1, 10))

    # Räume
    room_data = [["Raum", "Typ", "Abluft"]]

    for _, r in df_rooms.iterrows():
        room_data.append([r["Raum"], r["Typ"], r["Abluft (m³/h)"]])

    elements.append(Table(room_data))

    elements.append(Spacer(1, 10))

    # Maßnahmen
    elements.append(Paragraph("Maßnahmen", styles["Heading2"]))
    elements.append(Paragraph(measures_text, styles["Normal"]))

    doc.build(elements)