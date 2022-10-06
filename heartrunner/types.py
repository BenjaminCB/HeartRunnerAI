import itertools
from enum import Enum
from random import randrange

class NodeType(Enum):
    Intersection = 1
    AED = 2
    Runner = 3
    Patient = 4

class AED:
    def __init__(self, id, intersection_id, time_range, in_use = 'false'):
        self.id = id
        self.open_hour, self.close_hour = time_range
        self.intersection_id = intersection_id
        self.in_use = in_use
        self.csv = [self.id, self.intersection_id, self.in_use, self.open_hour, self.close_hour]

class Runner:
    id_iter = itertools.count(1)

    def __init__(self, id = None, speed = None, intersection_id = None):
        self.id = next(self.id_iter) if id == None else id
        self.speed = randrange(3,6) if speed == None else speed
        self.intersection_id = intersection_id

    @staticmethod
    def batch_merge_query() -> str:
        return (
            "UNWIND $batch AS row "
            "MATCH (i:Intersection) WHERE i.id = row.intersection_id "
            "MERGE (r:Runner {id: row.id, speed: row.speed})-[:LocatedAt]->(i) "
        )

class Patient:
    id_iter = itertools.count(1)

    def __init__(self, id = None, intersection_id = None):
        self.id = next(self.id_iter) if id == None else id
        self.intersection_id = intersection_id

    @staticmethod
    def batch_merge_query() -> str:
        return (
            "UNWIND $batch AS row "
            "MATCH (i:Intersection) WHERE i.id = row.intersection_id "
            "MERGE (p:Patient {id: row.id})-[:LocatedAt]->(i) "
        )

class Intersection:
    id_iter = itertools.count(1)

    def __init__(self, coord, id = None):
        self.id = next(self.id_iter) if id == None else id
        self.longitude, self.latitude = coord
        self.csv = [self.id, self.latitude, self.longitude]

class Streetsegment:
    def __init__(self, id, head_id, tail_id, length):
        self.id = id
        self.head_intersection_id = head_id
        self.tail_intersection_id = tail_id
        self.length = length
        self.csv = [self.id, self.head_intersection_id,
                    self.tail_intersection_id, self.length]