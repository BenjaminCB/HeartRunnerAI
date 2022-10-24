import networkx as nx
from .types import *
from geopy.distance import great_circle

def heuristic(node_a: Intersection, node_b: Intersection):
    return great_circle(node_a.coords(), node_b.coords()).meters


class Pathfinder:

    def __init__(self, patient: Patient):
        self.paths: list[tuple[Runner, Path, list[Path]]] = []
        self.patient = patient
        self.graph = nx.Graph()
        self.nodes: dict[int, Intersection] = {}
        self.edges: dict[int, Streetsegment] = {}
        self.aeds: dict[Intersection, list[AED]] = {}
        self.runners: dict[Intersection, list[Runner]] = {}

    def get_node(self, node_id: int):
        if node_id in self.nodes:
            return self.nodes[node_id]

    def get_nodes(self):
        return list(self.nodes.values())

    def add_edge(self, edge: Streetsegment):
        self.edges[edge.id] = edge
        self.nodes[edge.source.id] = edge.source
        self.nodes[edge.target.id] = edge.target
        self.graph.add_edge(edge.source, edge.target,
                            id=edge.id, weight=edge.length)

    def get_edge(self, edge_id: int):
        if edge_id in self.edges:
            return self.edges[edge_id]

    def get_edges(self):
        return list(self.edges.values())

    def add_aed(self, aed: AED):
        location = self.get_node(aed.intersection_id)
        if not location: return

        if location not in self.aeds:
            self.aeds[location] = [aed]
        else:
            self.aeds[location].append(aed)

    def get_aeds(self):
        return [aed for aeds in self.aeds.values() for aed in aeds]

    def add_runner(self, runner: Runner):
        location = self.get_node(runner.intersection_id)
        if not location: return

        if location not in self.runners:
            self.runners[location] = [runner]
        else:
            self.runners[location].append(runner)

    def compute_paths(self, n_runners: int = None, n_aeds: int = None):
        def to_path(nx_path: list[Intersection], aed=None):
            source = nx_path[0]
            target = nx_path[-1]
            edges = []
            if len(nx_path) > 0:
                for u, v in zip(nx_path, nx_path[1:]):
                    edge_id = self.graph[u][v]["id"]
                    edges.append(self.get_edge(edge_id))
            return Path(source=source, target=target, streets=edges, aed=aed)

        # Clear tasks
        self.paths = []

        # Get target intersection
        target = self.get_node(self.patient.intersection_id)
        
        # Limit amount of runner/aed paths to find (default is no limit)
        a_limit = isinstance(n_aeds, int)
        r_limit = isinstance(n_runners, int)
        r_i = 0

        # Sort runners by shortest heuristic distance to the target and iterate through them
        r_closest = sorted(self.runners, key=lambda x: heuristic(x, target))
        for r_source in r_closest:
            if r_limit and r_i >= n_runners: break
            
            try:
                patient_path = to_path(nx.astar_path(self.graph, r_source, target, heuristic))
            except nx.NetworkXNoPath:
                continue
            
            a_i = 0
            # Sort aeds by shortest summed heuristic distance between aed-runner and aed-target and iterate through them
            a_closest = sorted(self.aeds, key=lambda x: heuristic(x, r_source)+heuristic(x, target))
            aed_paths = []
            for a_source in a_closest:
                if a_limit and a_i >= n_aeds: break
                
                try:
                    rtoa = to_path(nx.astar_path(self.graph, r_source, a_source, heuristic))
                    atop = to_path(nx.astar_path(self.graph, a_source, target, heuristic))
                    aed_path = rtoa+atop
                except nx.NetworkXNoPath:
                    continue
                
                for aed in self.aeds[a_source]:
                    if a_i >= n_aeds: break
                    aed_path.aed = aed
                    aed_paths.append(aed_path)
                    a_i += 1
                
            for runner in self.runners[r_source]:
                if r_i >= n_runners: break
                self.paths.append((runner, patient_path, aed_paths))
                r_i += 1
        
        return self.paths
