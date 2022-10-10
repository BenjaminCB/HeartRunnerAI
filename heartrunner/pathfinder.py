import math
import heapq
from .types import *
from collections import deque
from geopy.distance import great_circle


class Graph:
    nodes: dict[int, Intersection]
    adj_list: dict[Intersection, list[tuple[Streetsegment, Intersection]]]
    runners: dict[Intersection, list[Runner]]
    aeds: dict[Intersection, list[AED]]

    def __init__(self):
        self.nodes = {}
        self.adj_list = {}
        self.runners = {}
        self.aeds = {}

    def add_edge(self, u: Intersection, v: Intersection, e: Streetsegment):
        if u.id not in self.nodes:
            self.nodes[u.id] = u
            self.adj_list[u] = []
        if v.id not in self.nodes:
            self.nodes[v.id] = v
            self.adj_list[v] = []

        if (e, v) not in self.adj_list[u]:
            self.adj_list[u].append((e, v))
        if (e, u) not in self.adj_list[v]:
            self.adj_list[v].append((e, u))

    def add_aed(self, intersection: Intersection, aed: AED):
        if intersection not in self.aeds:
            self.aeds[intersection] = []
        self.aeds[intersection].append(aed)

    def add_runner(self, intersection: Intersection, runner: Runner):
        if intersection not in self.runners:
            self.runners[intersection] = []
        self.runners[intersection].append(runner)


class Path:
    def __init__(
        self,
        start: Intersection,
        goal: Intersection,
        length: int,
        path: list[tuple[Intersection, Streetsegment]]
    ):
        self.start = start
        self.goal = goal
        self.length = length
        self.path = path

    def __str__(self) -> str:
        res = ""
        for p in self.path:
            res += f"{p[0].id} -> "
        res += str(self.goal.id)
        return res


class Pathfinder:
    graph: Graph
    patient: Patient
    aed_paths: list[tuple[Path, Path]]
    patient_paths: list[Path]

    def __init__(self, patient: Patient, graph: Graph):
        self.graph = graph
        self.patient = patient
        self.patient_paths = []
        self.aed_paths = []

        patient_location = graph.nodes[patient.intersection_id]
        shortest = math.inf
        for aed_location in graph.aeds:
            aed_path = shortest_path(aed_location, patient_location, graph)
            if aed_path is None:
                continue
            if aed_path.length < shortest:
                shortest = aed_path.length
                aed_to_patient = aed_path

        for runner_location in graph.runners:
            runner_to_patient = shortest_path(
                runner_location, patient_location, graph)
            if runner_to_patient is not None:
                self.patient_paths.append(runner_to_patient)

            runner_to_aed = shortest_path(
                runner_location, aed_to_patient.start, graph)
            if runner_to_aed is not None:
                self.aed_paths.append((runner_to_aed, aed_to_patient))


def shortest_path(
    start: Intersection,
    goal: Intersection,
    graph: Graph
):
    came_from = {}
    opened = [(heuristic(start, goal), start)]
    g_cost = {node: math.inf for node in graph.adj_list}
    g_cost[start] = 0
    while len(opened) > 0:
        current = heapq.heappop(opened)[1]

        if current == goal:
            path = deque()
            length = 0
            while current in came_from:
                current, edge = came_from[current]
                length += edge.length
                path.appendleft((current, edge))
            return Path(start, goal, length, path)

        for adj in graph.adj_list[current]:
            edge, neighbour = adj
            g = g_cost[current] + edge.length
            if g < g_cost[neighbour]:
                came_from[neighbour] = (current, edge)
                g_cost[neighbour] = g
                f = g + heuristic(neighbour, goal)
                if (f, neighbour) not in opened:
                    heapq.heappush(opened, (f, neighbour))
    return None


def heuristic(node_a: Intersection, node_b: Intersection):
    return great_circle(node_a.coords(), node_b.coords()).meters
