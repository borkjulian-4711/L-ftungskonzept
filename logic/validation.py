# logic/validation.py

from logic.din18017 import get_din18017_flow


def validate_din(df_rooms, qv_required, q_supply, system):

    errors = []
    warnings = []

    # ---------------------------------
    # 1. Innenliegende Räume
    # ---------------------------------
    for _, row in df_rooms.iterrows():
        if row.get("Innenliegend", False):
            if row.get("Typ") != "Abluft":
                errors.append(
                    f"Innenliegender Raum '{row['Raum']}' muss Abluft sein."
                )

            din18017_cat = str(row.get("DIN 18017 Kategorie", "")).strip()
            if not din18017_cat:
                errors.append(
                    f"Innenliegender Raum '{row['Raum']}' benötigt eine DIN 18017 Kategorie."
                )

    # ---------------------------------
    # 2. Mindest-Abluft
    # ---------------------------------
    min_values = {
        "Küche": 60,
        "Bad": 40,
        "WC": 30
    }

    for _, row in df_rooms.iterrows():
        if row.get("Typ") == "Abluft":
            kat = row.get("Kategorie (DIN 1946-6)")
            ab = row.get("Abluft (m³/h)", 0)

            if kat in min_values and ab < min_values[kat]:
                errors.append(
                    f"Abluft in '{row['Raum']}' zu gering ({ab} m³/h)."
                )

            if row.get("Innenliegend", False):
                din18017_cat = str(row.get("DIN 18017 Kategorie", "")).split(" ")[0]
                min_18017 = get_din18017_flow(din18017_cat)

                if min_18017 > 0 and ab < min_18017:
                    errors.append(
                        (
                            f"DIN 18017 nicht erfüllt in '{row['Raum']}' "
                            f"({ab} < {min_18017} m³/h)."
                        )
                    )

    # ---------------------------------
    # 3. Feuchteschutz
    # ---------------------------------
    if q_supply < qv_required:
        errors.append(
            f"Feuchteschutz nicht erfüllt ({q_supply} < {qv_required} m³/h)."
        )

    # ---------------------------------
    # 4. Überströmung
    # ---------------------------------
    abluft_raeume = df_rooms[df_rooms["Typ"] == "Abluft"]["Raum"].tolist()

    for _, row in df_rooms.iterrows():
        if row.get("Typ") == "Zuluft":
            ziel = row.get("Überströmt nach", "")

            if ziel == "" or ziel not in abluft_raeume:
                warnings.append(
                    f"Zuluft-Raum '{row['Raum']}' ohne sicheren Überströmweg."
                )

    # ---------------------------------
    # 5. Bilanz ventilatorgestützt
    # ---------------------------------
    if system == "ventilatorgestützt":
        zu = df_rooms["Zuluft (m³/h)"].sum()
        ab = df_rooms["Abluft (m³/h)"].sum()

        if abs(zu - ab) > 5:
            errors.append(
                f"Zuluft und Abluft nicht ausgeglichen ({zu} ≠ {ab})."
            )

    return errors, warnings
