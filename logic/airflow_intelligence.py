def auto_connect_rooms(df):

    df = df.copy()

    # Räume filtern
    supply = df[df["Typ"] == "Zuluft"]["Raum"].tolist()
    overflow = df[df["Typ"] == "Überström"]["Raum"].tolist()
    exhaust = df[df["Typ"] == "Abluft"]["Raum"].tolist()

    # Flur erkennen
    flur = None
    for _, row in df.iterrows():
        if row["Kategorie (DIN 1946-6)"] == "Flur":
            flur = row["Raum"]

    # -----------------------------
    # ZULUFT → FLUR / ABLUFT
    # -----------------------------
    for i, row in df.iterrows():

        if row["Typ"] == "Zuluft":

            if flur:
                df.at[i, "Überströmt nach"] = flur
            elif exhaust:
                df.at[i, "Überströmt nach"] = exhaust[0]

    # -----------------------------
    # ÜBERSTRÖM → ABLUFT
    # -----------------------------
    for i, row in df.iterrows():

        if row["Typ"] == "Überström":

            if exhaust:
                df.at[i, "Überströmt nach"] = exhaust[0]

    # -----------------------------
    # ABLUFT → kein Ziel
    # -----------------------------
    for i, row in df.iterrows():

        if row["Typ"] == "Abluft":
            df.at[i, "Überströmt nach"] = ""

    return df
