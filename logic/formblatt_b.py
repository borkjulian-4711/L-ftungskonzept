def evaluate_formblatt_b(
    gebaeudetyp,
    baujahr,
    wohneinheiten,
    personen,
    nutzung,
    fensterlueftung,
    infiltration
):

    hinweise = []

    # Gebäudealter
    if baujahr < 1995:
        hinweise.append("Altbau – erhöhte Infiltration möglich")

    # Nutzung
    if personen <= 1:
        hinweise.append("geringe Nutzung")
    elif personen >= 4:
        hinweise.append("hohe Nutzung")

    # Fensterlüftung
    if not fensterlueftung:
        hinweise.append("keine freie Lüftung möglich")

    # Infiltration
    if infiltration == "gering":
        hinweise.append("hohe Luftdichtheit")

    return {
        "gebaeudetyp": gebaeudetyp,
        "baujahr": baujahr,
        "wohneinheiten": wohneinheiten,
        "personen": personen,
        "nutzung": nutzung,
        "fensterlueftung": fensterlueftung,
        "infiltration": infiltration,
        "hinweise": ", ".join(hinweise)
    }
