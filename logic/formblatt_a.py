def evaluate_formblatt_a(neubau, sanierung, fensteranteil, luftdicht):

    # Ergebnis
    erforderlich = False
    begruendung = []

    # -----------------------------
    # Neubau
    # -----------------------------
    if neubau:
        erforderlich = True
        begruendung.append("Neubau gemäß DIN 1946-6")

    # -----------------------------
    # Sanierung
    # -----------------------------
    if sanierung and fensteranteil > 0.33:
        erforderlich = True
        begruendung.append("Sanierung > 1/3 Fensterfläche verändert")

    # -----------------------------
    # Luftdichtheit
    # -----------------------------
    if luftdicht:
        erforderlich = True
        begruendung.append("Gebäude ist luftdicht")

    return {
        "erforderlich": erforderlich,
        "begruendung": ", ".join(begruendung) if begruendung else "Keine Verpflichtung"
    }
