def evaluate_formblatt_c(levels, q_ab):

    result = {}

    for key, value in levels.items():

        if q_ab >= value:
            status = "erfüllt"
        else:
            status = "nicht erfüllt"

        result[key] = {
            "erforderlich": value,
            "vorhanden": q_ab,
            "status": status,
            "differenz": round(q_ab - value, 1)
        }

    return result
