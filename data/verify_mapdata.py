import csv
import json
import sys
from typing import Dict, List
from generate_mapdata import STREETS_PATH

GRAPH_JSON_PATH = "./graph/mapdata_graph.json"

def generate_graph():
    with (
        open(STREETS_PATH, "r") as street_file,
        open(GRAPH_JSON_PATH, "w+") as graph_file
    ):
        nodes = []
        edges = []
        adj_list = {}
        street_reader = csv.reader(street_file)
        next(street_reader)
        print("Parsing StreetSegment.csv")
        for street_row in street_reader:
            id_a = street_row[1]
            id_b = street_row[2]
            edges.append((id_a, id_b))
            if id_a not in nodes:
                nodes.append(id_a)
            if id_b not in nodes:
                nodes.append(id_b)
        print("Generating adjacency list")
        n = 1
        for node in nodes:
            print(n/len(nodes)*100)
            n += 1
            adj_list[node] = []
            for edge in edges:
                if edge[0] == node:
                    adj_list[node].append(edge[1])
                if edge[1] == node:
                    adj_list[node].append(edge[0])
        json.dump((nodes, edges, adj_list), graph_file)

def dfs(nodes, adj_list, v):
    print(f"Depth-first search from node: {v}")
    visited = []
    to_visit = [v]
    while len(to_visit) > 0:
        node = to_visit.pop()
        if node not in visited:
            visited.append(node)
            for adjacent in adj_list[node]:
                to_visit.append(adjacent)
    return visited

if __name__ == "__main__":
    if "-g" in sys.argv:
        generate_graph()

    with open(GRAPH_JSON_PATH, "r") as graph_file:
        data = json.load(graph_file)
        nodes = data[0]
        edges = data[1]
        adj_list = data[2]

        visited = dfs(nodes, adj_list, nodes[0])
        not_visited = set(nodes)-set(visited)
        disconnected = []
        for node in not_visited:
            for graph in disconnected:
                if node in graph:
                    break
            else:
                disconnected.append(dfs(nodes, adj_list, node))

        print("Listing all disconnected graphs:")
        for graph in disconnected:
            print(graph)
