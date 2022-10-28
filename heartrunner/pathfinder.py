import networkx as nx
from .types import *
from geopy.distance import great_circle


def heuristic(node_a: Intersection, node_b: Intersection):
    return great_circle(node_a.coords(), node_b.coords()).meters


class Path:
    def __init__(self, source: Intersection, target: Intersection, streets: list[Streetsegment], aed: AED = None):
        self.source = source
        self.target = target
        self.streets = streets
        self.length = sum([s.length for s in streets])
        self.aed = aed

    def __add__(self, p):
        source = self.source
        target = p.target
        path = self.streets + p.streets
        return Path(source=source, target=target, streets=path)

    def __repr__(self) -> str:
        rep = f"Path({self.source} -> {self.target}, {self.length}m):\n"
        for street in self.streets:
            rep += f"{street}\n"
        return rep

    def is_aed_path(self):
        return True if isinstance(self.aed, AED) else False

    def geojson(self, style={}):
        return [street.geojson(style=style) for street in self.streets]


class Task:
    def __init__(
        self, 
        runner: Runner, 
        patient_path: Path, 
        aed_paths: list[Path]
    ):
        self.runner = runner
        self.patient_path = patient_path
        self.patient_latency = self._latency(patient_path)
        self.aed_paths = aed_paths
        self.aed_latencies = [self._latency(aed_path) for aed_path in aed_paths]

    def _latency(self, path: Path):
        return path.length/self.runner.speed


class Pathfinder:

    def __init__(self, patient: Patient):
        self.tasks: list[Task] = []
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
        location = self.get_node(aed.intersection_id)
        if not location: return

        if location not in self._aeds:
            self._aeds[location] = [aed]
        else:
            self._aeds[location].append(aed)

    def get_aeds(self):
        return [aed for aeds in self._aeds.values() for aed in aeds]

    def add_runner(self, runner: Runner):
        location = self.get_node(runner.intersection_id)
        if not location: return

        if location not in self._runners:
            self._runners[location] = [runner]
        else:
            self._runners[location].append(runner)

    def get_runners(self):
        return [runner for runners in self._runners.values() for runner in runners]

    def calculate_tasks(self, n_runners: int = None, n_aeds: int = None):
        def to_path(nx_path: list[Intersection], aed=None):
            source = nx_path[0]
            target = nx_path[-1]
            edges = []
            if len(nx_path) > 0:
                for u, v in zip(nx_path, nx_path[1:]):
                    edge_id = self._graph[u][v]["id"]
                    edges.append(self.get_edge(edge_id))
            return Path(source=source, target=target, streets=edges, aed=aed)

        # Remove previous tasks, if any
        self.tasks = []

        # Get target intersection
        target = self.get_node(self._patient.intersection_id)
        
        # Limit amount of runner/aed paths to find (default is no limit)
        a_limit = isinstance(n_aeds, int)
        r_limit = isinstance(n_runners, int)
        r_i = 0

        # Sort runners by shortest heuristic distance to the target
        r_closest = sorted(self._runners, key=lambda x: heuristic(x, target))
        for r_source in r_closest:
            if r_limit and r_i >= n_runners: break
            
            try:
                patient_path = to_path(nx.astar_path(self._graph, r_source, target, heuristic))
            except nx.NetworkXNoPath:
                continue
            
            a_i = 0
            # Sort aeds by shortest summed heuristic distance between aed-runner and aed-target
            a_closest = sorted(self._aeds, key=lambda x: heuristic(x, r_source)+heuristic(x, target))
            aed_paths = []
            for a_source in a_closest:
                if a_limit and a_i >= n_aeds: break
                
                try:
                    rtoa = to_path(nx.astar_path(self._graph, r_source, a_source, heuristic))
                    atop = to_path(nx.astar_path(self._graph, a_source, target, heuristic))
                    aed_path = rtoa+atop
                except nx.NetworkXNoPath:
                    continue
                
                for aed in self._aeds[a_source]:
                    if a_i >= n_aeds: break
                    aed_path.aed = aed
                    aed_paths.append(aed_path)
                    a_i += 1
                
            for runner in self._runners[r_source]:
                if r_i >= n_runners: break
                self.tasks.append(Task(runner, patient_path, aed_paths))
                r_i += 1
        
        return self.tasks
