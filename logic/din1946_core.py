def calculate_qv_ges(ANE, n=0.4):
    h = 2.5
    V = ANE * h
    return round(V * n)


def calculate_levels(qv):
    return {
        "FL": round(qv * 0.3),
        "RL": round(qv * 0.5),
        "NL": round(qv * 1.0),
        "IL": round(qv * 1.3)
    }


def distribute_airflows(df_rooms, qv_total):

    df = df_rooms.copy()

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


def apply_exhaust_values(df):

    df = df.copy()

    mapping = {
        "Küche": 60,
        "Bad": 40,
        "WC": 30
    }

    ab = []

    for _, row in df.iterrows():
        if row["Typ"] == "Abluft":
            ab.append(mapping.get(row["Kategorie (DIN 1946-6)"], 30))
        else:
            ab.append(0)

    df["Abluft (m³/h)"] = ab

    return df


def balance_system(df):

    zu = df["Zuluft (m³/h)"].sum()
    ab = df["Abluft (m³/h)"].sum()

    return zu, ab, zu - ab


def balance_ventilation_system(df):

    df = df.copy()

    zu = df["Zuluft (m³/h)"].sum()
    ab = df["Abluft (m³/h)"].sum()

    if zu == 0:
        return df, 0, ab

    factor = ab / zu

    df["Zuluft (m³/h)"] = df["Zuluft (m³/h)"] * factor

    return df, df["Zuluft (m³/h)"].sum(), ab
