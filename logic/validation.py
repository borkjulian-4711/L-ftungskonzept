def validate_din(df, flows, q_req, q_ab):

    errors = []
    warnings = []

    raeume = df["Raum"].tolist()

    # -----------------------------
    # Pflicht: Abluft vorhanden
    # -----------------------------
    if not any(df["Typ"] == "Abluft"):
        errors.append("Kein Abluftraum vorhanden")

    # -----------------------------
    # Pflicht: Zuluft vorhanden
    # -----------------------------
    if not any(df["Typ"] == "Zuluft"):
        errors.append("Kein Zuluft-Raum vorhanden")

    # -----------------------------
    # Überströmziel prüfen
    # -----------------------------
    for _, row in df.iterrows():
        ziel = row.get("Überströmt nach", "")
        if ziel and ziel not in raeume:
            errors.append(f"Überströmziel '{ziel}' existiert nicht")

    # -----------------------------
    # Selbstverbindung
    # -----------------------------
    for _, row in df.iterrows():
        if row["Raum"] == row.get("Überströmt nach", ""):
            errors.append(f"Raum '{row['Raum']}' strömt in sich selbst")

    # -----------------------------
    # Luftführung endet nicht in Abluft
    # -----------------------------
    for r, f in flows.items():
        typ = df[df["Raum"] == r]["Typ"].values[0]

        if f > 0 and typ != "Abluft":
            warnings.append(f"Luft endet in '{r}', nicht im Abluftraum")

    # -----------------------------
    # Feuchteschutz
    # -----------------------------
    if q_ab < q_req:
        warnings.append("Feuchteschutzlüftung nicht erfüllt")

    return errors, warnings
