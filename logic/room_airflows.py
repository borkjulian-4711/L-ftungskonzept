def get_room_airflow(row):

    # sichere Zugriffe
    raum = str(row.get("Kategorie (DIN 1946-6)", "")).lower()
    typ = str(row.get("Typ", ""))

    # -----------------------------
    # ABLUFT
    # -----------------------------
    if typ == "Abluft":

        if "bad" in raum:
            return 40
        elif "wc" in raum:
            return 30
        elif "küche" in raum or "kuche" in raum:
            return 60
        else:
            return 30

    # -----------------------------
    # ZULUFT
    # -----------------------------
    if typ == "Zuluft":

        if "wohn" in raum:
            return 40
        elif "schlaf" in raum:
            return 30
        else:
            return 20

    return 0


def apply_room_airflows(df):

    df = df.copy()

    # Spalte sicherstellen
    if "Volumenstrom (m³/h)" not in df.columns:
        df["Volumenstrom (m³/h)"] = 0

    df["Volumenstrom (m³/h)"] = df.apply(get_room_airflow, axis=1)

    return df
