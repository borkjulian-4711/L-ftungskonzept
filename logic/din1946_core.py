# logic/din1946_core.py

def calculate_qv_ges(ANE, level="FL"):
    """
    DIN 1946-6: Luftvolumenstrom je Lüftungsstufe
    """

    h = 2.5
    V = ANE * h

    if level == "FL":      # Feuchteschutz
        n = 0.3
    elif level == "RL":    # Reduzierte Lüftung
        n = 0.5
    elif level == "NL":    # Nennlüftung
        n = 0.7
    elif level == "IL":    # Intensivlüftung
        n = 1.0
    else:
        n = 0.5

    return round(V * n)


def calculate_levels(ANE):
    """
    Alle Lüftungsstufen berechnen
    """
    return {
        "FL": calculate_qv_ges(ANE, "FL"),
        "RL": calculate_qv_ges(ANE, "RL"),
        "NL": calculate_qv_ges(ANE, "NL"),
        "IL": calculate_qv_ges(ANE, "IL"),
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

    return df, round(df["Zuluft (m³/h)"].sum()), ab
