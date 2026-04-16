def evaluate_system(q_mech, q_req, q_inf):

    result = {}

    if q_mech >= q_req:
        result["status"] = "mechanisch ausreichend"
        result["ald"] = False
        result["infiltration"] = False

    elif q_mech + q_inf >= q_req:
        result["status"] = "durch Infiltration gedeckt"
        result["ald"] = False
        result["infiltration"] = True

    else:
        result["status"] = "ALD erforderlich"
        result["ald"] = True
        result["infiltration"] = True

    result["q_mech"] = q_mech
    result["q_inf"] = q_inf
    result["q_req"] = q_req

    return result
