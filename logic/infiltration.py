# logic/infiltration.py

def get_ez_din(gebaeudetyp, wind, luftdicht=False):
    """
    DIN 1946-6: Infiltration (ez)
    Werte angelehnt an DIN Tabellen
    """

    # Basiswerte (DIN-typisch)
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

    # Luftdichtheit berücksichtigen
    if luftdicht:
        ez *= 0.7   # DIN: reduzierte Infiltration

    # DIN fordert: 2 Nachkommastellen
    return round(ez, 2)


def calculate_infiltration_din(Aenv, ez):
    """
    DIN: qv,inf = ez × Aenv
    """

    return round(Aenv * ez)
