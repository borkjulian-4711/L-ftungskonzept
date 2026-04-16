# logic/auto_fix.py

def auto_fix_system(df_rooms, qv_required, q_supply):

    df = df_rooms.copy()

    # ---------------------------------
    # 1. Innenliegende Räume → Abluft
    # ---------------------------------
    for i, row in df.iterrows():
        if row.get("Innenliegend", False):
            df.loc[i, "Typ"] = "Abluft"

    # ---------------------------------
    # 2. Mindest-Abluft sicherstellen
    # ---------------------------------
    min_values = {
        "Küche": 60,
        "Bad": 40,
        "WC": 30
    }

    for i, row in df.iterrows():
        if row.get("Typ") == "Abluft":
            kat = row.get("Kategorie (DIN 1946-6)")
            if kat in min_values:
                df.loc[i, "Abluft (m³/h)"] = max(
                    row.get("Abluft (m³/h)", 0),
                    min_values[kat]
                )

    # ---------------------------------
    # 3. Überströmung setzen
    # ---------------------------------
    abluft_raeume = df[df["Typ"] == "Abluft"]["Raum"].tolist()

    for i, row in df.iterrows():
        if row.get("Typ") == "Zuluft":
            ziel = row.get("Überströmt nach", "")

            if ziel == "" and abluft_raeume:
                df.loc[i, "Überströmt nach"] = abluft_raeume[0]

    # ---------------------------------
    # 4. Feuchteschutz prüfen
    # ---------------------------------
    if q_supply < qv_required:
        diff = round(qv_required - q_supply)
        return df, f"Zusätzliche {diff} m³/h erforderlich (ALD vorsehen)."

    return df, "System automatisch korrigiert."
