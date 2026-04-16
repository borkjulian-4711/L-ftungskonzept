from logic.room_airflows import apply_room_airflows


def calculate_ventilation(df_rooms, ANE, fWS):

    df = apply_room_airflows(df_rooms)

    # sichere Filter
    if "Typ" not in df.columns:
        return 0, 0, 0, df

    q_ab = df[df["Typ"] == "Abluft"]["Volumenstrom (m³/h)"].sum()

    q_req = ANE * fWS

    delta = q_ab - q_req

    return q_req, q_ab, delta, df
