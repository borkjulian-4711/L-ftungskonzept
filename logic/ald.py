import math


def calculate_pressure_difference(wind="windschwach"):
    """
    DIN typische Druckdifferenzen
    """
    if wind == "windschwach":
        return 2  # Pa
    elif wind == "windstark":
        return 5
    return 2


def ald_volume_flow(c, delta_p, n=0.5):
    """
    q = c * (Δp)^n
    """
    return c * (delta_p ** n)


def calculate_ald_number(q_required, c=10, delta_p=2):
    """
    Berechnet Anzahl ALD
    c = Kennwert eines ALD bei 1 Pa
    """

    q_per_ald = ald_volume_flow(c, delta_p)

    if q_per_ald == 0:
        return 0, 0

    n_ald = math.ceil(q_required / q_per_ald)

    return n_ald, round(q_per_ald, 1)


def calculate_ald_din(qv_fl, qv_inf, wind="windschwach"):
    """
    DIN-konforme ALD-Auslegung
    """

    delta_p = calculate_pressure_difference(wind)

    q_required = max(0, qv_fl - qv_inf)

    n_ald, q_per_ald = calculate_ald_number(
        q_required,
        c=10,         # typischer ALD-Wert
        delta_p=delta_p
    )

    return {
        "q_required": round(q_required),
        "delta_p": delta_p,
        "q_per_ald": q_per_ald,
        "anzahl": n_ald
    }
