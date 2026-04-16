import math

def calculate_ald(q_needed, q_per_ald=30):

    n = max(1, math.ceil(q_needed / q_per_ald))

    return {
        "anzahl": n,
        "pro_stueck": q_per_ald,
        "gesamt": n * q_per_ald
    }
