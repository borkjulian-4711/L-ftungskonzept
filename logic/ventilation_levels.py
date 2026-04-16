def calculate_ventilation_levels(ANE, personen, nutzung):

    # -----------------------------
    # Nutzungsabhängige Luftmenge
    # -----------------------------
    if nutzung == "normal":
        q_person = 30
    elif nutzung == "reduziert":
        q_person = 20
    else:
        q_person = 40

    # -----------------------------
    # Nennlüftung
    # -----------------------------
    q_NL = personen * q_person

    # -----------------------------
    # Reduzierte Lüftung
    # -----------------------------
    q_RL = q_NL * 0.7

    # -----------------------------
    # Intensivlüftung
    # -----------------------------
    q_IL = q_NL * 1.3

    # -----------------------------
    # Feuchteschutz
    # -----------------------------
    q_FL = max(ANE * 0.3, personen * 15)

    return {
        "FL": round(q_FL, 1),
        "RL": round(q_RL, 1),
        "NL": round(q_NL, 1),
        "IL": round(q_IL, 1),
    }
