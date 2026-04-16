def get_room_airflow(row):

    raum = str(row.get("Kategorie (DIN 1946-6)", "")).lower()
    typ = row.get("Typ")

    # -----------------------------
    # ABLUFT (DIN 18017-3)
    # -----------------------------
    if typ == "Abluft":

        if "bad" in raum:
            return 40
        elif "wc" in raum:
            return 30
        elif "küche" in raum or "kuche" in raum:
            return 60
        else:
            return 30  # fallback

    # -----------------------------
    # ZULUFT (DIN 1946-6)
    # -----------------------------
    if typ == "Zuluft":

        if "wohn" in raum:
            return 40
        elif "schlaf" in raum:
            return 30
        elif "kind" in raum:
            return 30
        else:
            return 20

    # -----------------------------
    # ÜBERSTRÖM
    # -----------------------------
    return 0


def apply_room_airflows(df):

    df = df.copy()

    df["Volumenstrom (m³/h)"] = df.apply(get_room_airflow, axis=1)

    return df
