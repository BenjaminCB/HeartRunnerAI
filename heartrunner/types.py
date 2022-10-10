import itertools
from enum import Enum
from neo4j import Record
from random import randrange


class NodeType(Enum):
    Intersection = 1
    AED = 2
    Runner = 3
    Patient = 4


class AED:
    def __init__(self, id, intersection_id, time_range, in_use='false'):
        self.id = id
        self.open_hour, self.close_hour = time_range
        self.intersection_id = intersection_id
        self.in_use = in_use
        self.csv = [self.id, self.intersection_id,
                    self.in_use, self.open_hour, self.close_hour]

    @staticmethod
    def from_record(record: Record):
        id = record['n']['id']
        open_hour = record['n']['open_hour']
        close_hour = record['n']['close_hour']
        in_use = record['n']['in_use']
        intersection_id = record['m']['id']
        return AED(id, intersection_id, (open_hour, close_hour), in_use)


class Runner:
    id_iter = itertools.count(1)

    def __init__(self, id=None, speed=None, intersection_id=None):
        self.id = next(self.id_iter) if id == None else id
        self.speed = randrange(3, 6) if speed == None else speed
        self.intersection_id = intersection_id

    @staticmethod
    def from_record(record: Record):
        id = record['n']['id']
        speed = record['n']['speed']
        intersection_id = record['m']['id']
        return Runner(id, speed, intersection_id)


class Patient:
    id_iter = itertools.count(1)

    def __init__(self, id=None, intersection_id=None):
        self.id = next(self.id_iter) if id == None else id
        self.intersection_id = intersection_id

    @staticmethod
    def from_record(record: Record):
        id = record['n']['id']
        intersection_id = record['m']['id']
        return Patient(id, intersection_id)


class Intersection:
    id_iter = itertools.count(1)

    def __init__(self, coords: tuple, id=None):
        self.id = next(self.id_iter) if id == None else id
        self.latitude, self.longitude = coords
        self.csv = [self.id, self.latitude, self.longitude]

    def __hash__(self) -> int:
        return hash((self.id, self.coords()))

    def __eq__(self, __o: object) -> bool:
        return (
            isinstance(__o, Intersection) and
            self.id == __o.id and
            self.coords() == __o.coords()
        )

    @staticmethod
    def from_record(record: Record):
        id = record['n']['id']
        lat = record['n']['latitude']
        lon = record['n']['longitude']
        return Intersection((lat, lon), id)

    def coords(self) -> tuple:
        return (self.latitude, self.longitude)


class Streetsegment:
    def __init__(self, id, head_id, tail_id, length):
        self.id = id
        self.head_intersection_id = head_id
        self.tail_intersection_id = tail_id
        self.length = length
        self.csv = [self.id, self.head_intersection_id,
                    self.tail_intersection_id, self.length]

    def __hash__(self) -> int:
        return hash((self.id, self.head_intersection_id, self.tail_intersection_id, self.length))

    def __eq__(self, __o: object) -> bool:
        return (
            isinstance(__o, Streetsegment) and
            self.id == __o.id and
            self.head_intersection_id == __o.head_intersection_id and
            self.tail_intersection_id == __o.tail_intersection_id and
            self.length == __o.length
        )
