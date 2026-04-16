def get_ez(wind, building_type):

    # typische DIN-Werte (vereinfachte Zuordnung)

    if wind == "windschwach":
        if building_type == "MFH":
            return 0.21
        else:
            return 0.18

    if wind == "windstark":
        return 0.30

    return 0.20


def calculate_infiltration(Aenv, ez):

    return round(Aenv * ez)


def calculate_effective_supply(qv_zu, qv_inf):

    return qv_zu + qv_inf
