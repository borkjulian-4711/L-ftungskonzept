import math
import networkx as nx
from logic.din1946 import calc_feuchteschutz
from logic.din18017 import get_abluft


# -----------------------------
# Hilfsfunktion für Kategorie
# -----------------------------
def clean_category(cat):

    if not cat:
        return ""

    return cat.split(" ")[0]  # "R-ZD (40 m³/h)" → "R-ZD"


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
# Graph erstellen
# -----------------------------
def build_graph(df_rooms, df_edges):

    G = nx.DiGraph()

    # alle Räume hinzufügen
    for r in df_rooms["Raum"]:
        if r:
            G.add_node(r)

    # Kanten hinzufügen
    for _, row in df_edges.iterrows():
        if row["Von"] and row["Nach"]:
            G.add_edge(row["Von"], row["Nach"])

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

            # Sicherheitscheck
            if s not in G.nodes or e not in G.nodes:
                continue

            try:
                if nx.has_path(G, s, e):
                    paths.append(nx.shortest_path(G, s, e))
            except:
                continue

    return paths


# -----------------------------
# ÜLD
# -----------------------------
def calculate_uld(paths):

    edges = {}
    total = 0

    for p in paths:
        for i in range(len(p) - 1):

            edge = (p[i], p[i + 1])

            if edge not in edges:
                edges[edge] = 0

            edges[edge] += 1

    # mindestens 1 je Verbindung
    for k in edges:
        edges[k] = max(1, edges[k])

    total = sum(edges.values())

    return total, edges
