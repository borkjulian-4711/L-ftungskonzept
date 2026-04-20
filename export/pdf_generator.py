# export/pdf_generator.py

from typing import Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


def _p(text: str, style):
    return Paragraph(str(text).replace("\n", "<br/>"), style)


def _table(data: List[List[str]], col_widths=None):
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDEFF2")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111111")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B0B7C3")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def _build_cover(meta: Dict, summary: Dict, styles):
    flow = []
    flow.append(_p("<b>Lüftungskonzept nach DIN 1946-6 / DIN 18017</b>", styles["Title"]))
    flow.append(Spacer(1, 6 * mm))
    flow.append(_p("<b>Projektübersicht</b>", styles["Heading2"]))

    cover_table = [
        ["Projekt", meta.get("projekt", "-")],
        ["Adresse", meta.get("adresse", "-")],
        ["Bearbeiter", meta.get("bearbeiter", "-")],
        ["Lüftungssystem", summary.get("system", "-")],
        ["Wohnfläche ANE", f"{summary.get('ane', '-')} m²"],
        ["Windzone", summary.get("wind", "-")],
        ["Hüllfläche", f"{summary.get('aenv', '-')} m²"],
        ["Luftdichtheit", "Ja" if summary.get("luftdicht") else "Nein"],
    ]
    flow.append(_table([["Parameter", "Wert"]] + cover_table, col_widths=[55 * mm, 120 * mm]))
    flow.append(Spacer(1, 6 * mm))

    levels = summary.get("levels", {})
    flow.append(_p("<b>Lüftungsstufen (DIN 1946-6)</b>", styles["Heading3"]))
    levels_rows = [
        ["FL", f"{levels.get('FL', '-')} m³/h"],
        ["RL", f"{levels.get('RL', '-')} m³/h"],
        ["NL", f"{levels.get('NL', '-')} m³/h"],
        ["IL", f"{levels.get('IL', '-')} m³/h"],
    ]
    flow.append(_table([["Stufe", "Erforderlicher Volumenstrom"]] + levels_rows, col_widths=[30 * mm, 145 * mm]))

    flow.append(PageBreak())
    return flow


def _build_room_situation(df_rooms, styles):
    flow = []
    flow.append(_p("<b>Raumsituation und Luftführung</b>", styles["Heading2"]))
    flow.append(
        _p(
            "Die Tabelle bildet die projektspezifische Raumsituation mit Raumtyp, Normkategorie, "
            "Innenliegend-Status, Überströmziel sowie berechneten Zu-/Abluftvolumenströmen ab.",
            styles["BodyText"],
        )
    )
    flow.append(Spacer(1, 3 * mm))

    header = [
        "Raum",
        "Typ",
        "Fläche",
        "DIN 1946-6",
        "Innenliegend",
        "DIN 18017",
        "Überströmt nach",
        "Zuluft",
        "Abluft",
    ]

    rows = [header]
    for _, row in df_rooms.iterrows():
        rows.append(
            [
                row.get("Raum", ""),
                row.get("Typ", ""),
                f"{row.get('Fläche', '')}",
                row.get("Kategorie (DIN 1946-6)", ""),
                "Ja" if bool(row.get("Innenliegend", False)) else "Nein",
                row.get("DIN 18017 Kategorie", ""),
                row.get("Überströmt nach", ""),
                f"{round(row.get('Zuluft (m³/h)', 0), 1)}",
                f"{round(row.get('Abluft (m³/h)', 0), 1)}",
            ]
        )

    col_widths = [26 * mm, 16 * mm, 14 * mm, 24 * mm, 18 * mm, 18 * mm, 26 * mm, 14 * mm, 14 * mm]
    flow.append(_table(rows, col_widths=col_widths))
    flow.append(PageBreak())
    return flow


def _build_result_summary(summary: Dict, validation: Dict, corrections: List[str], styles):
    flow = []
    flow.append(_p("<b>Ergebnisübersicht und Normprüfung</b>", styles["Heading2"]))

    key_rows = [
        ["Erforderlicher Volumenstrom qv", f"{summary.get('qv', '-')} m³/h"],
        ["Vorhandene Zuluft", f"{summary.get('zu', '-')} m³/h"],
        ["Vorhandene Abluft", f"{summary.get('ab', '-')} m³/h"],
        ["Infiltration", f"{summary.get('inf', '-')} m³/h"],
        ["Schachtanteil", f"{summary.get('shaft', '-')} m³/h"],
        ["Systemstatus", summary.get("status", "-")],
    ]
    flow.append(_table([["Kenngröße", "Wert"]] + key_rows, col_widths=[70 * mm, 105 * mm]))
    flow.append(Spacer(1, 4 * mm))

    errors = validation.get("errors", [])
    warnings = validation.get("warnings", [])

    flow.append(_p("<b>Festgestellte Fehler</b>", styles["Heading3"]))
    if errors:
        flow.append(_table([["#", "Fehler"]] + [[str(i + 1), e] for i, e in enumerate(errors)], col_widths=[12 * mm, 163 * mm]))
    else:
        flow.append(_p("Keine Fehler festgestellt.", styles["BodyText"]))

    flow.append(Spacer(1, 2 * mm))
    flow.append(_p("<b>Warnungen</b>", styles["Heading3"]))
    if warnings:
        flow.append(_table([["#", "Warnung"]] + [[str(i + 1), w] for i, w in enumerate(warnings)], col_widths=[12 * mm, 163 * mm]))
    else:
        flow.append(_p("Keine Warnungen festgestellt.", styles["BodyText"]))

    flow.append(Spacer(1, 2 * mm))
    flow.append(_p("<b>Korrekturvorschläge</b>", styles["Heading3"]))
    if corrections:
        flow.append(_table([["#", "Vorschlag"]] + [[str(i + 1), c] for i, c in enumerate(corrections)], col_widths=[12 * mm, 163 * mm]))
    else:
        flow.append(_p("Keine zusätzlichen Korrekturvorschläge.", styles["BodyText"]))

    flow.append(PageBreak())
    return flow


def _build_report_text(text: str, styles):
    flow = []
    flow.append(_p("<b>Formblatt E – Textliche Begründung</b>", styles["Heading2"]))

    for para in str(text).split("\n"):
        if para.strip():
            flow.append(_p(para, styles["BodyText"]))
            flow.append(Spacer(1, 1.5 * mm))

    return flow


def create_multi_pdf(filename, data):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="Lüftungskonzept DIN 1946-6",
    )

    styles = getSampleStyleSheet()
    story = []

    for unit_name, content in data.items():
        meta = content.get("meta", {})
        res = content.get("res", {})
        summary = res.get("validation", {}).get("summary", {})
        validation = res.get("validation", {})
        corrections = res.get("corrections", [])
        df_rooms = res.get("df_rooms")
        report_text = res.get("formblatt_e", "")

        story.append(_p(f"<b>Nutzungseinheit: {unit_name}</b>", styles["Heading1"]))
        story.append(Spacer(1, 2 * mm))

        story.extend(_build_cover(meta, summary, styles))

        if df_rooms is not None and len(df_rooms) > 0:
            story.extend(_build_room_situation(df_rooms, styles))

        story.extend(_build_result_summary(summary, validation, corrections, styles))
        story.extend(_build_report_text(report_text, styles))

    doc.build(story)
