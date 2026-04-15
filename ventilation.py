import math
from logic.din1946 import calc_feuchteschutz
from logic.din18017 import get_abluft


def calculate_ventilation(df_rooms, ANE, fWS):

    df_rooms["Abluft (m³/h)"] = df_rooms.apply(
        lambda row: get_abluft(row["Kategorie"])
        if row["Innenliegend"] else 0,
        axis=1
    )

    q_required = calc_feuchteschutz(ANE, fWS)
    q_abluft = df_rooms["Abluft (m³/h)"].sum()
    delta = q_required - q_abluft

    return q_required, q_abluft, delta, df_rooms


def calculate_ald_uld(delta, df_rooms):

    if delta <= 0:
        return 0, 0, {}

    q_ald = 30  # m³/h pro ALD

    n_ald = math.ceil(delta / q_ald)

    supply_rooms = df_rooms[df_rooms["Typ"] == "Zuluft"]

    distribution = {}

    if len(supply_rooms) > 0:
        per_room = math.ceil(n_ald / len(supply_rooms))

        for room in supply_rooms["Raum"]:
            distribution[room] = per_room

    exhaust_rooms = df_rooms[df_rooms["Typ"] == "Abluft"]
    n_uld = max(len(exhaust_rooms), n_ald)

    return n_ald, n_uld, distribution