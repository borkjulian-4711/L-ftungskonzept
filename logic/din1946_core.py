import pandas as pd


# -----------------------------
# 1. Gesamtvolumenstrom
# -----------------------------
def calculate_qv_ges(ANE, n=0.5):
    """
    Vereinfachte DIN-Berechnung:
    qv = n * Volumen
    """
    h = 2.5  # mittlere Raumhöhe
    V = ANE * h

    return round(V * n, 0)


# -----------------------------
# 2. Lüftungsstufen
# -----------------------------
def calculate_levels(qv):

    return {
        "FL": round(qv * 0.3),
        "RL": round(qv * 0.5),
        "NL": round(qv * 1.0),
        "IL": round(qv * 1.3)
    }


# -----------------------------
# 3. fR,zu Verteilung
# -----------------------------
def distribute_airflows(df_rooms, qv_total):

    df = df_rooms.copy()

    # nur Zuluft-Räume berücksichtigen
    zuluft_df = df[df["Typ"] == "Zuluft"]

    total_area = zuluft_df["Fläche"].sum()

    flows = []

    for _, row in df.iterrows():

        if row["Typ"] == "Zuluft" and total_area > 0:
            f = row["Fläche"] / total_area
            q = round(qv_total * f)

        elif row["Typ"] == "Abluft":
            # Abluft wird später angepasst
            q = 0

        else:
            q = 0

        flows.append(q)

    df["Zuluft (m³/h)"] = flows

    return df


# -----------------------------
# 4. Abluft DIN-Werte
# -----------------------------
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


# -----------------------------
# 5. Bilanz
# -----------------------------
def balance_system(df):

    zuluft_sum = df["Zuluft (m³/h)"].sum()
    abluft_sum = df["Abluft (m³/h)"].sum()

    diff = zuluft_sum - abluft_sum

    return zuluft_sum, abluft_sum, diff
