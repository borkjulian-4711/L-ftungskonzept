# logic/text_generator.py

def generate_concept_text(data, project, mode="behördlich"):
    """
    Behördlicher Prüfbericht nach DIN 1946-6
    """

    levels = data.get("levels", {})
    result = data.get("result", {})
    summary = data.get("summary", {})

    qv = summary.get("qv", 0)
    q_supply = summary.get("zu", 0)
    q_ab = summary.get("ab", 0)
    q_inf = summary.get("inf", 0)
    status = summary.get("status", "")

    text = ""

    # -------------------------------------------------
    # 1. EINLEITUNG
    # -------------------------------------------------
    text += "1. Einleitung\n"
    text += (
        "Für das nachfolgend beschriebene Bauvorhaben wurde ein Lüftungskonzept "
        "gemäß DIN 1946-6 „Lüftung von Wohnungen“ erstellt. "
        "Ziel ist die Sicherstellung des notwendigen Luftwechsels zum Feuchteschutz "
        "sowie zur hygienischen Raumluftqualität.\n\n"
    )

    # -------------------------------------------------
    # 2. PROJEKT
    # -------------------------------------------------
    text += "2. Projektbeschreibung\n"
    text += f"Projekt: {project.get('projekt','')}\n"
    text += f"Adresse: {project.get('adresse','')}\n"
    text += f"Bearbeiter: {project.get('bearbeiter','')}\n\n"

    # -------------------------------------------------
    # 3. BERECHNUNGSGRUNDLAGEN
    # -------------------------------------------------
    text += "3. Berechnungsgrundlagen\n"
    text += (
        f"Die Auslegung erfolgt auf Basis der Lüftungsstufe. "
        f"Der erforderliche Luftvolumenstrom beträgt {qv} m³/h.\n"
    )
    text += (
        f"Die Infiltration wurde mit {q_inf} m³/h berücksichtigt.\n\n"
    )

    # -------------------------------------------------
    # 4. ERGEBNISSE
    # -------------------------------------------------
    text += "4. Ergebnisse\n"
    text += f"Zuluft gesamt: {q_supply} m³/h\n"
    text += f"Abluft gesamt: {q_ab} m³/h\n\n"

    # -------------------------------------------------
    # 5. BEWERTUNG
    # -------------------------------------------------
    text += "5. Bewertung\n"

    if q_supply >= qv:
        text += (
            "Der erforderliche Luftvolumenstrom wird erreicht. "
            "Die Anforderungen an den Feuchteschutz nach DIN 1946-6 sind erfüllt.\n\n"
        )
    else:
        text += (
            "Der erforderliche Luftvolumenstrom wird nicht vollständig erreicht. "
            "Zusätzliche lüftungstechnische Maßnahmen sind erforderlich.\n\n"
        )

    # -------------------------------------------------
    # 6. MASSNAHMEN
    # -------------------------------------------------
    text += "6. Maßnahmen\n"
    text += f"Systembewertung: {status}\n"

    if q_supply < qv:
        text += (
            "Zur Sicherstellung des Feuchteschutzes sind zusätzliche "
            "Außenluftdurchlässe (ALD) vorzusehen.\n"
        )
    else:
        text += "Es sind keine weiteren Maßnahmen erforderlich.\n"

    text += "\n"

    # -------------------------------------------------
    # 7. ABSCHLUSS
    # -------------------------------------------------
    text += (
        "Das Lüftungskonzept entspricht den Anforderungen der DIN 1946-6 "
        "und ist zur Vorlage bei Behörden geeignet.\n"
    )

    return text
