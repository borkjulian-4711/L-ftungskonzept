import pandas as pd


def build_air_network(df):

    edges = []

    for _, row in df.iterrows():

        src = row["Raum"]
        dst = row.get("Überströmt nach", "")

        if dst:
            edges.append((src, dst))

    return edges


def calculate_flows(df):

    df = df.copy()

    flows = {r: 0 for r in df["Raum"]}

    # Start: Zuluft
    for _, row in df.iterrows():
        if row["Typ"] == "Zuluft":
            flows[row["Raum"]] = row["Volumenstrom (m³/h)"]

    return flows


def propagate_flows(df):

    df = df.copy()
    flows = calculate_flows(df)

    changed = True

    while changed:
        changed = False

        for _, row in df.iterrows():

            src = row["Raum"]
            dst = row.get("Überströmt nach", "")

            if dst:

                flow = flows.get(src, 0)

                if flow > 0:
                    prev = flows.get(dst, 0)
                    flows[dst] = prev + flow
                    changed = True

                    # nur einmal weitergeben
                    flows[src] = 0

    return flows


def calculate_uld(flows, df):

    uld = {}

    for _, row in df.iterrows():

        src = row["Raum"]
        dst = row.get("Überströmt nach", "")

        if dst:

            flow = flows.get(dst, 0)

            # 1 ÜLD ≈ 30 m³/h
            n = max(1, int(flow / 30) + 1)

            uld[(src, dst)] = {
                "Volumenstrom": flow,
                "Anzahl": n
            }

    return uld
