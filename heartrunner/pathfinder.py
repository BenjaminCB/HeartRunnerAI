from typing import Dict, List, Tuple
from .types import *

class Graph:
    nodes: Dict[int, Intersection]
    edges: Dict[int, Streetsegment]
    adj_list: Dict[int, List[Tuple]]
    runners: Dict[int, List[Runner]]
    aeds: Dict[int, List[AED]]
    
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.adj_list = {}
        self.runners = {}
        self.aeds = {}

    def add_node(self, node: Intersection):
        if node.id not in self.nodes:
            self.nodes[node.id] = node
            self.adj_list[node.id] = []

    def add_edge(self, edge: Streetsegment):
        self.edges[edge.id] = edge

        head_id = edge.head_intersection_id
        tail_id = edge.tail_intersection_id
        
        self.adj_list[head_id].append( (edge.id, tail_id) )
        self.adj_list[tail_id].append( (edge.id, head_id) )

    def add_aed(self, aed: AED, intersection_id: int):
        if intersection_id not in self.aeds:
            self.aeds[intersection_id] = []
        self.aeds[intersection_id].append(aed)
    
    def add_runner(self, runner: Runner, intersection_id: int):
        if intersection_id not in self.runners:
            self.runners[intersection_id] = []
        self.runners[intersection_id].append(runner)

class Pathfinder:
    def __init__(self, graph: Graph):
        self.graph = graph
