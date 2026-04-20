# export/pdf_generator.py

import os
import tempfile
from typing import Dict, List

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter


def _draw_header(c: canvas.Canvas, title: str, subtitle: str = "DIN 1946-6"):
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20 * mm, 280 * mm, title)
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, 275 * mm, subtitle)


def _draw_meta_block(c: canvas.Canvas, meta: Dict):
    c.setFont("Helvetica", 9)
    y = 265 * mm

    items = [
        ("Projekt", meta.get("projekt", "")),
        ("Adresse", meta.get("adresse", "")),
        ("Bearbeiter", meta.get("bearbeiter", "")),
    ]

    for label, value in items:
        c.drawString(20 * mm, y, f"{label}: {value}")
        y -= 5 * mm


def _draw_key_value_lines(c: canvas.Canvas, pairs: List[tuple], start_y_mm: float = 240):
    c.setFont("Helvetica", 10)
    y = start_y_mm * mm

    for key, value in pairs:
        c.drawString(22 * mm, y, f"{key}: {value}")
        y -= 7 * mm


def _create_simple_formblatt_page(filename: str, title: str, meta: Dict, rows: List[tuple]):
    c = canvas.Canvas(filename, pagesize=A4)
    _draw_header(c, title)
    _draw_meta_block(c, meta)
    _draw_key_value_lines(c, rows)
    c.save()


def _create_room_table_overlay(df_rooms, filename):
    c = canvas.Canvas(filename, pagesize=A4)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, 250 * mm, "Raum")
    c.drawString(70 * mm, 250 * mm, "Kategorie")
    c.drawString(130 * mm, 250 * mm, "Zuluft")
    c.drawString(160 * mm, 250 * mm, "Abluft")

    y = 244 * mm
    c.setFont("Helvetica", 9)

    for _, row in df_rooms.iterrows():
        if y < 30 * mm:
            break

        c.drawString(20 * mm, y, str(row.get("Raum", ""))[:28])
        c.drawString(70 * mm, y, str(row.get("Kategorie (DIN 1946-6)", ""))[:30])

        zuluft = row.get("Zuluft (m³/h)", 0)
        abluft = row.get("Abluft (m³/h)", 0)

        c.drawRightString(150 * mm, y, str(round(zuluft)))
        c.drawRightString(180 * mm, y, str(round(abluft)))

        y -= 6 * mm

    c.save()


def _create_text_overlay(lines: List[str], filename: str, title: str):
    c = canvas.Canvas(filename, pagesize=A4)
    _draw_header(c, title)

    y = 255 * mm
    c.setFont("Helvetica", 10)

    for line in lines:
        if y < 20 * mm:
            c.showPage()
            _draw_header(c, title)
            c.setFont("Helvetica", 10)
            y = 260 * mm

        c.drawString(20 * mm, y, line)
        y -= 6 * mm

    c.save()


def _merge_template_with_overlay(template_path: str, overlay_path: str, output_path: str):
    template = PdfReader(template_path)
    overlay = PdfReader(overlay_path)

    writer = PdfWriter()
    page = template.pages[0]
    page.merge_page(overlay.pages[0])
    writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)


def _append_pdf(writer: PdfWriter, path: str):
    reader = PdfReader(path)
    for page in reader.pages:
        writer.add_page(page)


def _build_formblatt_a(meta: Dict, summary: Dict) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    rows = [
        ("Lüftungskonzept erforderlich", "Ja"),
        ("Begründung", "Berechnung nach DIN 1946-6 durchgeführt"),
        ("Lüftungssystem", summary.get("system", "")),
    ]
    _create_simple_formblatt_page(tmp.name, "Formblatt A – Erfordernis", meta, rows)
    return tmp.name


def _build_formblatt_b(meta: Dict, summary: Dict) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    rows = [
        ("Wohnfläche ANE", f"{summary.get('ane', '-')} m²"),
        ("Wind", summary.get("wind", "-")),
        ("Luftdicht", "Ja" if summary.get("luftdicht") else "Nein"),
        ("Hüllfläche", f"{summary.get('aenv', '-')} m²"),
    ]
    _create_simple_formblatt_page(tmp.name, "Formblatt B – Grundlagen", meta, rows)
    return tmp.name


def _build_formblatt_c(meta: Dict, summary: Dict, df_rooms) -> str:
    tmp_overlay = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    _create_room_table_overlay(df_rooms, tmp_overlay.name)

    levels = summary.get("levels", {})
    lines = [
        f"FL: {levels.get('FL', '-')} m³/h | RL: {levels.get('RL', '-')} m³/h | "
        f"NL: {levels.get('NL', '-')} m³/h | IL: {levels.get('IL', '-')} m³/h",
        f"qv erforderlich: {summary.get('qv', '-')} m³/h",
        f"q_supply: {summary.get('zu', '-')} m³/h | q_mech: {summary.get('ab', '-')} m³/h",
    ]

    tmp_header = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    _create_text_overlay(lines, tmp_header.name, "Formblatt C – Luftvolumenströme")

    # Header + Tabelle zusammenführen
    tmp_join = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    _merge_template_with_overlay(tmp_header.name, tmp_overlay.name, tmp_join.name)

    template_path = "templates/formblatt_c_template.pdf"
    if os.path.exists(template_path):
        tmp_result = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        _merge_template_with_overlay(template_path, tmp_join.name, tmp_result.name)
        return tmp_result.name

    return tmp_join.name


def _build_formblatt_d(meta: Dict, summary: Dict, validation: Dict) -> str:
    lines = [
        f"Systembewertung: {summary.get('status', '-')}",
        f"Fehler: {len(validation.get('errors', []))}",
        f"Warnungen: {len(validation.get('warnings', []))}",
    ]

    errors = validation.get("errors", [])
    for e in errors[:8]:
        lines.append(f"- {e}")

    tmp_overlay = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    _create_text_overlay(lines, tmp_overlay.name, "Formblatt D – Systemfestlegung")

    template_path = "templates/formblatt_d_template.pdf"
    if os.path.exists(template_path):
        tmp_result = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        _merge_template_with_overlay(template_path, tmp_overlay.name, tmp_result.name)
        return tmp_result.name

    return tmp_overlay.name


def _build_formblatt_e(meta: Dict, text: str) -> str:
    lines = [line for line in text.split("\n") if line.strip()]

    tmp_overlay = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    _create_text_overlay(lines, tmp_overlay.name, "Formblatt E – Begründung")

    template_path = "templates/formblatt_e_template.pdf"
    if os.path.exists(template_path):
        tmp_result = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        _merge_template_with_overlay(template_path, tmp_overlay.name, tmp_result.name)
        return tmp_result.name

    return tmp_overlay.name


# -------------------------------------------------
# HAUPTFUNKTION
# -------------------------------------------------
def create_multi_pdf(filename, data):
    writer = PdfWriter()

    for _, content in data.items():
        meta = content.get("meta", {})
        res = content["res"]

        summary = res.get("validation", {}).get("summary", {})
        validation = res.get("validation", {})

        generated_pages = [
            _build_formblatt_a(meta, summary),
            _build_formblatt_b(meta, summary),
            _build_formblatt_c(meta, summary, res["df_rooms"]),
            _build_formblatt_d(meta, summary, validation),
            _build_formblatt_e(meta, res.get("formblatt_e", "")),
        ]

        for page_path in generated_pages:
            _append_pdf(writer, page_path)

    with open(filename, "wb") as f:
        writer.write(f)
