import networkx as nx

def run_checks(df_rooms, G, results):

    errors = []
    warnings = []

    for _, r in df_rooms.iterrows():

        if r["Typ"] == "Abluft":

            if r["Innenliegend"] and not r["DIN 18017 Kategorie"]:
                errors.append(f"{r['Raum']}: keine DIN 18017 Kategorie")

    supply = df_rooms[df_rooms["Typ"] == "Zuluft"]["Raum"]
    exhaust = df_rooms[df_rooms["Typ"] == "Abluft"]["Raum"]

    for s in supply:
        if not any(nx.has_path(G, s, e) for e in exhaust):
            errors.append(f"{s}: keine Verbindung zu Abluftraum")

    if results["delta"] > 0:
        warnings.append("Feuchteschutz nicht erfüllt")

    return errors, warnings
