def calculate_ventilation_levels(ANE, fWS):

    # -----------------------------
    # Feuchteschutzlüftung
    # -----------------------------
    q_FL = ANE * fWS

    # -----------------------------
    # Nennlüftung (Grundansatz)
    # -----------------------------
    q_NL = ANE * 0.5

    # -----------------------------
    # Reduzierte Lüftung
    # -----------------------------
    q_RL = q_NL * 0.7

    # -----------------------------
    # Intensivlüftung
    # -----------------------------
    q_IL = q_NL * 1.3

    return {
        "FL": round(q_FL, 1),
        "RL": round(q_RL, 1),
        "NL": round(q_NL, 1),
        "IL": round(q_IL, 1),
    }
