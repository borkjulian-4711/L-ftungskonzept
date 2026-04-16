def generate_concept_text(data, project, mode="lang"):

    levels = data.get("levels", {})
    d = data.get("formblatt_d", {})

    # -----------------------------
    # 1. EINLEITUNG (immer gleich)
    # -----------------------------
    intro = f"""
1. Einleitung

Für das nachfolgend beschriebene Bauvorhaben wurde ein Lüftungskonzept gemäß
DIN 1946-6 „Lüftung von Wohnungen“ erstellt.

Zusätzlich wurden, sofern erforderlich, innenliegende Räume gemäß DIN 18017-3
„Lüftung von Bädern und Toilettenräumen ohne Außenfenster“ berücksichtigt.
"""

    # -----------------------------
    # 2. PROJEKTBESCHREIBUNG
    # -----------------------------
    projekt = f"""
2. Projektbeschreibung

Projekt: {project.get("projekt", "-")}
Adresse: {project.get("adresse", "-")}
Bearbeiter: {project.get("bearbeiter", "-")}
Datum: {project.get("datum", "-")}
"""

    # -----------------------------
    # 3. GRUNDLAGEN
    # -----------------------------
    grundlagen = f"""
3. Grundlagen

Die Berechnung basiert auf den Vorgaben der DIN 1946-6 unter Berücksichtigung
der Nutzungseinheit sowie der vorgesehenen Nutzung.

Die maßgebliche Lüftungsstufe ergibt sich zu:
Nennlüftung: {levels.get("NL", "-")} m³/h
"""

    # -----------------------------
    # 4. KONZEPT (variabel)
    # -----------------------------
    if mode == "kurz":
        konzept = f"""
4. Lüftungskonzept

Die Luftführung erfolgt von Zuluft- zu Ablufträumen.
{d.get("massnahme", "-")}
"""

    elif mode == "behördlich":
        konzept = f"""
4. Lüftungskonzept

Die Auslegung des Lüftungskonzeptes erfolgt gemäß den Anforderungen
der DIN 1946-6.

Die Luftvolumenströme wurden entsprechend der Nutzung und Raumfunktion
dimensioniert. Die Luftführung erfolgt über definierte Überströmwege.

Innenliegende Räume werden gemäß DIN 18017-3 ventilatorgestützt entlüftet.

Maßnahme:
{d.get("massnahme", "-")}
"""

    else:  # lang
        konzept = f"""
4. Lüftungskonzept

Die erforderlichen Luftvolumenströme wurden auf Grundlage der
Gebäudenutzung und Raumaufteilung ermittelt.

Die Luftführung erfolgt von Zuluft- in Ablufträume über Überströmöffnungen.

Innenliegende Räume werden gemäß DIN 18017-3 mechanisch entlüftet.

Die gewählte Maßnahme lautet:
{d.get("massnahme", "-")}
"""

    # -----------------------------
    # 5. ERGEBNIS
    # -----------------------------
    ergebnis = f"""
5. Ergebnis

Die Anforderungen an die Feuchteschutzlüftung werden eingehalten.

Das Lüftungskonzept entspricht den Anforderungen der DIN 1946-6.
"""

    return intro + projekt + grundlagen + konzept + ergebnis
