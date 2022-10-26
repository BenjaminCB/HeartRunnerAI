from math import ceil
import geojson
import itertools
import random
from enum import Enum
from neo4j import Record


class NodeType(Enum):
    Intersection = 1
    AED = 2
    Runner = 3
    Patient = 4


_TIMERANGES = [(0, 2359), (900, 1700), (600, 2300), (300, 1200), (2000, 400)]
_TIMERANGES_PROB = [0.4, 0.3, 0.2, 0.05, 0.05]


class Intersection:
    id_iter = itertools.count(1)

    def __init__(self, coords: tuple, id=None):
        self.id = next(self.id_iter) if id == None else id
        self.latitude, self.longitude = coords

    def __hash__(self) -> int:
        return hash((self.id, self.coords()))

    def __eq__(self, __o: object) -> bool:
        return (
            isinstance(__o, Intersection) and
            self.id == __o.id and
            self.coords() == __o.coords()
        )

    def __repr__(self) -> str:
        return f"Intersection({self.id})"

    @staticmethod
    def from_record(record: Record):
        id = record['n']['id']
        lat = record['n']['latitude']
        lon = record['n']['longitude']
        return Intersection(id=id, coords=(lat, lon))

    def coords(self):
        return (self.latitude, self.longitude)

    def geojson(self, style={}):
        properties = {
            "type": "Intersection",
            "id": self.id
        }
        properties.update(style)

        return geojson.Feature(
            geometry=geojson.Point((self.longitude, self.latitude)),
            properties=properties
        )


class Streetsegment:
    id_iter = itertools.count(1)

    def __init__(
        self,
        id: int = None,
        source: Intersection = None,
        target: Intersection = None,
        length: float = None,
        geometry: str = None
    ):
        self.id = next(self.id_iter) if id == None else id
        self.source = source
        self.target = target
        self.length = length
        self.geometry = geojson.loads(geometry)

    def __hash__(self) -> int:
        return hash((self.id, self.source, self.target, self.length))

    def __eq__(self, __o: object) -> bool:
        return (
            isinstance(__o, Streetsegment) and
            self.id == __o.id and
            self.source == __o.source and
            self.target == __o.target and
            self.length == __o.length
        )

    def __repr__(self) -> str:
        return f"Streetsegment({self.id}, {self.source} <--> {self.target}, {self.length}m)"

    def geojson(self, style={}):
        properties = {
            "type": "Streetsegment",
            "id": self.id,
            "length": self.length,
        }
        properties.update(style)

        return geojson.Feature(
            id=self.id,
            geometry=self.geometry,
            properties=properties
        )


class AED:
    id_iter = itertools.count(1)

    def __init__(self, id=None, intersection_id=None, time_range=None, in_use='false'):
        self.id = next(self.id_iter) if id == None else id
        if time_range == None:
            time_range = random.choices(_TIMERANGES, _TIMERANGES_PROB)[0]
        self.open_hour, self.close_hour = time_range
        self.intersection_id = intersection_id
        self.in_use = in_use

    def __repr__(self) -> str:
        return f"A({self.id})"

    @staticmethod
    def from_record(record: Record):
        id = record['n']['id']
        open_hour = record['n']['open_hour']
        close_hour = record['n']['close_hour']
        in_use = record['n']['in_use']
        intersection_id = record['m']['id']
        return AED(
            id=id,
            intersection_id=intersection_id,
            time_range=(open_hour, close_hour),
            in_use=in_use
        )

    def geojson(self, location: Intersection, style={}):
        properties = {
            "type": "AED",
            "id": self.id,
            "in_use": self.in_use,
            "open_hour": self.open_hour,
            "close_hour": self.close_hour
        }
        properties.update(style)

        return geojson.Feature(
            geometry=geojson.Point((location.longitude, location.latitude)),
            properties=properties
        )


class Runner:
    id_iter = itertools.count(1)

    def __init__(self, id=None, speed=None, intersection_id=None):
        self.id = next(self.id_iter) if id == None else id
        self.speed = random.random()*3+3 if speed == None else speed
        self.intersection_id = intersection_id

    def __repr__(self) -> str:
        return f"R({self.id})"

    @staticmethod
    def from_record(record: Record):
        id = record['n']['id']
        speed = record['n']['speed']
        intersection_id = record['m']['id']
        return Runner(id=id, speed=speed, intersection_id=intersection_id)

    def geojson(self, location: Intersection, style={}):
        properties = {
            "type": "Runner",
            "id": self.id,
            "speed": self.speed
        }
        properties.update(style)

        return geojson.Feature(
            geometry=geojson.Point((location.longitude, location.latitude)),
            properties=properties
        )


class Patient:
    id_iter = itertools.count(1)

    def __init__(self, id=None, intersection_id=None):
        self.id = next(self.id_iter) if id == None else id
        self.intersection_id = intersection_id

    def __repr__(self) -> str:
        return f"P({self.id})"

    @staticmethod
    def from_record(record: Record):
        id = record['n']['id']
        intersection_id = record['m']['id']
        return Patient(id=id, intersection_id=intersection_id)

    def geojson(self, location: Intersection, style={}):
        properties = {
            "type": "Patient",
            "id": self.id
        }
        properties.update(style)

        return geojson.Feature(
            geometry=geojson.Point((location.longitude, location.latitude)),
            properties=properties
        )


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

    def eta(self, runner: Runner):
        return ceil(self.length/runner.speed)

    def is_aed_path(self):
        return True if isinstance(self.aed, AED) else False

    def geojson(self, style={}):
        return [street.geojson(style=style) for street in self.streets]
