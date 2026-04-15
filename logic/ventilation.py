import math
import networkx as nx
from logic.din1946 import calc_feuchteschutz
from logic.din18017 import get_abluft


# -----------------------------
# Hilfsfunktion Kategorie
# -----------------------------
def clean_category(cat):
    if not cat:
        return ""
    return cat.split(" ")[0]


# -----------------------------
# Hauptberechnung
# -----------------------------
def calculate_ventilation(df_rooms, ANE, fWS):

    df_rooms = df_rooms.copy()

    df_rooms["Abluft (m³/h)"] = df_rooms.apply(
        lambda row: get_abluft(
            row["Kategorie"],
            clean_category(row["DIN 18017 Kategorie"])
        )
        if row["Innenliegend"] and row["Typ"] == "Abluft"
        else 0,
        axis=1
    )

    q_required = calc_feuchteschutz(ANE, fWS)
    q_abluft = df_rooms["Abluft (m³/h)"].sum()
    delta = q_required - q_abluft

    return q_required, q_abluft, delta, df_rooms


# -----------------------------
# ALD
# -----------------------------
def calculate_ald(delta):
    if delta <= 0:
        return 0
    return math.ceil(delta / 30)


# -----------------------------
# Graph aus Raumtabelle
# -----------------------------
def build_graph_from_rooms(df_rooms):

    G = nx.DiGraph()

    # Nodes
    for r in df_rooms["Raum"]:
        if r:
            G.add_node(r)

    # Verbindungen
    for _, row in df_rooms.iterrows():

        src = row["Raum"]
        dst = row.get("Überströmt nach", "")

        if src and dst:
            G.add_edge(src, dst)

    return G


# -----------------------------
# Luftpfade
# -----------------------------
def calculate_paths(G, df_rooms):

    supply = df_rooms[df_rooms["Typ"] == "Zuluft"]["Raum"]
    exhaust = df_rooms[df_rooms["Typ"] == "Abluft"]["Raum"]

    paths = []

    for s in supply:
        for e in exhaust:

            if s not in G.nodes or e not in G.nodes:
                continue

            try:
                if nx.has_path(G, s, e):
                    paths.append(nx.shortest_path(G, s, e))
            except:
                continue

    return paths


# -----------------------------
# ÜLD direkt aus Verbindungen
# -----------------------------
def calculate_uld_from_graph(G, df_rooms, paths):

    q_per_uld = 30  # m³/h pro ÜLD

    # -----------------------------
    # Abluftströme je Raum
    # -----------------------------
    room_flows = {
        row["Raum"]: row["Abluft (m³/h)"]
        for _, row in df_rooms.iterrows()
    }

    # -----------------------------
    # Lasten je Verbindung sammeln
    # -----------------------------
    edge_flow = {}

    for path in paths:

        # Ziel = Abluftraum
        end_room = path[-1]
        q = room_flows.get(end_room, 0)

        for i in range(len(path) - 1):

            edge = (path[i], path[i + 1])

            if edge not in edge_flow:
                edge_flow[edge] = 0

            edge_flow[edge] += q

    # -----------------------------
    # ÜLD berechnen
    # -----------------------------
    uld_edges = {}
    total = 0

    for edge, q in edge_flow.items():

        n = max(1, math.ceil(q / q_per_uld))

        uld_edges[edge] = {
            "Volumenstrom": round(q, 1),
            "Anzahl": n
        }

        total += n

    return total, uld_edges
