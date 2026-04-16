# logic/infiltration.py

import math


def get_ez_din(gebaeudetyp, wind, luftdicht=False):
    """
    DIN 1946-6: Infiltration (ez)
    """

    ez_table = {
        "EFH": {
            "windschwach": 0.07,
            "windstark": 0.10
        },
        "DHH": {
            "windschwach": 0.06,
            "windstark": 0.09
        },
        "Wohnung": {
            "windschwach": 0.05,
            "windstark": 0.08
        },
        "MFH": {
            "windschwach": 0.05,
            "windstark": 0.07
        }
    }

    ez = ez_table.get(gebaeudetyp, {}).get(wind, 0.06)

    if luftdicht:
        ez *= 0.7

    return round(ez, 2)


def calculate_infiltration_din(Aenv, ez):
    """
    qv,inf = ez × Aenv
    """
    return round(Aenv * ez)


# -----------------------------
# SCHACHTLÜFTUNG (NEU)
# -----------------------------
def calculate_shaft_flow(height=8.0, delta_t=10.0, area=0.02):
    """
    Vereinfachte DIN-Näherung:
    thermischer Auftrieb im Schacht

    q ≈ A * sqrt(H * ΔT) * Faktor
    """

    q = area * math.sqrt(height * delta_t) * 50

    return round(q)
