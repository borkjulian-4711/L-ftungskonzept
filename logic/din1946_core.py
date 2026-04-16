# logic/din1946_core.py

def calculate_qv_ges(ANE, level="FL"):
    """
    DIN 1946-6 Luftvolumenstrom je Lüftungsstufe
    """

    h = 2.5
    V = ANE * h

    if level == "FL":
        n = 0.3
    elif level == "RL":
        n = 0.5
    elif level == "NL":
        n = 0.7
    elif level == "IL":
        n = 1.0
    else:
        n = 0.5

    return round(V * n)


def calculate_levels(ANE):
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

    df["Zuluft (m³/h)"] = 0

    if total_f > 0:
        for i, row in df.iterrows():
            if row["Typ"] == "Zuluft":
                df.loc[i, "Zuluft (m³/h)"] = round(qv_total * row["fR,zu"] / total_f)

    return df


def apply_exhaust_values(df):
    df = df.copy()

    mapping = {
        "Küche": 60,
        "Bad": 40,
        "WC": 30
    }

    df["Abluft (m³/h)"] = 0

    for i, row in df.iterrows():
        if row["Typ"] == "Abluft":
            df.loc[i, "Abluft (m³/h)"] = mapping.get(
                row["Kategorie (DIN 1946-6)"], 30
            )

    return df


def balance_system(df):
    zu = df["Zuluft (m³/h)"].sum()
    ab = df["Abluft (m³/h)"].sum()

    return zu, ab, zu - ab


# -----------------------------
# Ventilatorgestützt (DIN 5.x)
# -----------------------------
def dimension_ventilation_system(df, qv_target):

    df = df.copy()

    ab = df["Abluft (m³/h)"].sum()

    if ab == 0:
        return df, 0, 0

    factor = qv_target / ab

    df["Abluft (m³/h)"] = df["Abluft (m³/h)"] * factor
    df["Zuluft (m³/h)"] = df["Abluft (m³/h)"]

    return df, round(qv_target), round(qv_target)
