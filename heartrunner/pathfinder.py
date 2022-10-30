import networkx as nx
from heartrunner.types import *
from heartrunner.settings import *
from geopy.distance import great_circle

def heuristic(node_a: Intersection, node_b: Intersection):
    return great_circle(node_a.coords(), node_b.coords()).meters

class Pathfinder:

    def __init__(
        self, 
        patient: Patient 
    ):
        self.paths: list[tuple[Runner, Path, list[Path]]] = []
        self.patient_paths: list[Path] = []
        self._patient = patient
        self._graph = nx.Graph()
        self._nodes: dict[int, Intersection] = {}
        self._edges: dict[int, Streetsegment] = {}
        self._aeds: dict[Intersection, list[AED]] = {}
        self._runners: dict[Intersection, list[Runner]] = {}

    def add_node(self, node: Intersection):
        self._nodes[node.id] = node
        self._graph.add_node(node)

    def get_node(self, node_id: int):
        if node_id in self._nodes:
            return self._nodes[node_id]

    def get_nodes(self):
        return list(self._nodes.values())

    def add_edge(self, edge: Streetsegment):
        self._edges[edge.id] = edge
        self._nodes[edge.source.id] = edge.source
        self._nodes[edge.target.id] = edge.target
        self._graph.add_edge(edge.source, edge.target,
                            id=edge.id, weight=edge.length)

    def get_edge(self, edge_id: int):
        if edge_id in self._edges:
            return self._edges[edge_id]

    def get_edges(self):
        return list(self._edges.values())

    def add_aed(self, aed: AED):
        if aed.intersection not in self._aeds:
            self._aeds[aed.intersection] = {aed}
        else:
            self._aeds[aed.intersection].add(aed)

    def get_aeds(self):
        return [aed for aeds in self._aeds.values() for aed in aeds]

    def add_runner(self, runner: Runner):
        if runner.intersection not in self._runners:
            self._runners[runner.intersection] = {runner}
        else:
            self._runners[runner.intersection].add(runner)

    def get_runners(self):
        return [runner for runners in self._runners.values() for runner in runners]

    def compute_paths(self):
        def to_path(nx_path: list[Intersection]):
            source = nx_path[0]
            target = nx_path[-1]
            edges = []
            if len(nx_path) > 0:
                for u, v in zip(nx_path, nx_path[1:]):
                    edge_id = self._graph[u][v]["id"]
                    edges.append(self.get_edge(edge_id))
            return Path(source=source, target=target, streets=edges)

        # Remove any previous paths
        self.paths = []

        # Get target intersection
        target = self.get_node(self._patient.intersection.id)    

        # Sort runners by shortest heuristic distance to the target
        r_closest = sorted(self._runners, key=lambda x: heuristic(x, target))
        r_i = 0
        for r_source in r_closest:
            if r_i >= CANDIDATE_RUNNERS: break
            
            try:
                patient_path = to_path(nx.astar_path(self._graph, r_source, target, heuristic))
            except nx.NetworkXNoPath:
                continue
            
            a_i = 0
            # Sort aeds by shortest summed heuristic distance between aed-runner and aed-target
            a_closest = sorted(self._aeds, key=lambda x: heuristic(x, r_source)+heuristic(x, target))
            aed_paths = []
            for a_source in a_closest:
                if a_i >= CANDIDATE_AEDS: break
                
                try:
                    rtoa = nx.astar_path(self._graph, r_source, a_source, heuristic)
                    atop = nx.astar_path(self._graph, a_source, target, heuristic)
                    aed_path = to_path(rtoa+atop[1:])
                except nx.NetworkXNoPath:
                    continue
                
                for aed in self._aeds[a_source]:
                    if a_i >= CANDIDATE_AEDS: break
                    aed_path.assign_aed(aed)
                    aed_paths.append(aed_path)
                    a_i += 1

            for runner in self._runners[r_source]:
                if r_i >= CANDIDATE_RUNNERS: break
                self.paths.append((runner, patient_path, aed_paths))

                patient_path.assign_runner(runner)
                self.patient_paths.append(patient_path)

                r_i += 1
        
        return self.paths
