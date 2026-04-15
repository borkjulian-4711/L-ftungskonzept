import math
import networkx as nx
from logic.din1946 import calc_feuchteschutz
from logic.din18017 import get_abluft


# -----------------------------
# Grundberechnung
# -----------------------------
def calculate_ventilation(df_rooms, ANE, fWS):

    df_rooms["Abluft (m³/h)"] = df_rooms.apply(
        lambda row: get_abluft(row["Kategorie"], row["DIN 18017 Kategorie"])
        if row["Innenliegend"] else 0,
        axis=1
    )

    q_required = calc_feuchteschutz(ANE, fWS)
    q_abluft = df_rooms["Abluft (m³/h)"].sum()
    delta = q_required - q_abluft

    return q_required, q_abluft, delta, df_rooms


# -----------------------------
# ALD
# -----------------------------
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


# -----------------------------
# Luftgraph
# -----------------------------
def build_airflow_graph(df_rooms):

    G = nx.DiGraph()

    rooms = df_rooms["Raum"].tolist()

    for r in rooms:
        G.add_node(r)

    # einfache automatische Verbindung (linear)
    for i in range(len(rooms)-1):
        G.add_edge(rooms[i], rooms[i+1])

    return G


# -----------------------------
# Luftpfade prüfen
# -----------------------------
def check_airflow(G, df_rooms):

    supply = df_rooms[df_rooms["Typ"] == "Zuluft"]["Raum"].tolist()
    exhaust = df_rooms[df_rooms["Typ"] == "Abluft"]["Raum"].tolist()

    valid_paths = []
    missing = []

    for s in supply:
        found = False
        for e in exhaust:
            try:
                path = nx.shortest_path(G, s, e)
                valid_paths.append(path)
                found = True
            except:
                continue

        if not found:
            missing.append(s)

    return valid_paths, missing


# -----------------------------
# ÜLD entlang Pfad
# -----------------------------
def calculate_uld_from_graph(G, paths, df_rooms):

    q_uld = 30

    edge_load = {}

    # Lasten sammeln
    for path in paths:
        for i in range(len(path)-1):
            edge = (path[i], path[i+1])

            if edge not in edge_load:
                edge_load[edge] = 0

            edge_load[edge] += 30  # pauschal

    # ÜLD berechnen
    uld_edges = {}
    total = 0

    for edge, q in edge_load.items():
        n = max(1, math.ceil(q / q_uld))
        uld_edges[edge] = n
        total += n

    return total, uld_edges
