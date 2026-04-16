def get_din18017_flow(category):

    mapping = {
        "R-ZD": 40,
        "R-BD": 30,
        "R-PN": 60,
        "R-PD": 45
    }

    return mapping.get(category, 0)


def apply_din18017(df):

    df = df.copy()

    flows = []

    for _, row in df.iterrows():

        if row.get("Innenliegend"):

            cat = str(row.get("DIN 18017 Kategorie", "")).split(" ")[0]
            flow = get_din18017_flow(cat)

            flows.append(flow)

        else:
            flows.append(row.get("Volumenstrom (m³/h)", 0))

    df["Volumenstrom (m³/h)"] = flows

    return df


def check_moisture_protection(q_req, q_ab):

    if q_ab >= q_req:
        return True
    return False
