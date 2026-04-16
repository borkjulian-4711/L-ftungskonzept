def distribute_airflows(df_rooms, qv_total):

    df = df_rooms.copy()

    # DIN Faktoren
    factors = {
        "Wohnzimmer": 3,
        "Schlafzimmer": 2,
        "Kinderzimmer": 2
    }

    df["fR,zu"] = df["Kategorie (DIN 1946-6)"].map(factors).fillna(1)

    total_f = df[df["Typ"] == "Zuluft"]["fR,zu"].sum()

    zuluft = []

    for _, row in df.iterrows():

        if row["Typ"] == "Zuluft" and total_f > 0:
            q = round(qv_total * row["fR,zu"] / total_f)
        else:
            q = 0

        zuluft.append(q)

    df["Zuluft (m³/h)"] = zuluft

    return df
