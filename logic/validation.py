def validate_inputs(df_rooms):

    errors = []
    warnings = []

    raeume = df_rooms["Raum"].dropna().astype(str).tolist()

    for i, row in df_rooms.iterrows():

        raum = str(row.get("Raum", "")).strip()
        typ = str(row.get("Typ", "")).strip()
        kat = str(row.get("Kategorie (DIN 1946-6)", "")).strip()
        din18017 = str(row.get("DIN 18017 Kategorie", "")).strip()
        ueber = str(row.get("Überströmt nach", "")).strip()

        # -----------------------------
        # Pflichtfelder
        # -----------------------------
        if not raum:
            errors.append(f"Zeile {i+1}: Raumname fehlt")

        if not typ:
            errors.append(f"{raum}: Raumtyp fehlt")

        if not kat:
            errors.append(f"{raum}: Kategorie (DIN 1946-6) fehlt")

        # -----------------------------
        # Abluftregel
        # -----------------------------
        if typ == "Abluft" and row.get("Innenliegend"):
            if not din18017:
                errors.append(f"{raum}: DIN 18017 Kategorie fehlt")

        # -----------------------------
        # Überströmung prüfen
        # -----------------------------
        if ueber:

            if ueber not in raeume:
                errors.append(f"{raum}: Überströmziel '{ueber}' existiert nicht")

            if ueber == raum:
                errors.append(f"{raum}: Überströmung auf sich selbst")

        # -----------------------------
        # Warnungen
        # -----------------------------
        if typ == "Zuluft" and ueber == "":
            warnings.append(f"{raum}: keine Weiterleitung definiert")

        if typ == "Abluft" and ueber != "":
            warnings.append(f"{raum}: Abluftraum sollte kein Überströmziel haben")

    return errors, warnings
