import itertools
from random import randrange

class Aed:
    def __init__(self, id, intersection_id, time_range, in_use = 'false'):
        self.id = id
        self.start_hour, self.close_hour = time_range
        self.intersection_id = intersection_id
        self.in_use = in_use
        self.csv = [self.id, self.intersection_id, self.in_use, self.start_hour, self.close_hour]

class Runner:
    id_iter = itertools.count(1)

    def __init__(self, id = None, speed = None):
        self.id = next(self.id_iter) if id == None else id
        self.speed = randrange(3,6) if speed == None else speed

    def create_node(self):
        return f"CREATE (p:Runner {{id: {self.id}, speed: {self.speed}}})"
    
    def row2runner(row):
        return {"id": row["p"]["id"], "speed": row["p"]["speed"]}

class Patient:
    id_iter = itertools.count(1)

    def __init__(self, id = None):
        self.id = next(self.id_iter) if id == None else id

    def create_node(self):
        return f"CREATE (p:Patient {{id: {self.id}}})"

    def row2patient(row):
        return {"id": row["p"]["id"]}

class Intersection:
    id_iter = itertools.count(1)

    def __init__(self, coord, id = None):
        self.id = next(self.id_iter) if id == None else id
        self.longitude, self.latitude = coord
        self.csv = [self.id, self.latitude, self.longitude]

class StreetSegment:
    def __init__(self, id, head_id, tail_id, length):
        self.id = id
        self.head_intersection_id = head_id
        self.tail_intersection_id = tail_id
        self.length = length
        self.csv = [self.id, self.head_intersection_id,
                    self.tail_intersection_id, self.length]