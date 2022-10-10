import heapq
import math
from .types import *
from geopy import distance
import timeit

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
            self.adj_list[u].append( (e, v) )
        if (e, u) not in self.adj_list[v]:
            self.adj_list[v].append( (e, u) )

    def add_aed(self, intersection: Intersection, aed: AED):
        if intersection not in self.aeds:
            self.aeds[intersection] = []
        self.aeds[intersection].append(aed)
    
    def add_runner(self, intersection: Intersection, runner: Runner):
        if intersection not in self.runners:
            self.runners[intersection] = []
        self.runners[intersection].append(runner)

class Pathfinder:
    graph: Graph
    patient: Patient
    patient_location: Intersection

    def __init__(self, patient: Patient, graph: Graph):
        self.graph = graph
        self.patient = patient
        self.patient_location = graph.nodes[patient.intersection_id]

        for runner_location in graph.runners:
            start_time = timeit.default_timer()
            self.__shortest_path(runner_location, self.patient_location)
            elapsed = timeit.default_timer() - start_time
            print(elapsed)

    def __heuristic(self, node_a: Intersection, node_b: Intersection):
        return distance.great_circle(node_a.coords(), node_b.coords()).meters

    def __shortest_path(self, start: Intersection, goal: Intersection):
        opened = [ (self.__heuristic(start, goal), start) ]
        came_from = {}
        g_cost = {node: math.inf for node in self.graph.nodes.values()}
        g_cost[start] = 0
        while len(opened) > 0:
            current = heapq.heappop(opened)[1]
            if current == goal:
                path = [current.id]
                while current in came_from.keys():
                    current = came_from[current]
                    path.append(current.id)
                print(list(reversed(path)))

            for adjacent in self.graph.adj_list[current]:
                edge, neighbour = adjacent[0], adjacent[1]
                g = g_cost[current] + edge.length
                if g < g_cost[neighbour]:
                    came_from[neighbour] = current
                    g_cost[neighbour] = g
                    f = g + self.__heuristic(neighbour, goal)
                    if (f, neighbour) not in opened:
                        heapq.heappush(opened, (f, neighbour))


                
