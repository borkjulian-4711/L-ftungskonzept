def auto_connect_rooms(df):

    df = df.copy()

    # -----------------------------
    # Räume nach Typ
    # -----------------------------
    supply = df[df["Typ"] == "Zuluft"]
    overflow = df[df["Typ"] == "Überström"]
    exhaust = df[df["Typ"] == "Abluft"]

    supply_rooms = supply["Raum"].tolist()
    overflow_rooms = overflow["Raum"].tolist()
    exhaust_rooms = exhaust["Raum"].tolist()

    # -----------------------------
    # Abluftströme je Raum
    # -----------------------------
    exhaust_flows = []

    for _, row in exhaust.iterrows():
        q = row.get("Abluft (m³/h)", 0)
        if q == 0:
            q = 30  # fallback
        exhaust_flows.append((row["Raum"], q))

    if not exhaust_flows:
        return df

    # -----------------------------
    # Verhältnis bilden
    # -----------------------------
    total_q = sum(q for _, q in exhaust_flows)

    weighted_targets = []

    for room, q in exhaust_flows:

        share = max(1, round(q / total_q * len(supply_rooms)))

        weighted_targets += [room] * share

    if not weighted_targets:
        weighted_targets = [r for r, _ in exhaust_flows]

    # -----------------------------
    # Flur erkennen
    # -----------------------------
    flur = None
    for _, row in df.iterrows():
        if row["Kategorie (DIN 1946-6)"] == "Flur":
            flur = row["Raum"]

    # -----------------------------
    # ZULUFT → FLUR oder DIREKT
    # -----------------------------
    idx = 0

    for i, row in df.iterrows():

        if row["Typ"] == "Zuluft":

            if flur:
                df.at[i, "Überströmt nach"] = flur
            else:
                target = weighted_targets[idx % len(weighted_targets)]
                df.at[i, "Überströmt nach"] = target
                idx += 1

    # -----------------------------
    # ÜBERSTRÖM → ABLUFT (gewichtet)
    # -----------------------------
    idx = 0

    for i, row in df.iterrows():

        if row["Typ"] == "Überström":

            target = weighted_targets[idx % len(weighted_targets)]
            df.at[i, "Überströmt nach"] = target
            idx += 1

    # -----------------------------
    # ABLUFT → kein Ziel
    # -----------------------------
    for i, row in df.iterrows():
        if row["Typ"] == "Abluft":
            df.at[i, "Überströmt nach"] = ""

    return df
    
