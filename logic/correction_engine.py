# logic/correction_engine.py

def generate_corrections(df_rooms, errors, qv_required, q_supply):

    suggestions = []

    # ---------------------------------
    # 1. Innenliegende Räume
    # ---------------------------------
    for _, row in df_rooms.iterrows():
        if row.get("Innenliegend", False):
            if row.get("Typ") != "Abluft":
                suggestions.append(
                    f"Raum '{row['Raum']}': Typ auf 'Abluft' ändern (DIN 18017)."
                )

    # ---------------------------------
    # 2. Abluft erhöhen
    # ---------------------------------
    min_values = {
        "Küche": 60,
        "Bad": 40,
        "WC": 30
    }

    for _, row in df_rooms.iterrows():
        if row.get("Typ") == "Abluft":
            kat = row.get("Kategorie (DIN 1946-6)")
            ab = row.get("Abluft (m³/h)", 0)

            if kat in min_values and ab < min_values[kat]:
                suggestions.append(
                    f"Raum '{row['Raum']}': Abluft auf mindestens {min_values[kat]} m³/h erhöhen."
                )

    # ---------------------------------
    # 3. Feuchteschutz nicht erfüllt
    # ---------------------------------
    if q_supply < qv_required:
        diff = round(qv_required - q_supply)

        suggestions.append(
            f"Fehlender Volumenstrom: {diff} m³/h → ALD oder Ventilatorleistung erhöhen."
        )

    # ---------------------------------
    # 4. Überströmung
    # ---------------------------------
    abluft_raeume = df_rooms[df_rooms["Typ"] == "Abluft"]["Raum"].tolist()

    for _, row in df_rooms.iterrows():
        if row.get("Typ") == "Zuluft":
            ziel = row.get("Überströmt nach", "")

            if ziel == "" or ziel not in abluft_raeume:
                suggestions.append(
                    f"Raum '{row['Raum']}': Überströmung zu Abluftraum sicherstellen."
                )

    return suggestions
