import math
import networkx as nx
from logic.din1946 import calc_feuchteschutz
from logic.din18017 import get_abluft


def calculate_ventilation(df_rooms, ANE, fWS):

    df_rooms["Abluft (m³/h)"] = df_rooms.apply(
        lambda row: get_abluft(row["Kategorie"], row["DIN 18017 Kategorie"])
        if row["Innenliegend"] and row["Typ"] == "Abluft"
        else 0,
        axis=1
    )

    q_required = calc_feuchteschutz(ANE, fWS)
    q_abluft = df_rooms["Abluft (m³/h)"].sum()
    delta = q_required - q_abluft

    return q_required, q_abluft, delta, df_rooms


def calculate_ald(delta, df_rooms):

    if delta <= 0:
        return 0, {}

    q_ald = 30
    n_ald = math.ceil(delta / q_ald)

    supply = df_rooms[df_rooms["Typ"] == "Zuluft"]

    dist = {}
    if len(supply) > 0:
        per = math.ceil(n_ald / len(supply))
        for r in supply["Raum"]:
            dist[r] = per

    return n_ald, dist


def build_graph_from_edges(edge_list):

    G = nx.DiGraph()

    for e in edge_list:
        if e[0] and e[1]:
            G.add_edge(e[0], e[1])

    return G


def calculate_paths(G, df_rooms):

    supply = df_rooms[df_rooms["Typ"] == "Zuluft"]["Raum"]
    exhaust = df_rooms[df_rooms["Typ"] == "Abluft"]["Raum"]

    paths = []

    for s in supply:
        for e in exhaust:
            if nx.has_path(G, s, e):
                paths.append(nx.shortest_path(G, s, e))

    return paths


def calculate_uld_from_paths(paths):

    q_uld = 30
    edge_load = {}

    for path in paths:
        for i in range(len(path)-1):

            edge = (path[i], path[i+1])

            if edge not in edge_load:
                edge_load[edge] = 0

            edge_load[edge] += 30

    result = {}
    total = 0

    for edge, q in edge_load.items():
        n = max(1, math.ceil(q / q_uld))
        result[edge] = n
        total += n

    return total, result
