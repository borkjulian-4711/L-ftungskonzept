# export/pdf_generator.py

from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
import tempfile
import os


# -------------------------------------------------
# Overlay schreiben (Positionen anpassen!)
# -------------------------------------------------
def create_overlay_formblatt_c(df_rooms, filename):

    c = canvas.Canvas(filename)

    y = 700

    for _, row in df_rooms.iterrows():

        c.drawString(50, y, str(row["Raum"]))
        c.drawString(150, y, str(row["Kategorie (DIN 1946-6)"]))
        c.drawString(300, y, str(int(row["Zuluft (m³/h)"])))
        c.drawString(380, y, str(int(row["Abluft (m³/h)"])))

        y -= 20

    c.save()


# -------------------------------------------------
# PDF MERGE
# -------------------------------------------------
def merge_pdfs(template_path, overlay_path, output_path):

    template = PdfReader(template_path)
    overlay = PdfReader(overlay_path)

    writer = PdfWriter()

    page = template.pages[0]
    page.merge_page(overlay.pages[0])

    writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)


# -------------------------------------------------
# HAUPTFUNKTION
# -------------------------------------------------
def create_multi_pdf(filename, data):

    writer = PdfWriter()

    for _, content in data.items():

        res = content["res"]

        # -----------------------------
        # FORMBLATT C
        # -----------------------------
        tmp_overlay = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

        create_overlay_formblatt_c(res["df_rooms"], tmp_overlay.name)

        tmp_result = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

        merge_pdfs(
            "templates/formblatt_c_template.pdf",
            tmp_overlay.name,
            tmp_result.name
        )

        reader = PdfReader(tmp_result.name)
        writer.add_page(reader.pages[0])

        # -----------------------------
        # TEXTSEITE (Bericht)
        # -----------------------------
        tmp_text = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

        c = canvas.Canvas(tmp_text.name)

        y = 800
        for line in res["formblatt_e"].split("\n"):
            c.drawString(50, y, line)
            y -= 15

        c.save()

        reader = PdfReader(tmp_text.name)
        writer.add_page(reader.pages[0])

    with open(filename, "wb") as f:
        writer.write(f)
