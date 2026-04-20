# logic/auto_fix.py

import logic.din1946_core as core


def _ensure_required_columns(df):
    required_defaults = {
        "Raum": "",
        "Typ": "Zuluft",
        "Kategorie (DIN 1946-6)": "",
        "Innenliegend": False,
        "DIN 18017 Kategorie": "",
        "Überströmt nach": "",
    }

    for col, default in required_defaults.items():
        if col not in df.columns:
            df[col] = default

    return df


def _infer_din18017_category(din1946_category):
    mapping = {
        "Bad": "R-ZD",
        "WC": "R-BD",
        "Küche": "R-PN",
    }
    return mapping.get(str(din1946_category), "R-ZD")


def auto_fix_system(df_rooms, qv_required):
    """
    Wendet automatische Korrekturen an und berechnet danach Zuluft/Abluft neu.
    Dadurch werden Volumenströme nach DIN-Logik tatsächlich angepasst
    (nicht nur Raumtypen/Überströmbeziehungen).
    """

    df = _ensure_required_columns(df_rooms.copy())

    # ---------------------------------
    # 1. Innenliegende Räume normgerecht setzen
    # ---------------------------------
    for i, row in df.iterrows():
        if bool(row.get("Innenliegend", False)):
            df.loc[i, "Typ"] = "Abluft"

            if not str(row.get("DIN 18017 Kategorie", "")).strip():
                df.loc[i, "DIN 18017 Kategorie"] = _infer_din18017_category(
                    row.get("Kategorie (DIN 1946-6)")
                )

    # ---------------------------------
    # 2. Überströmung sicherstellen
    # ---------------------------------
    abluft_raeume = df[df["Typ"] == "Abluft"]["Raum"].tolist()
    default_target = abluft_raeume[0] if abluft_raeume else ""

    for i, row in df.iterrows():
        if row.get("Typ") == "Zuluft" and not str(row.get("Überströmt nach", "")).strip():
            df.loc[i, "Überströmt nach"] = default_target

    # ---------------------------------
    # 3. Volumenströme vollständig neu berechnen
    # ---------------------------------
    df = core.distribute_airflows(df, qv_required)
    df = core.apply_exhaust_values(df)

    return df
