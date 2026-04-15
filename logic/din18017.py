def get_abluft(room_type, category):

    base = {
        "Bad": 40,
        "WC": 25,
        "Küche": 60,
        "Sonstiger Abluftraum": 30
    }.get(room_type, 0)

    factor = {
        "R-ZD": 1.0,
        "R-BD": 0.8,
        "R-PN": 1.2,
        "R-PD": 1.0
    }.get(category, 1.0)

    return base * factor
