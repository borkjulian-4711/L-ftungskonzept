def get_abluft(room_type):
    mapping = {
        "Bad": 40,
        "WC": 25,
        "Küche": 60,
        "Sonstiger Abluftraum": 30
    }
    return mapping.get(room_type, 0)
