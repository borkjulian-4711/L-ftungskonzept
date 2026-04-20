from logic.din18017 import get_din18017_flow

# logic/din1946_core.py

# -----------------------------
# Lüftungsstufen (DIN 1946-6)
# -----------------------------
def calculate_qv_ges(ANE, level="FL"):
    """
    Luftvolumenstrom je Lüftungsstufe nach DIN
    """

    h = 2.5
    V = ANE * h

    if level == "FL":      # Feuchteschutz
        n = 0.3
    elif level == "RL":    # reduzierte Lüftung
        n = 0.5
    elif level == "NL":    # Nennlüftung
        n = 0.7
    elif level == "IL":    # Intensivlüftung
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


# -----------------------------
# ZULUFT (ECHTE DIN-NÄHERUNG)
# -----------------------------
def distribute_airflows(df_rooms, qv_target):
    """
    DIN-nahe Zuluftverteilung:
    feste Raumwerte + Skalierung
    """

    df = df_rooms.copy()

    # DIN-nahe Grundwerte
    supply_table = {
        "Wohnzimmer": 40,
        "Schlafzimmer": 30,
        "Kinderzimmer": 30,
        "Arbeitszimmer": 30,
        "Esszimmer": 30
    }

    df["Zuluft (m³/h)"] = 0

    # Grundverteilung
    for i, row in df.iterrows():
        if row["Typ"] == "Zuluft":
            df.loc[i, "Zuluft (m³/h)"] = supply_table.get(
                row["Kategorie (DIN 1946-6)"], 20
            )

    # Summe berechnen
    total_supply = df["Zuluft (m³/h)"].sum()

    # Skalierung auf Zielwert
    if total_supply > 0:
        factor = qv_target / total_supply
        df["Zuluft (m³/h)"] = (df["Zuluft (m³/h)"] * factor).round()

    return df


# -----------------------------
# ABLUFT (DIN)
# -----------------------------
def apply_exhaust_values(df):
    df = df.copy()

    exhaust_table = {
        "Küche": 60,
        "Bad": 40,
        "WC": 30,
        "Hauswirtschaftsraum": 30
    }

    df["Abluft (m³/h)"] = 0

    for i, row in df.iterrows():
        if row["Typ"] == "Abluft":
            din1946_flow = exhaust_table.get(
                row["Kategorie (DIN 1946-6)"], 30
            )

            din18017_flow = 0
            if row.get("Innenliegend", False):
                din18017_flow = get_din18017_flow(
                    str(row.get("DIN 18017 Kategorie", "")).split(" ")[0]
                )

            # Für innenliegende Ablufträume gilt der strengere Wert.
            df.loc[i, "Abluft (m³/h)"] = max(din1946_flow, din18017_flow)

    return df


# -----------------------------
# BILANZ (freie Lüftung)
# -----------------------------
def balance_system(df):
    zu = df["Zuluft (m³/h)"].sum()
    ab = df["Abluft (m³/h)"].sum()

    return zu, ab, zu - ab


# -----------------------------
# VENTILATORGESTÜTZT (DIN 5.x)
# -----------------------------
def dimension_ventilation_system(df, qv_target):
    """
    Dimensionierung nach DIN:
    Abluft wird auf Ziel skaliert
    Zuluft = Abluft
    """

    df = df.copy()

    ab = df["Abluft (m³/h)"].sum()

    if ab == 0:
        return df, 0, 0

    factor = qv_target / ab

    df["Abluft (m³/h)"] = df["Abluft (m³/h)"] * factor
    df["Zuluft (m³/h)"] = df["Abluft (m³/h)"]

    return df, round(qv_target), round(qv_target)