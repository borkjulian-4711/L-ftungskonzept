import math

def distance(a, b):
    return math.sqrt((a["x"]-b["x"])**2 + (a["y"]-b["y"])**2)

def auto_connect_rooms(rooms, max_dist=300):

    edges = []

    for i in range(len(rooms)):
        for j in range(i+1, len(rooms)):

            if distance(rooms[i], rooms[j]) < max_dist:
                edges.append((rooms[i]["name"], rooms[j]["name"]))

    return edges
