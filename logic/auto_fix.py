# logic/auto_fix.py

def auto_fix_system(df_rooms, qv_required):

    df = df_rooms.copy()

    # ---------------------------------
    # 1. Innenliegende Räume → Abluft
    # ---------------------------------
    for i, row in df.iterrows():
        if row.get("Innenliegend", False):
            df.loc[i, "Typ"] = "Abluft"

    # ---------------------------------
    # 2. Mindest-Abluft
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
            if not row.get("Überströmt nach"):
                if abluft_raeume:
                    df.loc[i, "Überströmt nach"] = abluft_raeume[0]

    return df
