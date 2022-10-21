import networkx as nx
from .types import *
from geopy.distance import great_circle


def heuristic(node_a: Intersection, node_b: Intersection):
    return great_circle(node_a.coords(), node_b.coords()).meters


class Path:
    def __init__(self, source: Intersection, target: Intersection, streets: list[Streetsegment]):
        self.source = source
        self.target = target
        self.streets = streets
        self.length = sum([s.length for s in streets])

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

    def geojson(self, style={}):
        return [street.geojson(style=style) for street in self.streets]


class Task:
    def __init__(self, runner: Runner, path: Path, aed: AED = None):
        self.runner = runner
        self.path = path
        self.cost = path.length/runner.speed
        self.aed = aed

    def is_aed_task(self):
        return True if isinstance(self.aed, AED) else False


class Pathfinder:

    def __init__(self, patient: Patient):
        self.graph = nx.Graph()
        self.nodes: dict[int, Intersection] = {}
        self.edges: dict[int, Streetsegment] = {}
        self.aeds: dict[Intersection, list[AED]] = {}
        self.runners: dict[Intersection, list[Runner]] = {}
        self.patient = patient
        self.tasks: dict[Runner, tuple[Task, list[Task]]] = {}

    def add_node(self, node: Intersection):
        self.nodes[node.id] = node
        self.graph.add_node(node)

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

    def calculate_tasks(self, n_runners: int = None, n_aeds: int = None):
        def to_path(nx_path: list[Intersection]):
            source = nx_path[0]
            target = nx_path[-1]
            edges = []
            if len(nx_path) > 0:
                for u, v in zip(nx_path, nx_path[1:]):
                    edge_id = self.graph[u][v]["id"]
                    edges.append(self.get_edge(edge_id))
            return Path(source=source, target=target, streets=edges)

        target = self.get_node(self.patient.intersection_id)
        a_limit = isinstance(n_aeds, int)
        r_limit = isinstance(n_runners, int)
        r_i = 0
        r_closest = sorted(self.runners, key=lambda x: heuristic(x, target))
        for r_source in r_closest:
            if r_limit and r_i > n_runners:
                break
            try:
                rtop = to_path(nx.astar_path(
                    self.graph, r_source, target, heuristic))
            except nx.NetworkXNoPath:
                continue
            for runner in self.runners[r_source]:
                self.tasks[runner] = (Task(runner, rtop), [])
                r_i += 1

            a_i = 0
            a_closest = sorted(self.aeds, key=lambda x: heuristic(
                x, r_source)+heuristic(x, target))
            for a_source in a_closest:
                if a_limit and a_i > n_aeds:
                    break
                try:
                    rtoa = to_path(nx.astar_path(
                        self.graph, r_source, a_source, heuristic))
                    atop = to_path(nx.astar_path(
                        self.graph, a_source, target, heuristic))
                    rtoatop = rtoa + atop
                except nx.NetworkXNoPath:
                    continue
                for aed in self.aeds[a_source]:
                    # TODO: filter aeds based on time/availability
                    for runner in self.runners[r_source]:
                        self.tasks[runner][1].append(
                            Task(runner, rtoatop, aed))
                    a_i += 1
