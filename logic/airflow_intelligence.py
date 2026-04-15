def auto_connect_rooms(df):

    df = df.copy()

    supply = df[df["Typ"] == "Zuluft"]["Raum"].tolist()
    overflow = df[df["Typ"] == "Überström"]["Raum"].tolist()
    exhaust = df[df["Typ"] == "Abluft"]["Raum"].tolist()

    # Flur erkennen
    flur = None
    for _, row in df.iterrows():
        if row["Kategorie (DIN 1946-6)"] == "Flur":
            flur = row["Raum"]

    # -----------------------------
    # ZULUFT → FLUR oder VERTEILT
    # -----------------------------
    ex_index = 0

    for i, row in df.iterrows():

        if row["Typ"] == "Zuluft":

            if flur:
                df.at[i, "Überströmt nach"] = flur
            elif exhaust:
                target = exhaust[ex_index % len(exhaust)]
                df.at[i, "Überströmt nach"] = target
                ex_index += 1

    # -----------------------------
    # ÜBERSTRÖM → VERTEILT AUF ABLUFT
    # -----------------------------
    ex_index = 0

    for i, row in df.iterrows():

        if row["Typ"] == "Überström":

            if exhaust:
                target = exhaust[ex_index % len(exhaust)]
                df.at[i, "Überströmt nach"] = target
                ex_index += 1

    # -----------------------------
    # ABLUFT → kein Ziel
    # -----------------------------
    for i, row in df.iterrows():
        if row["Typ"] == "Abluft":
            df.at[i, "Überströmt nach"] = ""

    return df
